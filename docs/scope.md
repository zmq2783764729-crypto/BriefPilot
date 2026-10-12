# BriefPilot 首版范围

研究一个产品主题，最多比较 3 个产品与 5 个维度，默认关注功能、部署、定价。用户确认计划后，Agent 检索内部产品文档和外部官方资料，产出有引用的报告。

- 上传仅支持 UTF-8 txt/md，先使用关键词检索。
- 输出 Markdown 和安全 HTML；事实、推断、未知项分开表达。
- 工具只读且受控，不执行任意 Shell，不自动发送报告或写企业系统。
- 持久化检查点、人工审批、证据快照、工具幂等、执行锁与预算按计划实现。
- 当前骨架仅包含配置、服务入口、生命周期、健康检查与领域/HTTP/验证错误格式。
- `agent_mode=fake/live` 只是后续适配器的配置入口，当前没有可运行的研究 Agent，也没有 Fake 模型实现；模型网关安排在第 02 天。
- 运行此骨架不需要数据库、模型或搜索 API；业务模块不会因存在空目录就被认为完成。

演示资料位于 `tests/fixtures/corpus/`，全部为虚构数据，用于固定输入，不代表真实企业产品。

资源生命周期采用 [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/)；配置使用 [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)。
