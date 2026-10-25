# 发布与后续维护

目标仓库：[Bananaaayee/creator-methods-skills](https://github.com/Bananaaayee/creator-methods-skills)。本轮按用户授权新建为Private，没有将其改为Public。此前未发现本项目已使用的Git远程或历史，本地旧Release独立保留。

本轮GitHub CLI设备授权返回`access_denied`，因此不能把命令行推送描述为成功。发布改用已登录的Google Chrome网页上传；是否提交完成、真实分支与提交哈希，以最终交付旁的发布记录及GitHub实际历史为准。空仓库已创建不等于源码已发布。

上传源应来自干净的发布文件清单，排除`.git`、缓存、账号文件、原始字幕、Research Cards、私有基线及完整执行提示词。`release-manifest.json`核对三套运行文件与便携版；测试结果保留输入、输出及裁判依据，源语料仍只在用户本地。

网页提交的远程历史与本地独立初始化的历史可能不同。后续维护建议用已授权的Git客户端从远程克隆，再复制需要的修改、检查差异并提交；不要用强制推送覆盖网页发布历史。命令行克隆入口为：

```bash
git clone https://github.com/Bananaaayee/creator-methods-skills.git
```

私有仓库需要通过GitHub正常登录授权；不应把访问令牌发进聊天或写进仓库。后续是否公开、是否选择开源许可，应由项目权利人另行决定。
