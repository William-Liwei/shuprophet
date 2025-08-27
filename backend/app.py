from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from sklearn.metrics import mean_absolute_error, mean_squared_error
import time
from models.arima_predictor import predict_with_arima

# --- 初始化 Flask 应用 ---
# app = Flask(__name__)
app = Flask(__name__, static_folder='../dist')
CORS(app)

# --- 定义路径 ---
STATIC_DATA_DIR = 'static_data'
UPLOADS_DIR = 'uploads'
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# --- 数据预处理与计算函数 ---
def smooth(y, win=11, poly=3):
    """Savitzky-Golay平滑函数"""
    if len(y) < win:
        return y
    return savgol_filter(y, window_length=win, polyorder=poly)

# --- API 路由 ---

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
        # 1. 读取模型名称 (约定在第二行)
        model_names_raw = pd.read_csv(file_path, skiprows=1, nrows=1, header=None).iloc[0].tolist()
        
        # 2. 读取数据 (从第三行开始)
        raw = pd.read_csv(file_path, skiprows=2, header=None)
        
        # 3. 数据清理与处理
        INVALID = -1.0145037163717687
        TOL = 1e-6
        
        response = {"actual_data": {}, "model_predictions": []}
        
        # 先处理并存储Ground Truth数据
        gt_x_col, gt_y_col = raw.columns[0], raw.columns[1]
        gt_df_raw = raw[[gt_x_col, gt_y_col]].dropna()
        gt_df = gt_df_raw.loc[~np.isclose(gt_df_raw[gt_y_col], INVALID, atol=TOL)].astype(float)
        gt_df = gt_df.groupby(gt_x_col, as_index=False)[gt_y_col].mean()
        gt_y_smooth = smooth(gt_df[gt_y_col].values)
        gt_processed_data = list(zip(gt_df[gt_x_col].values, gt_y_smooth))
        gt_name = str(model_names_raw[0]).replace('_x', '').replace('_X', '')
        response["actual_data"] = {"model_name": gt_name, "data": gt_processed_data}

        # 循环处理所有预测模型
        for i in range(2, len(raw.columns), 2):
            pred_x_col, pred_y_col = raw.columns[i], raw.columns[i+1]
            
            pred_df_raw = raw[[pred_x_col, pred_y_col]].dropna()
            pred_df = pred_df_raw.loc[~np.isclose(pred_df_raw[pred_y_col], INVALID, atol=TOL)].astype(float)
            pred_df = pred_df.groupby(pred_x_col, as_index=False)[pred_y_col].mean()
            
            pred_y_smooth = smooth(pred_df[pred_y_col].values)
            pred_processed_data = list(zip(pred_df[pred_x_col].values, pred_y_smooth))
            
            # 计算性能指标
            # 插值gt以对齐预测的x轴
            gt_y_interpolated = np.interp(pred_df[pred_x_col], gt_df[gt_x_col], gt_y_smooth)
            mae = mean_absolute_error(gt_y_interpolated, pred_y_smooth)
            mse = mean_squared_error(gt_y_interpolated, pred_y_smooth)
            
            model_name = str(model_names_raw[i]).replace('_x', '').replace('_X', '')
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