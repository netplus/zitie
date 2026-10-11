# A3.8：书写过程中始终可见笔压风格与力度

反馈：[Issue #131](https://github.com/netplus/zitie/issues/131)。原 A3.7「笔压风格：稳定版 / 模拟笔压版」控件虽然已恢复，但位于 201 字播放器的字格、进度条和全部播放按钮**下方**。观察写字动画时，力度百分比与曲线常在屏幕以外，形成严重的布局可用性回退。

## 调整

在 animation/book.html 中，将唯一的一份 pressureBox 直接移至 writingStage 中，与原始 1024×1024 SVG 字格共同布局。**没有复制控件、没有创建新的笔压组件。**

- 宽屏（页面宽度 >1150px）：为了不明显缩小 535px 田字格，主播放器相对主部首目录增加空间；笔压侧栏宽 220px，在字格右侧。将模式按钮分成两列，模拟力度表、百分比和小曲线竖向叠加，所有信息和书写字格同屏。
- 较窄的笔记本及手机（≤1150px）：保留原字格宽度，笔压面板转到字格正上方，按钮与横向的力度曲线组成紧凑观察条，避免占据大量高度。滚动到字格中部时压力条仍在书写阶段内 sticky；390px 手机再次压缩间距和字号。
- 只修改面板的 DOM 位置、CSS 栅格、边距、响应式规则和两句解释性文本。保持按钮 ID/ARIA、StyleController、选中状态、合成力度曲线、线条与触点计算完全不变。
- 原 A3.6 source-arc 墨迹守卫以及 A3.5 运动研究、不经人工批准的硬笔模型都不修改，原 v0.5.1 PDF（299页）及其所有 201 个部首/1045笔原始 SVG/中心线/笔顺数据亦不修改。

## 质量门槛

1. Node: 笔压栏必须位于单个 handwriting stage、字格旁边；不能在全部播放按钮后面重复展示，按钮、压力曲线仅一份，脚本依赖不变。
2. 实际 Chromium: iframe 模拟 1410px 宽屏，力度栏完整位于画布右侧；滚动字格期间读数仍在视口内；1020px 笔记本面板在画布上方；390px 手机面板紧凑、字格可见、滚动时读数与曲线持续可用。每个尺寸均不水平溢出，状态/字号/力度切换不会让计时器或选字发生变化。
3. 原 A3.7 两种风格像素严格一致、A3.6 2090帧真实墨迹前缘回归、A3.5 动作 A/B 完整性与正式 Book PDF 字节核对全部继续执行，不降低门槛。
4. 仅在最终 PR HEAD 的 A1 Chrome 和 Book CI 都成功后合入，并在合并 SHA 对应的 GitHub Pages Configure、Upload、实际 Deploy 完成后称上线。真实页面截图存档于 A1 QA 产物。

该工作解决**面板在视口外**的问题，不代表合成的压力是实测物理笔压，也不会把它改为影响墨迹粗细的模型。

## 正式发布记录（2026-10-11，已上线）

- [功能 PR #132](https://github.com/netplus/zitie/pull/132) 已合入，首次把唯一笔压控制区移入书写舞台，桌面并排、窄屏前置并设置 sticky；[Issue #131](https://github.com/netplus/zitie/issues/131) 已关闭。
- 真正的 Chromium 布局数据随后发现 **1020px 笔记本宽度下画布只剩 302px**，虽然主播放器可用宽度约 614px。原因是改用 column 布局时继承了 `align-items:start`；[修复 PR #133](https://github.com/netplus/zitie/pull/133) 显式采用 `align-items:stretch` 并新增浏览器断言：1020px 时画布宽至少 490px，窄屏笔压条与画布宽度匹配。
- [最终合并提交 f4ae83e](https://github.com/netplus/zitie/commit/f4ae83e338cff68bc9460d3f0eacfaef919d949a) 已成为 `main`，对应的 [A1 / 真正 Chromium 检查 #38145041178](https://github.com/netplus/zitie/actions/runs/38145041178)、[Book 完整性 #38145041109](https://github.com/netplus/zitie/actions/runs/38145041109)、[GitHub Pages 发布 #38145041123](https://github.com/netplus/zitie/actions/runs/38145041123) 均为 `completed/success`。Pages 发布作业中的 Configure / Upload / **Deploy** 三步均为 `success`，不是仅上传构建文件。
- A3.8 真正浏览器布局门槛：1410px 宽屏并排，1020px 笔记本完整宽度，390px 手机上方紧凑布局，滚动期间力度读数仍可见；原始压力控制器唯一、曲线确实绘制、字形和进度状态不被重排改变。质量门槛保持 A3.7 两模式原墨迹同一性、A3.6 1045 笔 / 2090 帧防超前回归、正式 v0.5.1 299 页 PDF 完整性。
- [A1 截图与布局 QA 归档 artifact #11704825962](https://github.com/netplus/zitie/actions/runs/38145041178/artifacts/11704825962)；[正式 201 字毛笔播放器](https://netplus.github.io/zitie/animation/book.html?id=77)。

**证据边界：**上述是 CI 在 Chromium 中完成的可见性、响应式及墨迹回归验证，不等于所有设备、所有浏览器都已人工目测审定。模拟笔压仍是合成数据显示，不是传感器实测值；不影响原 PDF、来源 SVG、书写笔顺与已发布笔迹形状。
