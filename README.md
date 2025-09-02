
# 鼠先知 (SHU Prophet) - 新一代时序智能预测与决策平台

<div align="center">
  <img src="./frontend/src/assets/logo.png" alt="Project Logo" width="600"/>
</div>

<p align="center">
  <strong>一个集前沿算法、交互验证与AI智能助理于一体的全栈Web应用，专为高水平科研成果的展示、探索与应用而生。</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js" alt="Vue 3">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python" alt="Python 3">
  <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/LangChain-Integration-8A2BE2?style=for-the-badge" alt="LangChain">
</p>

---

**鼠先知 (SHU Prophet)** 旨在将复杂的前沿时间序列预测算法，通过一个交互式、可视化的平台进行呈现、验证和应用，彻底打通从理论研究到实践决策的“最后一公里”。平台的核心驱动力不仅包括强大的自研模型矩阵，更引入了由大语言模型（LLM）赋能的 **AI智能助理**，将用户体验提升到全新高度。

## 项目亮点 (Highlights)

- **AI 智能助理 (AI Agent)**: 平台内置由 `LangChain` 和大语言模型（如Kimi, Claude）驱动的AI助理。它不仅能与用户进行自然语言对话，更能深度理解项目背景，引导用户上传数据，并自动生成专业的、图文并茂的预测分析报告。
- **自研模型矩阵 (Proprietary Models)**: 平台理论核心由四大独立设计和实现的SOTA（State-of-the-Art）模型驱动，共同构成了强大的预测能力：

  - **TimeFlowDiffuser**: 创新的层级式扩散框架，擅长长周期预测。
  - **EnergyPatchTST**: 专为能源领域设计，支持多尺度分解与不确定性量化。
  - **LWSpace**: 结合小波变换与状态空间，对噪声数据鲁棒性极强。
  - **SWIFT**: 双路径协同架构，完美平衡预测精度与效率。
- **成果即数据 (Achievement as Data)**: 采用“CSV驱动”策略，科研成果（模型预测结果）可作为核心输入，后端自动完成数据预处理、性能度量（MAE/MSE）和多模型可视化对比。
- **现代化全栈技术 (Modern Full-Stack)**: 前端采用 `Vue 3 + Vite + Element Plus + ECharts` 构建响应式界面；后端采用 `Python + Flask + Pandas` 提供高效数据API，并通过 `LangChain` 无缝集成大模型能力。
- **高度可扩展 (Highly Extensible)**: 在“科研成果探索”模块中，只需在CSV文件中增加数据列，即可在前端自动展示新模型的对比结果，无需修改任何代码，极大方便了算法的迭代与验证。

## 快速开始 (Quick Start)

在开始之前，请确保您的电脑上已经安装了以下环境：

- **Python** (>= 3.9)
- **Node.js** (>= 16)
- **pip** & **npm**

### 1. 启动后端服务 (Backend)

首先，启动提供数据处理和AI助理API的Flask后端。

```bash
# 1. 进入后端目录
cd backend

# 2. (推荐) 创建并激活Python虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 3. 安装所有Python依赖
pip install -r requirements.txt

# 4. 配置API密钥(重要!)
#    - 复制 .env.example 文件并重命名为 .env
#    - cp .env.example .env
#    - 在 .env 文件中填入你的大模型API Key (例如 Kimi 或 Claude)

# 5. 运行Flask后端服务
python app.py

# 服务将运行在 http://127.0.0.1:5000
# 请保持此终端窗口运行
```

### 2. 启动前端服务 (Frontend)

然后，在**一个新的终端窗口**中启动提供用户界面的Vite前端。

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装所有Node.js依赖
npm install

# 3. 启动Vite开发服务器
npm run dev

# 前端应用将运行在 http://localhost:5173 (或其它可用端口)
```

现在，打开您的浏览器并访问 `http://localhost:5173`，即可开始与“鼠先知”平台的AI智能助理互动！

## 技术栈 (Tech Stack)

| 分类                           | 技术                                                                              |
| :----------------------------- | :-------------------------------------------------------------------------------- |
| **前端 (Frontend)**      | `Vue 3`, `Vite`, `Vue Router`, `Element Plus`, `ECharts`, `Axios`     |
| **后端 (Backend)**       | `Python 3`, `Flask`, `Pandas`, `NumPy`, `Scikit-learn`, `Statsmodels` |
| **AI 核心 (AI Core)**    | `LangChain`, `ChatOpenAI` (兼容 Kimi, Claude 等), `ConversationChain`       |
| **开发工具 (Dev Tools)** | `VS Code`, `Git`, `npm`, `pip`, `venv`, `python-dotenv`               |

## 项目结构 (Project Structure)

```
shu-prophet/
├── backend/                  # 后端代码
│   ├── models/               # 核心逻辑模块
│   │   ├── agent_chain.py    # LangChain 智能助理核心
│   │   ├── prediction_tool.py# 数据分析与预测工具
│   │   └── ...
│   ├── static_data/          # 静态数据目录
│   │   └── research_datasets/  # 科研成果CSV存放处
│   ├── uploads/              # 用户上传文件存放处
│   ├── .env                  # (需自行创建) 环境变量，存放API Key
│   ├── .env.example          # 环境变量示例文件
│   ├── app.py                # Flask 主应用
│   └── requirements.txt      # Python 依赖
│
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── assets/           # 静态资源
│   │   ├── components/       # Vue 可复用组件 (AgentInteraction.vue 等)
│   │   ├── router/           # Vue 路由配置
│   │   ├── views/            # Vue 页面级组件 (AgentView.vue 等)
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 应用入口
│   ├── package.json          # Node.js 依赖
│   └── ...
│
└── README.md                 # 就是你正在看的这个文件
```

## 如何扩展？(How to Extend)

扩展本项目的核心成果展示非常简单！

假设您有一个新的模型 `MyAwesomeModel`，并已得到其预测结果。

1. 打开 `backend/static_data/research_datasets/` 目录下的CSV文件。
2. 在文件的**第二行（表头行）**，在末尾新增两列：`MyAwesomeModel_X,MyAwesomeModel_Y`。
3. 在下面的**数据行**中，将您的新模型预测的 `x` 和 `y` 结果数据，分别粘贴到这两列下方。
4. 保存文件。

**完成！** 您无需修改任何代码。刷新前端页面，在“核心功能”的图表和指标卡片中，就会自动出现新模型 `MyAwesomeModel` 的对比结果。

## 作者 (Author)

- **Wei Li, Shanghai University**
- liwei008009@163.com

---

<p align="center">
  <em>为推动时间序列研究的发展而构建。</em>
</p>
