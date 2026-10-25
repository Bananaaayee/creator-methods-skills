# 安装标准Agent Skill

不使用命令行的观众请回到[下载文件](../downloads/README.md)或[复制使用](../copy/README.md)。以下只适用于实际支持Agent Skills的开发工具。规范格式不等于所有AI聊天软件都有安装入口。

## 先用单个安装包

从对应下载页获取单个Skill ZIP。解压后应为`he-tongxue-creator/`、`lawrence-creator/`或`media-storm-creator/`，目录直接含`SKILL.md`及配套模块、references。不要只复制SKILL.md，也不要把三个文件夹都改名为skill。

| 工具／范围 | 整个同名目录放在哪里 |
|---|---|
| Codex，当前项目 | `.agents/skills/<name>/` |
| Codex，当前用户 | `~/.agents/skills/<name>/` |
| Claude Code，当前项目 | `.claude/skills/<name>/` |
| Claude Code，当前用户 | `~/.claude/skills/<name>/` |
| Gemini CLI，当前项目 | `.gemini/skills/<name>/`，也支持`.agents/skills/<name>/` |

Codex可显式调用`$he-tongxue-creator`等名称；Claude Code可用`/he-tongxue-creator`；Gemini CLI按自然语言要求使用指定技能，必要时`/skills reload`。Gemini项目需正常受信任，未信任工作区可能不发现技能。不要把Claude Code命令搬到其他产品。[Codex官方](https://learn.chatgpt.com/docs/build-skills)、[Claude Code官方](https://code.claude.com/docs/en/skills)、[Gemini CLI官方](https://geminicli.com/docs/cli/skills/)

## 使用通用Skills安装器

本轮以`skills 1.7.4`实际核对根`skills/<name>/SKILL.md`结构。维护者已明确授权现有仓库公开；现为Public，以下远程命令可匿名读取，无需本项目的GitHub访问授权。公开后已通过匿名远端安装，详见[发行状态](发行状态.md)，不能把可读状态当作安装已通过。

```sh
npx skills add Bananaaayee/creator-methods-skills --list
npx skills add Bananaaayee/creator-methods-skills --skill he-tongxue-creator
npx skills add Bananaaayee/creator-methods-skills --skill lawrence-creator
npx skills add Bananaaayee/creator-methods-skills --skill media-storm-creator
```

安装时按CLI选择工具和范围。无需为使用图谱统一购买某个AI平台；开发工具自身的登录、配额或订阅条件独立存在。[Skills安装器官方](https://github.com/vercel-labs/skills)

## Gemini CLI：必须指定正确目录

本轮以`Gemini CLI 0.65.0`实测：它不会从仓库根自动递归进入本项目的skills容器。安装三套：

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

先解压下载的普通`.zip`，再安装其中的同名目录。本轮实测`Gemini CLI 0.65.0`不直接识别普通`.zip`后缀；同字节内容改为临时`.skill`副本后可安装，但本项目没有发布`.skill`文件，也不把该对照称为普通ZIP直接安装成功。

不要在普通教程默认加跳过确认的`--consent`。`--scope workspace`明确只装当前项目，避免误装到所有项目；安装器本身的确认与工作区信任由用户判断。[官方命令](https://geminicli.com/docs/reference/commands/#skills)

## 测试范围

已记录**24项本地基线检查＋15项最终追加检查**：覆盖三个技能的发现、单独/整组安装、Gemini原生列出、Claude Code目标的实际复制安装与登记、文件哈希及三个发布ZIP的结构。最终安装目录的35个文件与源一致。检查数包含文件完整性、预期失败及归档对照，**不等于39次远端安装或39项平台模型验证**。

另以官方公开对照仓库执行过远程发现与子目录安装；本项目在Private阶段的无凭证`--list`曾实际被认证拒绝。该阶段的认证远端安装未测试；公开后的匿名远端验收已通过，详见发行状态，不追溯改写原测试。两个远端对照均不计入上述39项。Codex/Claude Code中的实际模型自动调用、Claude/Gemini网页ZIP导入均未实测，不能宣传全平台认证。检查条件、非敏感结果和隔离复现方法见[安装验证记录](../tests/installation/README.md)。

规范与当前工具说明可变，安装前查[开放规范](https://agentskills.io/specification)及对应官方文档；不要覆盖已有同名技能而不保留自己的备份。


### 公开后的真实匿名远端验收（2026-10-25）

仓库改为Public后，以无凭证隔离环境执行4条命令，全部exit0：根`npx skills add ... --list`发现3套；指定何同学`-a codex --copy`安装后12/12文件SHA相同；Gemini原生远端`--path skills --scope workspace`安装3套，`skills list`全部Enabled，35/35文件SHA相同。工具仍为Skills1.7.4、Gemini0.65.0、Node24.19.0、npm12.2.1。

首次受限网络无法解析GitHub，原失败独立保留；获准只读网络后同一隔离脚本成功。未使用认证凭据、未更改真实用户配置、没有模型调用。该增量不计入旧39+5项，也不证明聊天平台导入或创作效果。附件CDN下载与Git远端安装不同，先前Chrome客户端下载拦截记录继续保留。
