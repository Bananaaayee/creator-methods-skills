# 安装验证记录与隔离复现

检查日期：2026-10-25。官方工具版本：Node 24.19.0、npm/npx 12.2.1、Skills 1.7.4、Gemini CLI 0.65.0。实际验证环境为macOS；未据此宣称其他操作系统全部通过。

## 数字代表什么

**24项本地基线＋15项最终追加检查全部通过。** 这39项包含发现、复制、安装登记、文件哈希、预期失败和ZIP容器对照；不等于39次远端安装、39个平台，或39次平台模型验证。

公开脚本参数化后，另做了语法／帮助检查及最终目录7项、ZIP3项、归档5项的复核；没有用新脚本重跑历史24项，也没有把这些迁移复核累加为新的通过数量。历史24项保留的是此前真实执行的证据。

| 记录 | 检查范围 |
|---|---|
| [baseline-24.json](baseline-24.json) | 29个运行文件阶段：Skills整库／单个发现与安装、Gemini整组／单个安装及原生发现、`.agents/skills`别名发现、文件一致性；共24项 |
| [final-15.json](final-15.json) | 加入6个说明文件后的35文件阶段：Claude Code目标复制／登记、Gemini整组复制／发现与完整哈希7项，三个单ZIP检查3项，Gemini归档正反例5项 |
| [final-file-hashes.json](final-file-hashes.json) | 最终35文件的项目相对路径与SHA256，用于比较安装结果和发布ZIP |
| [public-remote-control.json](public-remote-control.json) | 另外执行的Vercel官方公开对照库检查，不计入上述39项，也不是Atlas私有仓库验证 |
| [private-unauthenticated-control.json](private-unauthenticated-control.json) | 另外执行的本项目私有URL无凭证`--list`负例：实际退出1并被认证拒绝；不计入上述39项，也未验证远端新版内容 |
| [legacy-coexistence.json](legacy-coexistence.json) | 旧88个跟踪文件与V3并存的独立本地增量：物理6个入口，默认根发现3个，按名称安装取新`skills/`源；不计入上述39项 |

**本项目私有仓库的认证远端安装未测试。** 公开对照库成功与本地文件成功不能证明本项目远端可被匿名或认证安装。没有执行模型调用、创作效果评测、登录或网页／手机Skills导入；Claude Code部分验证的是Skills安装器的目标目录、登记与复制完整性。

另一次对本项目私有URL的实际无凭证`npx skills add … --list`在60秒内被认证拒绝，没有超时。该负例禁止终端登录，使用新临时状态、空账户令牌环境与禁用的Git全局／系统认证配置，未提供OAuth、token或SSH身份；没有读取或安装私有远端的新内容，也没有更改真实用户配置。认证拒绝与本地成功分别记录。

公开对照记录保留了首次Gemini原生列出因工作区未受信任而失败的结果，以及只在隔离子进程信任临时工作区后的成功复核。它不是未解决的文件包装错误。正常使用Gemini项目技能时也需正常信任工作区。

## 冻结旧目录与V3并存的增量检查

独立临时夹具精确复制旧仓库`git ls-files`列出的88个实际跟踪文件，再按相对路径覆盖V3文件，排除Git元数据和缓存。夹具物理上有6个`SKILL.md`：旧`creators/`中3个、新`skills/`中3个。实际运行Skills 1.7.4的默认根`--list`仍精确发现3个标准名称；显式对`<组合目录>/skills --list`也发现3个。

从组合根按`he-tongxue-creator`名称实际`--copy -a codex`安装得到12文件，完整哈希匹配新`skills/he-tongxue-creator/`，包含新README和免责声明；旧目录仅10文件，因此安装来源得到实证。三套新旧29个运行文件SHA256均相同，V3另有6个说明文件，总35文件。**`skills/`是唯一持续维护的方法权威源，`creators/`只保留冻结旧版。**

该版本安装器优先查标准技能容器；`skills/`已有结果时不进入广泛递归后备扫描，普通发现也按名称去重。这里验证的是默认本地行为，没有另测`--full-depth`或私有远端新版内容。Gemini仍使用`--path skills`，本次未重复其既有检查。此增量不改变原24＋15项记录。

## 准备隔离工具目录

以下为贡献者的可选复现步骤，采用POSIX shell。Node需至少22.20；使用已安装的npm，仅把指定版本工具下载到新临时目录。该准备步骤需要网络，检查脚本本身不会安装依赖或触发登录。

```sh
atlas_tools="$(mktemp -d)"
npm install --prefix "$atlas_tools" --cache "$atlas_tools/npm-cache" --userconfig /dev/null --ignore-scripts npm@12.2.1 skills@1.7.4 @google/gemini-cli@0.65.0
```

所有命令从本仓库根运行。复现脚本通过参数取得工具目录，使用当前Node，不依赖作者的本机路径：

```sh
node scripts/run-isolated-checks.mjs --tooling "$atlas_tools" --phase versions
node scripts/run-isolated-checks.mjs --tooling "$atlas_tools" --phase final-local
```

`final-local`重放最终目录的7项检查。每次运行创建全新的系统临时目录，并输出结果位置；结果、完整命令日志和安装目录不会写入本仓库或用户技能目录。脚本使用独立的XDG状态／配置／缓存目录与`GEMINI_CLI_HOME`；不继承账户令牌，不覆盖`HOME`或`CODEX_HOME`，不输出环境变量或密钥。仅对这些隔离子进程设置`GEMINI_CLI_TRUST_WORKSPACE=true`，不会改用户信任表。

历史基线的24项检查流程也可重放，但在当前版本运行时会检查当前35文件，而不是恢复历史29文件快照：

```sh
node scripts/run-isolated-checks.mjs --tooling "$atlas_tools" --phase candidate
```

## 检查发布ZIP

先在本地已有三个单Skill发布ZIP时运行；也可用仓库构建器生成同级`release-assets/`：

```sh
python3 scripts/build_release.py --assets
python3 scripts/check-release-zips.py --archives ../release-assets
node scripts/run-isolated-checks.mjs --tooling "$atlas_tools" --phase final-archive --archives ../release-assets
```

ZIP脚本使用Python标准库，验证顶层同名目录、`SKILL.md`入口、CRC、安全路径、重复条目、完整文件集合和哈希；只解压到新临时目录。`--repo`可显式指定技能源仓库，`--archives`可指定其他发布包目录。

Gemini CLI 0.65.0直接安装普通`.zip`的预期结果是失败；它支持的是`.skill`后缀ZIP容器。归档检查把何同学ZIP复制为临时`.skill`副本，验证同字节内容可原生安装、列出并保留12个文件，原始发布包保持不变。这不表示普通ZIP直接安装成功。用户使用普通ZIP时应先解压，再安装得到的完整技能目录。

## 可选公开远端对照

仅以下显式阶段访问Vercel官方公开仓库，需要允许网络。它们不访问Atlas私有仓库，不读取Git认证配置或请求登录：

```sh
node scripts/run-isolated-checks.mjs --tooling "$atlas_tools" --phase remote
node scripts/run-isolated-checks.mjs --tooling "$atlas_tools" --phase remote-multi
```

`remote`重放Skills整库／子目录发现和Gemini单目录安装；`remote-multi`重放Gemini仓库根无`--path`的预期失败，以及`--path skills`整组安装和列出。公开仓库和工具未来可能变化，历史结果与新结果应分别记录。

公开JSON只保留必要检查摘要和相对文件哈希，未复制作者本机绝对路径、私有研究路径、环境变量、凭证或全部临时日志。脚本是本次已执行验证流程的参数化版本；它们只检查技能发现、复制和完整性，不调用模型。
