# 推理与 token 优化：来源、取舍与实现

检索日期：2026-10-25（Asia/Shanghai）。这是围绕 DeepSeek Harness 的定向工程检索，不是系统综述、穷尽检索或元分析。单人筛选；论文、作者仓库和官方文档优先。只将可核验、可局部实现的方法用于候选，不将其他模型的节省率移植为本项目结果。

## 推理应压缩到什么程度

[Chain of Draft](https://arxiv.org/abs/2502.18600)（Xu、Xie、Zhao、He，2025；v2）比较简短中间草稿与较长推理。[作者代码](https://github.com/sileix/chain-of-draft/blob/a7dbf5dea808b1aa1e12f7a90ea573321581df78/configs/gsm8k_cod.yaml)中确有每步五词的提示。已读摘要、方法、结果和局限相关全文段落，及该配置文件。

研究使用 GPT-4o、Claude 3.5 Sonnet 等条件，包含人工编写的 few-shot 草稿；论文也报告 zero-shot 和小模型下的质量损失。它支持“保留决定答案的必要中间信息”的实验方向，不能证明五词上限适合 DeepSeek 工具代理。本技能继续保留复杂任务所需推理，不限制每步词数，也不要求输出或披露完整内部思维链。

[Token-Budget-Aware LLM Reasoning（TALE）](https://aclanthology.org/2025.findings-acl.1274/)（Han 等，ACL Findings 2025，24842–24855，DOI: 10.18653/v1/2025.findings-acl.1274）按问题难度控制预算。已核验 ACL 出版页与方法摘要；[arXiv 预印本](https://arxiv.org/abs/2412.18547)与出版版本按同一研究处理，不重复算证据。作者 GitHub 链接检索返回 404，没有声称复跑其代码。

动态预算值得后续对照，但本项目每多一次模型往返都会重带工具和上下文；没有加入额外的“先让模型估算预算”调用。预算不足也可能损害正确性，不能用统一短答案上限代替验收。

## 编码代理的成本在哪里

[TokenEconomizer 作者仓库](https://github.com/microsoft/TokenEconomizer)及[预印本](https://arxiv.org/abs/2610.22732)（Li 等，2026-10-15）把反复出现的环境知识、工具选择、失败循环和缓存成本作为不同干预点。已读摘要与 README 的机制、使用及实验说明；未在本机安装或复跑作者插件。其 SWE 实验不包含本项目的 Harness 条件，不能直接推广数字。

这里可局部借鉴的是把已证实的环境约束写到对应项目，例如 [Harness 原生读取与写入衔接](HARNESS-TOOLS.md)。不自动裁剪全局工具集，不额外生成通用微技能，不让环境故障变成反复盲试。

[Anthropic：Code execution with MCP](https://www.anthropic.com/research/code-execution-with-mcp)（2025-11-04）说明工具定义与中间结果会占用上下文，并展示在代码中筛选、汇总后再返回必要结果的方式。已读相关正文。我们据此实现独立的标准库日志摘要器：原命令完整执行，完整日志留盘，只返回定位信息、哈希、退出状态和有限尾部。这是工程迁移，不是该文章的实验复现。

[context-mode 作者仓库](https://github.com/mksglu/context-mode)将中间数据留在执行环境，按需检索；已读 README 功能、原理与限制相关部分，未审计全实现、未安装。它采用 ELv2 许可证。本项目没有复制其代码，也不采用其宣传节省率；日志摘要器为本项目独立编写的 MIT 代码。

[Aider RepoMap 官方文档](https://aider.chat/docs/repomap.html)展示在 token 预算内选择相关符号和依赖上下文。它提示未来可对“大仓库定位”做独立实验；本轮不为短任务新增仓库索引，也不声称实现了 RepoMap。

## DeepSeek 的接口边界

[Thinking Mode 官方文档](https://api-docs.deepseek.com/guides/thinking_mode/)当前提供 low/high/max 等真实接口控制；温度等部分参数在 thinking 模式不生效。提示词不能替代 effort 配置。带工具的思考模式还要求按协议保留相关 reasoning_content；不通过删除协议字段省 token。

[上下文缓存官方说明](https://api-docs.deepseek.com/guides/kv_cache/)说明前缀缓存及命中/未命中计数。总 token 下降、未缓存输入下降和实际账单下降是不同指标；本项目分别保留 usage，不由字符数反推模型 token，也不把缓存 token 全按未缓存价格计费。

## 本轮实现及验证

可选工具：[完整日志、有限返回操作说明](../references/log-output.md)，脚本 [check_result.py](../scripts/check_result.py)。原型在 Harness 中创建子进程失败，因此改为只读原终端已生成的日志，保留失败原型结果。测量还修正了“只看最后几行”的遗漏：stderr 的测试汇总可能早于缓冲 stdout 的进度行出现，摘要器保留带行号的常见 unittest 标记，但标记本身不能证明通过。

[本轮实验](../benchmarks/research/README.md)公开冻结候选、全部产物、用量和预定门槛。只有通过门槛才能成为默认行为；工具输出的字符减少不等于端到端 token 必然减少。

检索记录见 [search-log.json](../benchmarks/research/search-log.json)。最初 CoD 文件名用了连字符而返回 404，随后从固定提交取到实际下划线文件；TALE 代码未取到的缺口保留。未读取所有论文全文，也未完成独立双人筛选、作者全部代码复现或未见任务验证。

本轮检索与实验设计过程参考：Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. https://doi.org/10.48550/arXiv.2609.00065
