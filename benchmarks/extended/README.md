# 扩展验证：终端、变化文件、多文件和两轮交接

日期：2026-10-24。完整脱敏数据见 [results.json](results.json)，固定顺序和采纳条件见 [plan.json](plan.json)。本实验用于比较原提示与候选改动，不包含无技能基线，不能当作新的技能节省率。

## 比较与结论

两种合成任务 × 三组 × 两次重复，共 12 个独立会话，每个会话完成任务后再进行一次只读交接，共 24 个用户轮次：

- `old_high`：原版 94 字符正文，High；总 token **425,157**，37 次模型请求，44 次工具调用。
- `new_high`：候选 136 字符正文，High；总 token **451,848**，38 次模型请求，47 次工具调用。
- `new_low`：同一候选正文，Low；总 token **401,779**，35 次模型请求，43 次工具调用。

候选在 High 下比原版多 **6.28%** token，四个配对比较均增加，因此没有采用。v0.1.1 保留与 v0.1.0 字节一致的 SKILL.md。两个提示快照分别在 [原版](../prompts/v0.1.0.txt) 和 [候选](../prompts/candidate-no-reload.txt)。候选仅额外加入“当前上下文已有且内容未变的技能或文件，不重复加载；内容变化或必要验证时重新读取。”

采纳条件在运行前确定：原版 High 与候选 High 均完成四次有效运行并通过代码、文件完整性及指定验证检查，同时候选 High 的合计 token 不高于原版 High。结果未达到用量条件。

候选 Low 比候选 High 少 **11.08%** token，两组本次均通过；这只是同一提示下的描述性档位比较，未验证复杂任务的质量，也没有原版 Low 组。不要据此把所有任务默认调为 Low。

## 任务与验收

- `reload`：先读规则，终端执行生成器，再读已变更的规则；修复十进制金额计算、动态配置、边界及工作目录独立性。每个产物通过 9 个 unittest 方法（包含子测试）。
- `cache`：从带 30 份无关文档的多文件目录中修复 TTL 边界、输入校验和嵌套对象隔离。每个产物通过 10 个 unittest 方法（包含子测试）。
- 两种任务都要求模型实际执行 `python -m unittest -v`；会话工具结果中核验了成功状态与 `OK`。受保护的测试、合同及生成器保持原样；reload 规则按要求更新到版本 2。
- 第二轮仅要求交接摘要。比较前后文件哈希，12 次均未修改文件。这是两轮上下文复用检查，不能代表长会话。

12 个产物均通过外部独立复跑，总计 114 次 unittest 方法执行。相同方法在多组重复，不是 114 个互不相同的测试。公开 [tasks.json](tasks.json) 为冻结的初始文件与任务合同；[artifacts](artifacts) 是实际产物，逐文件 SHA256 已记录。运行轨迹相关检查为本机观测，公开代码复跑不能证明这些轨迹或 token 用量。

## 本地复跑与新实验

只需 Python 3.10+，使用标准库，无需 API key。验收器会执行指定的代码，应只验收可信文件。

```powershell
python benchmarks/extended/fixture.py evaluate reload benchmarks/extended/artifacts/N01/money.py
python benchmarks/extended/fixture.py evaluate cache benchmarks/extended/artifacts/N04/src/cache.py
```

为新的模型运行生成初始目录（目标目录必须不存在）：

```powershell
python benchmarks/extended/fixture.py prepare reload old_high ../trial-old
python benchmarks/extended/fixture.py prepare reload new_high ../trial-candidate
```

在 Harness 分别打开目录、新建会话，设置相同模型和 High 档位，使用 plan.json 中的同类初始请求，结束后发送其中的 followup。Low 组须在宿主手动选择 Low；技能提示不能替代接口配置。保留每次运行，包括失败，记录实际加载、模型路由、工具结果、usage 和产物哈希。对原版和候选轮换顺序，保持相同 fixture、工具、账号及预算。公开生成器不包含平台相关的私有会话读取器，也不会自动调用模型或修改 Harness 设置。

## 环境问题与统计口径

沿用 DeepSeek Harness 0.2.1-rc.2 桌面安装包的 headless 入口、deepseek-account/deepseek-flash，dsh-ops shell/file 0.3.0。每轮超时上限 240 秒，正式批次固定 12 次，无自动重试。

正式批次前两次 old_high 试运行分别发生：继承 PSModulePath 导致模块准备冲突及错误工具 JSON；Python 创建的 0700 临时目录无法被受限终端遍历，诊断至超时。这两次失败保留在私有档案并作为环境试运行排除，不冒充通过，也不计入三组合计。排障与失败试运行的消耗不包含在报告的正式比较中。随后只清理子进程继承的 PSModulePath，并将“切换工作目录”测试改为预先创建的项目内目录；同一断言与 API 要求保留，三组使用相同改正后的夹具。没有调整系统权限或全局配置。

token 为已提交 assistant 请求 usage 的 inputTokens、cacheReadTokens、cacheWriteTokens 和 outputTokens 之和，包括缓存输入、加载与工具反馈。outputTokens 可能包含内部推理及答案，未拆分。会话命名请求无 usage，被排除；无法计算未返回 usage 的在途请求。不是账单费用，也不是总 token 的硬上限。

固定但非随机的顺序、每任务每组仅两次重复、单一模型与本机环境、两个小合成任务，均限制可推广性。没有 GUI 端到端、大仓库、联网工具、长会话或生产任务验证。原始私人会话与机器路径不公开；档案哈希仅用于本机追溯，不能替代公开可审计的原始轨迹。历史无技能 A/B 结果单独保留在 [首版报告](../README.md)。
