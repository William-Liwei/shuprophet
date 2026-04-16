# 鼠先知 (SHU Prophet)

<div align="center">
  <img src="./frontend/src/assets/logo.png" alt="SHU Prophet Logo" width="600"/>

<p>
    <strong>学术驱动的时间序列智能决策平台</strong>
  </p>

<p>
    <a href="https://github.com/William-Liwei/shuprophet/stargazers">
      <img src="https://img.shields.io/github/stars/William-Liwei/shuprophet?style=social" alt="GitHub stars">
    </a>
    <a href="https://github.com/William-Liwei/shuprophet/network/members">
      <img src="https://img.shields.io/github/forks/William-Liwei/shuprophet?style=social" alt="GitHub forks">
    </a>
    <a href="https://github.com/William-Liwei/shuprophet/issues">
      <img src="https://img.shields.io/github/issues/William-Liwei/shuprophet" alt="GitHub issues">
    </a>
    <a href="https://github.com/William-Liwei/shuprophet/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/William-Liwei/shuprophet" alt="License">
    </a>
  </p>

<p>
    <img src="https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js" alt="Vue 3">
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/LangChain-Powered-8A2BE2?style=for-the-badge" alt="LangChain">
    <img src="https://img.shields.io/badge/PostgreSQL-Supported-4169E1?style=for-the-badge&logo=postgresql" alt="PostgreSQL">
  </p>
</div>

## ⭐ Star History

<div align="center">
  <a href="https://star-history.com/#William-Liwei/shuprophet&Date">
    <img src="https://api.star-history.com/svg?repos=William-Liwei/shuprophet&type=Date" alt="Star History Chart" width="600">
  </a>
</div>

---

## 📖 项目简介

**鼠先知 (SHU Prophet)** 是一个将学术研究成果产品化的时间序列智能决策平台。平台背后的 6 个预测模型全部来自团队发表在 CCF 推荐国际会议上的原创论文（2 篇 CCF-B + 4 篇 CCF-C），覆盖小波变换、散射变换、状态空间模型、扩散模型等前沿方向。

与传统的"跑脚本看结果"不同，鼠先知提供了完整的 Web 交互体验：AI 智能助理对话式分析、多模型可视化对比、社区广场知识共享、用户积分与等级体系 — 让时序预测不再只是研究者的专属工具，更是企业决策者和数据分析师的得力助手。

### 🎓 学术背景

| 级别  | 会议                   | 论文数 |
| ----- | ---------------------- | ------ |
| CCF-B | ICASSP 2026            | 2 篇   |
| CCF-C | ICANN 2025 / ICIC 2025 | 4 篇   |

所有论文均由 **黎玮 (Wei Li)** 作为第一作者完成。

## 💡 为什么选择鼠先知？

### 🤖 AI 驱动的分析体验

- **对话式交互**：通过自然语言与 AI 助理沟通，无需编程即可完成数据分析
- **双引擎预测**：ARIMA 经典统计引擎 + 自研多 Agent 协作智能引擎，交叉验证结果
- **深度推理模式**：支持思考链（Chain-of-Thought）推理，展示完整分析轨迹
- **智能报告生成**：自动识别趋势、波动性、异常值，生成专业分析报告

### 📊 科研级可视化

- **多模型对比**：在同一图表中对比 6 个自研模型的预测效果
- **标准化评估**：自动计算 MAE、MSE 等指标，确保公平对比
- **交互式图表**：基于 ECharts 的动态图表，支持缩放、筛选、导出

### 🌐 社区与协作

- **社区广场**：分享 AI 对话和分析结果，与其他用户交流
- **等级体系**：基于累计积分的用户等级系统，升级获得奖励
- **积分系统**：每日免费对话额度 + 积分充值，支持兑换码
- **用户中心**：注册登录、个人资料、头像管理、对话历史
- **管理功能**：管理员可管理社区内容，维护平台秩序

### ☁️ 开箱即用

- **零环境配置**：云端部署，浏览器打开即用
- **跨平台**：PC、平板、手机均可访问
- **一键部署**：Docker + Zeabur，几分钟上线

## 🔬 集成模型

平台集成了 6 个自研时间序列预测模型，覆盖从经典信号处理到前沿生成式建模的多种技术路线：

