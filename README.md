# Agent Object Web Console

## 功能

- 数据库记忆用户切换与自定义用户 ID
- 记忆归档、恢复、删除
- 开启新对话
- 高德地图展示与地点搜索 API 预留
- 动态 MCP 工具发现与通用参数调用
- Agent 对话 API

## 配置

复制 `.env.example` 为 `.env`，填写模型、PostgreSQL 和高德密钥：

- `AMAP_JS_KEY`：前端高德 JS API Key
- `AMAP_SECURITY_JS_CODE`：可选安全密钥
- `AMAP_REST_API_KEY`：服务端地点搜索 Key

### 多环境配置

- 默认读取 `.env`。
- `APP_ENV=dev/test/prod` 时，会用 `.env.{APP_ENV}` 覆盖 `.env`。
- 不要提交 `.env`、`.env.*` 和 `logs/`；仓库保留 `.env.example` 作为模板。

### 工程化配置

- `CORS_ORIGINS`：跨域白名单，逗号分隔。
- `API_AUTH_TOKEN`：为空时匿名访问；配置后除健康检查与基础配置外的 `/api/*` 需要 `X-API-Token`。
- `RATE_LIMIT_ENABLED` / `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS`：固定窗口限流。
- `AMAP_TIMEOUT_SECONDS` / `AMAP_MAX_RETRIES`：高德接口超时与指数退避重试。
- `CHAT_TIMEOUT_SECONDS` / `TOOL_TIMEOUT_SECONDS`：对话与工具调用超时。
- `LOG_LEVEL` / `LOG_DIR`：结构化 JSON 日志级别与目录。
- `METRICS_ENABLED`：是否开放 `/metrics`。

## 启动

```powershell
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m utils.init_memory_db
.\.venv\Scripts\python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

打开 <http://127.0.0.1:8000>。

生产环境建议：

```powershell
$env:APP_ENV="prod"
.\.venv\Scripts\python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

## 工程化架构

- `api.py`：Controller，只负责路由、参数校验和响应。
- `services/`：业务服务层，包含对话、地图、记忆与工具服务。
- `repositories/`：数据访问层，当前包含 PostgreSQL 记忆 DAO。
- `schemas/`：Pydantic 入参 / 出参模型。
- `middleware/`：认证、审计、限流、安全响应头与可观测性。
- `core/`：多环境配置、结构化日志、指标和请求上下文。

可观测能力：

- `logs/app.log`：JSON 结构化应用日志，带 `requestId` 和耗时。
- `logs/audit.log`：POST / PUT / PATCH / DELETE 审计日志。
- `/metrics`：Prometheus 文本格式指标。
- 响应头返回 `X-Request-ID`，也支持请求传入 `X-Request-ID` 做链路追踪。

安全能力：

- Pydantic 输入校验。
- SQL 全部使用参数化查询。
- 前端使用 `textContent` / `replaceChildren` 降低 XSS 风险。
- 可选 `X-API-Token` API 认证，使用恒定时间比较。
- 请求日志中的 token、password、secret、apikey 等字段自动脱敏。

## API

- `GET /api/health`
- `GET /api/config`
- `GET /api/users`
- `GET /api/memories`
- `POST /api/memories`
- `PATCH /api/memories/{id}/archive`
- `DELETE /api/memories/{id}`
- `POST /api/conversations`
- `POST /api/chat`
- `GET /api/tools`
- `POST /api/tools/{name}/invoke`
- `GET /api/map/config`
- `GET /api/map/places`
- `GET /metrics`

## 测试

```powershell
.\.venv\Scripts\python -m pytest tests -q
```

如果旧脚本式测试在收集阶段失败，可先排除：

```powershell
.\.venv\Scripts\python -m pytest tests -q --ignore=tests\test_mcp_langchain_tool.py --ignore=tests\test_memory_writer.py --ignore=tests\test_research_mcp.py
```
