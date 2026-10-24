# 故障排查

## 没发现技能

- 确认 Harness 打开的项目根目录，与安装时的项目相同。
- 文件应在 `.agents/skills/deepseek-efficient/SKILL.md`，文件名和层级都要正确。
- SKILL.md 应保留 name、description 前置信息及非空正文。
- 新建会话并明确调用，查看加载轨迹；不要只根据回答风格判断是否加载。
- 检查是否存在同名技能或放在技能搜索目录中的旧备份。

## 回答变短，但 token 没减少

统计所有模型请求的输入、缓存输入与输出，以及失败和重试；不要只看最终答案长度。
对简单任务，新增提示开销可能超过节省量。先用匹配任务对照，再决定是否调用。

## 跳过必要验证

把它记为质量退化，而不是 token 优化成功。
保留用户验收标准，停用有退化的变体；提交问题时提供脱敏任务、模型档位、工具轨迹及实际检查结果。

## 命令行启动出现 Get-Acl / PowerShell 模块加载冲突

本机测试曾出现：从 PowerShell 7 启动子进程时，继承的 PSModulePath 导致 Windows PowerShell 加载模块的扩展类型冲突。
只读探测确认，清除该子进程继承的变量后，模块恢复加载。
这属于该启动环境的观察，不等于所有终端错误都由它引起。

可先从正常桌面入口启动 Harness，或在自己的启动器中仅调整子进程环境。Python 启动器示例：

```python
env = os.environ.copy()
for key in list(env):
    if key.lower() == "psmodulepath":
        del env[key]
subprocess.run(harness_command, env=env)
```

示例中的 os、subprocess 需要自行导入，harness_command 为你的现有启动参数。
不要因此改全局环境、关闭沙箱、提升权限或放宽安全策略。

## MALFORMED_RESPONSE 或非法工具 JSON

保留错误代码、工具名及可用 usage；失败调用不能算作成功。
先区分参数错误、环境失败和提供方响应异常，再决定是否有依据重试。
公开反馈前删除凭据、账号标识、个人文件路径与私人内容。

## 测试在临时目录报 WinError 5

扩展试运行中，受限终端无法遍历 Python 创建的 0700 临时目录，导致工作目录独立性测试报权限错误。最终合成夹具使用预先创建的项目内目录，保留切换工作目录和结果相等的断言，三组使用同一夹具。

遇到类似问题，先确认失败来自业务代码还是测试目录的访问条件。可以在自己的合成测试中用可访问的项目目录复现同一断言，记录这项环境调整。对真实项目应按既有权限和测试规范处理；不要把环境失败写成代码通过。详情见 [扩展报告](../benchmarks/extended/README.md)。

## 离线检查

在源码仓库根目录执行：

```text
python -X utf8 scripts/check_repository.py
python -X utf8 scripts/build_release.py
```

这些命令使用 Python 标准库，不调用模型或联网。构建结果写入 dist/。
