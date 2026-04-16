"""
鼠先知 思考模式 — 核心推理引擎
Thought → Action → Observation 推理循环，支持动态工具选择与自适应分析。
"""

import os
import json
import re
import numpy as np
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from .memory import ReasoningMemory
from .ensemble import ensemble_predict
from .prompts.system import SYSTEM_PROMPT
from .prompts.react import REACT_PROMPT
from .prompts.critic import CRITIC_PROMPT
from .tools import ALL_TOOLS
from utils.llm import build_chat_llm

load_dotenv()


def _init_llm():
    """Initialize LLM from environment."""
    return build_chat_llm(temperature=0.3)


class TSReasoner:  # 保留类名以兼容导入
    """Core ReAct agent for time series analysis and forecasting."""

    def __init__(self, max_steps: int = 8, max_critic_rounds: int = 0,
                 enable_correction: bool = False):
        self.llm = _init_llm()
        self.max_steps = max_steps
        self.max_critic_rounds = max_critic_rounds
        self.enable_correction = enable_correction
        self.tools = ALL_TOOLS

    def predict(self, data_y: list, steps: int = 10) -> dict:
        """完整推理流程: 统计画像 → 推理分析 → 集成预测 → 修正。"""
        memory = ReasoningMemory()
        data = list(data_y)

        # Phase 1: 统计画像
        profile = self._ground(data, memory)

        # Phase 2: 推理分析
        self._reason(data, steps, profile, memory)

        # Phase 3: 集成预测
        ensemble_result = ensemble_predict(data, steps=steps)
        predictions = ensemble_result.get("predictions", [])

        if not predictions:
            predictions = self._fallback(data, steps)

        memory.add_step(
            "Ensemble complete. Applying residual correction.",
            "ensemble_predict", {"steps": steps},
            {"weights": ensemble_result.get("weights", {})},
        )

        # Phase 4: 残差修正
        correction_log = []
        if self.enable_correction:
            cv_residuals = ensemble_result.get("cv_residuals", [])
            predictions, correction_log = self._residual_correction(
                data, predictions, steps, cv_residuals, memory
            )

        return {
            "engine": "思考模式",
            "predictions": predictions,
            "confidence": ensemble_result.get("weights", {}),
            "ci_lower": ensemble_result.get("ci_lower", []),
            "ci_upper": ensemble_result.get("ci_upper", []),
            "data_profile": profile,
            "trajectory": memory.to_dict(),
            "critic_log": correction_log,
            "steps": steps,
        }

    def _ground(self, data: list, memory: ReasoningMemory) -> dict:
        """Phase 1: 统计画像 — 零成本特征提取。"""
        profile = {}

        # Always run these core tools
        core_tools = ["trend_analysis", "volatility_analysis",
                      "stationarity_test", "correlation_analysis"]

        for name in core_tools:
            tool = self.tools.get(name)
            if tool:
                try:
                    result = tool["fn"](data)
                    profile[name] = result
                    memory.add_step(
                        f"Grounding: run {name} for baseline profile.",
                        name, {}, result,
                    )
                except Exception:
                    pass

        return profile

    def _reason(self, data: list, steps: int,
                profile: dict, memory: ReasoningMemory):
        """Phase 2: 推理循环 — 自适应工具选择。"""
        # Decide which additional tools to run based on profile
        extra_tools = self._select_tools(profile)

        for tool_name in extra_tools:
            if len(memory) >= self.max_steps:
                break
            tool = self.tools.get(tool_name)
            if not tool:
                continue
            try:
                result = tool["fn"](data)
                thought = f"Profile suggests running {tool_name}: {tool['description']}"
                memory.add_step(thought, tool_name, {}, result)
                profile[tool_name] = result
            except Exception:
                pass

    def _select_tools(self, profile: dict) -> list:
        """根据数据画像自适应选择分析工具。"""
        selected = []

        vol = profile.get("volatility_analysis", {})
        corr = profile.get("correlation_analysis", {})
        stat = profile.get("stationarity_test", {})

        # High volatility → wavelet + anomaly
        if vol.get("level") == "high":
            selected.extend(["wavelet_decomposition", "anomaly_detection"])

        # Strong periodicity → FFT + periodogram
        if corr.get("has_seasonality"):
            selected.extend(["fft_analysis", "seasonal_decompose"])

        # Non-stationary → difference transform
        if stat.get("verdict") in ("non_stationary", "difference_stationary"):
            selected.append("difference_transform")

        # Always useful
        if "changepoint_detection" not in profile:
            selected.append("changepoint_detection")

        # Deduplicate and skip already-run tools
        seen = set(profile.keys())
        return [t for t in dict.fromkeys(selected) if t not in seen]

    def _residual_correction(self, data, predictions, steps,
                              cv_residuals, memory):
        """Phase 4: Post-Predict — mean bias correction only.

        Only subtract the MEAN of CV residuals as a constant.
        Individual residuals are too noisy to transfer across horizons.
        """
        correction_log = []

        if not cv_residuals or len(cv_residuals) < 2:
            memory.add_step(
                "No CV residuals available, skipping post-predict.",
                "post_predict", {}, {"applied": False}
            )
            return predictions, correction_log

        res = np.array(cv_residuals, dtype=float)
        mean_bias = float(np.mean(res))

        # Only correct if bias is meaningful (|mean| > 0.01)
        if abs(mean_bias) < 0.01:
            memory.add_step(
                f"Mean bias too small ({mean_bias:+.4f}), skipping.",
                "post_predict", {}, {"applied": False, "mean_bias": round(mean_bias, 4)}
            )
            return predictions, correction_log

        preds = np.array(predictions, dtype=float)
        corrected = preds - mean_bias

        log_entry = {
            "applied": True,
            "mean_bias": round(mean_bias, 4),
        }
        correction_log.append(log_entry)
        memory.add_step(
            f"Post-predict: subtracted mean bias {mean_bias:+.4f}.",
            "post_predict", {}, log_entry,
        )

        return [round(float(v), 4) for v in corrected], correction_log

    @staticmethod
    def _fallback(data: list, steps: int) -> list:
        """Linear extrapolation fallback."""
        y = np.array(data, dtype=float)
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        return [round(float(slope * (len(y) + i) + intercept), 4)
                for i in range(steps)]