| 模型                       | 会议        | 级别  | 核心技术                   | 适用场景                 |
| -------------------------- | ----------- | ----- | -------------------------- | ------------------------ |
| **ScatterFusion**    | ICASSP 2026 | CCF-B | 层级散射变换，宏微观融合   | 非平稳序列、噪声鲁棒预测 |
| **AWGFormer**        | ICASSP 2026 | CCF-B | 自适应小波引导 Transformer | 长期依赖、多分辨率分析   |
| **EnergyPatchTST**   | ICIC 2025   | CCF-C | 序列分块与不确定性量化     | 能源预测、置信区间估计   |
| **SWIFT**            | ICANN 2025  | CCF-C | 状态空间与扩张卷积融合     | 边缘部署、低延迟推理     |
| **LWSpace**          | ICIC 2025   | CCF-C | 小波分解与选择性状态空间   | 精度与效率平衡           |
| **TimeFlowDiffuser** | ICANN 2025  | CCF-C | 层级式扩散框架             | 长周期预测、数据生成     |

## 👥 团队

**鼠先知**由上海大学计算机工程与科学学院本科生团队开发：

<div align="center">

| 姓名                           | 角色                  | 贡献                                 |
| ------------------------------ | --------------------- | ------------------------------------ |
| **黎玮 (Wei Li)**        | 项目负责人 & 算法研发 | 6 篇论文第一作者，核心算法与平台架构 |
| **王子欣 (Zixin Wang)**  | 前端开发              | 用户界面设计与交互优化               |
| **徐若轩 (Ruoxuan Xu)**  | 后端开发              | 服务架构与 API 设计                  |
| **杨哲涵 (Zhehan Yang)** | 全栈开发              | 系统集成与部署                       |

</div>

**联系方式**: liwei008009@163.com

## 🚀 部署指南

### 方式一：Zeabur 一键部署（推荐）

