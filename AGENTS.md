# 通用 Agent 入口

本仓库提供平台无关的医疗短视频粗剪与初检能力。

收到字幕、SRT、原片、粗剪、总版、删留排改反馈、账号复盘、AI修音或成片确认任务时：

1. 完整读取 `roughcut-review/SKILL.md`；
2. 只按该文件的路由加载当前阶段需要的 `roughcut-review/references/`；
3. 需要空白交付模板时使用 `roughcut-review/assets/`；
4. 以当前素材和用户明确提供的信息为事实源，不把 README、测试、平台元数据或示例当作病例证据。

`roughcut-review/SKILL.md` 是唯一业务入口。`roughcut-review/agents/openai.yaml` 只是 OpenAI 客户端的可选界面适配，不能覆盖或改变通用业务规则。

不伪造病例、患者经历、医生原意、现场原声、画面、身份、诊断、治疗结果或因果；外部检索只使用去身份化问题。用户、医生、机构合规与发布负责人保留最终决定权。
