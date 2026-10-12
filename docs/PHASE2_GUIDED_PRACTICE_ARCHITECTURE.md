# Phase II / P2.1 — 逐笔临摹技术架构与跨平台约束

状态：技术设计评审候选，**本 PR 仅设计，不包含功能代码**。Issue #137。
代码事实基线：netplus/zitie main @ 2c4082ff66141aa5853dfd1c3dfa296810ed3523；演示页 animation/book.html?id=77。

## 1. 代码事实与不可变边界

正式播放器 A3 的只读全书包由 scripts/build_a3_animation.py 从已发布 PDF 的相同输入生成：

- window.ZITIE_BOOK_PACK：201 glyph、1045 个 stroke；逐笔数据有 1-based index、原始 outline SVG 路径、median 采样点、可公开 name/name_status；glyph 有 main_id、order_code、source_sha256、trajectory_review_status 等。
- animation/book-ui.js：使用 ZitieTimeline.validateGlyph / StrokePlayer({frontGuard:true}) 并在 selectGlyph 时设置 player；按钮、进度与合成笔压反馈都在原 UI，未提供“真实触屏墨迹”状态机。
- animation/player.js：每次 setGlyph() 清空自身 svg 子节点，生成网格和字形图层，并用 g transform="translate(0 900) scale(1 -1)" 从源书写坐标渲染。注意：这不是简单的 1024-y 坐标变换。
- animation/ink-front-guard.js：限制**源轮廓动画**提前显墨；它不是手写笔迹自动捕捉或笔画评分工具；不得滥用于用户输入路径。
- A3.7 pressure-style.js 的 simulated 是**合成动画力度**，而 PointerEvent.pressure 是设备事件输入，两者 provenance 与语义必须完全隔离。

**不修改：** PDF v0.5.1 299页、deliverables/manifest.json、B01–B21、原 licenced vectors/overrides、201/1045 数据、animation/player.js 的已验证 source-arc 前缘、历史实验和冻结的硬笔。Practice 模块视字帖为只读数据，不给任何 glyph/stroke 写回轨迹。

## 2. 候选方案评估与 ADR

| 方案 | 优点 | 限制与风险 | 决议 |
| --- | --- | --- | --- |
| 在现有 StrokePlayer 上直接监听并叠笔迹 | 代码表面少 | setGlyph 会替换 SVG DOM；动画红墨 reveal 与真实人笔迹同层竞争；手写 input 数据难以独立测试 | **否** |
| 直接接 Hanzi Writer 整套 quiz()/renderer | 有成熟笔顺练习、提示、matcher | 默认画完会把用户路径隐藏/切换标准笔画；需自定义原 PDF 同源数据 loader、采样时间/笔压和 UI；集成后对 source/渲染一致性压力大 | **研究性 A/B，不直接取代** |
| 单独 PracticeStage：只读 outline SVG + 真实 Canvas ink + 状态机 + Matcher 策略接口 | 现有动画完全独立、保留真实输入原始数据、易做移动 Web / WebView，单元测试能无 DOM 执行 | 新增输入/坐标/撤销模块，要建立严格浏览器与实机测试 | **采用** |

上游参考：Hanzi Writer 代码 MIT，数据按 Arphic Public License 区分许可。其 src/strokeMatches.ts 使用起收笔距离、方向余弦、整体长度、平均距离、经旋转归一化的 Fréchet 曲线距离，以及和后续笔画的竞争识别；Quiz.ts 提供错误次数提示/回调和笔画序号。可参考并在独立 A/B 实验验证这些策略，但**不能不经本项目数据校验就照搬默认阈值或宣称教师认证**。引用时保留 MIT 声明；原矢量数据继续按 ARPHICPL 与原 NOTICE 处理。

## 3. 模块边界

~~~mermaid
flowchart TD
  A["原 A3 Book UI / StrokePlayer (只读动画)"] --> B["PracticeBridge: 点击进入/退出恢复状态"]
  C["PDF 同源的 ZITIE_BOOK_PACK (只读)"] --> D["SourceAdapter: 元数据/版本/笔顺核查"]
  B --> E["PracticeController: 笔画状态机"]
  D --> E
  F["PointerInputAdapter: touch/pen/mouse"] --> G["TraceSession: 原始点/单活动指针"]
  G --> E
  D --> H["ReferenceStage: SVG 原轮廓/当前笔提示"]
  E --> H
  G --> I["TraceRenderer: Canvas 实时本人墨迹"]
  E --> I
  E --> J["MatcherPolicy: P2.1 人工确认/P2.2 三态匹配"]
  D --> J
  E --> K["StorageAdapter: 本地版本化 IndexedDB"]
  L["PracticeView: Modal/可访问按钮/安全区"] <--> E
  M["PWA / WKWebView / Android WebView 容器"] --> F
  M --> L
