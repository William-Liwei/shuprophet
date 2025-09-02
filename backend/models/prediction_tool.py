# backend/models/prediction_tool.py

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")

def analyze_and_predict(csv_path: str, steps: int = 10) -> dict:
    """
    一个封装了数据读取、ARIMA模型拟合和预测的工具函数。
    
    :param csv_path: 用户上传的CSV文件路径。
    :param steps: 预测未来的步数。
    :return: 一个包含历史数据、预测数据和关键统计信息的字典。
    """
    print(f"INFO: 开始使用 ARIMA 工具分析文件: {csv_path}")
    try:
        # --- 终极修复 2.0: 处理多余的表头行 ---
        # 1. header=0: 明确告诉pandas，第1行（索引为0）是我们的表头。
        # 2. skiprows=[1]: 明确告诉pandas，跳过第2行（索引为1），因为它是多余的表头。
        # 3. dtype=str: 依然保留，先将所有“真正的数据”读为字符串，避免类型推断错误。
        # 4. encoding='utf-8-sig': 保留，以兼容不同编码。
        try:
            df = pd.read_csv(
                csv_path, 
                header=0,
                skiprows=[1], 
                dtype=str, 
                encoding='utf-8-sig'
            )
        except Exception as read_e:
            # 如果上面的读取失败（比如文件只有一行），我们尝试用标准方式再读一次
            try:
                df = pd.read_csv(csv_path, dtype=str, encoding='utf-8-sig')
            except Exception as final_read_e:
                 return {"error": f"读取CSV文件失败，请检查文件格式。错误: {final_read_e}"}

        if df.shape[1] < 2:
            return {"error": "CSV文件格式无效。文件必须至少包含两列 (X, Y)。"}

        x_col_name = df.columns[0]
        y_col_name = df.columns[1]

        df[x_col_name] = pd.to_numeric(df[x_col_name], errors='coerce')
        df[y_col_name] = pd.to_numeric(df[y_col_name], errors='coerce')

        df.dropna(subset=[x_col_name, y_col_name], inplace=True)

        if df.empty:
            return {"error": "在清理无效行后，没有剩余的有效数据。请检查文件内容。"}

        history_x = df[x_col_name].tolist()
        history_y = df[y_col_name].tolist()

        if len(history_y) < 10:
            return {"error": f"有效数据点过少 ({len(history_y)}个)，无法进行有效的ARIMA模型分析。请提供至少10个有效的数据点。"}

        model = ARIMA(history_y, order=(5, 1, 0))
        model_fit = model.fit()
        
        forecast_y = model_fit.forecast(steps=steps).tolist()
        
        last_x = history_x[-1]
        x_step = history_x[-1] - history_x[-2] if len(history_x) > 1 else 1
        forecast_x = [last_x + i * x_step for i in range(1, steps + 1)]
        
        history_data = list(zip(history_x, history_y))
        forecast_data = list(zip(forecast_x, forecast_y))

        result = {
            "model_name": "ARIMA(5,1,0)",
            "chart_data": {
                 "history_data": history_data,
                 "forecast_data": forecast_data,
            },
            "summary_stats": {
                "historical_points": len(history_y),
                "forecast_steps": steps,
                "historical_y_mean": round(pd.Series(history_y).mean(), 2),
                "forecast_y_mean": round(pd.Series(forecast_y).mean(), 2)
            }
        }
        return result

    except Exception as e:
        print(f"ERROR: 工具执行失败: {str(e)}")
        return {"error": f"在执行数据分析时发生内部错误: {str(e)}"}