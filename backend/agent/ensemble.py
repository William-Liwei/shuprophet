"""
置信度感知集成预测模块

Strategy: compare lightweight statistical forecasters on a temporal holdout,
prefer the lowest validation error, and keep ARIMA when scores are effectively tied.
"""

import numpy as np
from .tools.forecasters import (
    arima_forecast, ets_forecast, theta_forecast, linear_forecast
)

FORECASTERS = [
    ("arima", arima_forecast),
    ("ets", ets_forecast),
    ("theta", theta_forecast),
    ("linear", linear_forecast),
]

DEFAULT_MODEL = "arima"


def ensemble_predict(data: list, steps: int = 10) -> dict:
    """Run multiple forecasters, pick best via CV, apply bias correction."""
    y = np.array(data, dtype=float)

    # 1. Collect forecasts from all models
    results = {}
    for name, fn in FORECASTERS:
        try:
            r = fn(data, steps=steps)
            if "predictions" in r and len(r["predictions"]) == steps:
                results[name] = r["predictions"]
        except Exception:
            continue

    if not results:
        return {"predictions": [], "confidence": 0.1, "method": "none"}

    # 2. Select a model on a temporal holdout.
    chosen, cv_residuals, cv_errors = _select_model(y, results)

    preds_raw = np.array(results[chosen], dtype=float)
    preds = [round(float(v), 4) for v in preds_raw]
    ci_lower, ci_upper = _bootstrap_ci(y, preds)

    cv_confidence = _cv_confidence(y, chosen, cv_errors)

    return {
        "tool": "ensemble_predict",
        "predictions": preds,
        "selected_model": chosen,
        "weights": {chosen: 1.0},
        "cv_confidence": cv_confidence,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "models_used": list(results.keys()),
        "cv_residuals": cv_residuals,
        "cv_errors": cv_errors,
    }


def _select_model(y, results):
    """Select on a temporal holdout and use ARIMA as a near-tie breaker."""
    n = len(y)
    val_size = max(8, n // 5)
    train_end = n - val_size

    if train_end < 15 or DEFAULT_MODEL not in results:
        chosen = DEFAULT_MODEL if DEFAULT_MODEL in results else list(results.keys())[0]
        return chosen, [], {}

    train = y[:train_end].tolist()
    actual = y[train_end:]

    errors = {}
    cv_preds = {}
    for name, fn in FORECASTERS:
        if name not in results:
            continue
        try:
            r = fn(train, steps=val_size)
            p = np.array(r["predictions"][:len(actual)])
            mse = float(np.mean((p - actual[:len(p)]) ** 2))
            errors[name] = max(mse, 1e-10)
            cv_preds[name] = p
        except Exception:
            errors[name] = 1e6

    if not errors:
        chosen = DEFAULT_MODEL if DEFAULT_MODEL in results else list(results.keys())[0]
        return chosen, [], {}

    best_name = min(errors, key=errors.get)
    best_err = errors[best_name]
    arima_err = errors.get(DEFAULT_MODEL)

    # Prefer the simpler default only when it is within 5% of the best score.
    if arima_err is not None and arima_err <= best_err * 1.05:
        chosen = DEFAULT_MODEL
    else:
        chosen = best_name

    # CV residuals for post-predict correction
    cv_residuals = []
    if chosen in cv_preds:
        p = cv_preds[chosen][:len(actual)]
        cv_residuals = (p - actual[:len(p)]).tolist()

    return chosen, cv_residuals, {k: round(v, 6) for k, v in errors.items()}


def _cv_confidence(y, chosen, errors):
    """Convert normalized holdout RMSE into a bounded descriptive score."""
    if chosen not in errors:
        return 0.35

    scale = float(np.std(y))
    if scale < 1e-10:
        return 0.2

    normalized_rmse = float(np.sqrt(errors[chosen]) / scale)
    score = 1.0 / (1.0 + normalized_rmse)
    return round(max(0.1, min(0.95, score)), 3)


def _bootstrap_ci(y, preds, n_boot=200, alpha=0.05):
    """Bootstrap confidence intervals."""
    residuals = np.diff(y)
    std_r = float(np.std(residuals)) if len(residuals) > 0 else 1.0

    rng = np.random.RandomState(42)
    boot = np.array([np.array(preds) + rng.normal(0, std_r, len(preds))
                      for _ in range(n_boot)])

    lo = np.percentile(boot, 100 * alpha / 2, axis=0)
    hi = np.percentile(boot, 100 * (1 - alpha / 2), axis=0)

    return (
        [round(float(v), 4) for v in lo],
        [round(float(v), 4) for v in hi],
    )
