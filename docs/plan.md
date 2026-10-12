# BriefPilot｜企业产品情报研判 Agent：30 天开发计划

> 方向：Agent 应用工程。版本：v1.0。编制日期：2026-10-09。
> 本文是实施计划，任务尚未执行；验收指标是目标，不是现有能力或已经测得的成绩。

## 1. 项目定位与完成目标

**项目名称：BriefPilot（企业产品情报研判 Agent）。**

业务场景：企业产品经理提交“对比本公司产品与两个竞品在功能、部署方式、定价上的差异”。系统先澄清范围，再制定计划、查询内部产品文档、搜索公开产品资料、核对证据，最后产出可追溯的研究报告。用户可以确认计划、修改范围、暂停并继续执行。

参考 [DeerFlow](https://github.com/bytedance/deer-flow) 的任务执行、工具、子 Agent 和上下文管理思路，用 LangGraph 独立实现一个垂直业务应用。BriefPilot 的目录、数据结构、接口和功能均为本计划设计，不代表 DeerFlow 原仓库对应实现。当前 DeerFlow 主线为 2.0，与 `1.x` 早期研究框架不同；阅读时记录具体分支和提交。

**最终演示闭环：**上传本公司产品说明 → 提交研究请求 → Agent 生成计划 → 人工确认 → 检索内部与外部资料 → 形成结构化结论 → 检查来源和冲突 → 生成报告 → 修改研究范围并创建新版本。

重点展示：模型选择工具与调整计划、图状态设计、来源溯源、执行持久化、工具故障恢复、人工介入、成本约束及可重复评测。FastAPI 在此项目主要承载任务接口，核心精力放在 Agent 执行与结果质量。

## 2. 时间、前置条件和范围

- 30 个工作日，每天约 6–8 小时；以掌握 Python、基础 FastAPI、SQL 和模型 API 调用为前提。
- 每天建议：30–45 分钟读文档与设计、4–5 小时编码、1–1.5 小时验证、30 分钟记录结果。
- 主线研究一个产品主题，最多比较 3 个产品、5 个维度。支持中英文资料，首版输出中文 Markdown 与静态 HTML。
- 上传只支持 UTF-8 `.txt` / `.md`；先排除 PDF、Office、扫描件和图片 OCR 的解析复杂度。
- 内部检索先用 PostgreSQL 关键词检索；向量检索和 reranker 留作后续扩展，不把所有 RAG 技术堆进主线。
- 外部资料优先产品官方站点、官方文档和定价页，搜索结果只能作线索，正文快照才是主要证据。运行时记录获取时间，不保证来源页面永远最新。
- 首版不允许 Agent 执行任意 Shell/Python、不自动发送报告、不自动更新企业系统；它调用受控检索工具并生成研究产物。
- 使用一个模型提供方和一个搜索提供方。核心测试使用 fake 模型和固定资料；真实调用单独运行，需要自行配置相应账号和 API Key，可能产生费用。
- 不依赖 MeterGate 项目已经完成；BriefPilot 独立部署。后续可把它作为 MeterGate 的一个计量客户，但不计入 30 天主线。

## 3. 固定技术路线

| 层次 | 选择 | 用途 |
|---|---|---|
| Agent 编排 | LangGraph、LangChain | 图状态、工具循环、条件跳转、子任务 |
| 模型接口 | 统一 LLMGateway + 一个提供方适配器 | 结构化输出、工具调用、用量记录 |
| API | FastAPI、Pydantic | 任务、审批、事件流、报告接口 |
| 持久化 | PostgreSQL、SQLAlchemy、LangGraph PostgreSQL checkpointer | 业务数据与执行进度 |
| Worker | PostgreSQL 任务表 + 独立 Worker | 首版调度、租约、恢复；不另外引入消息队列 |
| 检索 | PostgreSQL FTS + pg_trgm | 英文词项及中文关键词/片段匹配 |
| 搜索与抓取 | 一个搜索 API、HTTPX、正文提取库 | 获取受控公开资料 |
| 验证 | pytest、HTTPX、固定 fixture、离线评测脚本 | 回归、故障、质量和成本验证 |
| 部署 | uv、Docker Compose、结构化日志、CI | 可复现开发与运行 |

第 1 天锁定可兼容依赖，提交锁文件。持久化按 [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) 设计；人工介入按 [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) 实现。检查点保存的是图进度，不自动保证外部工具副作用只发生一次，工具幂等要单独设计。

## 4. 代码目录约定

以下路径相对于本仓库根目录。实际实现进度以根目录 progress.md 为准。

```text
briefpilot/
  pyproject.toml
  uv.lock
  .env.example
  app/
    main.py
    core/{config,errors,logging}.py
    db/{base,session}.py
    auth/{models,dependencies}.py
    modules/
      documents/{models,schemas,service,router}.py
      research/{models,schemas,service,router}.py
      reports/{models,schemas,service,router}.py
    agents/
      state.py
      schemas.py
      graph.py
      nodes/{intake,planner,researcher,verifier,writer}.py
      subgraphs/topic_research.py
      prompts/
      policies/{budget,tool_access}.py
    llm/{base,provider,fake}.py
    tools/{base,registry,knowledge_search,web_search,web_fetch}.py
    retrieval/{parser,chunker,indexer,search}.py
    evidence/{models,schemas,repository,normalizer}.py
    runtime/{worker,runner,leases,events,tool_runs}.py
    templates/dashboard.html
  migrations/versions/
  tests/{unit,integration,fixtures}/
  evals/{datasets,runners,metrics}/
  scripts/
  storage/                 # 运行数据，gitignore 排除
  deploy/
  docs/
```

提示词进入文件，例如 `planner.md`、`researcher.md`、`verifier.md`、`writer.md`；记录提示词版本。业务授权、预算判断和状态转移写在程序里，不能只依赖提示词要求模型遵守。

## 5. 状态、数据与可信边界

### 5.1 核心数据表

| 表 | 关键字段及约束 |
|---|---|
| tenants / users / memberships | 租户、用户、researcher/admin 角色；由 bootstrap 脚本创建演示身份 |
| access_tokens | user_id、tenant_id、token_hash、expires_at、revoked_at；只保存 token 摘要 |
| documents / chunks | tenant_id、内容摘要、版本、解析状态；chunk 带 document_id 与 ordinal |
| research_tasks | tenant_id、owner_id、request、scope_version、status |
| research_runs | task_id、tenant_id、graph_thread_id、run_version、status、budget、lease_owner、lease_until、fencing_token |
| source_snapshots | tenant_id、run_id、URL/文档版本、标题、检索时间、正文摘要、内容位置 |
| evidence_items | source_snapshot_id、excerpt、location、产品、维度、evidence_id |
| tool_runs | tenant_id、run_id、scope_version、tool、args_hash、status、result_ref、provider_request_id |
| run_events | run_id、递增 sequence、event_type、sanitized_payload；run_id + sequence 唯一 |
| approvals | run_id、scope_version、interrupt_id、action、approved_by、created_at |
| reports / report_claims | run_id、version、Markdown/HTML 路径、内容摘要；结论与 evidence_id 关联 |
| usage_records | run_id、call_id、模型、输入/输出 token、估算费用、latency、status |

LangGraph 自己的 checkpoint 表由对应组件维护，与这些业务表分开。不要直接手写更新 checkpoint 表来“恢复任务”。

### 5.2 图状态草图

```python
class ResearchState(TypedDict):
    run_id: str
    scope_version: int
    request: str
    products: list[str]
    dimensions: list[str]
    plan: list[ResearchStep]
    current_step: int
    messages: list[BaseMessage]  # 实际实现使用框架的消息 reducer
    evidence_ids: list[str]     # 并发合并时去重，正文存在外部存储
    claims: list[Claim]
    unresolved_questions: list[str]
    tool_call_count: int
    revision_count: int
    report_id: str | None
```

鉴权、预算账本和工具能力白名单由服务端 ExecutionContext 提供；上面的 State 不包含 API Key、数据库凭据和可由模型自行改写的授权规则。即便 thread_id 是随机 UUID，每次访问仍要核验任务归属。

### 5.3 运行规则

1. 模型可以提出搜索词、选择允许的工具、指出证据缺口并修订研究计划；程序验证参数、scope、预算和次数，再执行工具。
2. `tenant_id/run_id` 由可信执行上下文注入工具，不能作为模型可任意指定的参数。
3. 报告每条关键事实引用 evidence_id；引用须属于当前租户、任务版本且可找到保存的快照。
4. 来源正文按不可信数据处理；正文中的“忽略指令”“调用内部工具”等文字不能提升为系统指令。
5. 主线工具均为只读检索；抓取只允许 HTTPS、配置允许的域名，逐跳校验重定向、限制时间和大小，并拒绝私网/本机地址。
6. 任务状态统一为 queued/running/waiting_approval/completed/failed/cancelled；通过 service 层检查合法转移。
7. 同一 run 同时只允许一个 Worker 持有有效执行权；丢失租约后禁止继续写工具结果、事件和报告。采用绑定独立数据库连接的 run 级 advisory lock 串行保护图/checkpoint 执行，租约和 fencing_token 再保护业务写入；不能只靠 lease_until 判断一个旧进程已经停止。
8. 恢复 interrupt 时前面的节点逻辑可能重跑；审批前的代码只做纯计算或幂等操作，不能直接重复扣费或落最终产物。
9. 首版预算限制研究维度、并行数、工具次数、token 和预估费用。实际额度账本与计数由服务端维护，State 中的计数仅用于展示和路由，不能让模型改写后绕过限制。外部调用断连时可能不知道实际消费，应记录 unknown 并按保守预算处理。
10. 修改已完成任务的研究范围会创建新 run/report 版本，不覆盖旧报告；批准前修改则废弃旧计划审批，生成新 scope_version。

## 6. 每日开发任务

### 第 01 天｜项目骨架与研究范围

**目标：**确定一个可以完成的 Agent 项目。

- 文件：`pyproject.toml`、`.env.example`、`app/main.py`、`app/core/config.py`、`docs/scope.md`。
- 编码：`create_app()`、lifespan、健康检查、统一错误处理；配置 uv、Ruff 和 pytest；预留数据库、模型、搜索配置，提交锁文件。
- 设计：准备一份本公司产品说明和两个虚构竞品资料作为固定演示数据，确定功能/部署/定价三个维度。
- 验收：服务启动、健康接口 200；项目目标、范围和 mock/真实模式切换写清楚；无真实密钥进入 Git。

### 第 02 天｜模型网关与确定性 Fake

**目标：**后续 Agent 能脱离真实模型 API 开发和验证。

- 文件：`app/llm/{base,provider,fake}.py`、`tests/unit/test_llm_gateway.py`。
- 编码：定义 `LLMGateway.generate_structured()`、`generate_with_tools()`；响应包含内容、usage、耗时、模型标识；实现一个真实提供方与按测试场景返回的 Fake。
- 编码：校验结构化响应；设置 timeout 与有限重试，认证错误不重试；不记录请求里的密钥。
- 验收：Fake 能稳定返回计划和工具调用；非法结构可识别；真实模式用一次小请求完成可选 smoke test，未配置账号时明确跳过。

### 第 03 天｜研究对象与图状态 Schema

**目标：**让模型输出和执行状态可验证。

- 文件：`app/agents/{state,schemas}.py`、`app/modules/research/schemas.py`。
- 编码：定义 `ResearchRequest`、`ResearchStep`、`Claim`、`ResearchPlan`、`BudgetConfig`；限制产品数和维度数；定义消息和证据列表的 reducer。
- 编码：Claim 必须有结论类型 factual/inference/unknown、对应产品维度和 evidence_ids；推断和缺失信息要显式标注。
- 验收：字段缺失、超出范围和不存在的工具名称被拦截；两个节点返回重复证据时能够去重合并。

### 第 04 天｜身份、任务持久化与归属

**目标：**创建的研究任务有明确的用户与租户边界。

- 文件：`app/db/{base,session}.py`、`app/auth/{models,dependencies}.py`、`app/modules/research/{models,service,router}.py`、首次迁移。
- 编码：`scripts/bootstrap_demo.py` 创建两个租户及研究者/admin、一次性显示的随机访问 token；`resolve_identity()` 校验摘要、过期与成员关系。
- 编码：`POST /v1/research/tasks`、`GET /v1/research/tasks/{id}`；首版登录界面和用户注册不在范围内，使用受控 token 认证。
- 验收：创建任务后重启仍存在；B 租户无法读取 A 任务；researcher 仅访问自己任务，admin 可管理本租户任务。

### 第 05 天｜内部文档上传与解析

**目标：**拥有可追溯的企业内部研究资料。

- 文件：`app/modules/documents/{models,schemas,service,router}.py`、`app/retrieval/parser.py`。
- 编码：`POST /v1/documents`、`parse_text_document()`；限制文件大小、UTF-8、扩展名与 MIME；文件名由服务端生成，不使用用户传入路径。
- 编码：保存 tenant_id、checksum、版本和标题；相同租户重复上传返回原版本或确定提示；增加文档列表与删除/停用接口。
- 验收：上传 txt/md 成功；路径穿越、非法编码和超大文件被拒绝；文档不跨租户可见。

### 第 06 天｜分块与关键词索引

**目标：**内部文档可被检索，检索片段可定位。

- 文件：`app/retrieval/{chunker,indexer,search}.py`、chunks 迁移、`scripts/index_documents.py`。
- 编码：`split_document()` 按段落/标题分块，设置长度上限及少量重叠；保存 ordinal、标题路径、字符偏移和版本；建立 FTS 与 pg_trgm 索引。
- 编码：英文采用 FTS，中文先用明确的关键词/片段匹配策略；不要假设 PostgreSQL 默认分词已经提供高质量中文语义检索。
- 验收：固定查询找到目标段落；返回 chunk_id 和原文位置；索引重跑不重复创建同版本 chunk。

### 第 07 天｜内部检索工具与证据模型

**目标：**第一个受控 Agent 工具能够返回引用证据。

- 文件：`app/tools/{base,knowledge_search}.py`、`app/evidence/{models,schemas,repository}.py`。
- 编码：定义 `ToolResult`、`EvidenceItem`；`knowledge_search(query, filters)` 由上下文注入租户和许可文档范围；保存源文档版本与检索片段。
- 编码：返回 evidence_id、标题、短 excerpt 和位置；长正文在存储中保留，不直接全部塞入模型上下文。
- 验收：引用可以定位到原文；跨租户 chunk 被过滤；租户字段不能由模型输入覆盖。

### 第 08 天｜外部搜索适配器

**目标：**Agent 可以查找可信公开资料。

- 文件：`app/tools/web_search.py`、`app/core/config.py`、`tests/fixtures/search_results.json`。
- 编码：定义 `SearchProvider.search()`，接入一个实际提供方；Fake 返回固定 URL、标题和摘要；支持官方域名筛选、数量上限和超时。
- 编码：记录 query、provider、retrieved_at；搜索摘要标记为 discovery，不直接当成已证实事实；过滤重复 URL。
- 验收：真实搜索能返回一组结果或被显式跳过；离线 fixture 可独立运行；限流、凭据错误和空结果都有明确类型。

### 第 09 天｜网页抓取与外部正文边界

**目标：**把搜索线索转成可保存的原始资料。

- 文件：`app/tools/web_fetch.py`、`app/agents/policies/tool_access.py`、`tests/unit/test_fetch_policy.py`。
- 编码：`validate_public_url()`、`fetch_page()`、正文提取；只抓 allowlist 中 HTTPS 域名，校验每次重定向及解析出的目标地址，拒绝私网和本机地址。
- 编码：禁止自动跟随未校验跳转，配置最大响应字节数、内容类型、超时及抓取频率；先支持静态 HTML，不承诺绕过登录或反爬。
- 验收：正常官方页可提取；私网 URL、跳转到私网、超大响应和非文本内容被拒绝；抓取失败不伪造正文。

### 第 10 天｜来源快照与证据规范化

**目标：**未来网页变更不影响已有报告引用。

- 文件：`app/evidence/normalizer.py`、`repository.py`、source_snapshots 迁移。
- 编码：`save_source_snapshot()`、`extract_evidence()`；保存最终 URL、标题、获取时间、正文 checksum、正文位置、引用短片段；内部来源保存文档版本。
- 编码：来源重复内容按 checksum 和 URL 规范化；验证 excerpt 确实存在于保存正文的对应位置，不能把模型改写句子当原文引用；正文截断明确记录；建立 `GET /v1/research/tasks/{id}/evidence/{evidence_id}`。
- 验收：引用读取保存快照，而不是现场重新抓网页；网页删除后历史证据仍可查；快照端点执行任务归属检查。

### 第 11 天｜规划 Agent

**目标：**从用户请求生成结构化研究步骤。

- 文件：`app/agents/nodes/{intake,planner}.py`、`app/agents/prompts/planner.md`。
- 编码：`normalize_request()`、`build_research_plan()`；识别产品、维度、时效要求和信息不足；输出每步目标、搜索线索与完成标准。
- 编码：程序校验计划长度和工具范围；需要用户补充的信息进入 awaiting_input 语义，由后续审批机制承载，首版可先返回澄清问题。
- 验收：清晰请求得到有效计划；含糊产品名称要求澄清；不会把未授权内部系统写进执行工具列表。

### 第 12 天｜LangGraph 工具循环

**目标：**完成一次由模型选择工具的研究执行。

- 文件：`app/agents/graph.py`、`app/agents/nodes/researcher.py`、`app/tools/registry.py`。
- 编码：`build_graph()` 连接 intake → planner → researcher ↔ tools；研究者根据缺口选择知识检索、网页搜索或网页抓取，条件边判断继续或完成。
- 编码：工具调用参数由 Schema 验证；程序限制循环次数、空结果次数和可用工具；证据 ID 汇总到 State，工具执行不接受模型指定身份。
- 验收：Fake 测试能够先查内部再查外部；证据不足时补搜；达到上限时输出缺口，不无限循环。

### 第 13 天｜PostgreSQL 检查点

**目标：**图进度不只存在进程内存中。

- 文件：`app/runtime/runner.py`、`app/agents/graph.py`、`app/main.py`、checkpoint 初始化脚本。
- 编码：使用所锁定版本对应的 PostgreSQL checkpointer；为每个 run 生成独立 graph_thread_id；在生命周期中初始化、关闭连接。
- 编码：`load_run_state()`、`resume_run()` 必须先查询业务 run 的归属；检查点数据库也按受控服务访问，不把任意 thread_id 直接开放给客户端。
- 验收：执行到研究中间，停止进程后加载到同一进度；不同 run 状态不串联；恢复接口不接受他人 thread_id。

### 第 14 天｜异步任务与 Worker 租约

**目标：**HTTP 请求返回后，研究任务仍可继续执行。

- 文件：`app/runtime/{worker,runner,leases}.py`、research_runs 迁移、`app/modules/research/service.py`。
- 编码：`POST /v1/research/tasks/{id}/runs` 创建 queued run；Worker 使用 `FOR UPDATE SKIP LOCKED` 领取，续租并设置 fencing_token；状态变更通过合法转换函数。
- 编码：用独立连接上的 PostgreSQL advisory lock 串行保护同 run 的图与 checkpoint 执行；旧 Worker 写业务数据前验证 fencing_token，失去租约立即终止；接管必须先拿到执行锁，不能仅因租约到期就并行推进图。
- 验收：启动两个 Worker，同一 run 不并发推进；API 重启不丢任务；Worker 中断后租约过期可被恢复领取。

### 第 15 天｜工具结果幂等与恢复语义

**目标：**恢复任务不会无条件重做已完成工具调用。

- 文件：`app/runtime/tool_runs.py`、tool_runs 迁移、`app/tools/base.py`。
- 编码：`execute_tool_once()` 以 run、scope_version、工具名与规范化参数摘要查记录；成功结果复用，失败按策略重试，force_refresh 产生明确的新缓存版本。
- 编码：写结果前核验租约；外部调用成功但落库前崩溃记为 unknown；只读搜索可重试，但报告中承认可能重复产生外部 API 费用。
- 验收：恢复后已保存的抓取结果不重复调用；用户修改范围不会错误沿用无效结果；unknown 状态可观测，不能假称严格只调用一次。

### 第 16 天｜可重连进度事件流

**目标：**用户可以看见执行阶段与工具状态。

- 文件：`app/runtime/events.py`、run_events 迁移、`app/modules/research/router.py`。
- 编码：持久化 plan_created、tool_started、tool_finished、evidence_added、run_status_changed 等业务事件；实现 `GET /v1/research/tasks/{id}/runs/{run_id}/events` SSE。
- 编码：sequence 在数据库原子分配；支持 Last-Event-ID、心跳和断线补读；只推送简短状态、摘要与来源信息，不暴露模型隐含推理、密钥或整段内部文档。
- 验收：断开再连能补齐已存事件；多个客户端观察不改变任务；未授权请求不能订阅事件流。

### 第 17 天｜计划审批与人工修改

**目标：**用户可以确认或修改研究方向再执行。

- 文件：`app/agents/graph.py`、`app/modules/research/{schemas,service,router}.py`、approvals 迁移。
- 编码：在 planner 后插入 LangGraph interrupt；返回结构化计划和澄清问题；实现审批/修改接口，以合法 resume 命令继续同一 run。
- 编码：审批包含 interrupt_id、scope_version 和审批人；重复审批返回确定结果，过期审批拒绝；计划变化时增加版本并重新审批。
- 验收：审批前不启动外部研究；重启后仍能批准继续；旧版本或另一租户无法批准；审批前逻辑重跑不产生重复副作用。

### 第 18 天｜结构化结论与首份报告

**目标：**把研究证据变成可阅读的交付物。

- 文件：`app/agents/nodes/writer.py`、`app/agents/prompts/writer.md`、`app/modules/reports/{models,service,router}.py`。
- 编码：`build_claims()`、`render_markdown_report()`；报告包含研究范围、对比表、关键发现、证据缺口、来源与获取时间。
- 编码：关键事实关联 evidence_id；事实、推断、未知项分开表达；证据不足时不能自动填造价格或功能。
- 验收：固定资料能生成完整报告；引用可以打开对应快照；未检索到的维度明确显示无法确认。

### 第 19 天｜证据核验与有界修订

**目标：**发现无依据、引用错配和冲突结论。

- 文件：`app/agents/nodes/verifier.py`、`app/agents/prompts/verifier.md`、`app/agents/graph.py`。
- 编码：`validate_claim_references()` 做确定性检查；`verify_claim_support()` 对证据与结论做辅助核验，输出 supported/unsupported/conflicting。
- 编码：发现缺口时回到 researcher 补搜，最多修订 2 轮；仍无依据时改成 unknown 或保留冲突说明；不以模型自报置信度作为正确性证明。
- 验收：故意加入无效 evidence_id 被直接拒绝；事实与引用不符可被标记；两份矛盾价格来源不被悄悄合并成一个数字。

### 第 20 天｜预算、Token 与调用追踪

**目标：**让长任务有明确停止条件和成本记录。

- 文件：`app/agents/policies/budget.py`、`app/llm/base.py`、usage_records 迁移。
- 编码：调用前预留保守预算，返回后核销；限制工具调用数、输入上下文、输出 token、研究轮数与预估金额；价格表由配置维护，注明估算口径。
- 编码：记录模型 call_id、usage、latency、工具耗时与错误；供应商没有提供实际 usage 时标记 estimated/unknown，不当成精确账单。
- 验收：预算不足时停止并保留已获取证据；超长资料先裁剪或摘要；并发调用不能分别看到同一份未扣减预算。

### 第 21 天｜有限并行的子研究 Agent

**目标：**让多个研究维度并行处理且结果可控合并。

- 文件：`app/agents/subgraphs/topic_research.py`、`app/agents/graph.py`、`state.py`。
- 编码：对独立维度创建子图，使用框架支持的分发机制；首版最多 2 个并行分支，每个分支有独立消息上下文，共享只读研究范围与原子预算账本。
- 编码：按 evidence_id 去重合并，保存分支任务状态；子图不能修改其他维度结论；记录父 run 与子任务关联。
- 验收：功能和部署两维度并行完成；来源不重复累加，预算不超支；单分支失败不丢弃其他分支已保存证据。

### 第 22 天｜工具故障、取消与任务恢复

**目标：**处理执行中最常见的失败。

- 文件：`app/runtime/runner.py`、`app/tools/base.py`、`app/modules/research/service.py`、故障 fixture。
- 编码：区分 timeout、429、认证失败、解析失败、空结果；有限退避重试，不可重试错误标记失败；实现取消请求及节点/工具边界的取消检查。
- 编码：deadline 约束单次调用；取消后不再排新调用，已发出的外部请求可能完成并产生费用，不能声称一定撤销；恢复利用检查点及 tool_runs。
- 验收：搜索超时后可以重试或报告缺口；任务取消能停止后续步骤；Worker 被杀后可继续，重复落库被阻止。

### 第 23 天｜不可信资料与越权测试

**目标：**把 Agent 权限落到程序而不是提示词上。

- 文件：`app/agents/policies/tool_access.py`、工具注册逻辑、`tests/integration/test_agent_boundaries.py`。
- 编码：工具参数二次验证、允许工具列表、来源文本标记及输出路径控制；报告文件名由服务端生成；拒绝模型请求读其他租户、调用未注册工具或提供系统角色消息。
- 验证：准备提示词注入网页，内容要求读取秘密、调用 Shell、换租户；测试应关注是否发生越权调用，而不只看模型有没有说拒绝。
- 验收：这些攻击不能获得凭据或执行越权动作；包含恶意指令的资料被记录为不可信证据；渲染前过滤主动 HTML 内容。

### 第 24 天｜报告版本与安全导出

**目标：**报告能分享为文件，历史内容可追溯。

- 文件：`app/modules/reports/{schemas,service,router}.py`、报告与结论表迁移。
- 编码：`publish_report_version()` 幂等写入数据库与原子文件；生成 Markdown 和经过转义/清洗的静态 HTML；接口校验任务归属再下载。
- 编码：修改已完成研究创建新 run 及报告版本；保留旧 scope、提示词/模型版本、证据快照和内容摘要；下载不使用用户输入的任意磁盘路径。
- 验收：报告版本 1 和 2 均可查看，引用保持各自快照；脚本标签不执行；中途失败不会留下被误认为完整报告的文件。

### 第 25 天｜创建有标注的评测集

**目标：**建立判断 Agent 好坏的依据。

- 文件：`evals/datasets/research_cases.jsonl`、`evals/datasets/README.md`、`tests/fixtures/corpus/`。
- 数据：准备 20 个小案例，覆盖正常对比、信息缺失、来源冲突、工具超时、审批修改和恶意来源；每例固定输入、资料、预期行为和允许的结论。
- 标注：关键事实人工标注支持片段；保留至少 5 个案例作为回归保留集，不用来调提示词；版本化语料与标注。
- 验收：每例能在离线模式复现；结论判定有依据；只有专家“觉得不错”而没有标注的样例不能算评测集。

### 第 26 天｜评测执行器与基线比较

**目标：**用同一资料比较改进前后的结果。

- 文件：`evals/runners/run_eval.py`、`evals/metrics/{references,coverage,cost}.py`、`docs/evaluation.md`。
- 编码：分别跑“单轮检索生成基线”与“规划 + 检索 + 核验 Agent”；保存每个 case 的输出、引用检查、耗时、调用数及成本估算。
- 指标：引用有效率、事实支持率、维度覆盖率、成功率、人工介入后恢复成功率；程序可核验指标与人工标注指标分开，给出分母。LLM judge 仅作辅助。
- 验收：Fake 用来检验执行器，不能证明真实模型质量；真实模型至少跑一组固定小样本，账号缺失则标注未实测，不填写虚构成绩。

### 第 27 天｜集成回归与 CI

**目标：**后续修改不破坏恢复、隔离和引用链路。

- 文件：`tests/conftest.py`、`tests/integration/test_full_research_flow.py`、`.github/workflows/ci.yml`。
- 编码：CI 启动 PostgreSQL，迁移业务表与 checkpoint 表；运行 Fake 模型全链路、跨租户、审批、并发租约、失败恢复和报告引用测试。
- 编码：模型和搜索网络调用默认禁用；真实 smoke/eval 单独命令启用，密钥来自运行环境；静态检查纳入 CI。
- 验收：空环境运行通过；人为关闭引用归属校验时对应测试失败，再恢复实现；CI 不消耗真实模型预算。

### 第 28 天｜基于评测的一次优化与可观测性

**目标：**用证据完成一次有价值的改进。

- 文件：`app/agents/prompts/`、`app/retrieval/search.py`、`app/core/logging.py`、`docs/evaluation.md`。
- 分析：选一个最大问题，例如检索不到某维度、引用不匹配或重复搜索；一次只改一类因素，记录模型、参数、语料与提示词版本。
- 编码：增加 run_id、step、tool、耗时和 budget 状态的结构化日志；准备失败任务与费用摘要查询，不记录模型隐含推理或原始凭据。
- 验收：同条件重新运行相关评测与保留集；报告是否改善及代价，不要求所有指标同时提升；能定位一个失败工具调用。

### 第 29 天｜容器部署与研究工作台

**目标：**让他人能够提交任务、审批和查看报告。

- 文件：`deploy/{Dockerfile,compose.yml}`、`app/templates/dashboard.html`、`app/modules/research/router.py`。
- 编码：部署 API、Worker、PostgreSQL；轻量页面提供输入范围、任务列表、计划审批、SSE 进度、证据查看和报告下载。
- 编码：演示 token 由用户输入，页面仅在会话内存使用，不写 URL；数据库与 storage 持久化；本地启动流程包含 bootstrap 和 checkpointer 初始化。
- 验收：从空环境按文档跑一例离线任务；配置真实账号后可跑在线模式；重启后任务和快照保留；页面不绕过服务端权限。

### 第 30 天｜交付与场景演示

**目标：**形成有工程和效果证据的 Agent 项目。

- 文件：`README.md`、`docs/{architecture,decisions,demo,limitations}.md`、`scripts/demo_research.py`。
- 演示：正常研究；中途停止 Worker 后恢复；审批时修改维度；来源冲突保留说明；恶意网页不能诱发越权工具调用。
- 整理：写清图结构、checkpoint 与业务表关系、工具幂等边界、预算和评测口径；保留实测报告、样例输出和参考来源，打版本标签。
- 验收：别人能按 README 启动并完成研究；所有关键离线测试通过；在线质量数据与未验证能力区分清楚；能在 10 分钟内讲清一次完整任务及失败处理。

## 7. 核心代码契约草图

以下内容用于指导实现，不是完整可运行代码。

```python
async def execute_tool_once(
    context: ExecutionContext,
    tool_name: str,
    arguments: dict,
) -> ToolResult:
    # context 来自服务端，包含身份、run 和有效租约。
    # 1. 校验工具权限与参数，拒绝 tenant_id 等可伪造身份字段。
    # 2. 用 run + scope_version + tool + args_hash 查已有结果。
    # 3. 校验并预留预算后执行受控工具。
    # 4. 核验 fencing_token 后持久化结果、来源和用量。
    # 5. 成功结果可重用，未知外部结果保守记录并按策略处理。
    ...

def validate_claim_references(
    claims: list[Claim],
    allowed_evidence: dict[str, EvidenceItem],
) -> list[ReferenceIssue]:
    # 检查每个引用存在、属于当前范围、能够打开对应快照。
    # 引用有效不等于结论正确，另做支持性核验与人工评测。
    ...
```

建议图结构：

```text
intake → planner → plan_approval(interrupt)
                         ↓
              researcher ↔ controlled_tools
                         ↓
                    build_claims
                         ↓
                      verifier
                    ↙         ↘
          researcher补搜       writer → save_report
          最多2次修订
```

第 21 天引入子研究图处理独立维度。审批、预算、取消和租约由确定性程序逻辑约束整个执行过程。业务状态中 waiting_approval 表示正常暂停，不能误判为失败后自动重试。

## 8. 评测口径和目标

| 指标 | 计算口径 | 主线目标 |
|---|---|---|
| 引用有效率 | 有效 evidence 引用数 / 全部引用数 | 固定离线案例达到 100% |
| 事实支持率 | 有充分标注证据支持的关键事实 / 全部关键事实 | 报告真实结果；目标至少 90% |
| 维度覆盖率 | 已给出有证据结论的维度 / 请求维度 | 报告覆盖率与未知项，不把 unknown 当覆盖成功 |
| 任务成功率 | 达到各 case 完成标准的任务 / 全部运行案例 | 报告真实结果与失败分类 |
| 恢复成功率 | 成功恢复且无重复产物的中断任务 / 全部中断任务 | 指定离线恢复案例全部通过 |
| 成本与耗时 | 每个任务独立记录，注明模型和价格配置 | 不超用户配置预算；未知消费明确标注 |

20 个小案例只足以做项目级回归，不能证明所有企业问题均可可靠处理。确定性 Fake 证明流程可控；真实模型评测才提供有限的效果证据。若没有真实模型账号，离线项目仍可交付，但真实质量与费用必须标注未验证。

## 9. 阶段交付与最终验收清单

| 时间点 | 必须能演示的成果 |
|---|---|
| 第 07 天 | 内部资料上传、检索、来源定位及租户隔离 |
| 第 12 天 | 模型规划、外部资料搜索/抓取、受控工具循环 |
| 第 17 天 | 持久化任务、Worker、断点恢复、事件流和人工审批 |
| 第 24 天 | 引用报告、核验修订、有限并行、成本控制及报告版本 |
| 第 30 天 | 评测集、CI、实测记录、部署、工作台及完整演示 |

- [ ] 每条关键事实可以追溯到当前任务保存的证据。
- [ ] 无证据的信息写成未知或推断，不凭空补齐竞品价格和功能。
- [ ] 其他租户的任务、文档、来源、事件和报告无法访问。
- [ ] Worker 中断后可以恢复；检查点、工具记录和任务状态一致。
- [ ] 用户可以确认计划、修改范围、取消任务并查看历史报告。
- [ ] 工具授权、预算和路径校验由程序执行。
- [ ] 真实模型结果与 Fake 验证分开，评测有固定资料和标注口径。
- [ ] 启动步骤、版本依赖、演示脚本与限制项完整。

## 10. 完成主线后再考虑的扩展

根据评测问题选择一项：中文语义检索、pgvector 与 reranker、PDF/OCR、人工评审工作流、定期情报更新、报告格式扩展、对接企业知识库。涉及定时监控、通知或写入外部系统时另行设计权限和运行策略，不纳入主线的只读研究工具。

求职描述以独立实现和实际结果为准。例如：“基于 LangGraph 实现可持久化的产品情报研究 Agent，在固定资料评测集上比较规划核验流程与单轮生成基线，记录引用有效率、事实支持率和任务成本。”不能把开源仓库所有能力写成自己实现，也不能用 Fake 的输出成绩代替真实模型质量。

## 11. 参考资料

- [DeerFlow 开源仓库](https://github.com/bytedance/deer-flow)：参考复杂 Agent 执行设计。
- [DeerFlow 中文说明](https://github.com/bytedance/deer-flow/blob/main/README_zh.md)：阅读能力边界和运行说明。
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)：检查点、thread 与恢复。
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)：人工介入和恢复执行语义。
- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)：API 层异步数据库连接与事务。

## 12. 每天的进度记录模板

```markdown
### 第 XX 天｜实际日期：
- 今日目标：
- 已完成文件/函数/接口：
- 本次模型/提示词/语料版本：
- 测试或评测命令与结果：
- 本次实际/估算调用费用：
- 问题、边界与下一步：
- Git commit：
```

执行原则：前一天核心验收通过再推进；模型不稳定时先使用固定资料和 Fake 查清流程，再调整真实模型行为。用可复现结果确认完成，不以“提示词已经写完”代替 Agent 能力完成。
