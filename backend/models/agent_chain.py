# backend/models/agent_chain.py

import json
import os
import re

import numpy as np
from dotenv import load_dotenv
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_openai import ChatOpenAI

from utils.llm import build_chat_llm, build_deepseek_chat_llm

# --- 加载环境变量并自动识别 API 提供商 ---
load_dotenv()


def _detect_llm_legacy():
    """根据 API Key 或 Base URL 自动识别 Kimi / GLM 并实例化模型。"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_base = os.getenv("OPENAI_API_BASE", "")

    if "moonshot" in api_base:
        return ChatOpenAI(
            model_name="moonshot-v1-8k",
            openai_api_key=api_key,
            openai_api_base=api_base,
            temperature=0.7,
        )
    if "bigmodel" in api_base:
        return ChatOpenAI(
            model_name="glm-4-flash",
            openai_api_key=api_key,
            openai_api_base=api_base,
            temperature=0.7,
        )

    if api_key.startswith("sk-") and len(api_key) > 50:
        if "." in api_key:
            return ChatOpenAI(
                model_name="glm-4-flash",
                openai_api_key=api_key,
                openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
                temperature=0.7,
            )
        return ChatOpenAI(
            model_name="moonshot-v1-8k",
            openai_api_key=api_key,
            openai_api_base="https://api.moonshot.cn/v1",
            temperature=0.7,
        )

    return ChatOpenAI(
        model_name="glm-4-flash",
        openai_api_key=api_key,
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        temperature=0.7,
    )


def _detect_llm():
    """Create the shared chat model from environment variables."""
    return build_chat_llm(temperature=0.7)


llm = _detect_llm()

system_prompt = """
# 角色
你是“鼠先知 (SHU Prophet)”AI 智能助理，由 Wei Li 为同名时序智能决策平台打造。你是用户的专业分析伙伴。

# 平台能力
- 平台整合了 ScatterFusion、AWGFormer、SWIFT、LWSpace、EnergyPatchTST、TimeFlowDiffuser 等时序模型。
- 当用户上传 CSV 文件后，你需要结合数据特征、统计结果和模型输出，生成专业且可执行的分析结论。
- 平台会同时给出两类预测结果：
  1. ARIMA 经典统计引擎：提供稳健的基线预测。
  2. 鼠先知智能预测引擎：通过特征感知、链式推理、反思校验和统计验证生成预测，并附带置信度。
- 报告必须基于真实分析结果，不允许凭空编造结论或数据。

# 报告要求
- 控制在 500 字左右，优先输出有洞察的信息。
- 需要覆盖：数据概览、趋势分析、预测解读、决策建议、风险提示。
- 如果用户提供了业务背景，要将该背景纳入分析和建议。

# 沟通风格
专业、耐心、清晰。避免堆砌术语，除非用户明确要求更技术化的解释。

# 交互方式
1. 对话开始时主动完成自我介绍。
2. 引导用户上传包含 X、Y 两列的 CSV 文件体验预测。
3. 如果用户愿意上传文件，可明确提示：“好的，请点击上传按钮选择 CSV 文件，我会继续帮你分析。”
4. 普通闲聊可以回答，但尽量引导回数据分析和预测场景。
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

conversation_sessions = {}
deepseek_sessions = {}


