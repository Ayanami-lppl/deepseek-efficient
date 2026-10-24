# DeepSeek Efficient

[![Offline checks](https://github.com/Ayanami-lppl/deepseek-efficient/actions/workflows/check.yml/badge.svg)](https://github.com/Ayanami-lppl/deepseek-efficient/actions/workflows/check.yml)

用于 DeepSeek Agent 的轻量技能：减少重复分析，保留正确性、必要验证和完整交付。

A small, prompt-only Agent Skill for DeepSeek. The skill itself requires no API key, package installation, service or background process.

当前版本 **v0.1.1**。正文保持经过实测的 **94 字符**；本次补齐安装、排障、离线验收、CI 和精简发布包。兼容标准 SKILL.md 格式，已验证 DeepSeek Harness 项目级加载及 headless 文件、终端任务；其他宿主尚未完成行为验证。

## 安装与使用

在准备用 Harness 打开的**目标项目根目录**执行：

```powershell
New-Item -ItemType Directory -Force .agents/skills | Out-Null
git clone --depth 1 --branch v0.1.1 https://github.com/Ayanami-lppl/deepseek-efficient.git .agents/skills/deepseek-efficient
```

无 Git 时，从 [v0.1.1 Release](https://github.com/Ayanami-lppl/deepseek-efficient/releases/tag/v0.1.1) 下载 deepseek-efficient-v0.1.1.zip 和 SHA256SUMS，核对哈希后，将解压的 deepseek-efficient 目录放入项目的 .agents/skills/。精简包只含技能、许可证、简短说明和文件哈希 manifest，便于避免把基准资料装进项目。

在 Harness 打开项目、新建会话，明确调用：

```text
请读取并使用当前项目 .agents/skills/deepseek-efficient/SKILL.md 技能，然后完成以下任务：
（写下具体任务与验收标准）
```

轨迹中应出现 skill 加载 deepseek-efficient，或读取该 SKILL.md 的记录。技能正文无需再次粘贴。正常使用 Harness 的账号、网络与模型费用仍由宿主处理。

- [完整安装、更新与卸载](docs/INSTALL.md)
- [任务示例与档位选择](docs/USAGE.md)
- [未加载、重复安装、环境问题等排查](docs/TROUBLESHOOTING.md)
- [变更记录](CHANGELOG.md) · [贡献与验证方法](CONTRIBUTING.md)

## 实测与边界

2026-10-24，Windows DeepSeek Harness 0.2.1-rc.2 桌面安装包自带 headless 入口，deepseek-account/deepseek-flash（界面名称 DeepSeek-V4.1-Flash），dsh-ops shell/file 0.3.0：

- **首版无技能 A/B**：两个修复任务、各两次配对重复，8 个独立会话。总 token 357,491 → 266,060，本次少 25.6%；8 个代码产物全部通过外部验收。见 [首版报告与数据](benchmarks/README.md)。
- **新增规则与档位比较**：终端执行、变化文件重读、多文件目录及两轮交接，共 12 个会话。全部通过代码与指定验证检查；候选“避免重复加载”规则在 High 下比原版多 6.28% token，未被采用。Low 的描述性结果与两次环境失败试运行也完整披露。见 [扩展报告与数据](benchmarks/extended/README.md)。
- **验收与不确定点候选（实验版）**：99 字符改写，两个新任务共 8 个会话，全部通过验收。本次总 token 少 11.45%，但只赢 2/4 配对，未达到预定稳定性条件，正式正文保持原样。见 [候选、完整结果与隔离试用](benchmarks/reasoning/README.md)。
- **读取与验证顺序候选（实验版）**：95 字符改写，四个新任务共 16 个会话，全部通过验收。请求与工具次数减少，总 token 少 4.74%，但仅赢 4/8 配对，输出 token 增加 17.52%，未达到预定条件。见 [完整结果、逐任务差异与候选](benchmarks/focused/README.md)。

这些是小样本观测，**不是通用节省率、费用承诺或推理能力提升证明**。总 token 包含缓存输入、加载与工具反馈、推理及答案输出；没有 usage 的会话命名请求不计入。扩展实验没有无技能组，两份报告不能混合计算新的节省率。原始私人会话不公开，公开材料只能复跑代码验收和检查脱敏数据的一致性，不能独立核验全部模型调用。

技能适合多步任务中的重复复述、等价方案反复比较等情况。简单问答应考虑加载开销，建议按需调用。推理档位、输出上限与缓存由宿主或接口配置，提示词不能硬性控制内部推理 token；用户要求的测试和交付仍应完成。尚未验证 GUI 端到端、大仓库或长会话。

## 离线验证与打包

Python 3.10+，只用标准库，不调用模型或网络：

```powershell
python -X utf8 scripts/check_repository.py
python -X utf8 scripts/build_release.py
```

检查覆盖：历史产物验收、扩展与候选产物 unittest、原始错误代码负对照、提示与产物哈希、数据汇总、文档链接、基础隐私扫描及发布包校验。Windows/Linux、Python 3.10/3.14 的 CI 执行同一流程。构建在 dist/ 生成内容可复现的 ZIP 与 SHA256SUMS；基准验收会执行仓库内合成代码。

## 技能正文

```text
按最短可靠路径求解。只分析决定答案的计算、约束和边界；选定可行解并完成必要核查后立即作答。无新矛盾不另列解法，不反复复述题目、格式或已确认结论。保留复杂任务必需的推理和用户要求的全部交付。
```

[MIT License](LICENSE)。本项目是社区技能，与 DeepSeek 官方无隶属关系。
