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

## 服务器一键启动

需要 Docker Engine 与 Compose v2。将私有交付包传到服务器并解压，在解压目录执行：

```bash
docker compose up --build -d
```

访问 `http://127.0.0.1:8080`。Web 与计算服务分开运行，任务与数据保存在命名卷 `shuprophet-data`；重启服务不会清空实验记录。只运行一个 worker，避免中断恢复相互影响。

如需远程演示，复制 `.env.example` 为 `.env`，配置随机的 `STUDIO_ACCESS_TOKEN`，再选择通过 HTTPS 反向代理转发本地 8080 端口。若直接绑定网卡，显式设置 `BIND_HOST=0.0.0.0`。浏览器左下角“连接设置”可输入工作区令牌。当前是单一工作区模型，不提供多租户数据隔离。

```bash
docker compose logs -f
curl http://127.0.0.1:8080/api/health
docker compose down
```

`down` 保留数据卷。不要使用 `down -v`，除非确实需要删除工作区数据。升级前备份数据卷；中断的运行任务会标记失败，等待中的任务继续执行，可用原配置重新运行。

## 验证范围

本地验收覆盖前端生产构建、API 闭环、导出、数据隔离协议和浏览器交互。Docker 启动需要在装有 Docker 的目标机器进一步验证；私有引擎的检查和测试不在公开 CI 中运行。