1. Fork 本仓库到你的 GitHub 账号
2. 在 [Zeabur](https://zeabur.com) 创建项目，导入 GitHub 仓库
3. 添加 **PostgreSQL** 服务（Zeabur 会自动注入 `DATABASE_URL`）
4. 在服务的环境变量中配置：

```
OPENAI_API_KEY=你的API密钥
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4/
ZHIPU_MODEL=glm-4-flash-250414
DEEPSEEK_API_KEY=你的天翼云AppKey
DEEPSEEK_API_BASE=https://wishub-x6.ctyun.cn/v1
DEEPSEEK_MODEL=24625803b01f4f90b72abbe9d9cdf5cc
ADMIN_PASSWORD=你的管理员密码
```

5. 部署完成后访问分配的域名即可

### 方式二：Docker 部署

```bash
# 构建镜像
docker build -t shuprophet .

# 运行（连接外部 PostgreSQL）
docker run -p 8080:8080 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e OPENAI_API_KEY=你的API密钥 \
  -e OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4/ \
  -e ZHIPU_MODEL=glm-4-flash-250414 \
  -e DEEPSEEK_API_KEY=你的天翼云AppKey \
  -e DEEPSEEK_API_BASE=https://wishub-x6.ctyun.cn/v1 \
  -e DEEPSEEK_MODEL=24625803b01f4f90b72abbe9d9cdf5cc \
  -e ADMIN_PASSWORD=你的管理员密码 \
  shuprophet
```

> 不设置 `DATABASE_URL` 时自动回退到 SQLite（仅适合本地开发）。

### 方式三：本地开发

```bash
git clone https://github.com/William-Liwei/shuprophet.git
cd shuprophet
```

**后端：**

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows CMD: .\.venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

在项目根目录创建 `.env` 文件：

```
OPENAI_API_KEY=你的API密钥
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4/
ZHIPU_MODEL=glm-4-flash-250414
DEEPSEEK_API_KEY=你的天翼云AppKey
DEEPSEEK_API_BASE=https://wishub-x6.ctyun.cn/v1
DEEPSEEK_MODEL=24625803b01f4f90b72abbe9d9cdf5cc
ADMIN_PASSWORD=你的管理员密码
```

**前端构建（通过 Flask 访问页面时需要先执行）：**

```bash
cd ../frontend
npm install
npm run build
```

**后端启动：**

```bash
cd ../backend
python app.py
# 后端运行在 http://127.0.0.1:5000
```

如果不想激活虚拟环境，也可以直接使用解释器启动：

```bash
.\backend\.venv\Scripts\python.exe .\backend\app.py
```

**前端独立开发（新终端，可选）：**

```bash
cd frontend
npm run dev
# 前端运行在 http://localhost:5173
```

### 环境变量说明

| 变量                | 必填 | 说明                                     |
| ------------------- | ---- | ---------------------------------------- |
| `OPENAI_API_KEY`  | 是   | LLM API 密钥；也兼容 `ZHIPU_API_KEY` / `ZAI_API_KEY` |
| `OPENAI_API_BASE` | 否   | API 地址；默认使用智谱 `https://open.bigmodel.cn/api/paas/v4/` |
| `ZHIPU_MODEL`     | 否   | 智谱模型名；默认 `glm-4-flash-250414` |
| `DEEPSEEK_API_KEY` | 否  | DeepSeek 模式的天翼云 AppKey；也兼容 `CTYUN_APP_KEY` |
| `DEEPSEEK_API_BASE` | 否 | DeepSeek 模式接口基址；默认 `https://wishub-x6.ctyun.cn/v1` |
| `DEEPSEEK_MODEL` | 否 | DeepSeek 模式模型 ID；默认 `24625803b01f4f90b72abbe9d9cdf5cc` |
| `DATABASE_URL`    | 否   | PostgreSQL 连接串，不填则使用 SQLite     |
| `ADMIN_PASSWORD`  | 否   | 管理后台密码，不设则管理功能禁用         |
| `JWT_SECRET_KEY`  | 否   | JWT 签名密钥，不填使用默认值             |

## 🛠️ 技术架构

| 层级   | 技术                                              |
| ------ | ------------------------------------------------- |
| 前端   | Vue 3 + Vite, Element Plus, ECharts, Pinia, Axios |
| 后端   | Flask, SQLAlchemy, Gunicorn (gthread)             |
| AI     | LangChain, 智谱 GLM, DeepSeek-V3.2-Pro（天翼云 OpenAI 兼容接口） |
| 数据库 | PostgreSQL（生产） / SQLite（开发）               |
| 部署   | Docker 多阶段构建, Zeabur                         |

## 📁 项目结构

```
shuprophet/
├── backend/
│   ├── models/
│   │   ├── agent_chain.py          # AI 助理对话 & 智能预测引擎
│   │   ├── prediction_tool.py      # 数据分析工具
│   │   └── arima_predictor.py      # ARIMA 基线模型
│   ├── agent/
│   │   └── reasoner.py             # 思考模式推理器
│   ├── blueprints/
│   │   ├── auth.py                 # 注册 / 登录 / JWT
│   │   ├── user.py                 # 个人资料 / 头像
│   │   ├── community.py            # 社区广场
│   │   ├── credits.py              # 积分 / 兑换码 / 用量控制
│   │   └── admin.py                # 管理后台
│   ├── extensions.py               # DB / 配置
│   ├── auto_migrate.py             # 数据库自动迁移
│   ├── app.py                      # Flask 主应用
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Vue 组件
│   │   ├── views/                  # 页面视图
│   │   ├── stores/                 # Pinia 状态管理
│   │   ├── utils/                  # 工具函数
│   │   ├── router/                 # 路由配置
│   │   └── assets/                 # 静态资源
│   └── package.json
│
├── Dockerfile                      # 多阶段构建
├── entrypoint.sh                   # 容器启动脚本
└── README.md
```

## 📄 许可证

Apache License 2.0 — 详见 [LICENSE](LICENSE)。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

## 📮 联系

- **项目负责人**: 黎玮 (Wei Li)
- **邮箱**: liwei008009@163.com
- **上海大学** 计算机工程与科学学院

---

<div align="center">
  <p>
    <strong>如果这个项目对你有帮助，请给我们一个 ⭐ Star</strong>
  </p>
  <p>
    <em>Academic-Driven Time Series Intelligence Platform by SHU Undergraduates</em>
  </p>
</div>
