# Phase II — 逐笔引导临摹：工程设计评审报告与实施放行

评审日期：2026-10-12。
范围：PRD docs/PHASE2_GUIDED_PRACTICE_PRD.md；架构 docs/PHASE2_GUIDED_PRACTICE_ARCHITECTURE.md。
已知实现基线：netplus/zitie main @ 2c4082ff66141aa5853dfd1c3dfa296810ed3523。
跟踪 Issue #137。评审方式：源码/数据契约核查、W3C/WebKit/MDN 规范依据、对 Hanzi Writer 已有 quiz/matcher 的结构比较，以及静态失败情形推演。**尚未实施、未跑临摹实机 QA，不能声称已完成用户体验或教学专家审定。**

## 1. 评审结论

**工程方案：有条件通过（GO to P2.1 staged implementation；NO-GO to mandatory automatic grading or App-store distribution）。**

允许开始 P2.1 的独立代码竖切片——含点击进入沉浸页、触屏真实墨迹、当前笔索引、手动确认后进入下一笔、撤销/重练、数据结构与回归验证。不得绕开小阶段门槛直接声称“正式教学评分”“全设备低延迟 Apple Pencil”或“已可发布原生 App”。生产默认入口的行为变化仍需真实 QA 及产品视觉验收后才放行。

此结论是**工程设计评审**，不替代实际代码审查/实机手写/书法教学专家审核；P2.2/P2.3 另设正式 Go/No-go。

### 1.1 审查结论清单

| ID / 等级 | 核查结果与风险 | 决策 | 阻断门槛 |
| --- | --- | --- | --- |
| R01 P0 | 原 StrokePlayer.setGlyph 重置整棵 SVG；手写 trace 放进去会随换字消失 | PracticeStage 与 source SVG 独立创建；source adapter read-only | 不允许修改第一阶段 player/source |
| R02 P0 | 源有 g transform translate(0 900) scale(1 -1)；简单 y=1024-y 将严重错位 | 用 referenceGroup.getScreenCTM().inverse()，CSS/DPR 改变重测 | 四角/水4笔/旋转黄金测试 |
| R03 P0 | 指针可取消、离开可视区、两指/掌托可抢事件 | 单 activePointerId、setPointerCapture、取消幂等、压制多点 | pointercancel 后已完成数绝对不增加 |
| R04 P0 | SVG source outlines 可核对 PDF，但 medians 是未批准的人体动作推演 | 初版“逐笔确认”而非强制专业判分；后续 matcher feature-gate | 未经标定不允许输出“书写正确” |
| R05 P0 | 合成笔压不是真实触控输入；0.5 有设备默认歧义 | 动画力值与用户 pressure 分 schema 归属；空/未知值标注 | 不做虚假压力展示 |
| R06 P0 | 绘画 path 自动补源墨会伪造用户轨迹 | 用户墨迹独立 Canvas，渲染只用用户实际点 | 真实轨迹与屏幕蓝墨匹配 |
| R07 P1 | 窄屏临摹区/底部操作键可能超屏，被浏览器手势打断 | 沉浸式 fixed layer、safe-area、100dvh + 纵横屏测试；仅画布 touch-action none | 390×844/820×1180/Pad 横屏均可用 |
| R08 P1 | 笔迹帧抖动、点丢失、超高 DPI 消耗 | coalesced 可用则读、rAF 绘制、保留 raw、可降级 | 设备实测 p95 输入延迟、DPR/掉帧证据 |
| R09 P1 | 本地习字数据可能含儿童书写轨迹 | 默认不上传；IndexedDB 本地，明确删除/保存错误处理 | 无未经同意的远程传输 |
| R10 P1 | PWA / WebView 并不等同所有 App Store / Pad 原生能力 | 容器与输入/渲染分离，先设备 spike 后打包决策 | App 渠道另设测试与审核 |
| R11 P1 | 打包 Hanzi Writer quiz 可能替换 PDF 同源轮廓，动画可视层不同步 | 研究其 matcher 与提示机制；不直接替换 PDF-backed 动画 | Source hash / 许可完整 |
| R12 P1 | 手指/笔形难以严苛匹配折钩、复笔和重叠路径 | M1 先人工逐笔确认；M2 特性实验不推主站 | 真实教学轨迹 + 专家复核 |