~~~

拟新增（具体文件名可在实施 PR 确定；初始保持项目既有 UMD/CommonJS 双端测试风格，无构建器与运行时 CDN）：

- animation/practice/source-adapter.js：为当前 glyph 建只读快照，核对 schema、glyph/source SHA、name_status 与 stroke.index，禁止源字段修改；
- animation/practice/controller.js：纯状态机（PRACTICE_READY / DRAWING / STROKE_REVIEW / COMPLETE / INTERRUPTED），命令化 enter/start/append/end/retry/accept/undo/exit；
- animation/practice/pointer-input.js：独立输入 adapter，规范化时序/笔压/指针捕获/取消，不混入 SVG DOM 和教学模型；
- animation/practice/reference-svg.js：原 outline 绘制字格及当前笔提示，直接复用原包的字符串，而不是系统字库，和原播放器 SVG 互不共享 DOM；
- animation/practice/trace-canvas.js：只画用户采集点；画笔渲染与原始采样分离；
- animation/practice/matcher.js：可替换判断策略，P2.1 为无评分/最低有效行程 + 用户确认，P2.2 才评估有证据的自动匹配；
- animation/practice/storage.js：IndexedDB SessionRepository，schema 升级、失败回退、清除/导出；
- animation/practice/practice-ui.js / practice-bridge.js：modal、焦点、按钮、临摹模式激活/退出、与原 player pause() / getState() 集成。

隔离原则：BookUI 只负责调用 PracticeBridge；PracticeController 和 Matcher 在 Node 环境可纯计算测试，TraceRenderer 不读取网络、PDF 或数据库；Storage 不能直接操作 SVG；Native/App 外壳不得私自变更 stroke order。

## 4. SVG 坐标、触控坐标与缩放：P0 高风险

现有源 median 原点遵循 Hanzi Writer/Make Me a Hanzi 的源坐标系，不是页面左上坐标。正式播放器在 SVG viewBox 0 0 1024 1024 中使用：

~~~xml
<g transform="translate(0 900) scale(1 -1)">
  <!-- source outline / median -->
</g>
~~~

所以源 (x,y) 在 root SVG 中对应 (x, 900-y)，不是 (x,1024-y)；某些有效源 y 可能小于 0，禁止以屏幕像素坐标直接与 median 比较。

PracticeStage 独立创建**相同坐标变换**的 SVG g（不可复用会在换字时 replaceChildren 的播放 SVG），事件转换使用：

~~~js
// 指针在 viewport 的 clientX/clientY -> 同源 1024-unit median 逻辑坐标。
const pt = new DOMPoint(ev.clientX, ev.clientY);
const modelPoint = pt.matrixTransform(referenceGroup.getScreenCTM().inverse());
// x/y 是源模型位置。校验 finite, strokeId, stage bounds，绘制时按相同 group 正向变换。
~~~

Canvas 与 SVG 精确叠放在同一个 1:1 square box；每次 ResizeObserver / orientationchange 重新计算真实 DOM 布局、CSS-to-device 尺寸和 DPR 变换，并重绘由**原始逻辑坐标**保存的历史轨迹。对 Canvas 不能用 css px 当 device px；canvas.width/height = round(client size × capped DPR)；实际显示尺寸由 CSS 控制；绘画的正向矩阵需与 referenceGroup.getScreenCTM() 同构。禁止因横竖屏或切换设备而修改已存点；需有四角坐标与“水”的起/落笔转换 golden tests。

## 5. Pointer Events 事件与数据生命周期

每根笔划仅有一个 activePointerId：

1. pointerdown：判定触控设备、是否右键/手掌、当前状态、落点、边界；只在 READY 状态锁定活动 pointer；在已挂载且可接收事件的绘图区 setPointerCapture(pointerId)；
2. pointermove：优先 getCoalescedEvents（feature detected/HTTPS；空数组 fallback 当前事件），使用单调 timestamp 去重，同一指针按时间排序追加有效点；立即标记 dirty 并 requestAnimationFrame 绘制；不在回调中做全笔 DTW 或 IndexedDB I/O；
3. pointerup：追加最后真实点 → release capture → session.completeDraft；先展示用户原墨迹，再触发当前笔的宽容验收，P2.1 等用户确认后推进；
4. pointercancel / lostpointercapture / visibilitychange / orientationchange：按幂等 cancel() 中止本次 draft，清空当前笔临时墨迹（或标记 aborted 供用户重写），已确认笔不变；
5. 多点：已锁定一个 pointerId 后忽略其他 pointer；若检测笔优先模式，忽略 touch 的掌托疑似输入；不能承诺完全浏览器级防掌托；
6. getPredictedEvents/pointerrawupdate 仅作为延迟优化实验，**P2.1 不使用**（预测样点不能写入真实数据或判分）。不能依赖 Apple Pencil hover/bearing、压力或 tilt 每个设备都有。

