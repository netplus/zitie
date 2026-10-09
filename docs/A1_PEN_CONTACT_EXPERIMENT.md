# A1.4 — 可变笔尖接触模型 A/B 实验实施与验收

创建日期：2026-10-09。关联 [A1.4 研究](A1_PEN_CONTACT_RESEARCH.md)、
[Issue #88](https://github.com/netplus/zitie/issues/88) 和实验 PR #90。

**状态：独立工程实验（未通过人工教学审定）。正式播放器仍使用 A1.2.3。**

## 实验入口与边界

- 本地：打开 `animation/experiments/pen-lab.html`（引用仓库相对 JS 文件，不需要网络和服务器）。
- GitHub Pages：仅在 PR #90 完成目标 HEAD CI、合入并确认部署后，独立访问
  `https://netplus.github.io/zitie/animation/experiments/pen-lab.html`；
  此路径不是正式教学播放器地址。不要将预期地址当成已部署。
- 左侧 **A：现有稳定遮罩**，复用未经修改的 `player.js`/ `brush-union.js`。
- 右侧 **B：实验性虚拟笔尖**，使用新 `pen-contact.js` 和 `pen-lab-engine.js`。
  六个字形（`一、口、水、月、火、龠`）共享完整 source `strokes/medians`、
  `timeline.js` 的笔顺/时间，以及倍率按钮。两侧不替换规范数据。
- 201项主部首中当前仍仅9项具有工程动画样本，A/B只验证其中6项，不能将实验结果
  外推为全部201项已可教学。

## 根因与工程模型

既有圆头 brush-union 以真实 SVG 矢量轮廓为界，且通过了520帧的像素不回退检查；
但它只知道从 `median` 的哪一点移动到下一点，没有实际**笔尖压强、
接触椭圆、转锋朝向、笔尖离纸**等状态。几何掩膜正确不代表手写动作自然。

实验将每笔拆为 *虚拟接触阶段*，但不在规范层把一笔拆成多个笔画：

1. 固定原始 `M(s)`（vendor median）和 `O`（原始填充轮廓），读取稳定时间模型的
   `s(t)`；不修正起点、方向、笔顺、折钩数量和最终矢量。
2. 用 `brush-union.makeProfile` 的 SVG 填充宽度探测，仅估计局部笔尖接触横截面。
   间距约5个源坐标单位产生候选接触印迹；每个印迹产生时的 `x/y/rx/ry/angle`
   和合成 `pressure` 预先固定。
3. 合成接触 `pressure(s)` 由起笔平滑增压、折处小幅调整和末端释放独立生成。
   **不使用** `pressure=1/speed`，不把模拟压强当作测得的写字力度。
4. 虚拟笔尖为可旋转椭圆，朝向由邻域切向拟合并限制相邻采样的角度变化；
   这是一种处理“折处立即90°翻转笔尖”的视觉策略，不是改变中心线本身。
5. 明确标注的实验动作点，仅用于 `口` 第2笔、`水` 第1笔、
   `月` 第2笔、`龠` 第14笔和其他六样本的候选接触变化。
   动作标签基于已审核的细笔名称及**原 median 点索引**，
   并标记 `source:engineering_heuristic_only`、`reviewed:false`。
   不能从角度大就推断钩，也不新增任何教学级来源。
6. 每一帧新增“此前已到达的印迹”，不会改变已沉积墨迹。B侧可见区域定义为

   \[
   I_B(t)=O\cap\bigcup_{k:d_k\le s(t)}E_k
   \]

   `E_k` 为到达时固定椭圆。SVG mask 自身不会把后续压力下降应用于已经绘制的
   印迹；因此可继续使用以前的逐像素单调性审计。
7. 完成100%时直接绘制**未经修改的原始 SVG `path d`**。
   如果 B 侧99%与100%形状差异较大，必须报告“缺失覆盖/收笔跳变”；
   不允许把强行填满所有细节解释为真实提笔动作。

## 预期的动作状态

| 实验阶段 | 意图 | 技术表现 |
|---|---|---|
| `touch` | 起笔接触 | 前若干采样逐步放大笔尖接触 |
| `travel` | 行笔 | 中心线位置随共用时间模型行进，接触椭圆变化 |
| `brake` | 折前制动 | 继承基线的局部转角减速，同时调整后续笔尖形状 |
| `pivot` | 转锋 | 接触保持，方向限速旋转；不虚构额外规范笔画 |
| `flick` | 出钩 | 明确标注的钩笔在后段减少接触大小 |
| `lift` | 提笔 | 末端印迹渐细；残余字形覆盖单独计分 |

**注意：** 此 POC 尚未实现独立的停笔驻留和真实椭圆刷毛变形，`brake`/
`pivot` 时间仍沿用基线运动学。它用于 A/B 观察和参数校准，不得宣称达到完整
虚拟毛笔物理仿真。

## 验收维度

- **原始数据**：六样本及其他原始九样本的每笔 SVG `path d`、medians、
  stroke count、规范字段和审查状态保持不变；无新字体文件。
- **状态数值**：压强取值0–1，笔尖尺寸有界，旋转逐样本连续，动作阶段源于明确标签，
  提笔期间不修改已经沉积的印迹。
- **真实浏览器**：Node 测试对全部40笔生成纯数据计划；Chrome 同步 A/B 在
  六个选中笔形各采样10个时间进度，逐像素检查实验侧已沉积红色不减少，
  不越出 source outline，0%不闪现，100%源矢量一致。
- **性能**：记录每帧 render wall time、每字印迹数、source fill 探针数及最大
  99.5%–100%原轮廓差异；这些值以真实 CI 结果为准，不预设 FPS。
- **视觉证据**：`animation/tests/pen-lab-frames.html` 生成六笔 × 五进度 ×
  左右对照的 PNG，供实际检查横折、竖钩、横折钩和复杂折笔。
- **人工审定（尚未完成）**：同一笔的接触真实感、转锋平顺性、出钩自然度，
  匿名 A/B 主观评价及真实压强数据对照；人工不接受则不能替换默认播放器。
- **跨浏览器（待办）**：Chromium 之外需评估 Firefox/WebKit 的 mask/ellipse、
  关键帧像素稳定性和移动设备上资源消耗。

## 重要限制

这不是从静态 PDF 推断真实压力的系统，也没有使用 CASIA 等真实书写数据库
直接训练或校准。接触强度、转锋阈值、椭圆形参数均为**合成工程参数**。
使用现有 source medians 的方向属于结构性数据利用，**不等于独立的教学方向审核**。

代码只包含原创实验逻辑，不直接复制 Tegaki / Perfect Freehand 的源码，
仅引用其公开算法思路及论文说明；原 Hanzi Writer / Make Me a Hanzi 源码分发
和 ARPHIC 公共许可证约束继续保留，不能随意发布字体。

安全回退：即使实验路径渲染失败或得到较差主观评价，
线上 `animation/index.html` 继续保持 A1.2.3 正式工程演示，不启用新 renderer。

## A1.4.1: independent gesture microtiming experiment

The opt-in experiment additionally computes a separate **gesture-aware time→arclength warp** (source `animation/experiments/pen-kinematics.js`). It reweights the stable profile's strictly positive time-density by a local Gaussian **dwell** around explicitly annotated fold/hook pivot source vertices; for annotated hook types only, it adds a bounded post-pivot **flick acceleration**. Dot strokes receive a short opening delay. Unlike the default player, B-side nib and contact positions can be at a **different position at the same elapsed wall time**, which is the intended A/B comparison; the global stroke start/end, inter-stroke pause, total animation time, final outline and canonical stroke count remain identical.

This is a deliberately tunable phenomenological model, **not a fitted sigma-lognormal model** or force recording. Time-density remains positive; each stroke remains monotone and cannot reverse. The model cannot assert real pivots or validated source directions solely from vendor geometry.

To support expert inspection, the A/B page shows a chart on the same normalized time axis with **stable spatial progress** (gray), **experimental spatial progress** (red), and **independently synthesized pressure** (cyan). Curves should differ on curated folds/hooks. A shared cursor marks the selected moment.

New unit tests assert 40/40 original stroke trajectories remain unmodified, strict time→distance monotonicity, locally longer fold residence, hook release acceleration and finite pressure/orientation. Chrome A/B tests quantify pixel-set monotonicity and clipping, compare both engines with the same elapsed time, verify timing differences, provide frame-sheet artifacts and record the largest remaining terminal contour mismatch. Performance is measured as wall-time per local render call but not converted into an unverified universal FPS claim.


## A1.4.2：椭圆笔尖“一”字描迹填充不足修复（2026-10-09）

用户在线反馈：在 **B 椭圆笔尖接触模型** 书写“一”时，已经经过的笔画仍保留灰边和未填满部分。历史 A/B 测试采样显示：一的99.5%时间点与完整原始轮廓面积相差 **2.30%**，六个样例最大差距 **6.55%（火，第1笔）**。面积指标不能反映所有中间时刻的灰边，不能把曾经“0个像素倒退”的结果当成“笔画填满”。

### 确认的原因

原始 `pen-contact.js` 使用合成压力 `p(s)` 决定每个椭圆印迹实际尺寸：
`contactFactor(s)=0.12+0.88p(s)`。起笔约 `p(0)=0.18`，
所以首笔尖有效尺寸缩小到 **27.84%**；
一旦印迹绘制便不会重新加粗。随着中心线继续前行，这一部分原始
SVG 笔画会**永久未显露**，直至100%时把整个 mask 移除，
形成视觉上的灰色空缺和最后一帧的补齐跳变。

这是**显示层覆盖不足**，不是规范笔画轮廓或中心线数据错误。
直接永久加大椭圆、抹平合成压力或提前揭示整笔，均会使
真实起落笔实验失去研究意义。

### 已实现的修复

- **椭圆印迹不变**：`E_k` 的压强、旋转、长度和时间到达顺序都保留；
  合成压力只描述接触模型，不再独占“原轮廓是否必须覆盖”的责任。
- 在同一 source-constrained alpha mask 内增加**延时轮廓补全轨迹**，
  它复用 `brush-union.makeProfile` 已经按原 SVG 轮廓法向测得的
  笔刷宽度，以彼此独立的 round stroke fragments 递增生成。
  这些补全片段的几何中心**永远在目前笔尖位置之后**。
  圆头面积可能延伸到局部接触区域，但所有最终可见像素仍严格裁剪
  在原始 `stroke.outline` 以内。
- 令 \(u\in[0,1]\) 为**空间弧长进度**，
  \(L\) 为原始中心线总弧长，
  \(\ell_0=\max(18,\min(48,0.055L))\)，
  末段回收函数
  \(q(u)=\operatorname{smoothstep}((u-0.82)/0.18)\)。
  补全走到的弧长定义为：

  \[
  d_{\rm repair}(u)=\max(0,Lu-\ell_0[1-q(u)]).
  \]

  其距离和已完成片段个数都随 \(u\) **严格单调不减**；
  早期只补齐笔尖已经经过的区域，82%之后逐渐追上笔尖，
  到100%时才达到原始中心线终点，不另开快闪的全轮廓补丁。
- 最终绘制仍来自原样 SVG `path d`；原始 `medians`、
  `order_code`、笔画数量与规范来源版本均未变更。
  **默认 A1.2.3 播放器完全不受影响**。

### 定量验收（真实 Chrome，384×384，工程样例）

与合并前相同的6个真实来源部首（60个 A/B 进度采样）运行：
- 一的99.5%末帧缺口：**2.30% → 0.00%**；
- 六样例最大99.5%至原始完整轮廓差：**6.55% → 0.00%**；
- 在“一”的7个中间时刻，逐像素核对“比笔尖早走过10%原始弧长”
  的**稳定参考填充**，此前已写区域未覆盖红色像素 **0**；
- 以前已经显露的像素消失 **0**；原始轮廓外红色像素 **0**；
  规范中心线、SVG完成轮廓和39项几何/运动学 Node 测试保持通过。
- 这些结果必须来自对应分支**最终目标 HEAD** 的 GitHub CI；
  未部署到 Pages 前不能标记新版本已上线。

**限制：** 只说明样例与本测试分辨率下的绘制覆盖改善。
不同浏览器的 SVG mask 抗锯齿、触控采样、真正握笔姿势和
物理压力仍需独立验证。“修复覆盖”不等于实验模型已获得教学审定。
