# 鼠先知 (SHU Prophet)

<div align="center">
  <img src="./frontend/src/assets/logo.png" alt="SHU Prophet Logo" width="600"/>
</div>

---

## 📖 项目简介

**鼠先知 (SHU Prophet)** 是一个将学术研究成果转化为可验证分析能力的时间序列智能决策平台。当前研究组合包含 9 项论文成果：1 篇 CCF-A、3 篇 CCF-B、4 篇 CCF-C 和 1 篇审稿中的 arXiv 预印本，覆盖时间序列聚类、生成、预测、不确定性估计与多尺度建模。

平台当前提供 6 个论文预测模型的统一可视化对比；面向用户上传数据，则由轻量工具 Agent 完成数据画像、自适应工具选择、多预测器回测、结果校验和报告生成。研究成果、展示模型和实际执行引擎在系统中分别标注，避免把论文名称等同于已经部署的推理能力。

与传统的"跑脚本看结果"不同，鼠先知提供了完整的 Web 交互体验：AI 智能助理对话式分析、多模型可视化对比、社区广场知识共享、用户积分与等级体系 — 让时序预测不再只是研究者的专属工具，更是企业决策者和数据分析师的得力助手。

### 🎓 学术背景

| 类型  | 会议 / 状态               | 成果数 |
| ----- | ------------------------- | ------ |
| CCF-A | KDD 2026                  | 1 篇   |
| CCF-B | DASFAA 2026 / ICASSP 2026 | 3 篇   |
| CCF-C | ICANN 2025 / ICIC 2025    | 4 篇   |
| arXiv | Under Reviewing           | 1 篇   |

全部成果均由 **黎玮 (Wei Li)** 作为第一作者或共同第一作者完成。

### 最新论文成果

