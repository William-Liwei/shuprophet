# backend/models/agent_chain.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
import json
import re
import numpy as np

# --- 加载环境变量并自动识别 API 提供商 ---
load_dotenv()

def _detect_llm():
    """根据 API Key 或 Base URL 自动识别 Kimi / GLM 并实例化模型"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_base = os.getenv("OPENAI_API_BASE", "")

    # 按 base URL 识别
    if "moonshot" in api_base:
        return ChatOpenAI(model_name="moonshot-v1-8k", openai_api_key=api_key,
                          openai_api_base=api_base, temperature=0.7)
    if "bigmodel" in api_base:
        return ChatOpenAI(model_name="glm-4-flash", openai_api_key=api_key,
                          openai_api_base=api_base, temperature=0.7)

    # 无 base URL 时按 key 前缀猜测
    if api_key.startswith("sk-") and len(api_key) > 50:
        # 智谱 key 通常较长（含 . 分隔）
        if "." in api_key:
            return ChatOpenAI(model_name="glm-4-flash", openai_api_key=api_key,
                              openai_api_base="https://open.bigmodel.cn/api/paas/v4/", temperature=0.7)
        return ChatOpenAI(model_name="moonshot-v1-8k", openai_api_key=api_key,
                          openai_api_base="https://api.moonshot.cn/v1", temperature=0.7)

    # 默认 GLM
    return ChatOpenAI(model_name="glm-4-flash", openai_api_key=api_key,
                      openai_api_base="https://open.bigmodel.cn/api/paas/v4/", temperature=0.7)

llm = _detect_llm()

# --- 核心升级：为 Agent 注入丰富的角色和个性的系统提示词 ---
system_prompt = """
# 角色
你是"鼠先知 (SHU Prophet)"AI智能助理，由Wei Li为同名时序智能决策平台打造。你是用户的专业分析伙伴。

# 平台能力
- 平台基于6篇CCF论文（2篇CCF-B + 4篇CCF-C）的SOTA模型：ScatterFusion、AWGFormer、SWIFT、LWSpace、EnergyPatchTST、TimeFlowDiffuser。
1.  **ScatterFusion** (ICASSP 2026, CCF-B): 层级散射变换框架，通过多尺度不变特征提取实现鲁棒预测。
2.  **AWGFormer** (ICASSP 2026, CCF-B): 自适应小波引导Transformer，擅长多分辨率时序预测。
3.  **SWIFT** (ICANN 2025, CCF-C): 状态空间与小波集成技术，轻量化边缘推理。
4.  **LWSpace** (ICIC 2025, CCF-C): 多尺度状态空间框架，结合小波分解与选择性状态空间。
5.  **EnergyPatchTST** (ICIC 2025, CCF-C): 专为能源领域设计，支持多尺度分解和不确定性量化。
6.  **TimeFlowDiffuser** (ICANN 2025, CCF-C): 层级式扩散框架，擅长长周期预测。
在用户上传CSV文件后，你将基于数据特征分析，智能推荐最适合的模型，并生成专业的预测报告。预测报告将包含数据洞察、趋势分析、预测解读、模型推荐和风险提示等内容，帮助用户深入理解预测结果。但要注意，报告内容必须基于数据特征分析和模型预测结果，不能凭空编造。
数据分析报告字数保持在500字以内，内容必须专业且有洞察力，避免过于冗长或表面化的描述。

- 当用户上传CSV文件后，平台会同时启动两个预测引擎：
  1. **ARIMA经典统计引擎**：基于自回归积分滑动平均模型，提供稳健的基线预测。
  2. **鼠先知智能预测引擎**：平台自研的多Agent协作框架，通过特征感知(FAP)、链式推理(CoTP)、反思校验(RC)、统计验证(SV)四阶段流水线生成预测，并输出置信度评分。
- 两个引擎的预测结果会在同一张图表上对比展示（ARIMA为绿色虚线，智能引擎为橙色点线），帮助用户交叉验证。

# 报告增强要求
在生成预测报告时，除了技术分析外，还应包含商业决策建议：
- 根据预测趋势给出可执行的业务建议
- 识别关键时间节点和风险点
- 提供资源配置或决策优化方向
- 避免编造具体数据（如百分比），基于实际预测结果给建议

# 沟通风格
专业、耐心、清晰。避免过于技术性的黑话，除非用户先提出。

