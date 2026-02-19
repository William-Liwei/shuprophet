# 鼠先知 (SHU Prophet) - 时序预测模型可视化平台

<div align="center">
  <img src="./frontend/src/assets/logo.png" alt="Project Logo" width="600"/>
</div>

<p align="center">
  <strong>基于团队自研的时间序列分析模型交互式展示平台</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js" alt="Vue 3">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python" alt="Python 3">
  <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/LangChain-Integration-8A2BE2?style=for-the-badge" alt="LangChain">
</p>

---

**鼠先知 (SHU Prophet)** 是一个用于展示和对比时间序列预测模型性能的Web应用平台。平台集成了多个已发表的学术模型，提供交互式可视化界面和AI辅助分析功能，便于研究人员和开发者直观地理解不同模型的预测效果。

## 核心功能

### 📊 模型性能可视化

- **多模型对比展示**: 在同一图表中对比多个预测模型的表现
- **性能指标计算**: 自动计算并展示MAE、MSE等评估指标
- **交互式图表**: 基于ECharts的动态图表，支持缩放、数据筛选等操作
- **性能排名**: 按预测精度自动排序，直观展示模型优劣

### 🤖 AI智能分析

平台集成了基于LangChain的AI助理，提供以下功能：

- **数据特征分析**: 自动识别趋势、波动性、异常值和周期性
- **模型推荐**: 根据数据特征智能推荐适合的预测模型
- **分析报告生成**: 自动生成包含数据洞察和预测结果的专业报告
- **对话式交互**: 支持自然语言问答，解答用户关于模型和预测的疑问

### 🔬 集成模型

平台展示了以下已发表的时间序列预测模型：

| 模型                       | 会议        | 级别  | 核心技术                  |
| -------------------------- | ----------- | ----- | ------------------------- |
| **ScatterFusion**    | ICASSP 2026 | CCF-B | 层级散射变换              |
| **AWGFormer**        | ICASSP 2026 | CCF-B | 自适应小波引导Transformer |
| **EnergyPatchTST**   | ICIC 2025   | CCF-C | 序列分块与不确定性量化    |
| **SWIFT**            | ICANN 2025  | CCF-C | 状态空间与扩张卷积融合    |
| **LWSpace**          | ICIC 2025   | CCF-C | 小波分解与选择性状态空间  |
| **TimeFlowDiffuser** | ICANN 2025  | CCF-C | 层级式扩散框架            |

## 快速开始

### 环境要求

- **Python** >= 3.9
- **Node.js** >= 16
- **pip** & **npm**

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 为 .env，并填入API密钥
cp .env.example .env

# 启动服务
python app.py
```

后端服务将运行在 `http://127.0.0.1:5000`

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将运行在 `http://localhost:5173`

## 技术架构

### 前端技术栈

- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **数据可视化**: ECharts
- **路由**: Vue Router
- **HTTP客户端**: Axios

### 后端技术栈

- **Web框架**: Flask
- **数据处理**: Pandas, NumPy
- **统计分析**: Scikit-learn, Statsmodels
- **AI集成**: LangChain, OpenAI-compatible APIs

### AI功能实现

平台的AI分析功能采用混合架构：

- **统计分析**: 使用Python进行趋势检测、异常识别等计算（无API调用成本）
- **自然语言生成**: 使用LLM将分析结果转化为易读的报告
- **对话管理**: 基于LangChain的会话记忆和上下文管理

## 项目结构

```
shu-prophet/
├── backend/
│   ├── models/
│   │   ├── agent_chain.py          # AI助理核心逻辑
│   │   ├── prediction_tool.py      # 预测分析工具
│   │   └── arima_predictor.py      # ARIMA基线模型
│   ├── static_data/
│   │   └── research_datasets/      # 预测数据集
│   ├── app.py                      # Flask主应用
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Vue组件
│   │   ├── views/                  # 页面视图
│   │   ├── router/                 # 路由配置
│   │   └── assets/                 # 静态资源
│   └── package.json
│
└── README.md
```

## 数据格式

平台使用标准CSV格式存储预测数据。每个数据集包含：

- `actual_x`, `actual_y`: 真实观测值
- `{ModelName}_x`, `{ModelName}_y`: 各模型的预测值

示例：

```csv
actual_x,actual_y,ScatterFusion_x,ScatterFusion_y,AWGFormer_x,AWGFormer_y
0.0,-1.086,0.0,-1.089,0.0,-1.092
0.1,-1.006,0.1,-1.008,0.1,-1.011
...
```

## 使用说明

### 查看模型对比

1. 访问"科研成果探索"页面
2. 选择数据集（如ETTh1_full.csv）
3. 系统自动加载并展示所有模型的预测结果
4. 查看性能对比图表和评估指标

### 使用AI分析

1. 访问"智能助手"页面
2. 上传自己的时间序列数据（CSV格式）
3. AI助理自动分析数据特征并生成报告
4. 可通过对话进一步询问分析细节

### 查看算法详情

1. 访问"算法文库"页面
2. 浏览各模型的技术细节和论文信息
3. 查看BibTeX引用格式

## 作者

**Wei Li**
Shanghai University
liwei008009@163.com

## 许可

本项目仅用于学术研究和教学展示。

---

<p align="center">
  <em>Time Series Forecasting Research Platform</em>
</p>
