"""
统计分析工具集

Each function is an Agent-callable tool that returns structured results
for LLM reasoning without requiring token-expensive raw data processing.
"""

import numpy as np
import warnings
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from statsmodels.tsa.stattools import adfuller, kpss, acf, pacf


def trend_analysis(data: list) -> dict:
    """Mann-Kendall trend test + linear regression slope."""
    y = np.array(data, dtype=float)
    n = len(y)

    # Linear regression slope
    x = np.arange(n)
    slope, intercept, r_value, p_value_lr, std_err = stats.linregress(x, y)

    # Mann-Kendall test (simplified)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = y[j] - y[i]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1

    var_s = n * (n - 1) * (2 * n + 5) / 18.0
    if s > 0:
        z_mk = (s - 1) / np.sqrt(var_s) if var_s > 0 else 0
    elif s < 0:
        z_mk = (s + 1) / np.sqrt(var_s) if var_s > 0 else 0
    else:
        z_mk = 0

    mk_p = 2 * (1 - stats.norm.cdf(abs(z_mk)))

    if mk_p < 0.05:
        direction = "increasing" if z_mk > 0 else "decreasing"
    else:
        direction = "no_trend"

    return {
        "tool": "trend_analysis",
        "direction": direction,
        "slope": round(float(slope), 6),
        "r_squared": round(float(r_value ** 2), 4),
        "mann_kendall_z": round(float(z_mk), 4),
        "mann_kendall_p": round(float(mk_p), 4),
        "significant": mk_p < 0.05,
    }


