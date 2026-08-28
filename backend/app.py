from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import os
import tempfile
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from sklearn.metrics import mean_absolute_error, mean_squared_error
import time
from models.arima_predictor import predict_with_arima

from models.prediction_tool import analyze_and_predict
from models.agent_chain import get_conversational_response, generate_standalone_report
from agent.reasoner import TSReasoner
from agent.public import public_agent_result
from utils.auth_utils import login_required, decode_token
from blueprints.credits import check_and_consume_chat

from extensions import db, SECRET_KEY, DATABASE_URL

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# --- 初始化 Flask 应用 ---
app = Flask(__name__, static_folder='../dist')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or (
    'sqlite:///' + os.path.join(DATA_DIR, 'shu_prophet.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
CORS(app)

# 初始化数据库
db.init_app(app)

# 注册蓝图
from blueprints.auth import auth_bp
from blueprints.user import user_bp
from blueprints.community import community_bp
from blueprints.credits import credits_bp
from blueprints.admin import admin_bp
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(community_bp)
app.register_blueprint(credits_bp)
app.register_blueprint(admin_bp)

# 创建数据库表
with app.app_context():
    from models.db_models import User, Post, Comment, PostLike, RedeemCode, DailyUsage, CreditLog
    try:
        db.create_all()
    except Exception:
        pass

    # 自动迁移：添加新字段
    try:
        db.session.execute(db.text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS avatar_data TEXT'))
        db.session.execute(db.text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1'))
        db.session.execute(db.text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE'))
        db.session.execute(db.text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS total_credits INTEGER DEFAULT 0'))
        # 初始化已有用户的累计积分
        db.session.execute(db.text('UPDATE "user" SET total_credits = credits WHERE total_credits = 0'))
        # 清理可能损坏的 avatar_data
        db.session.execute(db.text('UPDATE "user" SET avatar_data = NULL WHERE LENGTH(COALESCE(avatar_data, \'\')) > 10000000'))
        db.session.commit()
    except Exception:
        db.session.rollback()

# --- 定义路径 ---
STATIC_DATA_DIR = os.path.join(BASE_DIR, 'static_data')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)


def _save_csv_upload(file_storage):
    """Validate and persist an uploaded CSV under a collision-free name."""
    filename = (file_storage.filename or '').lower()
    if not filename.endswith('.csv'):
        raise ValueError('仅支持CSV文件')

    fd, filepath = tempfile.mkstemp(suffix='.csv', dir=UPLOADS_DIR)
    os.close(fd)
    file_storage.save(filepath)
    return filepath


def _remove_upload(filepath):
    if filepath and os.path.isfile(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass


def _read_uploaded_series(filepath):
    frame = pd.read_csv(filepath, dtype=str, encoding='utf-8-sig')
    if frame.shape[1] < 2:
        raise ValueError('CSV文件必须至少包含两列')
    values = pd.to_numeric(frame.iloc[:, 1], errors='coerce').dropna().tolist()
    if len(values) < 10:
        raise ValueError(f'有效数据点过少（{len(values)}个），至少需要10个')
    return values

# --- 数据预处理与计算函数 ---
def _sanitize(obj):
    """递归将 numpy 类型转为 Python 原生类型。"""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def smooth(y, win=11, poly=3):
    """Savitzky-Golay平滑函数"""
    if len(y) < win:
        return y
    return savgol_filter(y, window_length=win, polyorder=poly)

# --- API 路由 ---

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "shu-prophet",
        "agent": "ready",
    })

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """API: 获取所有可用的科研数据集文件名。"""
    datasets_path = os.path.join(STATIC_DATA_DIR, 'research_datasets')
    try:
        files = [f for f in os.listdir(datasets_path) if f.endswith('.csv')]
        return jsonify(files)
    except FileNotFoundError:
        return jsonify([])

@app.route('/api/parse-csv', methods=['POST'])
def parse_csv():
    """
    【静态核心API - 终极版】: 
    读取CSV(含模型名称)，执行预处理，计算MAE/MSE，并返回所有数据。
    """
    data = request.json
    dataset_file = data.get('dataset')
    if not dataset_file:
        return jsonify({"error": "Missing dataset filename"}), 400

    file_path = os.path.join(STATIC_DATA_DIR, 'research_datasets', dataset_file)

    try:
        # 1. 读取CSV（第一行是列名）
        raw = pd.read_csv(file_path)

        # 2. 从列名中提取模型名称
        model_names_raw = raw.columns.tolist()

        # 3. 数据清理与处理
        INVALID = -1.0145037163717687
        TOL = 1e-6

        response = {"actual_data": {}, "model_predictions": []}

        # 先处理并存储Ground Truth数据
        gt_x_col, gt_y_col = 'actual_x', 'actual_y'
        gt_df_raw = raw[[gt_x_col, gt_y_col]].dropna()
        gt_df = gt_df_raw.loc[~np.isclose(gt_df_raw[gt_y_col], INVALID, atol=TOL)].astype(float)
        gt_df = gt_df.groupby(gt_x_col, as_index=False)[gt_y_col].mean()
        gt_y_smooth = smooth(gt_df[gt_y_col].values)
        gt_processed_data = list(zip(gt_df[gt_x_col].values, gt_y_smooth))
        response["actual_data"] = {"model_name": "Actual", "data": gt_processed_data}

        # 循环处理所有预测模型
        model_cols = [col for col in raw.columns if col.endswith('_x') and col != 'actual_x']
        for model_x_col in model_cols:
            model_name = model_x_col.replace('_x', '')
            model_y_col = model_name + '_y'

            if model_y_col not in raw.columns:
                continue

            pred_df_raw = raw[[model_x_col, model_y_col]].dropna()
            pred_df = pred_df_raw.loc[~np.isclose(pred_df_raw[model_y_col], INVALID, atol=TOL)].astype(float)
            pred_df = pred_df.groupby(model_x_col, as_index=False)[model_y_col].mean()

            pred_y_smooth = smooth(pred_df[model_y_col].values)
            pred_processed_data = list(zip(pred_df[model_x_col].values, pred_y_smooth))

            # 计算性能指标
            gt_y_interpolated = np.interp(pred_df[model_x_col], gt_df[gt_x_col], gt_y_smooth)
            mae = mean_absolute_error(gt_y_interpolated, pred_y_smooth)
            mse = mean_squared_error(gt_y_interpolated, pred_y_smooth)

            response["model_predictions"].append({
                "model_name": model_name,
                "data": pred_processed_data,
                "metrics": {
                    "mae": round(mae, 4),
                    "mse": round(mse, 4)
                }
            })
        
        time.sleep(1.5)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Backend Error: {str(e)}"}), 500

@app.route('/api/live-predict', methods=['POST'])
def live_predict():
    """【动态核心API】: 接收用户上传的文件并进行实时预测。"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filepath = os.path.join(UPLOADS_DIR, file.filename)
        file.save(filepath)
        prediction_result = predict_with_arima(filepath, steps=10)
        return jsonify(prediction_result)
    return jsonify({"error": "File upload failed"}), 500

# --- 核心升级：新增一个只处理文本消息的API ---
@app.route('/api/agent-message', methods=['POST'])
@login_required
def agent_message():
    """【智能助理对话API】: 接收用户文本消息，返回助理的文本回复。"""
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id', 'default_session')

    if not user_message:
        return jsonify({"error": "消息内容不能为空"}), 400

    # 简单问候直接返回静态回复，不消耗配额和AI调用
    _GREETING_KEYWORDS = ['你好', '您好', 'hello', 'hi', '嗨', '在吗']
    if user_message.strip().lower() in _GREETING_KEYWORDS:
        return jsonify({"reply": (
            "你好！我是**鼠先知 (SHU Prophet)** AI智能助理 🐭\n\n"
            "我可以帮你进行时间序列数据的分析与预测。"
            "只需上传一个CSV文件（含X、Y两列），"
            "我就能为你生成专业的预测报告。\n\n"
            "有什么我可以帮你的吗？"
        )})

    # 检查用量并消耗配额
    ok, err = check_and_consume_chat(g.user_id)
    if not ok:
        return jsonify({"error": err}), 403

    try:
        agent_reply = get_conversational_response(user_message, session_id)
    except Exception as e:
        return jsonify({"reply": "抱歉，AI服务暂时不可用，请稍后再试。"}), 200

    return jsonify({"reply": agent_reply})

# --- 工具Agent文件处理API ---
@app.route('/api/agent-upload-predict', methods=['POST'])
@login_required
def agent_upload_predict():
    """Run the complete analysis, model selection, and validation workflow."""
    ok, err = check_and_consume_chat(g.user_id)
    if not ok:
        return jsonify({"error": err}), 403

    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400

    user_message = request.form.get('message', '')
    try:
        forecast_steps = int(request.form.get('steps', 10))
    except (TypeError, ValueError):
        return jsonify({"error": "预测步数必须是整数"}), 400
    if not 1 <= forecast_steps <= 90:
        return jsonify({"error": "预测步数必须在1到90之间"}), 400

    filepath = None
    try:
        filepath = _save_csv_upload(file)
        analysis_result = analyze_and_predict(filepath, steps=forecast_steps)
        if "error" in analysis_result:
            return jsonify(analysis_result), 400

        data_y = analysis_result["summary_stats"]["historical_y"]
        agent_result = TSReasoner().predict(data_y, steps=forecast_steps)
        report_markdown = generate_standalone_report(
            analysis_result,
            user_message,
            agent_result,
        )

        public_agent = public_agent_result(agent_result)
        response_data = {
            "report": report_markdown,
            "chart_data": analysis_result.get("chart_data"),
            "smart_prediction": {
                "engine": public_agent["engine"],
                "predictions": public_agent["predictions"],
                "prediction_interval": public_agent["prediction_interval"],
                "confidence": public_agent["confidence"],
            },
            "agent_run": {
                "trajectory": public_agent["trajectory"],
                "candidates_evaluated": public_agent["candidates_evaluated"],
                "selection_basis": public_agent["selection_basis"],
                "validation": public_agent["validation"],
                "confidence": public_agent["confidence"],
            },
        }
        return jsonify(_sanitize(response_data))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Agent执行失败: {str(exc)}"}), 500
    finally:
        _remove_upload(filepath)

@app.route('/api/smart-predict', methods=['POST'])
def smart_predict_api():
    """Execute the tool Agent and return a routing-safe public result."""
    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400

    steps = request.form.get('steps', 10, type=int)
    if steps is None or not 1 <= steps <= 90:
        return jsonify({"error": "预测步数必须在1到90之间"}), 400

    filepath = None
    try:
        filepath = _save_csv_upload(file)
        result = TSReasoner().predict(_read_uploaded_series(filepath), steps=steps)
        return jsonify(_sanitize(public_agent_result(result)))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"预测失败: {str(exc)}"}), 500
    finally:
        _remove_upload(filepath)

@app.route('/api/agent-reason', methods=['POST'])
def agent_reason():
    """Execute the auditable Agent workflow without exposing routing details."""
    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400

    steps = request.form.get('steps', 10, type=int)
    if steps is None or not 1 <= steps <= 90:
        return jsonify({"error": "预测步数必须在1到90之间"}), 400

    filepath = None
    try:
        filepath = _save_csv_upload(file)
        result = TSReasoner().predict(_read_uploaded_series(filepath), steps=steps)
        return jsonify(_sanitize(public_agent_result(result)))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Agent执行失败: {str(exc)}"}), 500
    finally:
        _remove_upload(filepath)

# --- 服务前端静态文件的路由 ---
# 这个路由捕获所有不是API的请求
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # 如果请求的是一个存在的文件 (如/assets/index.js), 则直接发送该文件
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # 否则，发送入口index.html，让Vue Router接管路由
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
