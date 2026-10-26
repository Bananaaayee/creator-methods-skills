# 安装标准Agent Skill

**想让AI代办：** 复制[交给AI的安装指令](交给AI安装.md)。成功需要当前环境能联网、写入文件并支持技能发现；使用Work、Claude Code或Codex的名称本身不保证这些条件。

**只用聊天窗口：** 直接[下载完整TXT](../downloads/README.md)或[复制全文](../copy/README.md)，不用运行下面命令。TXT是聊天资料，Skill ZIP是完整安装目录，两种用途不同。

<a id="使用通用skills安装器"></a>

## 先列出，再安装一套

从你希望使用技能的项目目录运行。需要可用的Node.js和npm；当前安装器官方要求Node.js至少22.20。只列出名称不会安装技能：

```sh
npx skills add Bananaaayee/creator-methods-skills --list
```

确认目标工具、项目级或用户级范围与完整路径，检查已有同名目录／链接／安装登记；有冲突先停止，请用户决定，不直接运行可能覆盖它的命令。默认项目级；用户级会影响其他项目，须单独明确确认。保留交互确认，只选下面一条：

```sh
npx skills add Bananaaayee/creator-methods-skills --skill he-tongxue-creator
npx skills add Bananaaayee/creator-methods-skills --skill lawrence-creator
npx skills add Bananaaayee/creator-methods-skills --skill media-storm-creator
```

