# A1 浏览器在线预览

## 官方 GitHub Pages 预览已上线（2026-10-09）

[直接打开在线书写播放器](https://netplus.github.io/zitie/animation/) · [GitHub Pages 部署通过记录](https://github.com/netplus/zitie/actions/runs/37880818335)。该次工作流实际完成配置、资源上传和部署，非仅生成构建产物。后续 `main` 动画目录更新由 Actions 自动发布；站点仍属工程预览，轨迹教学复核未完成。

## 备用：第三方静态预览

[打开 main 上的 A1 动画](https://raw.githack.com/netplus/zitie/main/animation/index.html)

此地址由第三方 **raw.githack.com** 读取公开 GitHub 资源并以正确 HTML / JavaScript MIME 类型提供；首次打开 HTML 可能要求点击安全确认，缓存更新可能延迟几分钟。它不是 GitHub Pages 官方托管，也不保证永久可用。仓库真实运行文件为 [animation/index.html](../animation/index.html)，仅需同目录的 `samples.js`、`timeline.js`、`player.js`，无需在线 API、外部字体或 CDN。本阶段都是轨迹工程预览，**不是经教学审定的笔顺视频**。

## GitHub Pages 自动部署（当前已启用）

官方地址：`https://netplus.github.io/zitie/animation/`。仓库通过 `.github/workflows/animation-pages.yml` 打包经核验的 HTML/JS 和对应的原始 ARPHIC 许可文本；不上传正式 PDF、字体、规范全文或 manifest。部署源已配置为 GitHub Actions，后续动画更新合入 `main` 后触发自动部署。需要重试时可从 [发布工作流](https://github.com/netplus/zitie/actions/workflows/animation-pages.yml) 手动运行；是否真正上线应以部署步骤完成为准。

## 质量与授权边界

线上动画仍是 A1 实验成果，201个主部首虽然有完整的原版中心线数据，但其逐笔起收、转折和钩笔方向未获得新的教学级审核。不得使用 Pages 预览成功作为解除 fail-closed 限制的依据。其他 A1 工作进展见 [A1 技术设计](A1_ANIMATION.md) 及 [Issue #79](https://github.com/netplus/zitie/issues/79)。

数据遵守已归档 Hanzi Writer / Make Me a Hanzi、ARPHIC PUBLIC LICENSE 的来源限制，所有预览页面不得上传原始字体文件。
