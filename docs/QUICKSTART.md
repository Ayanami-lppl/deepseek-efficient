# DeepSeek Efficient：精简技能包

把本目录放到目标项目的 `.agents/skills/deepseek-efficient/`。
在 DeepSeek Harness 中打开该项目，新建会话并明确调用：

```text
请使用 deepseek-efficient 技能，完成下面的任务和必要验证。
```

运行轨迹中应有 skill 加载记录，或读取本目录 SKILL.md 的记录。
推理档位由 Harness 设置；技能提供简短行为指导，不保证固定节省比例。

完整安装、更新、卸载与故障排查：
[GitHub 文档](https://github.com/Ayanami-lppl/deepseek-efficient#readme)

许可证：本目录 LICENSE。包内 manifest.json 列出版本及文件 SHA-256。

可选：对长日志任务，可明确要求读取 [日志工具用法](https://github.com/Ayanami-lppl/deepseek-efficient/blob/main/references/log-output.md)，按需运行 scripts/check_result.py（Python 3.10+）。它仅读取原终端已完成的完整日志，不调用模型、不启动测试子进程。默认 94 字符正文保持独立；新工具未在小样本中降低总 token，不默认用于短任务。