安装时按CLI选择工具、范围和复制／链接方式；它可能写入共享目录、工具目录或锁文件，也要先核对目标。不要添加`-y`、`--yes`、`--all`等跳过确认的参数。无需为使用图谱统一购买某个AI平台；开发工具自身的登录、配额或订阅条件独立存在。[Skills安装器官方](https://github.com/vercel-labs/skills)

## 安装后怎么调用

先检查所选目录的`SKILL.md`、六个编号模块及`references/`都在，核对完整文件集合和内容与所取源一致。影视飓风11文件、何同学12文件、小鹿12文件；文件数只辅助排错，不能代替内容比对。

再检查工具是否发现技能，例如`npx skills list`或`gemini skills list`。发现成功与实际模型调用分开报告；没有调用就写“已安装并识别，调用尚未实测”。

用你实际安装的名称替换下列影视飓风示例：

- **Codex CLI／IDE：** `$media-storm-creator 请根据我的真实素材设计90秒结构。已有素材：……。不能改的地方：……。` 也可从技能选择器选中名称；未出现时按当前宿主说明刷新或重启。
- **Claude Code：** `/media-storm-creator 请根据我的真实素材设计90秒结构。已有素材：……。`
- **Gemini CLI：** “请使用 media-storm-creator，先读取对应规则，再根据我的真实素材设计90秒结构。已有素材：……。” 必要时`/skills reload`，保留技能激活与工作区信任确认。
- **Work及其他Agent：** 先确认当前会话中能发现该技能，再按该宿主的选择器或自然语言调用；不要假定本机安装自动同步到云端或其他项目。

另外两套对应名称为`he-tongxue-creator`、`lawrence-creator`。普通聊天窗口若只是上传了TXT，发送“请根据我提供的完整方法……”即可，不使用不属于该产品的斜杠命令。

## 权限或工具不支持时

无法联网、不能写入文件、宿主没有技能发现机制、目标冲突无法安全处理时，明确报告哪一步未完成，改用[完整TXT](../downloads/README.md)或[全文复制](../copy/README.md)。只阅读GitHub、下载ZIP或复制单个入口文件，均不能称为已安装完整Skill。

<a id="先用单个安装包"></a>

## 不用安装器：完整目录或单个安装包

先确认目标路径空闲且有写入权限；已有同名目录或链接时停止，由用户决定是否备份和替换。确认后从对应下载页获取单个Skill ZIP。解压后应为`he-tongxue-creator/`、`lawrence-creator/`或`media-storm-creator/`，目录直接含`SKILL.md`及配套模块、references。不要只复制SKILL.md，也不要把三个文件夹都改名为skill。

| 工具／范围 | 整个同名目录放在哪里 |
|---|---|
| Codex，当前项目 | `.agents/skills/<name>/` |
| Codex，当前用户 | `~/.agents/skills/<name>/` |
| Claude Code，当前项目 | `.claude/skills/<name>/` |
| Claude Code，当前用户 | `~/.claude/skills/<name>/` |
| Gemini CLI，当前项目 | `.gemini/skills/<name>/`，也支持`.agents/skills/<name>/` |

[Codex官方](https://learn.chatgpt.com/docs/build-skills)、[Claude Code官方](https://code.claude.com/docs/en/skills)、[Gemini CLI官方](https://geminicli.com/docs/cli/skills/)

## Gemini CLI：必须指定正确目录

V3发行时以`Gemini CLI 0.65.0`实测：它不会从仓库根自动递归进入本项目的skills容器。安装三套：

```sh
gemini skills install https://github.com/Bananaaayee/creator-methods-skills --path skills --scope workspace
```

单独安装，例如：

```sh
gemini skills install https://github.com/Bananaaayee/creator-methods-skills --path skills/he-tongxue-creator --scope workspace
```

另外两套把最后目录替换为`skills/lawrence-creator`或`skills/media-storm-creator`。Public仓库可匿名读取；安装器自己的确认、工作区信任和网络条件仍适用，不能省略`--path`。

本地包不需要远程仓库权限：

```sh
gemini skills install ./he-tongxue-creator --scope workspace
gemini skills list
```

先解压下载的普通`.zip`，再安装其中的同名目录。V3发行时实测`Gemini CLI 0.65.0`不直接识别普通`.zip`后缀；同字节内容改为临时`.skill`副本后可安装，但本项目没有发布`.skill`文件，也不把该对照称为普通ZIP直接安装成功。

不要在普通教程默认加跳过确认的`--consent`。`--scope workspace`明确只装当前项目，避免误装到所有项目；安装器本身的确认与工作区信任由用户判断。[官方命令](https://geminicli.com/docs/reference/commands/#skills)


<details>
<summary>兼容限制与历史测试记录</summary>

## 测试范围

已记录**24项本地基线检查＋15项最终追加检查**：覆盖三个技能的发现、单独/整组安装、Gemini原生列出、Claude Code目标的实际复制安装与登记、文件哈希及三个发布ZIP的结构。最终安装目录的35个文件与源一致。检查数包含文件完整性、预期失败及归档对照，**不等于39次远端安装或39项平台模型验证**。

另以官方公开对照仓库执行过远程发现与子目录安装；本项目在Private阶段的无凭证`--list`曾实际被认证拒绝。该阶段的认证远端安装未测试；公开后的匿名远端验收已通过，详见发行状态，不追溯改写原测试。两个远端对照均不计入上述39项。Codex/Claude Code中的实际模型自动调用、Claude/Gemini网页ZIP导入均未实测，不能宣传全平台认证。检查条件、非敏感结果和隔离复现方法见[安装验证记录](../tests/installation/README.md)。

规范与当前工具说明可变，安装前查[开放规范](https://agentskills.io/specification)及对应官方文档；不要覆盖已有同名技能而不保留自己的备份。


### 公开后的真实匿名远端验收（2026-10-25）

仓库改为Public后，以无凭证隔离环境执行4条命令，全部exit0：根`npx skills add ... --list`发现3套；指定何同学`-a codex --copy`安装后12/12文件SHA相同；Gemini原生远端`--path skills --scope workspace`安装3套，`skills list`全部Enabled，35/35文件SHA相同。工具仍为Skills1.7.4、Gemini0.65.0、Node24.19.0、npm12.2.1。

首次受限网络无法解析GitHub，原失败独立保留；获准只读网络后同一隔离脚本成功。未使用认证凭据、未更改真实用户配置、没有模型调用。该增量不计入旧39+5项，也不证明聊天平台导入或创作效果。附件CDN下载与Git远端安装不同，先前Chrome客户端下载拦截记录继续保留。

</details>

本轮新增真实匿名下载、发现和安装检查见[获取与安装体验验证](../tests/ux/README.md)。规范与账户功能可能变化，所引官方说明仅支持路径和调用方式，不代表已登录验证所有平台。[完整免责声明](../DISCLAIMER.md)
