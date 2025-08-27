import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")

def predict_with_arima(csv_path, steps=10):
    """
    使用ARIMA模型对上传的CSV文件进行实时预测。
    该函数现在处理X-Y数据对。

    :param csv_path: 用户上传的CSV文件路径。
    :param steps: 预测未来的步数。
    :return: 包含历史数据和预测数据的字典。
    """
    try:
        # 读取数据，假设至少有两列
        df = pd.read_csv(csv_path)
        
        # 提取历史数据 (前两列)
        history_x = df.iloc[:, 0].dropna().tolist()
        history_y = df.iloc[:, 1].dropna().tolist()

        # 使用历史Y值拟合ARIMA模型
        model = ARIMA(history_y, order=(5, 1, 0))
        model_fit = model.fit()
        
        # 预测未来Y值
        forecast_y = model_fit.forecast(steps=steps).tolist()
        
        # 生成未来的X值（这里简单地进行线性外插）
        last_x = history_x[-1]
        x_step = history_x[-1] - history_x[-2] if len(history_x) > 1 else 1
        forecast_x = [last_x + i * x_step for i in range(1, steps + 1)]
        
        # 准备返回结果
        result = {
            "history_data": list(zip(history_x, history_y)),
            "forecast_data": list(zip(forecast_x, forecast_y))
        }
        return result

    except Exception as e:
        return {"error": str(e)}