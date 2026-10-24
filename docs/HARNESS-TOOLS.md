# Harness 工具衔接与上下文开销

本页是针对特定工具组合的使用参考，不是所有 DeepSeek 宿主的通用要求，也没有替换正式技能正文。

## 已复现：查看过文件，原生 write 仍要求先读

2026-10-25（Asia/Shanghai），在 DeepSeek Harness 0.2.1-rc.3、dsh-ops shell/file 0.3.0 的 headless 环境，用四个全新会话和四个独立合成目录验证：

- 两次先用 ops_inspect_local_file 查看 marker.txt，随后原生 write 均报 file has not been read；补用原生 read 后，write 重试成功。
- 两次先用原生 read，再用原生 write，首次写入均成功。
- 四次最终内容均为预期的 after 加换行，项目说明保持原样；没有调用 shell 或 edit。

这说明在该组合下，ops_inspect_local_file 的查看没有满足原生 write 的“已读”检查。它不意味着查看失败或丢失文件内容，也不能推出其他版本、其他写入工具具有相同机制。完整请求顺序见 [复现资料](../benchmarks/angles/read-guard/results.json)。

需要在该组合中用原生 write 修改已有文件时，直接用原生 read 读取待改文件。若已用预览工具查看，则在写入前补一次原生 read；按读取到的内容完成修改。保留写入器的读取检查。

可在对应项目的说明中使用这条约定：

```text
本项目中，若使用原生 write 修改已有文件，先用原生 read 读取待改文件；ops_inspect_local_file 的预览不替代此读取。
```

不要把多个查看工具都当成完成同一个读取前置条件。是否满足写入要求，应由写入器的实际反馈和对应工具文档确认。

## 为什么一次小错误会带来大量请求 token

上一轮 F02 联表任务发生上述错误，随后补读和重写两个模型请求的 usage 合计为 **29,528 token**。这是实际恢复请求的计数，不能当作消除错误后必然节省的反事实数字；两份实现的长度、后续上下文和生成过程也可能不同。

同一轮 F01 首次模型请求已有 **8,962 个输入 token**；该请求列出 30 个工具，工具说明序列化 JSON 长 24,783 字符。字符数不是 tokenizer 计数，不能据此把输入 token 按比例分配给工具、系统提示或历史记录。可确认的是，每多一个模型步骤都会再次携带相应上下文；只把技能正文减少几个字符，未必能抵消额外步骤。

缓存复用与输入减少是不同指标。DeepSeek 的缓存按可复用前缀匹配，尽力命中，不保证每次命中；缓存 token 仍应在完整 usage 中单独报告。[官方缓存说明](https://api-docs.deepseek.com/guides/kv_cache/)

## 档位与工具输出应分开检验

Low 与 High 由 Harness 或接口配置决定，不能靠提示词声称切换。Low 是较低推理强度，不能直接等同于关闭思考。[官方思考模式说明](https://api-docs.deepseek.com/guides/thinking_mode/)

工具会话的上下文管理需要遵守接口协议。当前官方文档要求带 tools 的思考模式请求完整回传先前的 reasoning_content；不能把删掉必需字段当成有效优化。可以独立检验额外请求、无关工具输出、输出长度和推理档位，保持任务验收与协议完整。

四组“技能有无 × High/Low”的固定对照单独见 [本轮报告](../benchmarks/angles/README.md)。本页的工具衔接复现不属于该四组干预，不能将两者混算为技能节省率。
