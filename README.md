# Medical Roughcut Review — 通用 Agent 能力包

一个开源、平台无关的医疗门诊纪实短视频粗剪与初检能力包，遵循开放的 [Agent Skills 规范](https://agentskills.io/specification)。同一份业务内核可以被 OpenAI Codex、Claude Code、GitHub Copilot / VS Code Agent Mode，以及其他兼容 Agent Skills 的智能体加载。

它先判断素材是否值得做、可以拆成几条，再按实际需要完成删、留、排、改、医学核查、最小修音、账号复盘和标题最小交接。它不依赖母项目，不绑定某位医生，也不把任何一家 Agent 平台当作业务规则来源。

## 它是什么

- **主体：** `roughcut-review/SKILL.md` 与其 `references/`、`assets/`，这是跨 Agent 共用的唯一业务内核；
- **通用入口：** 根目录 `AGENTS.md`，让支持项目指令的 Agent 打开仓库后知道从哪里开始；
- **平台适配：** `roughcut-review/agents/openai.yaml` 只补充 OpenAI 界面与调用元数据，不改变业务逻辑，其他 Agent 可以忽略；
- **不是：** Codex 专用提示词、某位医生的固定模板，或必须复制整个母项目才能运行的工程。

## 最省事的用法

当前团队如果使用 Codex，第一次发送：

> 请从 https://github.com/MIAOzhenhao2002/medical-roughcut-review-skill 安装 `roughcut-review` Agent Skill。

安装后重新打开 Codex，新建任意任务，上传字幕或 SRT，发送：

> 使用 `$roughcut-review`，先判断这份素材做不做、拆几条，再按需完成粗剪初检。

以后需要更新时，在已安装的Skill中运行：

```bash
python3 roughcut-review/scripts/update_skill.py
```

该命令会主动检查公开仓库；发现新版本后先备份当前安装，再自动更新。普通粗剪任务不会静默联网或自我修改。只检查不安装时添加 `--check-only`。完整边界见 [INSTALL.md](INSTALL.md)。

换成其他 Agent 时，业务包不用重做，只需按该 Agent 的 Skill 目录或安装方式加载同一个 `roughcut-review/` 文件夹。完整说明见 [INSTALL.md](INSTALL.md)。

不支持 Agent Skills 的普通智能体，也可以直接打开本仓库并发送：

> 读取 `roughcut-review/SKILL.md`，只按当前任务需要加载其中引用的文件，然后初检这份字幕。

## 仓库结构

```text
AGENTS.md                    # 通用项目入口，不复制业务规则
INSTALL.md                   # 不同 Agent 的安装与调用说明
roughcut-review/
├── SKILL.md                 # 唯一业务入口，遵循 Agent Skills 开放规范
├── VERSION                  # 当前通用包版本
├── agents/openai.yaml       # 可选的 OpenAI 适配元数据
├── scripts/update_skill.py  # 用户主动触发的检查与自动更新
├── references/              # 只在对应阶段加载的规则
└── assets/                  # 可复制使用的空白模板
```

公开仓库只包含通用规则和空白模板，不包含病例、患者身份信息、医生私有画像、账号后台数据、历史输出或访问凭据。

## 能做什么

- 一份素材输出零条、一条或多条候选；
- 长短内容按独立兑现判断，不按固定时长裁决；
- 动态合并或跳过删、留、排、改；
- 支持同一候选V1、V2、V3等不限次数增量复检，只重开新版变化影响的结论；
- 先识别并修复过度碎剪，再按需用可追溯字卡补足前因、人物背景和时间语境；
- 只有新增、强化、存疑或有时效性的医学主张才启动新核查；
- 锁定条件、概率、因果、部位、诊断范围和治疗选择；
- 区分医生、发布账号、病例主体和操作者；
- 用最强反证和缺失证据抑制迎合与无证据推断。

## 重要边界

本能力包不能代替临床诊断、机构合规、法务审核或发布平台终审。只有字幕时不能声称完成画面、口型或声音检查；任何患者材料在交给模型或外部检索前都应去身份化。

## 开发验证

```bash
python3 -m unittest discover -s tests -v
```

## 许可证

[MIT License](LICENSE)
