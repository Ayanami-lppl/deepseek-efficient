# 安装、更新与卸载

推荐安装到一个明确的项目。以下命令均在目标项目根目录执行。
技能不会替你改变模型、权限、网络或全局配置。

## 用 Git 安装固定版本

```powershell
New-Item -ItemType Directory -Force .agents/skills | Out-Null
git clone --depth 1 --branch v0.1.1 https://github.com/Ayanami-lppl/deepseek-efficient.git .agents/skills/deepseek-efficient
```

固定 tag 克隆可能显示 detached HEAD 提示，这是固定版本的正常状态。
安装路径应直接包含 SKILL.md，不要再多套一层压缩包目录。

## 无 Git 的精简 ZIP 安装

1. 打开 [Releases](https://github.com/Ayanami-lppl/deepseek-efficient/releases)，下载 `deepseek-efficient-v0.1.1.zip` 和 `SHA256SUMS`。
2. 用 `Get-FileHash .\deepseek-efficient-v0.1.1.zip -Algorithm SHA256` 查看压缩包哈希，与 SHA256SUMS 的对应行核对；哈希可识别下载内容变化，不能单独证明发布者身份。
3. 解压后把 `deepseek-efficient` 文件夹放到项目的 `.agents/skills/` 下。
4. 在 Harness 中打开该项目并新建会话，明确调用技能。

精简包只包含 SKILL.md、LICENSE、简短使用说明和 manifest.json；离线验收器及合成产物在源码仓库中。

## 验证加载

```text
请读取并使用当前项目 .agents/skills/deepseek-efficient/SKILL.md 技能，然后完成我的任务与必要验证。
```

轨迹中应出现 `skill` 加载 `deepseek-efficient`，或直接读取该路径的记录。
如果没有加载记录，见 [故障排查](TROUBLESHOOTING.md)。

## 更新 Git 安装

```powershell
git -C .agents/skills/deepseek-efficient status --short
git -C .agents/skills/deepseek-efficient fetch --tags origin
git -C .agents/skills/deepseek-efficient checkout v0.1.1
```

如果 status 显示本地修改，先备份或提交这些修改，再决定如何合并。
不要用强制 reset 覆盖自己的定制。更新后新建会话，以免继续沿用旧正文。

## 更新 ZIP 安装

把旧技能目录备份到技能搜索目录以外，再按精简 ZIP 安装步骤放入新版。
若曾定制 SKILL.md，请先比较、合并自己的修改。不要把同名技能的备份也留在 `.agents/skills/` 下。

## 卸载

仅移除这个项目的 `.agents/skills/deepseek-efficient/` 目录，然后新建会话。
保留项目源码、模型设置及其他技能。历史会话已经加载的正文可能继续存在于该会话上下文中。

## 支持范围

已验证 DeepSeek Harness 的项目级 `.agents/skills/` 加载。
其他宿主请按其技能目录规范安装；本仓库不把格式相容当作已完成的行为验证，也不自动进行用户级或全局安装。
