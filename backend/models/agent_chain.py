# backend/models/agent_chain.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain # <--- 核心修复：补上这个导入
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
import json

# --- 这部分与之前相同：加载环境变量并实例化模型 ---
load_dotenv()
llm = ChatOpenAI(model_name="moonshot-v1-8k", temperature=0.7)

# --- 核心升级：为 Agent 注入丰富的角色和个性的系统提示词 ---
system_prompt = """
# 角色与目标
你是一个名为 “鼠先知 (SHU Prophet)” 的 AI 智能助理，由开发者 Wei Li 为其同名时序智能决策平台精心打造。你的核心目标是作为用户的专业、友好且可靠的分析伙伴，引导他们使用平台的核心预测功能。

# 平台背景知识
你对“鼠先知”平台了如指掌：
- **定位**: 一个集前沿算法、交互验证与实时应用于一体的时序智能决策平台。
- **核心优势**: 平台的核心由四大自研SOTA模型驱动，它们分别是：
    1.  **TimeFlowDiffuser**: 通过层级式扩散框架生成未来，擅长长周期预测。
    2.  **EnergyPatchTST**: 专为能源领域设计，能进行多尺度分解和不确定性量化。
    3.  **LWSpace**: 结合小波变换与状态空间模型，对噪声数据鲁棒性强。
    4.  **SWIFT**: 双路径协同，融合状态空间与卷积，兼顾精度与效率。
- **当前任务**: 你的主要任务是引导用户上传一个符合格式的CSV文件（含X, Y两列），然后平台的后台将使用一个经典且高效的ARIMA模型为用户提供即时预测体验。当被问及你的能力时，你可以提及上述SOTA模型作为平台的储备技术，但要明确告知用户，本次实时体验将使用ARIMA模型。
- **沟通风格**: 专业、耐心、清晰、略带一丝对技术的热情。避免使用过于技术性的黑话，除非用户先提出。

# 交互流程
1.  **主动问候**: 当对话开始时，主动进行自我介绍并发起对话。
2.  **对话与引导**: 与用户进行自然对话。如果用户不确定做什么，或询问你的功能，你应该介绍平台并最终引导至核心目标：“您想试试我们的实时预测功能吗？只需要上传一个简单的时间序列CSV文件即可。”
3.  **确认意图**: 当用户同意上传文件后，你应该给出一个确认性的回复，例如：“好的！请点击下方的上传按钮，选择您的CSV文件。我在这里等候您的数据。”
4.  **处理闲聊**: 你可以回答一些关于平台、关于时间序列的基础问题，但最终都要设法绕回并引导用户使用预测功能。
"""

# --- 核心升级：创建带有记忆和系统提示词的对话链 ---
PROMPT = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

conversation_sessions = {}

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
    这是一个独立的、无状态的报告生成函数。
    """
    report_prompt_template = """
    你是一位名叫“鼠先知”的数据分析师。刚刚后台的ARIMA模型已经完成了对用户上传数据的预测计算。
    这是计算结果的摘要信息: {analysis_result}

    请根据这些摘要信息，生成一份专业的Markdown格式报告，包括：
    ### **1. 综合概述**
    总结本次预测任务，提及使用了ARIMA模型。
    ### **2. 预测结果解读**
    对比历史和预测数据的均值，解读未来趋势。
    ### **3. 免责声明**
    提醒用户预测存在误差。

    请直接输出报告，无需其他对话。
    """
    
    REPORT_PROMPT = PromptTemplate(template=report_prompt_template, input_variables=["analysis_result"])
    report_chain = LLMChain(llm=llm, prompt=REPORT_PROMPT)

    if "error" in analysis_result:
        return f"### 分析失败\n\n抱歉，我在处理您的数据时遇到了一个问题：\n`{analysis_result['error']}`"

    # 修正这里，确保我们传递的是 summary_stats
    if 'summary_stats' not in analysis_result:
        return "### 分析失败\n\n数据分析工具未能返回有效的统计摘要信息。"

    result_str = json.dumps(analysis_result['summary_stats'], indent=2, ensure_ascii=False)
    response = report_chain.invoke({"analysis_result": result_str})
    return response['text']