def volatility_analysis(data: list) -> dict:
    """Volatility profiling with rolling statistics and GARCH-like metrics."""
    y = np.array(data, dtype=float)
    n = len(y)
    mean_val = float(np.mean(y))
    std_val = float(np.std(y))

    # Rolling volatility (window = min(20, n//4))
    win = max(3, min(20, n // 4))
    rolling_std = []
    for i in range(win, n):
        rolling_std.append(float(np.std(y[i - win:i])))

    # Coefficient of variation
    cv = std_val / abs(mean_val) if abs(mean_val) > 1e-10 else float("inf")

    # Volatility clustering: autocorrelation of squared returns
    if n > 10:
        returns = np.diff(y)
        sq_returns = returns ** 2
        if len(sq_returns) > 5 and np.std(sq_returns) > 1e-10:
            vol_autocorr = float(np.corrcoef(sq_returns[:-1], sq_returns[1:])[0, 1])
        else:
            vol_autocorr = 0.0
    else:
        vol_autocorr = 0.0

    level = "high" if cv > 0.3 else "medium" if cv > 0.1 else "low"

    return {
        "tool": "volatility_analysis",
        "level": level,
        "std": round(std_val, 4),
        "cv": round(float(cv), 4),
        "volatility_clustering": round(vol_autocorr, 4),
        "rolling_std_mean": round(float(np.mean(rolling_std)), 4) if rolling_std else 0,
        "rolling_std_trend": "increasing" if len(rolling_std) > 1 and rolling_std[-1] > rolling_std[0] else "stable",
    }


def anomaly_detection(data: list) -> dict:
    """Multi-method anomaly detection: 3-sigma, Isolation Forest, LOF."""
    y = np.array(data, dtype=float).reshape(-1, 1)
    n = len(y)
    mean_val, std_val = float(np.mean(y)), float(np.std(y))

    # 3-sigma
    z_scores = np.abs((y.flatten() - mean_val) / std_val) if std_val > 1e-10 else np.zeros(n)
    sigma_anomalies = [int(i) for i in np.where(z_scores > 3)[0]]

    # Isolation Forest
    if n >= 10:
        iso = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
        iso_labels = iso.fit_predict(y)
        iso_anomalies = [int(i) for i in np.where(iso_labels == -1)[0]]
    else:
        iso_anomalies = []

    # LOF
    if n >= 10:
        k = min(5, n - 1)
        lof = LocalOutlierFactor(n_neighbors=k, contamination=0.05)
        lof_labels = lof.fit_predict(y)
        lof_anomalies = [int(i) for i in np.where(lof_labels == -1)[0]]
    else:
        lof_anomalies = []

    # Consensus: flagged by at least 2 methods
    all_idx = set(sigma_anomalies) | set(iso_anomalies) | set(lof_anomalies)
    consensus = sorted([i for i in all_idx if sum([
        i in sigma_anomalies, i in iso_anomalies, i in lof_anomalies
    ]) >= 2])

    return {
        "tool": "anomaly_detection",
        "total_points": n,
        "sigma_count": len(sigma_anomalies),
        "isolation_forest_count": len(iso_anomalies),
        "lof_count": len(lof_anomalies),
        "consensus_anomalies": consensus[:20],  # cap for LLM context
        "consensus_count": len(consensus),
        "anomaly_ratio": round(len(consensus) / n, 4),
    }


def stationarity_test(data: list) -> dict:
    """ADF + KPSS stationarity tests."""
    y = np.array(data, dtype=float)

    # ADF test (H0: unit root exists = non-stationary)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(y, autolag="AIC")
        adf_stationary = adf_p < 0.05
    except Exception:
        adf_stat, adf_p, adf_stationary = 0, 1, False
        adf_crit = {}

    # KPSS test (H0: stationary)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kpss_stat, kpss_p, kpss_lags, kpss_crit = kpss(y, regression="c", nlags="auto")
        kpss_stationary = kpss_p > 0.05
    except Exception:
        kpss_stat, kpss_p, kpss_stationary = 0, 0, True
        kpss_crit = {}

    # Combined verdict
    if adf_stationary and kpss_stationary:
        verdict = "stationary"
    elif not adf_stationary and not kpss_stationary:
        verdict = "non_stationary"
    else:
        verdict = "trend_stationary" if adf_stationary else "difference_stationary"

    return {
        "tool": "stationarity_test",
        "verdict": verdict,
        "adf_statistic": round(float(adf_stat), 4),
        "adf_p_value": round(float(adf_p), 4),
        "adf_stationary": adf_stationary,
        "kpss_statistic": round(float(kpss_stat), 4),
        "kpss_p_value": round(float(kpss_p), 4),
        "kpss_stationary": kpss_stationary,
    }


def distribution_test(data: list) -> dict:
    """Shapiro-Wilk normality + KS test against normal distribution."""
    y = np.array(data, dtype=float)
    n = len(y)

    # Shapiro-Wilk (works best for n < 5000)
    sample = y[:5000] if n > 5000 else y
    try:
        sw_stat, sw_p = stats.shapiro(sample)
    except Exception:
        sw_stat, sw_p = 0, 0

    # KS test against normal
    try:
        ks_stat, ks_p = stats.kstest(y, "norm", args=(np.mean(y), np.std(y)))
    except Exception:
        ks_stat, ks_p = 0, 0

    skewness = float(stats.skew(y))
    kurt = float(stats.kurtosis(y))

    return {
        "tool": "distribution_test",
        "is_normal": sw_p > 0.05 and ks_p > 0.05,
        "shapiro_p": round(float(sw_p), 4),
        "ks_p": round(float(ks_p), 4),
        "skewness": round(skewness, 4),
        "kurtosis": round(kurt, 4),
        "distribution_hint": "normal" if sw_p > 0.05 else (
            "heavy_tailed" if kurt > 1 else "skewed" if abs(skewness) > 1 else "non_normal"
        ),
    }


def changepoint_detection(data: list) -> dict:
    """PELT-style changepoint detection using cumulative sum."""
    y = np.array(data, dtype=float)
    n = len(y)

    if n < 10:
        return {"tool": "changepoint_detection", "changepoints": [], "count": 0}

    # Binary segmentation approach
    def _cost(segment):
        if len(segment) < 2:
            return 0
        return len(segment) * np.var(segment)

    def _find_best_split(arr, start_idx):
        best_gain, best_pos = -1, -1
        base_cost = _cost(arr)
        for i in range(2, len(arr) - 2):
            gain = base_cost - _cost(arr[:i]) - _cost(arr[i:])
            if gain > best_gain:
                best_gain = gain
                best_pos = start_idx + i
        return best_pos, best_gain

    # Penalty based on BIC
    penalty = 3 * np.log(n) * np.var(y)
    changepoints = []

    segments = [(0, n)]
    for _ in range(min(10, n // 10)):
        best_cp, best_g, best_seg = -1, -1, -1
        for idx, (s, e) in enumerate(segments):
            seg = y[s:e]
            if len(seg) < 6:
                continue
            pos, gain = _find_best_split(seg, s)
            if gain > best_g:
                best_g, best_cp, best_seg = gain, pos, idx
        if best_g > penalty and best_seg >= 0:
            s, e = segments[best_seg]
            segments[best_seg] = (s, best_cp)
            segments.insert(best_seg + 1, (best_cp, e))
            changepoints.append(best_cp)
        else:
            break

    changepoints.sort()

    return {
        "tool": "changepoint_detection",
        "changepoints": changepoints,
        "count": len(changepoints),
        "segment_means": [round(float(np.mean(y[s:e])), 4) for s, e in segments],
    }


def correlation_analysis(data: list) -> dict:
    """ACF, PACF, and dominant lag detection."""
    y = np.array(data, dtype=float)
    n = len(y)
    max_lag = min(40, n // 3)

    if max_lag < 2:
        return {"tool": "correlation_analysis", "dominant_lag": 0, "has_seasonality": False}

    acf_vals = acf(y, nlags=max_lag, fft=True)
    try:
        pacf_vals = pacf(y, nlags=max_lag, method="ywm")
    except Exception:
        pacf_vals = np.zeros(max_lag + 1)

    # Find dominant lag (skip lag 0)
    conf_bound = 1.96 / np.sqrt(n)
    significant_lags = [i for i in range(1, len(acf_vals)) if abs(acf_vals[i]) > conf_bound]
    dominant_lag = significant_lags[0] if significant_lags else 0

    # Seasonality: look for repeating peaks in ACF
    peaks = []
    for i in range(2, len(acf_vals) - 1):
        if acf_vals[i] > acf_vals[i - 1] and acf_vals[i] > acf_vals[i + 1] and acf_vals[i] > conf_bound:
            peaks.append(i)

    has_seasonality = len(peaks) >= 2
    period = peaks[0] if peaks else 0

    return {
        "tool": "correlation_analysis",
        "dominant_lag": dominant_lag,
        "acf_top5": [round(float(v), 4) for v in acf_vals[1:6]],
        "pacf_top5": [round(float(v), 4) for v in pacf_vals[1:6]],
        "significant_lags": significant_lags[:10],
        "has_seasonality": has_seasonality,
        "estimated_period": period,
        "confidence_bound": round(float(conf_bound), 4),
    }


# --- Tool Registry ---
STATISTICAL_TOOLS = {
    "trend_analysis": {
        "fn": trend_analysis,
        "description": "Mann-Kendall trend test with linear regression. Use when you need to determine trend direction and significance.",
        "triggers": ["trend", "direction", "slope"],
    },
    "volatility_analysis": {
        "fn": volatility_analysis,
        "description": "Volatility profiling with rolling stats and clustering detection. Use for high-variance or heteroscedastic data.",
        "triggers": ["volatility", "variance", "unstable"],
    },
    "anomaly_detection": {
        "fn": anomaly_detection,
        "description": "Multi-method anomaly detection (3-sigma, IsolationForest, LOF). Use when outliers may affect forecasting.",
        "triggers": ["anomaly", "outlier", "spike"],
    },
    "stationarity_test": {
        "fn": stationarity_test,
        "description": "ADF + KPSS stationarity tests. Use to decide if differencing is needed before forecasting.",
        "triggers": ["stationary", "unit_root", "differencing"],
    },
    "distribution_test": {
        "fn": distribution_test,
        "description": "Shapiro-Wilk + KS normality tests with skewness/kurtosis. Use to understand data distribution shape.",
        "triggers": ["distribution", "normal", "skew"],
    },
    "changepoint_detection": {
        "fn": changepoint_detection,
        "description": "Binary segmentation changepoint detection. Use when regime shifts or structural breaks are suspected.",
        "triggers": ["changepoint", "regime", "shift", "break"],
    },
    "correlation_analysis": {
        "fn": correlation_analysis,
        "description": "ACF/PACF analysis with seasonality detection. Use to identify autocorrelation structure and periodicity.",
        "triggers": ["correlation", "seasonality", "period", "lag"],
    },
}