# 交互流程
1. 对话开始时主动自我介绍。
2. 引导用户上传CSV文件（含X, Y两列）体验双引擎预测。
3. 用户同意后确认："好的！请点击上传按钮选择CSV文件，我在这里等候。"
4. 闲聊时可回答时间序列相关问题，但最终引导至预测功能。
"""

# --- 核心升级：创建带有记忆和系统提示词的对话链 ---
PROMPT = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

conversation_sessions = {}

def analyze_data_insights(data_y: list) -> dict:
    """
    使用Python统计分析数据特征（不耗token）
    返回数据洞察，供LLM生成报告使用
    """
    y = np.array(data_y)

    # 基础统计
    mean_val = float(np.mean(y))
    std_val = float(np.std(y))

    # 趋势检测（线性拟合斜率）
    x = np.arange(len(y))
    slope = float(np.polyfit(x, y, 1)[0])
    trend = "上升" if slope > 0.01 else "下降" if slope < -0.01 else "平稳"

    # 波动性
    volatility = "高" if std_val > abs(mean_val) * 0.3 else "中" if std_val > abs(mean_val) * 0.1 else "低"

    # 异常值检测（3-sigma规则）
    z_scores = np.abs((y - mean_val) / std_val) if std_val > 0 else np.zeros_like(y)
    anomaly_count = int(np.sum(z_scores > 3))

    # 周期性检测（简单自相关）
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
        "std": round(std_val, 3)
    }

def get_conversational_response(user_input: str, session_id: str = "default_session"):
    """
    处理用户的文本对话输入，返回模型的文本回复。
    """
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = ConversationBufferMemory(return_messages=True)
    
    memory = conversation_sessions[session_id]

    conversation_chain = ConversationChain(
        llm=llm,
        prompt=PROMPT,
        memory=memory,
        verbose=True
    )

    response = conversation_chain.predict(input=user_input)
    return response

# --- 这部分是从旧代码保留的，用于文件处理完成后生成报告 ---
def generate_standalone_report(analysis_result: dict) -> str:
    """
    专门用于在文件上传和分析成功后，生成最终的分析报告。
    结合Python统计分析和LLM生成，提供深度洞察。
    """
    if "error" in analysis_result:
        return f"### 分析失败\n\n抱歉，我在处理您的数据时遇到了一个问题：\n`{analysis_result['error']}`"

    if 'summary_stats' not in analysis_result:
        return "### 分析失败\n\n数据分析工具未能返回有效的统计摘要信息。"

    summary = analysis_result['summary_stats']

    # 从 summary 中提取原始数据进行统计分析
    insights = {}
    if 'historical_y' in summary:
        insights = analyze_data_insights(summary['historical_y'])

    trend = insights.get('trend', '未知')
    volatility = insights.get('volatility', '中')
    anomaly_count = insights.get('anomaly_count', 0)
    pred_mean = summary.get('forecast_y_mean', summary.get('historical_y_mean', 'N/A'))
    hist_mean = summary.get('historical_y_mean', 'N/A')

    model_rec = "ScatterFusion（鲁棒性强）" if volatility == '高' else \
                "AWGFormer（多尺度分析）" if insights.get('has_seasonality') else \
                "EnergyPatchTST（不确定性量化）"

    report_prompt_template = """你是"鼠先知"平台的AI数据分析师。请基于以下分析结果，生成一份专业的数据洞察报告。

分析数据：
- 数据规模：{hist_points}个历史观测点，预测未来{forecast_steps}步
- 历史均值：{hist_mean}，预测均值：{pred_mean}
- 整体趋势：{trend}，波动性：{volatility}
- 检测到{anomaly_count}个异常点
- 推荐深度模型：{model_rec}

请严格按以下Markdown格式输出（每个标题前必须空一行）：

## 数据概览

简要描述数据的基本特征，包括规模、分布和整体走势。

## 趋势与模式分析

详细分析数据的趋势方向、波动特征、是否存在周期性模式，以及异常点的可能成因。

## 预测解读

对比历史均值与预测均值的变化，解读预测结果的含义和可信度。

## 模型推荐

基于数据特征推荐最适合的深度学习模型，并简要说明推荐理由。

## 风险提示