**阻断性设计缺陷：目前未发现**。这并不意味着实现一定无缺陷；R02/R03/R04/R06 为首批代码必须验证的优先级最高的风险。

## 2. 关键 ADR 决议（Implementation-Ready）

**ADR-01 独立 PracticeStage：接受。** 新 SVG 参考层 + Canvas 真实墨迹层是硬边界；原 StrokePlayer 仅 pause()/restore，原播放器的 SVG DOM、timer、pressure-style.js 不重构。

**ADR-02 Pointer Events：接受。** 事件流为 down→move(coalesced/fallback)→up/cancel；只允许一个 active pointer；touch-action none 仅书写表面；native 高保真输入以后按 adapter 替换。不能把 getCoalescedEvents 当成普遍总是有值。

**ADR-03 来源坐标：接受。** 存 source units，而非 CSS/device px；getScreenCTM.inverse() 与重绘时 forward transform 成对测试；明确原 g 的 900 翻转，绝不假定 1024 翻转。

**ADR-04 P2.1 逐笔学习逻辑：接受，保守实现。** 当前笔提示 + 用户一笔连续采集 + 提笔后显示本人真实轨迹 + 手动“确认这一笔”后才推进。避免不可证明的匹配阈值将合理不同写法当成错误；此模式仍是严格的先后顺序引导，非“自由涂鸦”。

**ADR-05 Hanzi Writer：分拆考虑。** 经过官方文档及 src/Quiz.ts、src/strokeMatches.ts 研究，上游有完整 quiz 和 shape matcher，且源码 MIT；但整套 quiz 的自动隐藏用户描线/源字填充行为不符合“保留本人真实墨迹”要求。P2.1 不引入其渲染器；P2.2 将上游 matcher 作为对照策略，保持版权声明与 Arphic 数据许可。

**ADR-06 数据：接受本地优先。** 标准 Session/Stroke/Point JSON 带版本、glyph.source_sha256、PDF publication SHA；样点不经平滑改写，若存储失败提供可恢复内存状态，不上传。保留删除控制。

**ADR-07 跨端：Web-first，容器待定。** 先 Safari+iPad Pencil 与 Android Pad Chrome/WebView spike，再决定 PWA 还是原生 WebView 容器；未来 Flutter UI 重做不得改变 source adapter、笔顺和序列化 golden fixture。

## 3. 未完成的验证及责任归属

| 类别 | 当前证据 | 缺失 | 解除条件 |
| --- | --- | --- | --- |
| 现有源与动画 | main 中已实现并经 A3.9 上线核验的 201/1045、A3.6/7/9 | practice 代码尚未存在 | 分阶段 CI 及 source hash gate |
| 平台 API | W3C Pointer Events、WebKit Safari Pointer 支持、SVG CTM 规范 | iPad 不同 Pencil 设备的笔压/掌托体验 | 真实 iPad 手写、取消与延迟日志 |
| Android | Chrome/Pointer Events 标准能力 | Android Pad OEM/Android WebView 设备差异 | 实际 Pad stylus + 手机上机 QA |
| 教学评价 | 正式 PDF 源笔顺/源 SVG；Hanzi Writer quiz 研究 | 临摹动作数据非师资审核 | 专家与经许可样本的 A/B 评审 |
| 性能 | 设计里定义 60Hz/50ms p95 目标 | 当前没有 measured trace renderer | 真机录屏/采样帧间隔测试 |
| 产品视觉 | 静态交互框架 | 用户还未看新版沉浸 UI 与笔迹实际效果 | M1 页面截图 + 用户体验验收 |
| 发布渠道 | 已有 Pages Web 部署能力 | Apple/Google 商店、WebView 原生笔压验证 | P2.3 专项工程及渠道审核 |

“本评审通过”仅允许**启动工程实现与受控试验**。正式部署和主流平台商店交付不得跳过以上实测。

## 4. 实施阶段与每一步交付门槛

### P2.1a — 只读临摹场景 / 无触控输入

新增 PracticeStage，用户点击当前字书写区进入/退出；单独复刻同源 SVG 轮廓与网格（不是绘制新字体）；当前笔灰红高亮，能够切换指定 glyph 与第 n 笔；沉浸式横竖屏 CSS，焦点与 Esc/返回处理。**验收：** 原 A3 不动、禁用未来笔越序入口、截图及 390px/iPad 大屏空间占比、严格 SVG hash 一致。

