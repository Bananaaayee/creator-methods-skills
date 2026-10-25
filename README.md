# Creator Methods Atlas｜创作方法图谱

从影视飓风、何同学和小鹿 Lawrence 的公开作品中整理创作方法，帮助你选择题目、组织真实素材、设计结构与修改表达。

**[下载文件](downloads/README.md) ｜ [复制使用](copy/README.md) ｜ [安装Skill](docs/安装Skill.md)**

维护者：**BANANAAAYEE**。发行V3，更新于**2026-10-25**。仓库现已公开，可直接下载、阅读和复制；实际验证结果见[发行状态](docs/发行状态.md)。

## 先选一位，再选一种用法

| 方法 | 先解决什么 | 使用入口 |
|---|---|---|
| **影视飓风** | 技术或产品问题怎样用影像回答，展示与测试怎样支持结论 | **[下载](downloads/MediaStorm.md)** · [复制](copy/MediaStorm/README.md) |
| **何同学**（老师好我叫何同学） | 哪个具体问题值得拍，怎样设计看得懂的验证与制作任务 | **[下载](downloads/Hetongxue.md)** · [复制](copy/Hetongxue/README.md) |
| **小鹿 Lawrence** | 真实观察怎样长成主题，人物、旅程、信息与个人体验怎样连接 | **[下载](downloads/Lawrence.md)** · [复制](copy/Lawrence/README.md) |

它不是创作者的官方AI模型，也不是简单模仿口吻。你自己的判断、素材和表达始终优先；同一任务可能合理地得到相近方案，不必强行套成三种“风格”。

## 如何使用

**能上传文件：**选一份完整TXT，上传到你常用的聊天AI，再发送创作任务。若当前客户端支持MD，也可下载同内容MD。无需安装代码工具或提供原始语料库。

**不能上传：**点“复制”，按页面先发短启动说明，再发完整方法，最后发任务。全文太长就按编号分段。短启动词不是完整Skill；没读全、漏分段或上下文不够时，必须说明目前只是有限上下文版本。

**开发工具用户：**下载单个标准Skill包，或按[安装说明](docs/安装Skill.md)使用Codex、Claude Code、Gemini CLI与兼容安装器。只在支持的工具中安装；普通聊天软件不必也不一定能安装SKILL目录。

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

```sh
npx skills add Bananaaayee/creator-methods-skills --list
npx skills add Bananaaayee/creator-methods-skills --skill he-tongxue-creator
gemini skills install https://github.com/Bananaaayee/creator-methods-skills --path skills --scope workspace
```

三套标准名称为`he-tongxue-creator`、`lawrence-creator`、`media-storm-creator`。Gemini整库需要`--path skills`；单个需要`--path skills/<name>`，不要省略。[确切目录、其他命令与测试范围](docs/安装Skill.md)

## 本次实际升级与限制

本轮把已验证的同一方法源构建为完整MD、等价TXT、可复制全文、无损分段及三个标准安装包，加入独立声明、跨平台说明与实际安装器测试。没有重新发明作者模型，也没有重跑大规模创作评测；VNext事实边界与作品纠错全部保留。

方法版本：何同学**1.3.0**、小鹿**1.3.0**、影视飓风**1.22.0**。VNext通用创作题未证明稳定全面优于旧版，精确字数和重叠任务的方法区分仍有限制。[更新记录](CHANGELOG.md) · [已知限制](KNOWN_LIMITS.md) · [历史评测](https://github.com/Bananaaayee/creator-methods-skills/blob/e8a0d4747d26e63f79e873a3c4ad7fb539d04862/tests/REPORT.md)

本项目为BANANAAAYEE的第三方独立研究，与三位创作者及团队无已确认官方合作、授权或背书，不代表其真实内部流程。第三方作品权利归权利人，使用者应核实事实与引用，不复制受保护的长篇原文。**[完整免责声明](DISCLAIMER.md)**

技术文件统一由`skills/`方法源构建；普通观众只需上方三个入口。[发行验证记录](docs/发行验证记录.md)

为完整保留旧版，GitHub中的`creators/`、旧测试／文档文件与`release-manifest.json`继续保留，后者只对应VNext。V3只维护`skills/`并使用`distribution-manifest.json`；旧构建器已另存档，普通用户仍从页面顶部三个入口开始。