CSS touch-action: none **仅**加到 practice 绘图区，旁边操作条仍允许辅助滚动/浏览器系统操作；必要时支持可访问的系统放大与“书写时临时禁止手势”的清楚提示。其他页面绝不全局禁用触控滚动。

每个输入点建议模型（schema v1）：

~~~json
{
  "x": 512.8,
  "y": 481.4,
  "tMs": 325.4,
  "pressure": null,
  "tiltX": null,
  "tiltY": null,
  "pointerType": "touch"
}
~~~

- x/y 使用上述同源逻辑坐标；tMs 是从当前笔 pointerdown 起的**单调相对时间**；压力、倾角不可检测时为 null，不要把 mouse 的默认 0.5 伪装实测压力；
- RawTrace 追加保存未经过滤的样点。平滑/圆角/可变线宽只作用于渲染视图，不能悄悄重写原始样点；
- 完成笔画: strokeIndex、source_sha256、samples、durationMs、deviceType、status(traced/assisted/skipped)及辅助标志；session 包括 schemaVersion、glyphId、publicationHash、sourceRevision、beganAt、updatedAt、acceptedStrokes、currentIndex，避免记住设备可识别信息；
- 保存版本不可恢复时明确提示/拒绝当作旧版字帖继续评分；仅本地 IndexedDB，能暂停/删除，处理 quota/隐私模式 I/O failure。

## 6. 真实墨迹渲染和性能契约

渲染层不使用 A3.6 的原轮廓+遮罩自动填充，因为那会替学习者“补写”而不是呈现真实轨迹。

- 静态源 SVG：仅在换字/换笔/提示变化重建局部 path 的颜色/opacity；它不会因为 pointermove 而重算原有 1045 笔轮廓。
- Canvas 2D 用户轨迹：用户当前 raw sample 驱动单独 stroke，线帽/拐角圆滑，渲染插值不覆盖 raw 数据；极短笔画可见起落点，小笔速变化不会导致断线。
- 在每次 rAF 的限定预算内，优先画已经确认的笔迹+当前增量；undo/resize/DPR 变化可依靠原始样点确定性重建；不允许清空历史 canvas 后又只画当前段造成“墨迹消失”。
- 首版固定接触宽度（能分辨蓝墨与源淡红）。只有确认移动端实际压力通道可靠后，可在独立选项启用 pressure-aware 线宽；**不得引用 A3.7 动画合成压力曲线控制用户墨迹**。
- 建议性能验收（工程目标而非已达成）：60Hz 平板笔迹帧间隔目标 ≤16.7ms；笔迹 input→可见 p95 目标 ≤50ms；输入监听处理 p95 ≤4ms；旋转/Resize 后坐标定位误差目标 ≤1 CSS pixel。记录长笔画、DPR=3、连续 17 笔与后台恢复的 worst case，不用截图通过代替时序数据。真实设备达不到时记录降级而不是假报数值。

## 7. MatcherPolicy：研究路线与教学门槛

**P2.1 只保证“逐笔顺序 + 本人真实笔迹 + 用户确认”，绝不自动产出严格正确/错误分数。** 宽容的空笔/零位移/异常边界判定用于防误操作。任何用户自己确认的笔仍存为 userConfirmed；“有帮助跳过”另记 assisted/skipped。这样既做到逐笔引导，又不会把未经校准的 median 误认为唯一正确笔法。

**P2.2 才是 Matcher A/B：**

- 归一化点列并按弧长重采样（去除过密噪声，不修改 RawTrace）；按当前 strokeIndex 读取原 median；
- 特征：起笔与收笔距离、方向一致性、路径长度比、对源中线的有序/无序距离、动态时间规整 DTW 或离散 Fréchet 距离、回头/折钩局部转角；再比较“更像后续哪个笔画”，避免乱画也通过；
- 输出 {match: near | ambiguous | far, reasons[], metrics, matcherVersion, referenceQuality}，不直接输出“教师评分”。near 可以自动晋级；ambiguous 保留人工继续选择；far 建议重试。阈值按不同屏幕/触控粗细、不同笔画类型和经校准的离线真迹统计拟合，不能直接复制 Hanzi Writer 的全局数值；
- 水（横撇、竖钩、撇、捺等按当前已审顺序）、口的折、月的横折钩、龠17笔交叉是典型高风险样例：median 有折回、自交/相邻候选时需要有序对齐，不能只计算最近点距离；
- 最终“正确书写”产品措辞需明确书法教师/教研复核与真实学习者轨迹数据集授权。工程端测试通过不代表教学判分通过。