### P2.1b — 用户真实笔迹引擎（无自动评分）

接入 PointerInputAdapter、TraceSession、TraceRenderer；仅一个活动指针，真实 coalesced/fallback 样点和 time/pressure provenance，rAF 绘制；取消/翻转/resize/离屏/高 DPR；保留已写蓝墨，不以源轮廓补画。**验收：** Node + Chromium 实际事件流 + 指针离区、取消和 DPR/CTM golden test；iPad/Android 真实触控初验。

### P2.1c — 逐笔状态机、撤销与恢复

手动确认第 n 笔推进 n+1，M1 非评分标签、撤销/重练、完成4笔“水”、扩到201/1045；本地 session（IndexedDB schema 版本、来源锁定，失败回退/删除），源名受限项目保持序数名称。**验收：** 严格不越序、真实点不丢、退出恢复、不上传输入、所有历史动画/Book QA 不退步。

### P2.1d — 正式 MVP 验收与受控 Web 部署

视觉 QA、输入延迟日志、安全区、pad portrait/landscape、iPad Pencil 与 Android Pad 手写真实 QA；正式 Chromium + Book 按精确 SHA 全量，合入后 Pages 配置/上传/真正 Deploy 并核对提交 SHA。**未满足实机/用户可用性门槛时只上研究路径，不替换现有正式入口。**

### P2.2 — 自动匹配/教学反馈 A/B（独立）

参照 Hanzi Writer Quiz/matcher 机制，与自研顺序感知/DTW/Fréchet 策略在水、一、口、月、龠等错笔与人工真迹上比较误接收/误拒绝率；教师审核通过才启用自动晋级。“near/ambiguous/far”与置信来源可解释，人工继续是始终保留的安全回退。

### P2.3 — 可安装/可发布 App 的平台工程

PWA/service worker 离线预加载策略与版本锁定；在 iPadOS/iOS、Android Pad/手机上测试 WebView/Capacitor 是否可达同等笔迹性能，再决议原生渲染器/Flutter；打包、签名、隐私声明、许可合规、Apple/Google 发布审核分别建里程碑。不能以 P2.1 的 web CI 代表 App 渠道通过。

## 5. 对下一轮开发的明确约束

- 一轮 PR 只落一个可回归的独立阶段；功能默认 gate OFF，等浏览器验证才在正式 A3 页面提供“开始临摹”入口。
- GitHub 按 docs PR / code PR 分离：本 PR **仅 docs**，必须让用户可以先审阅方案；后续写代码需单独 branch/PR。
- CI 不能因为新测试长而绕过：原 A1/Book/全201数据、A3.6前缘/2090帧/真实页面压力，必须继续运行；无许可证争议、不引入在线依赖。
- 源几何与原播放器稳定性优先级高于临摹算法精细程度；不以“手感像真笔”为理由丢弃未经验证的自动生成数据事实边界。
- 人体动作尚未经师资审定，界面应称“逐笔引导临摹 / 参考笔画”，不能写“百分百正确笔顺轨迹”。

## 6. 用户需要审阅的三项产品默认值

这一轮为了可以实施，提出以下**默认**，不是未经确认的永久政策：

1. 临摹输入完成当前笔后先让用户“确认这一笔”再进入下一笔（不强制基于未验证 median 自动打分），之后才考虑可选自动进阶；
2. 学习者真实笔迹用蓝墨色，与灰/淡红参考字明确区分；每笔用户轨迹完整保留；
3. 练习结果先仅本机保存，默认不上传，不做公开排名/专业书法评分。

若评审者认可这些默认项，P2.1a 的实施没有尚需澄清的关键产品依赖。若其中一项更改，应先修改本设计与验收标准，再让代码 PR 开始。

## 7. 评审签字/推进记录模板

- 工程设计审查：**有条件通过**，允许启动 P2.1a/P2.1b 独立工程试验；
- 产品/交互验收：**待用户审阅**；
- 教学评判模型：**未通过 / 暂不纳入 P2.1**；
- Apple Pencil / Android Pad 真实硬件兼容：**待实机测试**；
- 正式代码开发：**尚未启动**；在本设计评审被用户接受之后另建功能 PR。

本文件是“正式设计评审结果”，不是由 CI 生成的临摹功能上线凭据。
