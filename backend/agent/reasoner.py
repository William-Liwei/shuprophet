"""Lightweight, auditable time-series tool agent."""

import math

import numpy as np

from .ensemble import ensemble_predict
from .memory import ReasoningMemory
from .tools import ALL_TOOLS


class TSReasoner:
    """Run a goal-directed analysis, forecasting, and validation workflow."""

    def __init__(self, max_analysis_steps: int = 8):
        self.max_analysis_steps = max_analysis_steps
        self.tools = ALL_TOOLS

    def predict(self, data_y: list, steps: int = 10) -> dict:
        data = self._validate_input(data_y, steps)
        memory = ReasoningMemory()

        profile = self._build_profile(data, memory)
        self._run_adaptive_analysis(data, profile, memory)

        forecast = ensemble_predict(data, steps=steps)
        predictions = forecast.get("predictions", [])
        if not predictions:
            raise ValueError("没有预测器成功生成结果")

        memory.add_step(
            "依据留出集误差选择预测器，并在完整序列上生成未来值。",
            "forecast_model_selection",
            {"steps": steps},
            {
                "selected_model": forecast.get("selected_model"),
                "models_compared": forecast.get("models_used", []),
                "cv_errors": forecast.get("cv_errors", {}),
            },
        )

        validation = self._validate_forecast(data, predictions, memory)
        confidence = self._confidence_score(forecast, validation)

        return {
            "engine": "SHU Prophet Tool Agent",
            "predictions": predictions,
            "prediction_interval": {
                "lower": forecast.get("ci_lower", []),
                "upper": forecast.get("ci_upper", []),
            },
            "selected_model": forecast.get("selected_model", "unknown"),
            "models_used": forecast.get("models_used", []),
            "cv_errors": forecast.get("cv_errors", {}),
            "confidence": confidence,
            "data_profile": profile,
            "validation": validation,
            "trajectory": memory.to_dict(),
            "steps": steps,
        }

    @staticmethod
    def _validate_input(data_y: list, steps: int) -> list:
        if not 1 <= int(steps) <= 90:
            raise ValueError("预测步数必须在1到90之间")

        try:
            data = [float(value) for value in data_y]
        except (TypeError, ValueError) as exc:
            raise ValueError("时间序列必须全部为数值") from exc

        if len(data) < 10:
            raise ValueError("至少需要10个有效数据点")
        if not all(math.isfinite(value) for value in data):
            raise ValueError("时间序列包含无穷值或非数值")
        if float(np.std(data)) < 1e-12:
            raise ValueError("时间序列为常数，无法进行有效的模型比较")
        return data

    def _build_profile(self, data: list, memory: ReasoningMemory) -> dict:
        profile = {}
        core_tools = (
            "trend_analysis",
            "volatility_analysis",
            "stationarity_test",
            "correlation_analysis",
        )
        for tool_name in core_tools:
            result = self._run_tool(tool_name, data)
            if result is None:
                continue
            profile[tool_name] = result
            memory.add_step(
                "建立基础数据画像。",
                tool_name,
                {},
                result,
            )
        return profile

    def _run_adaptive_analysis(
        self,
        data: list,
        profile: dict,
        memory: ReasoningMemory,
    ) -> None:
        selected = self._select_analysis_tools(profile)
        for tool_name, rationale in selected:
            if len(memory) >= self.max_analysis_steps:
                break
            result = self._run_tool(tool_name, data)
            if result is None:
                continue
            profile[tool_name] = result
            memory.add_step(rationale, tool_name, {}, result)

    def _select_analysis_tools(self, profile: dict) -> list:
        selected = []
        volatility = profile.get("volatility_analysis", {})
        correlation = profile.get("correlation_analysis", {})
        stationarity = profile.get("stationarity_test", {})

        if volatility.get("level") == "high":
            selected.extend([
                ("wavelet_decomposition", "波动性较高，检查不同时间尺度上的能量分布。"),
                ("anomaly_detection", "波动性较高，使用多方法共识检查异常点。"),
            ])

        if correlation.get("has_seasonality"):
            selected.extend([
                ("fft_analysis", "自相关显示潜在周期，使用频谱工具确认主周期。"),
                ("seasonal_decompose", "检测到潜在季节性，分离趋势、季节与残差。"),
            ])

        if stationarity.get("verdict") in {
            "non_stationary",
            "difference_stationary",
        }:
            selected.append(
                ("difference_transform", "平稳性检验提示需要差分，检查差分后的统计特征。")
            )

        selected.append(
            ("changepoint_detection", "检查结构突变，避免用单一稳定机制解释整段序列。")
        )

        deduplicated = []
        seen = set(profile)
        for tool_name, rationale in selected:
            if tool_name not in seen:
                deduplicated.append((tool_name, rationale))
                seen.add(tool_name)
        return deduplicated

    def _validate_forecast(
        self,
        data: list,
        predictions: list,
        memory: ReasoningMemory,
    ) -> dict:
        validation = {}
        for tool_name in (
            "prediction_range_check",
            "trend_consistency_check",
            "confidence_scoring",
        ):
            tool = self.tools.get(tool_name)
            if not tool:
                continue
            try:
                result = tool["fn"](data, predictions)
            except Exception:
                continue
            validation[tool_name] = result
            memory.add_step(
                "对预测结果执行独立统计校验。",
                tool_name,
                {},
                result,
            )
        return validation

    def _run_tool(self, tool_name: str, data: list):
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        try:
            return tool["fn"](data)
        except Exception:
            return None

    @staticmethod
    def _confidence_score(forecast: dict, validation: dict) -> float:
        cv_score = float(forecast.get("cv_confidence", 0.35))
        validation_score = float(
            validation.get("confidence_scoring", {}).get("confidence", 0.5)
        )
        score = 0.65 * cv_score + 0.35 * validation_score

        if not validation.get("prediction_range_check", {}).get("pass", True):
            score *= 0.85
        if not validation.get("trend_consistency_check", {}).get("consistent", True):
            score *= 0.9

        return round(max(0.1, min(0.95, score)), 3)
