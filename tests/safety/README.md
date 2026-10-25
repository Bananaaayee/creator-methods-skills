# 安全检查证据

- `github-history-before-v3.json`：实际打开全部20个GitHub提交页面，记录其文件路径、父提交及增删统计；88条不同路径均为新增。分支、标签与Release状态是V3整理前的实际快照。
- `embedded-reference-overlap.json`：完整方法源与本地77/83/442份原始素材的连续文本对照结果。未发现规范化后连续60字符完全一致片段；不等于法律授权或所有相似表达均已排除。
- `assets-pattern-scan.json`：18个发行附件解包后的95个文本条目，包含重复的同源安装包，模式扫描无命中。
- `candidate-pattern-scan.json`：最终候选正文的非敏感扫描摘要；可使用 `python3 scripts/check_publication_safety.py` 在新环境复查。

未分发原始字幕、音视频、研究中间文件、账户资料或密钥。变为Public时可达历史与Release都可能公开，具体范围见 [公开范围与安全检查](../../docs/公开范围与安全检查.md)。
