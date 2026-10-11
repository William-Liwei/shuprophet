# Data Studio 部署

公开仓库提供前端、公开 API 契约和部署工具。鼠先知引擎通过私有交付包提供，公开克隆不包含后端源码。

## 本地运行（完整交付）

需要 Python 3.11 和 Node.js 22。将私有 `backend/` 放入项目根目录：

```bash
python scripts/start_local.py
```

脚本创建隔离的 Python 环境、安装依赖、构建前端并启动本地服务与任务处理器。浏览器访问 `http://127.0.0.1:8080`。首次安装后，可使用对应虚拟环境的 Python 执行 `scripts/start_local.py --skip-setup`，避免重复安装。

只开发公开前端：

```bash
cd frontend
npm ci
npm run dev
```

Vite 将 `/api` 代理到 `127.0.0.1:5000`。前端只读展示无需后端，交互实验需要鼠先知引擎。

## 制作私有服务器交付包（项目所有者）

先构建前端，再打包：

```bash
cd frontend
npm ci
npm run build
cd ..
python scripts/package_private.py
```

得到 `.private-release/shuprophet-private-mvp.tar.gz`。包内含构建后的前端、私有引擎和 Docker 配置，不包含 `.env`、上传数据、工作区数据库或模型凭据。该目录已被 Git 忽略，不要发布到公开 Release。

## 服务器配置一次，后续一键更新

需要 Linux、Python 3.9+、Docker Engine 与支持 `up --wait` 的 Compose v2。将私有交付包传到服务器并解压，在解压目录执行：

```bash
python3 scripts/deploy.py
```

首次运行会在终端询问模型 API Key（隐藏输入）、服务地址和模型名称。随后自动构建、启动并等待健康检查。后续在新版交付包目录执行同一条命令，直接复用配置；没有交互终端时，脚本要求先初始化，不会使用空配置悄悄上线。

配置默认保存在部署用户的 `~/.config/shuprophet/`，独立于代码和镜像。`server.env` 保存模型地址、型号和随机生成的工作区访问令牌，权限为 `0600`；`llm_api_key` 通过 Compose secret 只读挂载到 Web 容器，不传给计算 worker，不作为密钥环境变量注入。父目录权限 `0700` 阻止其他普通系统用户访问；密钥文件为 `0444`，以兼容容器内非 root 用户读取文件型 secret。不要把该文件复制到公开可读目录。服务器管理员及具有 Docker 管理权限的人仍可读取，Compose secret 本身不提供静态加密。[Docker secrets 文档](https://docs.docker.com/compose/how-tos/use-secrets/)

首次初始化后，在服务器上私下读取 `server.env` 的 `STUDIO_ACCESS_TOKEN`，填入网页左下角“连接设置”。它是工作区门禁，与模型 API Key 分开；不要把模型密钥填到网页。默认仅监听 `127.0.0.1:8080`，远程演示可使用 HTTPS 反向代理。当前是单一工作区模型，不提供多租户数据隔离。

```bash
# 查看运行状态
python3 scripts/deploy.py --status
# 修改模型连接或轮换密钥；留空保留已有值
python3 scripts/deploy.py --configure
# 需要自定义目录时，每次使用同一路径
python3 scripts/deploy.py --config-dir /secure/path/shuprophet
```

升级始终使用同一系统用户和配置目录；不需要重新输入密钥。部署使用固定 Compose 项目名 `shuprophet-studio`，即使新版解压目录不同，也复用命名数据卷。只运行一个 worker。直接执行普通 `docker compose` 不会自动使用这份外部配置，运维时请使用上述脚本，或显式传入相同项目名、配置文件和两个 Compose 文件。

升级前备份数据卷与服务器配置；中断的运行任务会标记失败，等待中的任务继续执行。不要删除数据卷。迁移到另一台服务器仍需通过可信通道迁移配置和数据；以后可接入云厂商密钥管理服务，通过服务器身份自动读取，减少逐台配置。

## 本地 LLM 对话配置

本地 `scripts/start_local.py` 读取被 Git 忽略的 `.env`。可配置 `OPENAI_API_KEY`、`OPENAI_API_BASE`、`OPENAI_MODEL`；也支持通过 `OPENAI_API_KEY_FILE` 读取密钥文件，文件设置优先于密钥环境变量。浏览器只调用 `/api/studio/assistant`，不接收模型凭据。

助手调用真实 LLM 并携带近期多轮对话及当前实验摘要，不发送原始上传窗口。没有配置或上游调用失败时返回明确错误，不使用预设答案替代模型回复。数据实验模块可以独立运行。模型地址应使用可信服务；当前 Moonshot 默认对话型号为 `kimi-k2.6`，可通过服务器配置替换。旧的 `moonshot-v1` 系列已下线。[模型列表](https://platform.kimi.com/docs/models)

## 验证范围

本地验收覆盖前端生产构建、API 闭环、导出、数据隔离协议和浏览器交互。Docker 启动需要在装有 Docker 的目标机器进一步验证；私有引擎的检查和测试不在公开 CI 中运行。
