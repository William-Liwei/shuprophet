"""
预测模型工具
Each forecaster returns predictions + metadata for ensemble weighting.
"""

import numpy as np
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA


def arima_forecast(data: list, steps: int = 10) -> dict:
    """ARIMA forecaster with automatic order selection."""
    y = np.array(data, dtype=float)

    # Try common orders, pick best AIC
    best_aic, best_order, best_model = np.inf, (1, 1, 0), None
    for p in [1, 2, 3, 5]:
        for d in [0, 1]:
            for q in [0, 1]:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        m = ARIMA(y, order=(p, d, q)).fit()
                    if m.aic < best_aic:
                        best_aic, best_order, best_model = m.aic, (p, d, q), m
                except Exception:
                    continue

    if best_model is None:
        # Fallback: simple ARIMA(1,1,0)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                best_model = ARIMA(y, order=(1, 1, 0)).fit()
            best_order = (1, 1, 0)
        except Exception:
            return _fallback_forecast(y, steps, "arima")

    fc = best_model.forecast(steps=steps)
    preds = [round(float(v), 4) for v in fc]

    return {
        "tool": "arima_forecast",
        "model": f"ARIMA{best_order}",
        "predictions": preds,
        "aic": round(float(best_aic), 2),
    }


def ets_forecast(data: list, steps: int = 10) -> dict:
    """Exponential Smoothing (ETS) forecaster."""
    y = np.array(data, dtype=float)
    n = len(y)

    # Choose config based on data length
    seasonal = None
    sp = 0
    if n >= 14:
        sp = min(7, n // 3)
        seasonal = "add"

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ExponentialSmoothing(
                y, trend="add", seasonal=seasonal,
                seasonal_periods=sp if seasonal else None,
            ).fit(optimized=True)
        fc = model.forecast(steps)
        preds = [round(float(v), 4) for v in fc]
    except Exception:
        return _fallback_forecast(y, steps, "ets")

    return {
        "tool": "ets_forecast",
        "model": f"ETS(add,{'add' if seasonal else 'none'},{sp})",
        "predictions": preds,
    }


def theta_forecast(data: list, steps: int = 10) -> dict:
    """Theta method forecaster (simplified)."""
    y = np.array(data, dtype=float)
    n = len(y)

    # SES for level
    alpha = 0.5
    level = y[0]
    for v in y[1:]:
        level = alpha * v + (1 - alpha) * level

    # Linear trend
    x = np.arange(n)
    slope = float(np.polyfit(x, y, 1)[0])

    preds = []
    for i in range(1, steps + 1):
        preds.append(round(float(level + slope * i), 4))

    return {
        "tool": "theta_forecast",
        "model": "Theta",
        "predictions": preds,
    }


def linear_forecast(data: list, steps: int = 10) -> dict:
    """Linear regression forecaster with value clipping."""
    y = np.array(data, dtype=float)
    n = len(y)
    x = np.arange(n)

    # Pure linear regression (no quadratic — it extrapolates wildly)
    coeffs = np.polyfit(x, y, 1)
    poly = np.poly1d(coeffs)
    future_x = np.arange(n, n + steps)
    raw = poly(future_x)

    # Clip to [mean - 4*std, mean + 4*std] to prevent runaway extrapolation
    mean_val = float(np.mean(y))
    std_val = float(np.std(y)) if float(np.std(y)) > 1e-10 else 1.0
    lo = mean_val - 4 * std_val
    hi = mean_val + 4 * std_val
    clipped = np.clip(raw, lo, hi)

    preds = [round(float(v), 4) for v in clipped]

    return {
        "tool": "linear_forecast",
        "model": "Linear",
        "predictions": preds,
    }


def _fallback_forecast(y, steps, name):
    """Linear extrapolation fallback."""
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    preds = [round(float(slope * (len(y) + i) + intercept), 4) for i in range(steps)]
    return {"tool": f"{name}_forecast", "model": "fallback_linear", "predictions": preds}


# --- Tool Registry ---
FORECASTER_TOOLS = {
    "arima_forecast": {
        "fn": arima_forecast,
        "description": "ARIMA forecaster with auto order selection. General-purpose statistical forecasting.",
        "triggers": ["arima", "autoregressive"],
    },
    "ets_forecast": {
        "fn": ets_forecast,
        "description": "Exponential Smoothing (ETS) forecaster. Good for data with trend and seasonality.",
        "triggers": ["ets", "exponential", "smoothing"],
    },
    "theta_forecast": {
        "fn": theta_forecast,
        "description": "Theta method forecaster. Simple and robust baseline.",
        "triggers": ["theta", "baseline"],
    },
    "linear_forecast": {
        "fn": linear_forecast,
        "description": "Linear/quadratic regression forecaster. Use for strong trend data.",
        "triggers": ["linear", "regression", "extrapolation"],
    },
}
