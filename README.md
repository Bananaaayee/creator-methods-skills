# Creator Methods Atlas｜创作方法图谱

这是一套研究**影视飓风、何同学、小鹿 Lawrence**创作方法的独立工具，帮助你选题、组织真实素材、设计结构和修改表达，同时保留你自己的判断。

### ① 让AI帮我安装

把[整段安装指令](docs/交给AI安装.md)交给能联网、能操作文件的AI Agent。它会先检查环境，在你确认后安装所选的一套。

### ② 下载文件直接使用

[选择一份完整TXT](downloads/README.md)，上传给你常用的聊天AI，让它读取完整内容，再输入自己的创作任务。普通聊天用户优先选这条，不用下载整个仓库。

### ③ 复制文字使用

[打开全文复制入口](copy/README.md)，先发加载说明，再发完整方法，最后发任务。手机不便下载时可按编号分段；短启动词不是完整Skill。

<a id="先选一位再选一种用法"></a>

## 选一套方法

| 创作者与入口 | 适合先解决的问题 |
|---|---|
| **[影视飓风](downloads/MediaStorm.md)** | 技术、产品与影像证据 |
| **[何同学](downloads/Hetongxue.md)** | 具体问题与可理解的验证 |
| **[小鹿 Lawrence](downloads/Lawrence.md)** | 真实观察、人物与旁白 |

## 交给AI的安装指令

<details>
<summary><strong>展开，整段复制给Agent</strong></summary>

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

[独立指令页与执行说明](docs/交给AI安装.md)

</details>

安装成功应分别确认**文件已安装、宿主已识别、调用如何验证**。仅访问GitHub网页不等于安装；普通聊天窗口不因模型名称就拥有本机文件权限。[安装后怎么调用](docs/安装Skill.md#安装后怎么调用)

本项目由 **BANANAAAYEE** 独立整理，与三位创作者及团队无已确认官方合作、授权或背书。它不代表真实内部流程，也不以模仿口吻为目标。[完整免责声明](DISCLAIMER.md)

## 使用与项目说明

<details>
<summary>聊天平台步骤、任务示例与安装命令</summary>

## 如何使用

**能上传文件：** 选一份完整TXT，上传到你常用的聊天AI，再发送创作任务。若当前客户端支持MD，也可下载同内容MD。无需安装代码工具或提供原始语料库。

**不能上传：** 点“复制”，按页面先发短启动说明，再发完整方法，最后发任务。全文太长就按编号分段。短启动词不是完整Skill；没读全、漏分段或上下文不够时，必须说明目前只是有限上下文版本。

**开发工具用户：** 下载单个标准Skill包，或按[安装说明](docs/安装Skill.md)使用Codex、Claude Code、Gemini CLI与兼容安装器。只在支持的工具中安装；普通聊天软件不必也不一定能安装SKILL目录。

方法文件本身不以任何特定平台的付费订阅为统一前提。平台自身的账户、套餐、版本、地区、管理员设置和上下文限制仍可能不同。

### 你使用哪个AI

| 平台 | 推荐起步 |
|---|---|
| ChatGPT | 完整TXT附件；常用时放入Project资料并添加启动指令；专用Skills入口按账号条件使用 |
| Claude网页／App | 完整TXT或Project知识；已有Skills导入入口时使用单个标准包 |
| Gemini网页／App | 完整附件或粘贴；Skills/Gems正有迁移，以当前官方入口为准 |
| 豆包 | 当前客户端若接受TXT附件就上传；不能上传就复制全文或分段，不需要代码工具 |
| DeepSeek网页／App | 能接受附件时用完整TXT，否则复制全文；不需要开发者API密钥 |
| 其他聊天AI | 文件、完整粘贴或分段任选；不要把提供资料称为永久训练或完整安装 |

详见**[简单跨平台使用指南](docs/使用指南.md)**。各聊天平台本轮均未登录实测，教程依据官方说明并逐项标明未确认功能；安装器发现／复制测试另有实际记录。

## 一句话任务示例

> 请先读取我提供的完整方法，说明缺失或未读部分。我只有手机和周末两天，已有修好台灯的画面、回答“还能用”的录音、排队的人和桌面零件。请设计90秒结构，保留平实语气，不补失败，也不替人物写心理。先给结构，不写全文。

## 安装命令

仓库现为Public，下列Git命令可匿名读取，无需本项目的GitHub访问授权。公开后的匿名远端安装已实测通过；普通用户可以直接用文件，不必运行它们。

先确认目标工具、范围和路径；已有同名内容时停止，不默认覆盖。以下命令保留交互确认。

先只列出名称：

```sh
npx skills add Bananaaayee/creator-methods-skills --list
```

再从下面三条中**只选你需要的一条**，不用整段执行：

```sh
npx skills add Bananaaayee/creator-methods-skills --skill he-tongxue-creator
npx skills add Bananaaayee/creator-methods-skills --skill lawrence-creator
npx skills add Bananaaayee/creator-methods-skills --skill media-storm-creator
```

Gemini CLI若明确选择安装三套，可使用下列命令；只装一套见独立安装页：

```sh
gemini skills install https://github.com/Bananaaayee/creator-methods-skills --path skills --scope workspace
```

三套标准名称为`he-tongxue-creator`、`lawrence-creator`、`media-storm-creator`。Gemini整库需要`--path skills`；单个需要`--path skills/<name>`，不要省略。[确切目录、其他命令与测试范围](docs/安装Skill.md)


</details>

<details>
<summary>版本、研究边界与历史发行记录</summary>

维护者：**BANANAAAYEE**。发行V3，2026-10-25；本次入口维护为2026-10-26。现有Release、方法内容和版本保持不变。

## 本次实际升级与限制

本轮把已验证的同一方法源构建为完整MD、等价TXT、可复制全文、无损分段及三个标准安装包，加入独立声明、跨平台说明与实际安装器测试。没有重新发明作者模型，也没有重跑大规模创作评测；VNext事实边界与作品纠错全部保留。

方法版本：何同学**1.3.0**、小鹿**1.3.0**、影视飓风**1.22.0**。VNext通用创作题未证明稳定全面优于旧版，精确字数和重叠任务的方法区分仍有限制。[更新记录](CHANGELOG.md) · [已知限制](KNOWN_LIMITS.md) · [历史评测](https://github.com/Bananaaayee/creator-methods-skills/blob/e8a0d4747d26e63f79e873a3c4ad7fb539d04862/tests/REPORT.md)

本项目为BANANAAAYEE的第三方独立研究，与三位创作者及团队无已确认官方合作、授权或背书，不代表其真实内部流程。第三方作品权利归权利人，使用者应核实事实与引用，不复制受保护的长篇原文。**[完整免责声明](DISCLAIMER.md)**

技术文件统一由`skills/`方法源构建；普通观众只需上方三个入口。[发行验证记录](docs/发行验证记录.md)

为完整保留旧版，GitHub中的`creators/`、旧测试／文档文件与`release-manifest.json`继续保留，后者只对应VNext。V3只维护`skills/`并使用`distribution-manifest.json`；旧构建器已另存档，普通用户仍从页面顶部三个入口开始。

本轮只调整获取和使用入口，未重新生成完整便携文件或Release附件。`distribution-manifest.json`保留V3构建快照的校验信息，不随本轮说明页面刷新。[本轮实际检查](tests/ux/README.md)

</details>