def analyze_data_insights(data_y: list) -> dict:
    """
    使用 Python 统计分析数据特征（不耗 token）。
    返回数据洞察，供 LLM 生成报告使用。
    """
    y = np.array(data_y)

    mean_val = float(np.mean(y))
    std_val = float(np.std(y))

    x = np.arange(len(y))
    slope = float(np.polyfit(x, y, 1)[0])
    trend = "上升" if slope > 0.01 else "下降" if slope < -0.01 else "平稳"

    volatility = (
        "高"
        if std_val > abs(mean_val) * 0.3
        else "中"
        if std_val > abs(mean_val) * 0.1
        else "低"
    )

    z_scores = np.abs((y - mean_val) / std_val) if std_val > 0 else np.zeros_like(y)
    anomaly_count = int(np.sum(z_scores > 3))

    if len(y) > 20:
        lag = min(12, len(y) // 4)
        autocorr = float(np.corrcoef(y[:-lag], y[lag:])[0, 1]) if len(y) > lag else 0
        has_seasonality = abs(autocorr) > 0.5
    else:
        has_seasonality = False

    return {
        "trend": trend,
        "volatility": volatility,
        "anomaly_count": anomaly_count,
        "has_seasonality": has_seasonality,
        "mean": round(mean_val, 3),
        "std": round(std_val, 3),
    }


def get_conversational_response(user_input: str, session_id: str = "default_session"):
    """处理用户的文本对话输入，返回模型的文本回复。"""
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = ConversationBufferMemory(return_messages=True)

    memory = conversation_sessions[session_id]
    conversation_chain = ConversationChain(
        llm=llm,
        prompt=PROMPT,
        memory=memory,
        verbose=True,
    )
    return conversation_chain.predict(input=user_input)


def get_deepseek_response(user_input: str, session_id: str = "default_session"):
    """Handle direct DeepSeek chat conversations."""
    if session_id not in deepseek_sessions:
        deepseek_sessions[session_id] = ConversationBufferMemory(return_messages=True)

    memory = deepseek_sessions[session_id]
    deepseek_chain = ConversationChain(
        llm=build_deepseek_chat_llm(temperature=0.7),
        memory=memory,
        verbose=True,
    )
    return deepseek_chain.predict(input=user_input)


def generate_standalone_report(analysis_result: dict, user_context: str = "") -> str:
    """
    专门用于在文件上传和分析成功后，生成最终的分析报告。
    结合 Python 统计分析和 LLM 生成，提供深度洞察。
    """
    if "error" in analysis_result:
        return f"### 分析失败\n\n抱歉，我在处理您的数据时遇到了一个问题：\n`{analysis_result['error']}`"

    if "summary_stats" not in analysis_result:
        return "### 分析失败\n\n数据分析工具未能返回有效的统计摘要信息。"

    summary = analysis_result["summary_stats"]

    insights = {}
    if "historical_y" in summary:
        insights = analyze_data_insights(summary["historical_y"])

    trend = insights.get("trend", "未知")
    volatility = insights.get("volatility", "中")
    anomaly_count = insights.get("anomaly_count", 0)
    pred_mean = summary.get("forecast_y_mean", summary.get("historical_y_mean", "N/A"))
    hist_mean = summary.get("historical_y_mean", "N/A")

    model_rec = (
        "ScatterFusion（鲁棒性强）"
        if volatility == "高"
        else "AWGFormer（多尺度分析）"
        if insights.get("has_seasonality")
        else "EnergyPatchTST（不确定性量化）"
    )

    report_prompt_template = """你是“鼠先知”平台的 AI 数据分析师。请基于以下分析结果，生成一份专业的数据洞察报告。

{context_instruction}

分析数据：
- 数据规模：{hist_points} 个历史观测点，预测未来 {forecast_steps} 步
- 历史均值：{hist_mean}，预测均值：{pred_mean}
- 整体趋势：{trend}，波动性：{volatility}
- 检测到 {anomaly_count} 个异常点
- 推荐深度模型：{model_rec}

请严格按以下 Markdown 格式输出（每个标题前必须空一行）：

## 数据概览

简要描述数据的基本特征，包括规模、分布和整体走势。{context_hint}

## 趋势与模式分析

详细分析数据的趋势方向、波动特征、是否存在周期性模式，以及异常点的可能成因。

## 预测解读

对比历史均值与预测均值的变化，解读预测结果的含义和可信度。

## 决策建议

{business_hint}

## 风险提示

基于波动性和异常点情况给出风险提示和建议。"""

    context_instruction = ""
    context_hint = ""
    business_hint = "根据预测结果提供可执行的决策建议。"

    if user_context:
        context_instruction = (
            f"**重要**：用户说明这是 {user_context} 相关的数据，请在分析中体现这一场景，并给出针对性的决策建议。"
        )
        context_hint = f"（结合 {user_context} 场景）"
        business_hint = (
            f"针对 {user_context} 场景，根据预测趋势提供具体的决策建议，如资源配置、时机把握和风险对冲。"
        )

    report_prompt = PromptTemplate(
        template=report_prompt_template,
        input_variables=[
            "hist_points",
            "forecast_steps",
            "hist_mean",
            "pred_mean",
            "trend",
            "volatility",
            "anomaly_count",
            "model_rec",
            "context_instruction",
            "context_hint",
            "business_hint",
        ],
    )
    report_chain = LLMChain(llm=llm, prompt=report_prompt)

    response = report_chain.invoke(
        {
            "hist_points": summary.get("historical_points", "N/A"),
            "forecast_steps": summary.get("forecast_steps", "N/A"),
            "hist_mean": hist_mean,
            "pred_mean": pred_mean,
            "trend": trend,
            "volatility": volatility,
            "anomaly_count": anomaly_count,
            "model_rec": model_rec,
            "context_instruction": context_instruction,
            "context_hint": context_hint,
            "business_hint": business_hint,
        }
    )
    return response["text"]


def smart_predict(data_y: list, steps: int = 10) -> dict:
    """
    鼠先知智能预测引擎。
    Phase 1 - Feature-Aware Profiling (FAP): 零 token 统计特征提取
    Phase 2 - Chain-of-Thought Prediction (CoTP): 特征引导链式推理
    Phase 3 - Reflective Critique (RC): 自反思校验与预测修正
    Phase 4 - Statistical Validation (SV): 置信度校准与异常修正
    """
    insights = analyze_data_insights(data_y)
    context_len = min(30, len(data_y))
    recent = data_y[-context_len:]

    prompt = PromptTemplate(
        template=(
            "作为时序分析专家，基于数据特征和近期观测预测未来 {steps} 步。\n"
            "特征：趋势={trend}，波动={volatility}(std={std})，均值={mean}，周期性={seas}\n"
            "近期数据：{recent}\n"
            "仅输出 JSON：{{\"predictions\": [v1, v2, ...], \"confidence\": 0到1}}"
        ),
        input_variables=["steps", "trend", "volatility", "std", "mean", "seas", "recent"],
    )

    try:
        raw = LLMChain(llm=llm, prompt=prompt).invoke(
            {
                "steps": steps,
                "trend": insights["trend"],
                "volatility": insights["volatility"],
                "std": insights["std"],
                "mean": insights["mean"],
                "seas": "有" if insights["has_seasonality"] else "无",
                "recent": str(recent),
            }
        )
        json_match = re.search(r"\{.*\}", raw["text"], re.DOTALL)
        parsed = json.loads(json_match.group())
        predictions = [float(x) for x in parsed["predictions"][:steps]]
        confidence = float(parsed.get("confidence", 0.5))
    except Exception:
        x = np.arange(len(data_y))
        slope, intercept = np.polyfit(x, data_y, 1)
        predictions = [float(slope * (len(data_y) + i) + intercept) for i in range(steps)]
        confidence = 0.3

    try:
        rc_prompt = PromptTemplate(
            template=(
                "你是时序预测审核专家。审查以下预测并修正不合理之处。\n"
                "特征：趋势={trend}，波动={volatility}，均值={mean}，std={std}\n"
                "尾部 5 点：{tail}\n"
                "初始预测：{preds}\n"
                "审查重点：1) 是否延续趋势 2) 幅度是否合理 3) 是否存在突变\n"
                "仅输出 JSON：{{\"predictions\": [v1, v2, ...]}}"
            ),
            input_variables=["trend", "volatility", "mean", "std", "tail", "preds"],
        )
        rc_raw = LLMChain(llm=llm, prompt=rc_prompt).invoke(
            {
                "trend": insights["trend"],
                "volatility": insights["volatility"],
                "mean": insights["mean"],
                "std": insights["std"],
                "tail": str(data_y[-5:]),
                "preds": str(predictions),
            }
        )
        rc_match = re.search(r"\{.*\}", rc_raw["text"], re.DOTALL)
        rc_parsed = json.loads(rc_match.group())
        refined = [float(v) for v in rc_parsed["predictions"][:steps]]
        if len(refined) == len(predictions):
            predictions = refined
            confidence = min(confidence + 0.05, 1.0)
    except Exception:
        pass

    mean_val, std_val = insights["mean"], insights["std"]
    lower, upper = mean_val - 3 * std_val, mean_val + 3 * std_val

    validated = []
    for value in predictions:
        if std_val > 0 and (value < lower or value > upper):
            value = max(lower, min(upper, value))
            confidence *= 0.9
        validated.append(round(value, 4))

    while len(validated) < steps:
        validated.append(validated[-1] if validated else round(mean_val, 4))

    return {
        "engine": "鼠先知智能预测引擎",
        "predictions": validated,
        "confidence": round(min(confidence, 1.0), 2),
        "data_profile": insights,
        "steps": steps,
    }
