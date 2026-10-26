# 让AI帮我安装

把下面整段发给**能联网并操作文件**的AI Agent。它会先检查环境与目标，在你确认位置、范围及同名文件处理方式后安装你选择的一套。把链接交给Work、Claude Code或Codex也遵循这些条件；仅有模型名称或网页阅读能力并不够。

普通ChatGPT、Claude、Gemini、豆包和DeepSeek聊天窗口若没有这类工具，直接用[完整TXT](../downloads/README.md)或[全文复制](../copy/README.md)。本轮未实测这些聊天平台的导入或模型调用。

## 整段复制给Agent

```text
请帮我获取并使用 Creator Methods Atlas｜创作方法图谱。
仓库：https://github.com/Bananaaayee/creator-methods-skills
我想用的创作者：请先让我选影视飓风、何同学或小鹿 Lawrence。
如果我已经选好，就沿用我的选择，不默认安装全部。

1. 访问仓库，阅读 README.md、docs/交给AI安装.md、
   docs/安装Skill.md 和 DISCLAIMER.md。
   以当前文件和你的实际工具能力为准，不执行无关操作。
2. 核对 skills/ 下所选目录的 SKILL.md、配套模块和 references。
   判断你是否有网络、文件写入权限及可发现 Agent Skills 的宿主。
   Work、Codex、Claude Code等名称本身不证明这些权限存在。
3. 安装前说明：所选技能、宿主、项目级或用户级范围、
   完整目标路径，以及是否已有同名目录、链接或登记。
   获得我对这些事项的确认；已明确授权的范围不重复询问。
   未确认不写入；有同名内容就停下，不自动覆盖、合并或删除。
4. 支持安装时，优先按仓库中已验证的方式安装所选完整目录。
   保留工具的权限与信任确认，不使用跳过确认的参数。
   不只复制 SKILL.md，不改方法内容，不索要聊天中的密码或令牌。
5. 安装后核对目标文件集合和内容与所取源一致，确认 SKILL.md
   入口存在；用宿主的技能列表或发现功能检查是否识别。
   分别报告文件已安装、宿主已识别、实际调用是否验证。
   给我准确的安装位置、技能名称、调用示例和未完成项目。
6. 只能联网读取、不能安装时，改为读取所选完整 portable 文件，
   明确这是本次对话参考而非已安装；说明未读部分和上下文限制。
   连完整文件也无法读取时，如实说明，给我普通TXT下载页：
   https://github.com/Bananaaayee/creator-methods-skills/blob/main/downloads/README.md
   不用搜索摘要或短启动词冒充完整方法。
```

可将第三行改成“我想用影视飓风／何同学／小鹿 Lawrence”，再发送；不必先理解安装命令。

## 给执行安装的Agent

### 真实文件与名称

只使用当前维护的 `skills/`。`creators/`是保留历史，不能作为本轮安装源；不要用广泛递归扫描把新旧版本安装两次。

| 创作者 | Skill名称 |
|---|---|
| 影视飓风 | `media-storm-creator` |
| 何同学 | `he-tongxue-creator` |
| 小鹿 Lawrence | `lawrence-creator` |

对应目录均为 `skills/<Skill名称>/`，内含入口`SKILL.md`、六个编号模块、`references/`、`README.md`与`DISCLAIMER.md`。完整文件数依次是11、12、12；请仍以当前源目录为准。

先执行只读发现：

```sh
npx skills add Bananaaayee/creator-methods-skills --list
```

确认目标后才按[安装说明](安装Skill.md)选择单套命令或完整目录复制。当前项目优先只作为提议，不擅自写入用户级位置。安装器也可能写入共享目录、链接或锁文件；在说明计划时检查这些位置。来源同名也不能默认覆盖。遇到冲突停止，列出冲突位置，由用户决定保留、备份后替换或取消。

无终端但有文件工具时，可通过工具正常下载／读取所选完整目录，按宿主官方位置安装。无Skills安装器时不必为了本项目安装额外开发环境；完整目录复制须保留相对结构与全部文件。工具无法保证不覆盖已有内容时，不继续写入，改给手动步骤。

Gemini CLI整组安装需要`--path skills`；单套为`--path skills/<Skill名称>`。本项目普通ZIP需先解压，不把读取仓库或下载ZIP称为安装。不要跳过权限或工作区信任确认。

### 验证后怎样报告

- **文件已安装：** 实际路径、所选名称和文件集合／内容比对结果。
- **宿主已识别：** 实际技能列表或发现结果；未检查时直说“尚未验证识别”。
- **调用方法：** 使用[对应工具的调用示例](安装Skill.md#安装后怎么调用)，附用户自己的创作任务。没有模型调用就标“尚未实测调用”，不要因为复制成功宣布创作效果通过。

### 无法安装时的完整文件

- 影视飓风：[完整TXT](../portable/MediaStorm-Portable.txt) · [完整MD](../portable/MediaStorm-Portable.md)
- 何同学：[完整TXT](../portable/Hetongxue-Portable.txt) · [完整MD](../portable/Hetongxue-Portable.md)
- 小鹿 Lawrence：[完整TXT](../portable/Lawrence-Portable.txt) · [完整MD](../portable/Lawrence-Portable.md)

这些是完整方法，TXT与MD字节相同。网页工具可能只返回摘要或部分章节；必须实际取得全文，才能说明取得完整文件。资料是否在当前模型上下文中完整可见仍须另行说明；检索到一部分时只能作为有限上下文参考。联网也失败时，给用户[普通下载页面](https://github.com/Bananaaayee/creator-methods-skills/blob/main/downloads/README.md)，请其自行下载上传；不能声称你完成了下载或安装。

[返回首页](../README.md) · [手动与CLI安装](安装Skill.md) · [完整免责声明](../DISCLAIMER.md)
