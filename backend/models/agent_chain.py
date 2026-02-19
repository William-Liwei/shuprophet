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
import numpy as np

# --- 这部分与之前相同：加载环境变量并实例化模型 ---
load_dotenv()
llm = ChatOpenAI(model_name="moonshot-v1-8k", temperature=0.7)

# --- 核心升级：为 Agent 注入丰富的角色和个性的系统提示词 ---
system_prompt = """
# 角色与目标
你是一个名为 "鼠先知 (SHU Prophet)" 的 AI 智能助理，由开发者 Wei Li 为其同名时序智能决策平台精心打造。你的核心目标是作为用户的专业、友好且可靠的分析伙伴，引导他们使用平台的核心预测功能。

# 平台背景知识
你对"鼠先知"平台了如指掌：
- **定位**: 一个集前沿算法、交互验证与实时应用于一体的时序智能决策平台。
- **核心优势**: 平台基于6篇CCF高水平论文（2篇CCF-B + 4篇CCF-C）的SOTA模型驱动，它们分别是：
    1.  **ScatterFusion** (ICASSP 2026, CCF-B): 层级散射变换框架，通过多尺度不变特征提取实现鲁棒预测。
    2.  **AWGFormer** (ICASSP 2026, CCF-B): 自适应小波引导Transformer，擅长多分辨率时序预测。
    3.  **SWIFT** (ICANN 2025, CCF-C): 状态空间与小波集成技术，轻量化边缘推理。
    4.  **LWSpace** (ICIC 2025, CCF-C): 多尺度状态空间框架，结合小波分解与选择性状态空间。
    5.  **EnergyPatchTST** (ICIC 2025, CCF-C): 专为能源领域设计，支持多尺度分解和不确定性量化。
    6.  **TimeFlowDiffuser** (ICANN 2025, CCF-C): 层级式扩散框架，擅长长周期预测。
- **当前任务**: 你的主要任务是引导用户上传一个符合格式的CSV文件（含X, Y两列），然后平台的后台将使用一个经典且高效的ARIMA模型为用户提供即时预测体验。当被问及你的能力时，你可以提及上述SOTA模型作为平台的储备技术，但要明确告知用户，本次实时体验将使用ARIMA模型。
- **沟通风格**: 专业、耐心、清晰、略带一丝对技术的热情。避免使用过于技术性的黑话，除非用户先提出。

# 交互流程
1.  **主动问候**: 当对话开始时，主动进行自我介绍并发起对话。
2.  **对话与引导**: 与用户进行自然对话。如果用户不确定做什么，或询问你的功能，你应该介绍平台并最终引导至核心目标："您想试试我们的实时预测功能吗？只需要上传一个简单的时间序列CSV文件即可。"
3.  **确认意图**: 当用户同意上传文件后，你应该给出一个确认性的回复，例如："好的！请点击下方的上传按钮，选择您的CSV文件。我在这里等候您的数据。"
4.  **处理闲聊**: 你可以回答一些关于平台、关于时间序列的基础问题，但最终都要设法绕回并引导用户使用预测功能。
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

    # 提取数据并进行深度分析
    summary = analysis_result['summary_stats']

    # 使用Python分析数据特征（不耗token）
    insights = {}
    if 'historical_y' in summary:
        insights = analyze_data_insights(summary['historical_y'])

    # 构建精简的提示词
    report_prompt_template = """你是"鼠先知"AI分析师。基于以下数据生成专业报告：

数据特征：{insights}
预测结果：{summary}

生成简洁报告（200字内），包括：
1. 数据趋势：{trend}趋势，波动性{volatility}
2. 预测结果：未来均值{pred_mean}
3. 模型推荐：基于{volatility}波动性，推荐使用{model_rec}
4. 风险提示：发现{anomaly_count}个异常点

用专业但易懂的语言，直接输出Markdown。"""

    # 智能模型推荐
    model_rec = "ScatterFusion（鲁棒性强）" if insights.get('volatility') == '高' else \
                "AWGFormer（多尺度分析）" if insights.get('has_seasonality') else \
                "EnergyPatchTST（不确定性量化）"

    REPORT_PROMPT = PromptTemplate(
        template=report_prompt_template,
        input_variables=["insights", "summary", "trend", "volatility", "pred_mean", "model_rec", "anomaly_count"]
    )
    report_chain = LLMChain(llm=llm, prompt=REPORT_PROMPT)

    response = report_chain.invoke({
        "insights": json.dumps(insights, ensure_ascii=False),
        "summary": json.dumps(summary, ensure_ascii=False)[:200],  # 限制长度
        "trend": insights.get('trend', '未知'),
        "volatility": insights.get('volatility', '中'),
        "pred_mean": summary.get('predicted_mean', 'N/A'),
        "model_rec": model_rec,
        "anomaly_count": insights.get('anomaly_count', 0)
    })
    return response['text']