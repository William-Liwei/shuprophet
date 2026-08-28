"""Public serialization boundary for Agent results."""

import re

import numpy as np


SENSITIVE_KEYS = {
    "selected_model",
    "models_used",
    "models_compared",
    "cv_errors",
    "model",
    "weights",
}

_INTERNAL_ROUTE_PATTERN = re.compile(
    r"\b(arima|ets|theta|linear)\b",
    flags=re.IGNORECASE,
)


def public_agent_result(result: dict) -> dict:
    """Return useful evidence without exposing internal routing details."""
    return {
        "engine": "鼠先知引擎",
        "predictions": result.get("predictions", []),
        "prediction_interval": result.get("prediction_interval", {}),
        "confidence": result.get("confidence"),
        "candidates_evaluated": len(result.get("models_used", [])),
        "selection_basis": "temporal_holdout",
        "data_profile": _redact(result.get("data_profile", {})),
        "validation": _redact(result.get("validation", {})),
        "trajectory": _format_trajectory(result.get("trajectory", {})),
        "steps": result.get("steps"),
    }


def _format_trajectory(trajectory: dict) -> list:
    formatted = []
    for step in trajectory.get("steps", []):
        observation = step.get("observation", {})
        summary_parts = []
        for key, value in observation.items():
            if key in SENSITIVE_KEYS or key == "tool":
                continue
            display_value = _safe_text(str(value))
            if len(display_value) > 50:
                display_value = display_value[:47] + "..."
            summary_parts.append(f"{key}={display_value}")

        if step.get("action") == "forecast_model_selection":
            compared = observation.get("models_compared", [])
            summary_parts = [
                f"candidates_evaluated={len(compared)}",
                "selection_basis=temporal_holdout",
            ]

        formatted.append({
            "step": step.get("step"),
            "rationale": _safe_text(step.get("thought", "")),
            "tool": step.get("action"),
            "result": ", ".join(summary_parts) if summary_parts else "done",
            "time": step.get("timestamp", 0),
        })
    return formatted


def _redact(value):
    if isinstance(value, dict):
        return {
            key: _redact(item)
            for key, item in value.items()
            if key not in SENSITIVE_KEYS
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, tuple):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, np.ndarray):
        return [_redact(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    return value


def _safe_text(value: str) -> str:
    return _INTERNAL_ROUTE_PATTERN.sub("内部路径", value)