基于波动性和异常点情况给出风险提示和建议。"""

    REPORT_PROMPT = PromptTemplate(
        template=report_prompt_template,
        input_variables=["hist_points", "forecast_steps", "hist_mean", "pred_mean",
                         "trend", "volatility", "anomaly_count", "model_rec"]
    )
    report_chain = LLMChain(llm=llm, prompt=REPORT_PROMPT)

    response = report_chain.invoke({
        "hist_points": summary.get('historical_points', 'N/A'),
        "forecast_steps": summary.get('forecast_steps', 'N/A'),
        "hist_mean": hist_mean,
        "pred_mean": pred_mean,
        "trend": trend,
        "volatility": volatility,
        "anomaly_count": anomaly_count,
        "model_rec": model_rec
    })
    return response['text']


# === 鼠先知智能预测引擎 ===
# 四阶段 Agent 协作框架：FAP → CoTP → RC → SV

def smart_predict(data_y: list, steps: int = 10) -> dict:
    """
    鼠先知智能预测引擎
    Phase 1 - Feature-Aware Profiling (FAP): 零token统计特征提取
    Phase 2 - Chain-of-Thought Prediction (CoTP): 特征引导链式推理
    Phase 3 - Reflective Critique (RC): 自反思校验与预测修正
    Phase 4 - Statistical Validation (SV): 置信度校准与异常修正
    """
    # === Phase 1: FAP ===
    insights = analyze_data_insights(data_y)
    context_len = min(30, len(data_y))
    recent = data_y[-context_len:]

    # === Phase 2: CoTP ===
    prompt = PromptTemplate(
        template=(
            "作为时序分析专家，基于数据特征和近期观测预测未来{steps}步。\n"
            "特征：趋势={trend}, 波动={volatility}(std={std}), "
            "均值={mean}, 周期性={seas}\n"
            "近期数据：{recent}\n"
            "仅输出JSON：{{\"predictions\": [v1,v2,...], \"confidence\": 0到1}}"
        ),
        input_variables=["steps", "trend", "volatility", "std", "mean", "seas", "recent"]
    )

    try:
        raw = LLMChain(llm=llm, prompt=prompt).invoke({
            "steps": steps, "trend": insights["trend"],
            "volatility": insights["volatility"], "std": insights["std"],
            "mean": insights["mean"],
            "seas": "有" if insights["has_seasonality"] else "无",
            "recent": str(recent)
        })
        json_match = re.search(r'\{.*\}', raw["text"], re.DOTALL)
        parsed = json.loads(json_match.group())
        predictions = [float(x) for x in parsed["predictions"][:steps]]
        confidence = float(parsed.get("confidence", 0.5))
    except Exception:
        # Fallback: 线性外推
        x = np.arange(len(data_y))
        slope, intercept = np.polyfit(x, data_y, 1)
        predictions = [float(slope * (len(data_y) + i) + intercept) for i in range(steps)]
        confidence = 0.3

    # === Phase 3: RC (Reflective Critique) ===
    try:
        rc_prompt = PromptTemplate(
            template=(
                "你是时序预测审核专家。审查以下预测并修正不合理之处。\n"
                "特征：趋势={trend}, 波动={volatility}, 均值={mean}, std={std}\n"
                "尾部5点：{tail}\n初始预测：{preds}\n"
                "审查：1)是否延续趋势 2)幅度是否合理 3)有无突变\n"
                "仅输出JSON：{{\"predictions\": [v1,v2,...]}}"
            ),
            input_variables=["trend", "volatility", "mean", "std", "tail", "preds"]
        )
        rc_raw = LLMChain(llm=llm, prompt=rc_prompt).invoke({
            "trend": insights["trend"], "volatility": insights["volatility"],
            "mean": insights["mean"], "std": insights["std"],
            "tail": str(data_y[-5:]), "preds": str(predictions)
        })
        rc_match = re.search(r'\{.*\}', rc_raw["text"], re.DOTALL)
        rc_parsed = json.loads(rc_match.group())
        refined = [float(v) for v in rc_parsed["predictions"][:steps]]
        if len(refined) == len(predictions):
            predictions = refined
            confidence = min(confidence + 0.05, 1.0)
    except Exception:
        pass  # RC失败保留原始预测

    # === Phase 4: SV ===
    mean_val, std_val = insights["mean"], insights["std"]
    lower, upper = mean_val - 3 * std_val, mean_val + 3 * std_val

    validated = []
    for p in predictions:
        if std_val > 0 and (p < lower or p > upper):
            p = max(lower, min(upper, p))
            confidence *= 0.9
        validated.append(round(p, 4))

    while len(validated) < steps:
        validated.append(validated[-1] if validated else round(mean_val, 4))

    return {
        "engine": "鼠先知智能预测引擎",
        "predictions": validated,
        "confidence": round(min(confidence, 1.0), 2),
        "data_profile": insights,
        "steps": steps
    }