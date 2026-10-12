# BriefPilot｜企业产品情报研判 Agent

当前完成第 01 天服务骨架与研究范围。已具备环境配置、FastAPI 工厂、生命周期、健康接口、基础错误格式及固定演示资料。研究 Agent、Fake 模型与数据库尚未实现。

## 启动

需要 Python 3.12 与 uv。在本项目目录执行：

```powershell
uv sync --locked
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

若已经有 `.env`，保留原配置。当前不需要模型密钥、搜索密钥或数据库。

- 健康接口：`http://127.0.0.1:8001/health/live`
- OpenAPI 文档：`http://127.0.0.1:8001/docs`
- `BP_AGENT_MODE=fake` 是第 02 天模型适配器的配置入口，此版本不会执行研究任务。

## 检查

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## 结构与配置

`app/api` 汇总 HTTP 路由；`core` 管理配置与错误；`modules` 管理文档、研究任务与报告；`agents` 放图/状态/节点/提示词；`llm`、`tools`、`retrieval`、`evidence`、`runtime` 是后续实现入口。

`migrations`、`scripts`、`deploy`、`evals` 暂存目录占位，没有数据库迁移、部署配置或评测执行器。三个虚构产品说明在 `tests/fixtures/corpus/`，用于后续固定资料研究。

环境变量使用 `BP_` 前缀；模型与搜索适配器后续通过配置切换。密钥采用 SecretStr，`.env` 和 `storage/` 不进入 Git。数据库和 LangGraph 等依赖在对应步骤加入，不预先把尚未使用的组件装进首版骨架。

后续依据 [开发计划](docs/plan.md) 推进；唯一进度记录为 [progress.md](progress.md)。


## GitHub 同步

本文件所在目录是独立仓库根目录，Git 命令在这里执行。仓库包含自己的计划和 progress.md，无需下载另一个项目。

远端：[BriefPilot](https://github.com/zmq2783764729-crypto/BriefPilot)。本机工作分支 codex/initial 跟踪远端同名分支。换电脑时 clone 本仓库，按当前分支执行 `git pull --ff-only`；开发结束时更新 progress.md，并提交、推送。