上游 Hanzi Writer matcher 是**可复用算法参考/独立对照基准**，不是这里唯一合法的评判权威。使用任何源代码需保留 MIT copyright/license；使用字符轮廓继续保持现有 Arphic 许可和 NOTICE。

## 8. App 可移植边界

**现在优先 Web 平台的 Pointer Events + SVG/Canvas 2D + 独立 Model/Controller；不要为尚未选定的 Flutter 或原生框架重写已投入验证的 A3。**

- Web / PWA：现有 GitHub Pages HTTPS 静态资产 + service worker 缓存策略（独立评审）；可使用主屏幕安装和 standalone 布局，并不自动意味着 Apple/Google 应用商店发布。
- iPadOS/iOS：优先 Safari/iPad Web 真实 Apple Pencil 测试，再评估 WKWebView/Capacitor 分发 App Store；不能假定 WebKit 能提供系统级掌托过滤、低延迟原生墨迹路径或完整 pressure/tilt。
- Android：优先 Chrome + 触控笔实际 QA，之后 Android WebView/Capacitor 包装评估；注意 OEM 内核/笔型不同，不可把 Chrome 测试等同原生所有设备。
- 如果确需 Flutter 原生绘制层，将 UI/Input/Render 迁移到 Flutter，领域层的 schema、source adapter 测试向量、state commands 和 matcher 策略保持语言无关的版本化 contract（可 TypeScript 实现 + 对照 JSON golden fixtures）。不要让 Flutter UI 直接解析字帖 PDF 或自行重排笔顺。
- 产品架构决定：**Web-first + 可替换 Native Host/Render Adapter**；选择最终 App 容器要以 P2.3 的 iPad/Android 实机触控延迟、压力可用性及商店政策验收为依据，不提前承诺一套浏览器事件在所有设备获得同样硬件指标。

## 9. QA/CI 接入与上线约束

新增独立 P2 suite（不替换现有 gate）：

1. Node：source adapter / state transitions / monotone raw timestamps / no empty or double-committed strokes / undo、redo 与 cancel 幂等 / 201×1045 数据 integrity；
2. 真 Chromium：真实 pointerdown/move/up、两指竞争、pointercancel、离区 pointer capture、页面隐藏/旋转，所画蓝色用户墨迹与输入坐标位置吻合；无自填源轮廓；操作、focus、模式返回；
3. 尺寸：390×667、390×844、820×1180、1180×820、1366×768/1024、1920×1080；DPR1/2/3，包含动态浏览器工具栏、安全区/横竖屏；
4. 原完整 A3.6 1045笔/2090 帧、A3.7 同墨、A3.8/A3.9 布局和 Book 的299页、受限细笔名/拼音、PDF哈希/manifest 都持续通过；
5. 实机：Safari+iPad Apple Pencil、Android Pad Chrome/WebView 手写笔、iPhone 手指、Android 手机手指，不以 Chrome synthetic events 代替低延迟、压力和掌托判定；
6. 功能 PR 精确 HEAD 双 CI pass、main 合并 SHA、同 SHA Pages Configure+Upload+实际 Deploy 都成功，才称 Web 上线；原生上架单独按商店流程验收。

## 10. 核验依据

- 本项目：docs/A3_PDF_BRUSH_ANIMATION.md；animation/player.js（SVG translate(0 900) scale(1 -1)）；animation/book-ui.js；animation/timeline.js；docs/A36_INK_FRONT_AUDIT.md；docs/A39_COMPACT_HANDWRITING_VIEWPORT.md。
- W3C Pointer Events: https://www.w3.org/TR/pointerevents/
- MDN touch-action: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/touch-action
- MDN coalesced events: https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent/getCoalescedEvents
- MDN SVG inverse coordinate mapping: https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/Scripting
- MDN IndexedDB: https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API/Using_IndexedDB
- WebKit Pointer Events: https://webkit.org/blog/9674/new-webkit-features-in-safari-13/
- WebKit PWA installing: https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/
- Hanzi Writer quiz API: https://hanziwriter.org/docs.html
- Hanzi Writer MIT source and Arphic artwork license: https://hanziwriter.org/license.html
- Hanzi Writer matcher code: https://github.com/chanind/hanzi-writer/blob/83a762374e2344f2fb8cceca4a2ac5dfeca386f5/src/strokeMatches.ts
