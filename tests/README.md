# 评测复核

先读[协议](PROTOCOL.md)与[报告](REPORT.md)。`results/`保存真实输出、评分及运行元数据，原始执行提示词和完整事件日志在用户本地研究资产中；其中附有旧方法全文，不在发布包重复分发。

脚本使用Python标准库和已登录的Codex CLI。执行模型固定为`gpt-6.1-sol`、推理档`high`；本轮CLI为`0.164.0-alpha.11.1`。脚本使用独立临时目录、全新临时会话、相同输出格式与无工具要求。不同账号、系统提示、模型服务和随机采样可能改变结果；本轮没有宣称统计显著性或逐字可复现。

准备一个私有工作目录：其中`repo/`指向本仓库，`private-baselines/`放有合法来源的三个旧正式Release文件夹。旧版来源由`docs/baseline-manifest.json`核对；不要把原始语料或账号凭证放进仓库。`--work`以下的`evaluation-private/`只作本地输出。

```bash
python3 tests/run_eval.py --work /your/private-eval-work --conditions plain he-tongxue:old lawrence:old media-storm:old --revision baseline --workers 3
python3 tests/run_eval.py --work /your/private-eval-work --conditions he-tongxue:new lawrence:new media-storm:new --revision candidate --workers 3
```

对照评分需要将对应基线与候选的`all-outputs.json`按条件合并为独立轮次，不能覆盖初始答案；然后用`score_blind.py --work ... --revision ... --pass-name blind-scoring-corrected`。评分脚本会隐藏名称与版本、固定随机打乱标签，并在评分完成后解盲。标签种子不是模型采样种子。`audit-regressions.json`与`repair-regressions.json`为审计和实际失败后设计的定向测试，须单独报告，不能混进预注册通用分数。

本轮判读还人工复核了模型裁判：初轮裁判曾把身份隐藏标记当成未填占位符、把真实的方法附件语境当成不存在的背景。相关评分已标为无效用于比较，原始记录保留；修订评分说明后重新执行。不能只看最后一行分数而略过评价依据。

构建与安装检查与行为评测分开。`scripts/validate_release.py`测试临时安装、覆盖保护、相对引用与校验和；可通过`--official-validator`接入技能格式校验器（需PyYAML）。这些检查不能证明写作更好、所有结论正确或第三方素材已有许可。