| # | 成果                       | 方向                         | 发表信息                            | 链接                                                                                                     |
| - | -------------------------- | ---------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 1 | **APCL**             | 未知簇数下的时间序列聚类     | KDD 2026，CCF-A，Full Paper，Poster | [ACM DL](https://dl.acm.org/doi/10.1145/3770855.3817773) / [GitHub](https://github.com/William-Liwei/apcl) |
| 2 | **SDFlow**           | 相似性驱动的时间序列生成     | arXiv 2026，Under Reviewing         | [arXiv](https://arxiv.org/abs/2605.05736)                                                                 |
| 3 | **ClusterPatchTST**  | 不确定性感知的异构时序预测   | DASFAA 2026，CCF-B，Full Paper      | -                                                                                                        |
| 4 | **EnergyPatchTST**   | 多尺度能源预测与不确定性估计 | ICIC 2025，CCF-C，Oral              | [GitHub](https://github.com/William-Liwei/EnergyPatchTST)                                                 |
| 5 | **ScatterFusion**    | 层级散射变换时序预测         | ICASSP 2026，CCF-B                  | -                                                                                                        |
| 6 | **AWGFormer**        | 小波引导的多分辨率时序预测   | ICASSP 2026，CCF-B                  | -                                                                                                        |
| 7 | **SWIFT**            | 状态空间与小波融合预测       | ICANN 2025，CCF-C，Oral             | [GitHub](https://github.com/William-Liwei/SWIFT)                                                          |
| 8 | **TimeFlowDiffuser** | 层级扩散多视野时序预测       | ICANN 2025，CCF-C，Oral             | -                                                                                                        |
| 9 | **LWSpace**          | 多尺度状态空间时序预测       | ICIC 2025，CCF-C，Oral              | -                                                                                                        |

## 💡 为什么选择鼠先知？

### 🤖 工具 Agent 驱动的分析体验

- **目标驱动执行**：上传 CSV 并指定预测步数，Agent 自动完成分析与预测任务
- **自适应工具选择**：依据趋势、平稳性、波动性和周期性选择统计、频谱与分解工具
- **回测选择与校验**：在内部比较多条候选预测路径，以验证误差选择执行路径并完成范围、趋势与置信度检查；对外统一显示为“鼠先知引擎”
- **可追溯报告**：展示实际调用的工具、模型选择依据和校验结果；LLM 只组织已计算事实，不生成预测数值

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

### 📦 标准化交付

- **统一入口**：浏览器即可完成数据分析、预测与报告导出
- **跨平台界面**：兼容 PC、平板与手机视口
- **一键部署**：Docker Compose 统一构建前端、后端与持久化目录

## 🔬 集成模型

平台集成了 6 个自研时间序列预测模型，覆盖从经典信号处理到前沿生成式建模的多种技术路线：

| 模型                       | 会议        | 级别  | 核心技术                   | 适用场景                 |
| -------------------------- | ----------- | ----- | -------------------------- | ------------------------ |
| **ScatterFusion**    | ICASSP 2026 | CCF-B | 层级散射变换，宏微观融合   | 非平稳序列、噪声鲁棒预测 |
| **AWGFormer**        | ICASSP 2026 | CCF-B | 自适应小波引导 Transformer | 长期依赖、多分辨率分析   |
| **EnergyPatchTST**   | ICIC 2025   | CCF-C | 序列分块与不确定性量化     | 能源预测、置信区间估计   |
| **SWIFT**            | ICANN 2025  | CCF-C | 状态空间与小波多尺度融合   | 多尺度模式与长程依赖     |
| **LWSpace**          | ICIC 2025   | CCF-C | 小波分解与选择性状态空间   | 精度与效率平衡           |
| **TimeFlowDiffuser** | ICANN 2025  | CCF-C | 层级式扩散框架             | 长周期预测、数据生成     |

## 👥 团队

**鼠先知**由上海大学计算机工程与科学学院本科生团队开发：

**联系方式**: liwei008009@163.com

## 🚀 一键部署

仓库提供单体镜像和标准 Compose 入口，数据库目录会自动持久化。LLM 凭据是可选项：未配置时，数据画像、预测、验证和结构化报告仍可运行；论文问答与自然语言润色需要兼容的模型接口。

```bash
# 可选：配置模型、管理员和数据库参数
cp .env.example .env

# 构建并启动
docker compose up --build -d

# 验证服务状态
curl http://127.0.0.1:8080/api/health
```

停止服务：

```bash
docker compose down
```

### 环境变量说明

| 变量                | 必填 | 说明                                             |
| ------------------- | ---- | ------------------------------------------------ |
| `OPENAI_API_KEY`  | 否   | OpenAI 兼容模型的 API 密钥；仅影响对话与报告润色 |
| `OPENAI_API_BASE` | 否   | OpenAI 兼容接口地址                              |
| `OPENAI_MODEL`    | 否   | 模型名称                                         |
| `DATABASE_URL`    | 否   | SQLAlchemy 数据库连接串                          |
| `DATA_DIR`        | 否   | 默认数据库持久化目录                             |
| `ADMIN_PASSWORD`  | 否   | 管理后台密码；不设则禁用管理员入口               |
| `JWT_SECRET_KEY`  | 否   | JWT 签名密钥；建议显式设置                       |
| `APP_PORT`        | 否   | Compose 对外端口，默认`8080`                   |

## 🛠️ 技术架构

| 层级   | 技术                                                     |
| ------ | -------------------------------------------------------- |
| 前端   | Vue 3 + Vite, Element Plus, ECharts, Pinia, Axios        |
| 后端   | Flask, SQLAlchemy, Gunicorn (gthread)                    |
| Agent  | 自适应统计工具链、时间留出验证、预测校验、可追溯执行记录 |
| LLM    | 可选的 OpenAI 兼容接口，仅用于对话与证据转述             |
| 数据库 | SQLAlchemy，默认 SQLite，兼容 PostgreSQL                 |
| 部署   | Docker 多阶段构建 + Docker Compose                       |

## 📁 项目结构

```
shuprophet/
├── backend/
│   ├── models/
│   │   ├── agent_chain.py          # AI 助理对话 & 智能预测引擎
│   │   ├── prediction_tool.py      # 数据分析工具
│   │   └── arima_predictor.py      # 统计基线预测器
│   ├── agent/
│   │   └── reasoner.py             # 轻量工具 Agent 编排器
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

---

<div align="center">
  <p>
    <strong>如果这个项目对你有帮助，请给我们一个 ⭐ Star</strong>
  </p>
  <p>
    <em>Academic-Driven Time Series Intelligence Platform by SHU Undergraduates</em>
  </p>
</div>
