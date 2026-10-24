# DeepSeek Efficient

用于 DeepSeek Agent 的轻量技能：减少重复分析与无效操作，保留任务正确性、必要验证和完整交付。

A small, prompt-only Agent Skill for DeepSeek. No API key, service, package installation or background process is required by the skill itself.

首版 **v0.1.0** 保留经过实测的 94 字符正文。使用标准 `SKILL.md` 格式；已在 DeepSeek Harness 中验证技能加载和文件工具任务。其他宿主尚未验证。

## 安装到 DeepSeek Harness 项目

在你准备用 Harness 打开的**目标项目目录**中执行：

```powershell
New-Item -ItemType Directory -Force .agents/skills | Out-Null
git clone --depth 1 --branch v0.1.0 https://github.com/Ayanami-lppl/deepseek-efficient.git .agents/skills/deepseek-efficient
```

也可以从 [Releases](https://github.com/Ayanami-lppl/deepseek-efficient/releases) 下载源码压缩包，把包含 `SKILL.md` 的目录放成：

```text
你的项目/
└── .agents/
    └── skills/
        └── deepseek-efficient/
            └── SKILL.md
```

在 Harness 中打开该项目并新建会话，明确调用：

```text
请读取并使用当前项目 .agents/skills/deepseek-efficient/SKILL.md 技能，然后完成以下任务：
（写下你的具体任务与验收标准）
```

运行轨迹中应出现 `skill` 加载 `deepseek-efficient`，或读取该目录 `SKILL.md` 的记录。技能正文无需再重复粘贴。技能本身不需要额外依赖；正常使用 Harness 所需的模型账号、网络和模型费用仍由宿主处理。

## 适用范围

适合包含多步分析、文件读取与编辑的任务，尤其是出现重复复述、反复比较等价方案或无新增证据地重复检查时。简单问答是否值得加载，需要结合新增输入开销判断。建议先按需调用。

技能提供行为指导。推理档位、最大输出量和缓存策略通过宿主或接口配置；这段提示不保证精确限制内部推理 token。用户要求的测试、边界检查和交付物仍应完成。

## 实测摘要

2026-10-24，在 Windows 桌面安装包自带的官方 **headless** 入口中，沿用 `deepseek-account / deepseek-flash / high`；桌面界面显示模型为 DeepSeek-V4.1-Flash / High。Harness 版本 0.2.1-rc.2，加载 dsh-ops shell/file 0.3.0。

两个代码修复任务，每个任务两次配对重复，共 8 个独立 Agent 会话：

- 请求 token 合计：基线 **357,491**，技能组 **266,060**，本次减少 **25.6%**。
- 四组 token 均下降，单组降幅为 **3.7%—52.8%**。
- 八个产物均通过外部验收：每个 CSV 产物 119 项、每个区间合并产物 310 项。
- 模型请求步骤合计：29 → 23；工具调用合计：30 → 24。

总 token 包含缓存输入、技能加载、工具反馈和推理及答案输出。自动会话命名请求没有 usage，因此未计入。**这些数字是小样本观测，不是通用节省率或费用承诺。** GUI 端到端交互、终端开发、大仓库及长会话尚未验证；本次也没有证明模型的推理能力提升。

完整口径、逐组数据和限制见 [benchmarks/README.md](benchmarks/README.md)。公开的合成任务与代码产物可在本地验收：

```powershell
python benchmarks/evaluate.py csv benchmarks/artifacts/T01/totals.py
python benchmarks/evaluate.py intervals benchmarks/artifacts/T03/intervals.py
```

验收器仅使用 Python 标准库，不调用模型或联网。原始私人会话档案、个人记忆、凭据和机器路径未发布。公开 token 数据是本机观测的脱敏汇总，无法仅凭公开材料独立核验全部模型调用。

## 技能正文

```text
按最短可靠路径求解。只分析决定答案的计算、约束和边界；选定可行解并完成必要核查后立即作答。无新矛盾不另列解法，不反复复述题目、格式或已确认结论。保留复杂任务必需的推理和用户要求的全部交付。
```

## 版本与许可证

当前版本：v0.1.0。正文与本次 Harness 实验所用版本一致。后续针对重复加载等现象的改动，将在复测后单独发布。

[MIT License](LICENSE)。本项目是社区技能，与 DeepSeek 官方无隶属关系。
