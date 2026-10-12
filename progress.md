# BriefPilot｜进度与交接

> 最后更新：2026-10-12（Asia/Shanghai）。开发完成 1 / 30。
> 本文件是本仓库唯一的进度记录；计划见 [docs/plan.md](docs/plan.md)。

## 接续规则

1. 开发前读取本文件、对应日计划和实际代码，从下一步继续，不重新初始化已有实现。
2. 部分完成时写清剩余子任务；通过验收后才推进任务编号。
3. 开发结束后更新当前状态、修改文件、验证结果、问题和下一步；未执行的检查写未执行。
4. 路径相对于本仓库；密钥、.env、.venv、运行数据不进 Git。
5. 本项目已有独立 .git、.gitignore、.gitattributes、依赖锁文件和计划，可以单独 clone 和运行。

## 仓库状态

- 本地根目录：当前 briefpilot 文件夹。初始化分支为 codex/initial。
- 2026-10-12 从原共享工作目录拆分；原父仓库的暂存区与配置备份在父目录 .local/repository-backups，不是本项目依赖。
- origin：https://github.com/zmq2783764729-crypto/BriefPilot.git。提交身份使用用户选择的 GitHub 用户名与隐私邮箱；同步状态按 git status 与远端检查核实。
- Python 3.12；按 README 用 uv sync --locked 重建环境。本机辅助 uv 在父目录 .local/bootstrap/bin，不随仓库同步。
- Docker 的 Virtual Machine Platform/WSL 环境仍待安装后验证；这不影响此前骨架验收。

## BriefPilot｜企业产品情报研判 Agent

### 项目约定

- 计划：[BriefPilot 30 天计划](docs/plan.md)。
- 代码目录：本仓库根目录；可独立开发，不依赖 MeterGate。启动说明见 [README](README.md)。
- 核心业务：上传内部资料、规划研究、人工确认、受控检索、证据核验和报告生成。
- 技术路线：LangGraph、LangChain、FastAPI、PostgreSQL、独立 Worker；模型提供方由适配器封装。
- 首版限制：只读研究、txt/md 上传、关键词检索、Markdown/安全 HTML 输出；不执行任意 Shell，不自动发送报告。
- 关键设计：来源快照与引用、检查点恢复、工具结果记录、任务执行锁、预算限制；细节按原计划。
- 验证约定：Fake 证明流程可复现，真实模型另做效果评测；切换提供方后记录模型与评测结果。

### 当前进度

- 已完成：第 01 天；配置、服务入口、健康检查、领域/HTTP/验证错误格式、独立依赖锁文件、范围文档、3 份虚构产品资料和目录骨架。
- 当前任务：第 01 天验收已通过，等待开始第 02 天。
- 关键文件：`pyproject.toml`、`uv.lock`、`.python-version`、`.env.example`、`app/main.py`、`app/core/{config,errors}.py`、`app/api/{router,health}.py`、`tests/test_app.py`、`tests/fixtures/corpus/*.md`、`docs/scope.md`、`README.md`。
- 已实现：`Settings`、`create_app()`、`lifespan()`、`register_error_handlers()`、`DomainError`、`GET /health/live`。配置用 `BP_` 前缀，默认 agent_mode=fake；当前只有模式配置，**尚未实现 Fake 模型或研究 Agent**。
- 验证（工作目录为本仓库根目录）：`uv run --locked --offline ruff check .`、`uv run --locked --offline ruff format --check .` 均通过；`uv run --locked --offline pytest -p no:cacheprovider` 为 **2 passed**，覆盖生命周期、离线启动和错误响应不回显无效输入。本机用本地 uv 的完整路径执行这些命令。
- 启动验证：实际启动 Uvicorn，在 8001 端口请求 `/health/live` 返回 200，`/openapi.json` 标题与健康路径正确；验证后已停止进程。
- 问题/待定项：模型/搜索提供方尚未选定；数据库、LangGraph、模型适配器和评测执行器尚未实现。真实模型未调用，质量与费用未验证。

### 下一步：第 02 天

1. 读取计划第 02 天；在已有配置与错误结构上增加模型网关，不重建应用。
2. 实现 `app/llm/base.py` 的 `LLMGateway.generate_structured()`、`generate_with_tools()` 及响应/usage 类型。
3. 实现 `app/llm/fake.py` 的确定性场景响应，覆盖有效计划、工具调用、非法结构、超时和失败。
4. 根据用户选定提供方实现 `app/llm/provider.py`，配置 timeout、有限重试和密钥读取；外部认证失败不无限重试。
5. 新增 `tests/unit/test_llm_gateway.py`；离线检查必须可运行。若没有在线配置，真实 smoke test 明确跳过，不能填写效果或费用实测结果。

## 最近记录

### 2026-10-12｜拆为独立仓库

- 完成：本项目单独的计划、进度、Git 忽略/换行规则；README 和范围文档链接改为仓库内路径。
- 代码：保留第 01 天全部实现与依赖锁文件，未改动业务代码。
- 验证：第 01 天测试结果沿用上文已有记录；此次仅检查拆分后的 Git 边界、文件链接和排除规则，不声称重新执行应用测试。
- 下一步：完成首次提交与 GitHub 推送；应用开发继续第 02 天。

## 开工提示词

```text
请读取本仓库 progress.md 与 docs/plan.md，核对现有代码，从下一步继续；结束后更新同一个 progress.md，记录完成项、实际验证结果、问题和下一步。
```
