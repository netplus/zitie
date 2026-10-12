# P2.1b — 真实触屏/触控笔笔迹采样与蓝墨 Canvas 渲染

状态：工程候选。经用户确认的 Phase II 设计 PR #138，P2.1a 已合并部署；本阶段由 Issue #141 跟踪。

## 用户可见行为

- 点击正式字帖页面的田字格，进入此前 P2.1a 的沉浸式逐笔参考区；在参考层上新增透明的 Canvas 书写表面。
- 使用真实手指、支持 Pointer Events 的触控笔或桌面鼠标落笔，用户真实走过的轨迹逐点以蓝墨呈现，抬笔后仍保留当前**草稿**。不磁吸参考中心线、不触发原 PDF SVG 轮廓的自动填充。
- 「重写本笔」清除当前临时草稿；“上一笔参考/下一笔参考”仍只是观察参考次序，切换会清空未确认的笔迹；不会把任何一次书写算作完成的笔顺。
- 退出/刷新会清除本次草稿。**本阶段没有逐笔确认、撤销历史、多笔提交、IndexedDB、本地持久化或云同步**，这些是已批准的 P2.1c 范围；已在界面明确告知。
- 默认蓝墨笔迹固定屏幕观感线宽，与 A3.7 的“模拟笔压版”完全独立。Touch 或 Mouse 的通用 0.5 不呈现成实测压力；Pen 的浏览器上报值标记为 device-reported-unverified，而不是权威的物理笔压。

## 代码与输入数据契约

| 模块 | 职责 | 保护约束 |
| --- | --- | --- |
| animation/practice/trace-session.js | 每笔单活动指针、单调相对时间、真实原始点、草稿/取消/重写状态 | Node 可测试；无 DOM/网络/存储/评分；点对象冻结 |
| animation/practice/pointer-input.js | Pointer Events + 可选 getCoalescedEvents/当前事件兜底、setPointerCapture、window fallback、pointercancel/丢失捕获/后台/旋转/resize 处理 | 第二触点不得混入；只在 canvas 上 touch-action:none |
| animation/practice/trace-canvas.js | 源坐标样点以独立透明 Canvas 画蓝色实笔迹；rAF 合批、增量绘画、ResizeObserver 后重绘、设备 DPR 分辨率 | 没有任何源 outline/刷子算法自动填涂 |
| animation/practice/practice-bridge.js | 在独立 SVG 上叠 Canvas；维持原 A3 播放状态、模式和焦点恢复；把临时 trace 生命周期绑定沉浸层 | 不改变原 StrokePlayer、A3.6 显墨前缘、规范笔顺或旧 Pages 资源 |

模型坐标继续采用正式字帖中被验证的 g(transform=translate(0 900) scale(1 -1))：clientX/Y → referenceGroup.getScreenCTM().inverse() → 0..1024 × -124..900 源单位；**不是** 1024-y。RawSample: {x,y,tMs,pressure:null|number,tiltX:null|number,tiltY:null|number,pointerType,pressureSource}。只有真实笔型数据以“设备报告、未经认证”保存；触点超过源坐标可视范围时有界截断，避免逸出无限轨迹。绘制时使用参考 SVG 的正向 CTM 对齐 Canvas 设备像素，保存原始逻辑坐标，不修改原始采样以适应屏幕缩放。

输入生命周期：DOWN 锁定 activePointerId → MOVE （使用 coalesced 如可用，合并当前事件并去重）→ UP 留下草稿；CANCEL/LOST CAPTURE/ORIENTATION/RESIZE/HIDDEN 放弃未完成笔，已完成草稿在调整 DPI、手机竖屏等时以原始点重绘，绝不变成“已确认笔画”。特意不使用 predicted events，不保存预测轨迹。

### 需谨慎阅读的边界

- CSS touch-action:none 仅施于 #practiceInk；其他页面正常滚动。使用 stylus 时遵循 first active pointer，浏览器/系统掌托识别仍需 Pad 实机测定。
- “合成力度曲线”属于原动画提示，只有动画播放器使用；当前真实练习轨迹不由模拟压力决定线宽或位置。
- 设计目标为 60Hz 16.7ms/frame、input→paint p95 ≤50ms，**尚无真实 Apple Pencil/Android Pad 物理延迟量测**。真实 CDP 是受信任的 Chromium 触摸事件测试，但不证明设备硬件延迟、原生笔压/倾角可用性。
- 浏览器真实原生接触验证采用 Chrome DevTools Protocol Input.dispatchTouchEvent，而独立的窗口级合成 PointerEvent 回归用于大屏/Pad/手机屏幕和安全性边界；两者结果不能混为一谈。
- 发生浏览器后台挂起、WebView 生命周期中断等情况可能主动舍弃当前未完成笔，避免错误拼接；学习者需重试当前笔。P2.1c 会对已确认笔的存储/恢复单独定义。

## 验收和发布条件

1. Node 模型测试涵盖双指忽略、pressure/tilt provenance、0.5 假压力、相对单调时间、原始点不可变、取消幂等、maxPoints 限制、coalesced/fallback。
2. 真实 Chromium：源 SVG 逆变换后的起笔与收笔实际点、蓝色像素绘制（不补源轮廓）、DPR/resize 重新画出相同原轨迹，笔内 resize 中断不保存、pointercancel 不推进、重写清空、退出不存储。适配 1366×820、1180×820 Pad 横屏、820×1180 Pad 竖屏、390×844 与 390×667。
3. 真正 Chromium CDP Input.dispatchTouchEvent：浏览器确实捕获 touch 指针、触摸抬起后保留蓝墨、390×844 @ DPR2 重布局仍保持像素一致、touchCancel 放弃未完成笔；生成真实屏幕截图和 JSON 证据。
4. 所有既有 P2.1a、A3.6 201字/1045笔前缘 2090帧、A3.7 双笔压、A3.8/A3.9 布局、Book v0.5.1 299页完整 CI 必须全部通过，正式源、许可证、manifest、数据等字节保持原样。
5. 最终功能 PR HEAD A1 Chromium + Book 两 CI 都成功方可合并；同一合并 SHA 的 GitHub Pages Configure/Upload/**Deploy** 均完成才视为 Web 工程上线。真实 iPadOS/Android 设备硬件验收仍为后续必需门槛。

下一步 P2.1c：人工确认这一笔后按审定笔顺推进、按笔撤销、重练、结果对照与本地持久化；此阶段的原始点格式为其基础。
