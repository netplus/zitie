# A1 浏览器在线预览

## 立即可尝试：第三方静态预览

[打开 main 上的 A1 动画](https://raw.githack.com/netplus/zitie/main/animation/index.html)

此地址由第三方 **raw.githack.com** 读取公开 GitHub 资源并以正确 HTML / JavaScript MIME 类型提供；首次打开 HTML 可能要求点击安全确认，缓存更新可能延迟几分钟。它不是 GitHub Pages 官方托管，也不保证永久可用。仓库真实运行文件为 [animation/index.html](../animation/index.html)，仅需同目录的 `samples.js`、`timeline.js`、`player.js`，无需在线 API、外部字体或 CDN。本阶段都是轨迹工程预览，**不是经教学审定的笔顺视频**。

## 目标：GitHub Pages（已配置发布工作流，启用待办）

预期官方地址：

- 根目录：`https://netplus.github.io/zitie/`
- 播放器：`https://netplus.github.io/zitie/animation/`

链接只有 GitHub Pages 真正启用且部署完成后才会可用。仓库当前原始检查 `has_pages=false`，不得把上述地址称为已发布。

官方 Pages 初次启用需要通过仓库管理员操作完成（GitHub `GITHUB_TOKEN` 不具备创建 Pages 站点所需的 administration 权限）。已在 `.github/workflows/animation-pages.yml` 设置以下过程：

1. 每次 `main` 的动画相关文件变更或手动启动工作流时，先执行 `node --test animation/tests/timeline.test.cjs`。
2. 仅打包播放器、必要 JS、原版 `ARPHICPL.TXT` 与改编数据告知文件 `animation/NOTICE.md`；**不上传正式 PDF、manifest、字体及未授权来源原文**。
3. 通过只读的 GitHub Pages API 检查站点是否已启用；未启用时只发出说明并跳过部署，不让常规 CI 失败。
4. 启用后使用 `actions/configure-pages@v5`、`actions/upload-pages-artifact@v4` 和 `actions/deploy-pages@v4` 完成自动部署。

**仅需一次**（当你决定采用官方 Pages 时）：

- 打开 [netplus/zitie 的 Pages 设置](https://github.com/netplus/zitie/settings/pages)，在 **Build and deployment → Source** 选择 **GitHub Actions**。
- 然后打开 [Actions](https://github.com/netplus/zitie/actions/workflows/animation-pages.yml)，选择 **Run workflow**，目标分支 `main`。后续 `main` 上的动画资源更新会自动重新发布，无需重复操作。

之后以 **Pages 部署工作流 completed/success** 和浏览器能实际播放为上线事实。工作流只部署已合入 `main` 的代码，不为 PR 提供未经审核的公开预览。

## 质量与授权边界

线上动画仍是 A1 实验成果，201个主部首虽然有完整的原版中心线数据，但其逐笔起收、转折和钩笔方向未获得新的教学级审核。不得使用 Pages 预览成功作为解除 fail-closed 限制的依据。其他 A1 工作进展见 [A1 技术设计](A1_ANIMATION.md) 及 [Issue #79](https://github.com/netplus/zitie/issues/79)。

数据遵守已归档 Hanzi Writer / Make Me a Hanzi、ARPHIC PUBLIC LICENSE 的来源限制，所有预览页面不得上传原始字体文件。
