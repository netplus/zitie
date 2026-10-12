# P2.1a — 沉浸式临摹准备界面（只读参考）

跟踪 Issue #139，设计基线为已合入的 Phase II PR #138。

## 本期范围

点击正式 201 字播放器的田字格，或使用可键盘访问的「临摹」按钮，进入独立的占屏参考区。平板横屏显示大田字格与右侧参考控制栏，平板竖屏及手机上下布局。只读 SVG 的每笔轮廓和 median 均直接来自正式 PDF 同源数据，使用原坐标变换 translate(0 900) scale(1 -1)；不生成、修改或重新标定任何字形。源起收笔位置属于未经教师审核的工程参考。

上一笔参考、下一笔参考只改变高亮的范字笔画，**不代表学习者已经完成笔画**。本期不收集指针事件、没有实时手写墨迹、不会出评分或上传学习者数据。P2.1b 才增加手指/笔的真实点采集与墨迹；P2.1c 才加入逐笔确认、撤销和本地存储。

## 代码边界

- animation/practice/reference-stage.js：独立 SVG + 只读字形适配器。
- animation/practice/practice-bridge.js：点击进入、键盘、模态焦点、播放器保存/恢复。
- animation/practice/practice.css：沉浸层与平板/手机布局。
- animation/book.html：可访问入口及独立的模态 DOM。
- animation/book-ui.js：模态打开时只屏蔽旧页面的播放快捷键，不改变 StrokePlayer。
- animation/tests/p21a-reference.test.cjs：全 201 字/1045笔只读一致性，细笔名受限保护。
- animation/tests/p21a-immersive-viewport-smoke.html：真实 Chromium 源轮廓对比、键盘、状态恢复、不同屏幕。
- .github/workflows/animation-checks.yml 与 animation-pages.yml：追加 CI/发布资产，不减少历史回归检查。

## 必须通过的质量门槛

1. 完整保留发布的 v0.5.1 299 页 PDF、manifest、B01–B21、源 SVG、许可证和全部原动画算法；不修改 player.js / ink-front-guard.js / motion.js。
2. 原 A3.6 1045笔/2090帧、A3.7 双笔压、A3.8/A3.9 窄屏布局及 Book 全书完整性检查继续执行。
3. 实际 Chrome 检查水字四笔路径一致、复杂龠17笔不缺、受限名称只显示序数、可通过鼠标和键盘开启/关闭、modal 不中断或破坏原 A3 状态。
4. 测试 1366×768、1180×820 平板横屏、820×1180 平板竖屏、390×844 与 390×667 手机；字格显著放大、保持 1:1、无横向溢出。
5. 最终 PR HEAD 的 A1/Chromium、Book 检查均成功后才合入；同一 main SHA 对应的 Pages 配置/上传/实际 Deploy 通过后才算 Web 发布。

工程界限：本期只完成临摹场景与笔顺参考，不得将它描述为已经可用于真实触屏书写或自动评判。
