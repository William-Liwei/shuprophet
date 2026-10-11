# 鼠先知引擎 · Data Studio API

前缀：`/api/studio`。响应为 JSON。受保护的工作区使用 `X-Studio-Token` 请求头；令牌不放在 URL 中。

| 方法与路径 | 用途 |
| --- | --- |
| `GET /capabilities` | 引擎版本、可用任务、数据限制 |
| `GET /datasets` | 数据资产与内置示例目录 |
| `POST /datasets/demo` | `{ "demo": "energy" }` 或 `equipment`，载入示例 |
| `POST /datasets/upload` | multipart 表单 `file`，上传 UTF-8 CSV |
| `POST /discover` | 提交结构发现任务，返回 HTTP 202 与实验记录 |
| `POST /generate` | 提交生成和评估任务，返回 HTTP 202 |
| `GET /jobs` | 最近实验记录 |
| `GET /jobs/{id}` | 任务状态与结果 |
| `GET /jobs/{id}/export` | 下载已完成生成实验的 ZIP 数据包 |
| `POST /assistant` | `{ "message": "问题", "dataset_id": "<id>", "discovery_id": "<id>", "generation_id": "<id>" }`，后三项可省略，返回基于工作区的解释与导航建议 |

结构发现请求：

```json
{ "dataset_id": "<id>", "window": 48, "stride": 48, "seed": 42, "columns": ["load_kw", "temperature_c"] }
```

生成请求：

```json
{ "discovery_id": "<id>", "count": 96, "seed": 42, "target": null, "strength": 0.08 }
```

`target` 为 `null` 时探索整体分布；指定已发现的模式 ID 时执行定向扩充。窗口长度 8–256，生成数量 8–512。每个合成窗口独立，CSV 导出中的 `sample_id` 与 `step` 明确标识边界。

任务状态：`queued` → `running` → `completed` / `failed`。完成后 `result` 包含鼠先知引擎的结构或生成/评估结果。错误响应使用 `{ "error": "可显示的信息" }`，常见 HTTP 状态为 400、401、404、413。

ZIP 包含 `synthetic.csv`、`report.html`、`report.json` 与 `manifest.json`。清单记录来源指纹、实验配置、引擎版本和各交付文件 SHA-256。HTML 可直接用浏览器阅读或打印为 PDF。

服务内部实现与模型适配接口属于私有引擎，不通过公开 API 暴露。APCL / SDFlow 的产品化接入使用同一产品接口，前端无需依赖具体模型实现。

## LLM 对话

`POST /assistant` 额外接受 `history`：最多 12 条 `{ "role": "user" | "assistant", "content": "文本" }`。每条最多 6000 字符，服务端会收紧上下文预算；不接受客户端传入 `system` 角色。前端仅携带当前数据集的近期对话。当前问题 `message` 为 1–2000 字符。

成功响应包含 `message`、`answer_source: "llm"`、`evidence`（实验来源）、`actions`（页面导航）及 `truncated`（回复是否触及长度限制）。助手不会直接创建实验任务。工作区证据由后端读取并校验归属；不接受客户端伪造指标。

`GET /capabilities` 的 `assistant` 字段为 `{ "mode": "llm", "configured": true | false }`；`configured` 只代表已配置，不保证网络、额度或上游可用性。接口不会返回密钥、服务地址或内部模型名称。

未配置返回 HTTP 503 / `llm_not_configured`；模型认证或限流返回 503；连接失败返回 502；超时返回 504 / `llm_timeout`。这些响应包含 `error` 与 `code`，没有伪造的模型 `message`。客户端建议设置至少 60 秒请求超时。密钥仅在服务端管理，见[部署文档](DEPLOYMENT.md)。
