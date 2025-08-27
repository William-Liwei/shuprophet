

# 鼠先知 (SHU Prophet) - 新一代时序智能预测与决策平台

![Project Screenshot](./frontend/src/assets/logo.png)

**鼠先知 (SHU Prophet)** 是一个为高水平科研量身打造的全栈Web应用。它旨在将前沿的时间序列预测算法成果，通过一个交互式、可视化的平台进行展示、验证和应用，打通从理论研究到实践决策的“最后一公里”。

## 项目亮点 (Highlights)

- **成果即数据 (Achievement as Data)**: 采用先进的“CSV驱动”策略，将您的科研成果（即模型跑出的卓越结果）作为核心输入，后端自动完成数据预处理、性能度量和可视化，完美聚焦于展示算法的优越性。
- **全栈技术栈 (Full-Stack Architecture)**: 前端采用 Vue 3 + Vite + Element Plus + ECharts 构建现代化、响应式的用户界面；后端采用 Python + Flask + Pandas + Scikit-learn 提供稳定、高效的数据处理API。
- **丰富的交互体验 (Rich Interaction)**: 提供多页面导航、酷炫的欢迎页、图文并茂的算法介绍以及核心的数据探索与实时预测功能，为用户提供专业、流畅的体验。
- **专业的性能度量 (Professional Metrics)**: 后端会自动计算每个预测模型相对于真实值的 **MAE (平均绝对误差)** 和 **MSE (均方根误差)**，并在前端清晰展示，让模型优劣一目了然。
- **高度可扩展 (Highly Extensible)**: 只需在CSV文件中增加新的数据列，即可在前端自动展示新模型的对比结果，无需修改任何代码，极大方便了算法的迭代与验证。

## 快速开始 (Quick Start)

在开始之前，请确保您的电脑上已经安装了以下环境：

- **Python** (>= 3.7)
- **Node.js** (>= 16)
- **pip** & **npm**

### 1. 启动后端服务 (Backend)

首先，启动提供数据处理API的Flask后端。

```bash
# 1. 进入后端目录
cd backend

# 2. (推荐) 创建并激活Python虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 3. 安装所有Python依赖
pip install -r requirements.txt

# 4. 运行Flask后端服务
python app.py

# 服务将运行在 http://127.0.0.1:5000
# 请保持此终端窗口运行
```

### 2. 启动前端服务 (Frontend)

然后，在**新的终端窗口**中启动提供用户界面的Vite前端。

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装所有Node.js依赖
npm install

# 3. 启动Vite开发服务器
npm run dev

# 前端应用将运行在 http://localhost:5173 (或其它可用端口)
```

现在，打开您的浏览器并访问 `http://localhost:5173`，即可开始探索“鼠先知”平台！

## 技术栈 (Tech Stack)

| 分类               | 技术                                                                        |
| ------------------ | --------------------------------------------------------------------------- |
| **前端**     | `Vue 3`, `Vite`, `Vue Router`, `Element Plus`, `ECharts`          |
| **后端**     | `Python 3`, `Flask`, `Pandas`, `NumPy`, `Scikit-learn`, `SciPy` |
| **开发工具** | `VS Code`, `Git`, `npm`, `pip`                                      |

## 项目结构 (Project Structure)

```
prophet-project-v2/
├── backend/                  # 后端代码
│   ├── app.py                # Flask 主应用
│   ├── requirements.txt      # Python 依赖
│   └── static_data/          # 静态数据目录
│       └── research_datasets/  # 科研成果CSV存放处
├── frontend/                 # 前端代码
│   ├── public/               # 静态资源 (如favicon)
│   ├── src/
│   │   ├── assets/           # 静态资源 (会被Vite处理)
│   │   ├── components/       # Vue 可复用组件
│   │   ├── router/           # Vue 路由配置
│   │   ├── views/            # Vue 页面级组件
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 应用入口
│   ├── package.json          # Node.js 依赖
│   └── vite.config.js        # Vite 配置文件
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

## 作者 (Authors)

- **Wei Li**

---
