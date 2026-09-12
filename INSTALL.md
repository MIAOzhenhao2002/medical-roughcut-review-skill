# 安装与调用

## 通用原则

真正需要安装的是完整的 `roughcut-review/` 文件夹，不是单独复制 `SKILL.md`，也不需要复制原始母项目。

Agent Skills 兼容客户端会先读取 `name` 和 `description` 判断是否启用，再按任务需要加载正文、参考文件与模板。不同客户端的安装位置和显式调用符号可能不同，但使用的是同一份业务内核。

## OpenAI Codex

在 Codex 中发送：

> 请从 https://github.com/MIAOzhenhao2002/medical-roughcut-review-skill 安装 `roughcut-review` Agent Skill。

安装后重新打开 Codex。显式调用使用 `$roughcut-review`；自动匹配开启后，也可以直接说“帮我初检这份字幕”。

## Claude Code

把完整文件夹放到个人级 `~/.claude/skills/roughcut-review/`，或当前项目的 `.claude/skills/roughcut-review/`。调用时说明使用 `roughcut-review` Skill，并附上字幕或文件路径。

## GitHub Copilot / VS Code Agent Mode

个人共用可放到 `~/.agents/skills/roughcut-review/` 或 `~/.copilot/skills/roughcut-review/`；项目级可放到 `.agents/skills/roughcut-review/`、`.github/skills/roughcut-review/` 或 `.claude/skills/roughcut-review/`。

GitHub CLI 2.90.0 或更高版本也支持从仓库预览和安装 Agent Skill：

```bash
gh skill preview MIAOzhenhao2002/medical-roughcut-review-skill roughcut-review
gh skill install MIAOzhenhao2002/medical-roughcut-review-skill roughcut-review
```

## 不原生支持 Agent Skills 的智能体

打开或上传本仓库，使智能体可以访问相对路径，然后发送：

> 读取 `roughcut-review/SKILL.md`，只按当前任务需要加载其中引用的文件，然后初检这份字幕。

如果智能体只能接收单个文本，不能访问引用文件，它只能执行简化版流程，不能声称已经运行完整能力包。

## 团队使用边界

- 每台设备、每个 Agent 客户端通常只需安装一次；新建“粗剪”项目只是整理素材的可选方式，不是运行条件；
- 更换医生或账号时提供对应身份和已确认画像；身份未知时保持通用模式，不猜；
- 不向公开仓库、Issue 或外部检索提交患者身份信息、原始病例、住院号、影像编号、未授权录音、账号后台数据或凭据。
