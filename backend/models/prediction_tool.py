"""CSV parsing and ARIMA baseline generation."""

import pandas as pd
import warnings
from statsmodels.tsa.arima.model import ARIMA


def analyze_and_predict(csv_path: str, steps: int = 10) -> dict:
    """Read the first two CSV columns and produce an ARIMA baseline."""
    try:
        frame = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig")
    except Exception as exc:
        return {"error": f"读取CSV文件失败，请检查文件格式：{exc}"}

    if frame.shape[1] < 2:
        return {"error": "CSV文件必须至少包含两列（时间/索引列与数值列）"}

    x_name, y_name = frame.columns[:2]
    cleaned = pd.DataFrame({
        "x": pd.to_numeric(frame[x_name], errors="coerce"),
        "y": pd.to_numeric(frame[y_name], errors="coerce"),
    }).dropna()

    if len(cleaned) < 10:
        return {"error": f"有效数据点过少（{len(cleaned)}个），至少需要10个"}

    history_x = cleaned["x"].astype(float).tolist()
    history_y = cleaned["y"].astype(float).tolist()
    steps = max(1, min(int(steps), 90))

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model_fit = ARIMA(history_y, order=(5, 1, 0)).fit()
        forecast_y = [float(value) for value in model_fit.forecast(steps=steps)]
    except Exception as exc:
        return {"error": f"ARIMA基线拟合失败：{exc}"}

    x_step = history_x[-1] - history_x[-2]
    if x_step == 0:
        x_step = 1.0
    forecast_x = [history_x[-1] + index * x_step for index in range(1, steps + 1)]

    return {
        "model_name": "ARIMA(5,1,0)",
        "chart_data": {
            "history_data": list(zip(history_x, history_y)),
            "forecast_data": list(zip(forecast_x, forecast_y)),
        },
        "summary_stats": {
            "historical_points": len(history_y),
            "forecast_steps": steps,
            "historical_y_mean": round(float(pd.Series(history_y).mean()), 4),
            "forecast_y_mean": round(float(pd.Series(forecast_y).mean()), 4),
            "historical_y": history_y,
            "forecast_y": forecast_y,
        },
    }
