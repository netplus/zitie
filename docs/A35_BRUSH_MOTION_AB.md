# A3.5 — PDF同源毛笔运笔 A/B（独立研究版已部署，未教学认可）

**用户决策（2026-10-11）**：A3 主线继续使用已发布 201 主部首、1045 笔、299 页正式 v0.5.1 字帖及毛笔默认。此前硬笔优化已冻结。A3.5 需要让起笔、折、钩、撇捺、收笔动作更自然，但**不擅自重写源字形、笔顺、PDF 及来源审核字段，也不直接切换已发布的默认播放器**。本轮独立实验页面为 animation/experiments/brush-motion-lab.html。

## 实际发布与可复核证据

实际独立研究版 [A3.5 201字 A/B](https://netplus.github.io/zitie/animation/experiments/brush-motion-lab.html) 已上线：[PR #123](https://github.com/netplus/zitie/pull/123) 最终 HEAD `e7938b29725488dcf9491d143cf746391808533e` 的 [A1 Chrome #38125276874](https://github.com/netplus/zitie/actions/runs/38125276874) 与 [Book #38125276827](https://github.com/netplus/zitie/actions/runs/38125276827) 双 completed/success，合并至main SHA `0da37d5c1965a4f9d798b228de8d081263c1d81c`，其 [Pages #38125707083](https://github.com/netplus/zitie/actions/runs/38125707083) Configure、Upload和实际Deploy 全 success。**201字、1045笔**全部加载；960个有界运动候选、85个保守回退、193处来源中线角点候选事件；54对真实Chromium A/B 帧（两侧红墨不消失）、其中21对有时间运动差异，另21对相同空间位置的实际像素对照 **0 差异**，390px通过。截图/metrics见 [A1 QA artifact #11697280799](https://github.com/netplus/zitie/actions/runs/38125276874/artifacts/11697280799)。**人工审美/真实书法运笔教学审核仍待完成，绝不自动推广B为默认**；正式 [A3毛笔播放器](https://netplus.github.io/zitie/animation/book.html)、原PDF及硬笔冻结决策不变。

## 源模型与严格边界

两侧分别实例化原版 animation/player.js 中的 StrokePlayer。它们均加载同一个由 scripts/build_a3_animation.py 生成并校验过正式 PDF 201 ID 书签与 SHA 的 book-pack.js。A 侧使用动画基线；B 侧**仅在独立副本的 T.buildTimeline 结果里**把原 sourceMotion.fractions 换成单调时间映射，其余字段完全不改：

- 每笔的 SVG outline、median、字、名称审核级别、顺序、起止时间、笔间停顿和总时长不变；
- 两侧继续调用同一个原始 SVG brush-union 遮罩算法及视觉墨迹前沿；
- 唯一真实的播放时钟为 A 侧 elapsedMs；B 侧以同样毫秒位置进行只读渲染，不启动第二个独立 rAF；
- 在 **相同时间位置** 比较两种运笔，红墨空间进度可以不同；在 **相同中线空间进度** 比较，红墨形状应与 A 完全相同；
- 正式 animation/book.html 仍为默认毛笔 A3；A3.5 只是显式进入才显示的研究页面。

画面墨迹是从正式 PDF 同源笔画矢量裁出的工程动画，不代表墨迹生成自真人动作数据。特别区分 stroke order reviewed 与 **trajectory_unreviewed**。

## 为什么不直接应用 sigma-lognormal 模型

Plamondon 1993 提出以速度控制解释书写时钟的非对称钟形分布；1998 年的相关研究指出曲率–速率的 2/3 次幂关系在一些条件下成立，但并不普遍适用于所有笔迹。书法动画文献（Yang & Li 2009）把笔画、轨迹及控制点的专业知识并列，提醒：从静态图样重建真实书写是欠定问题，不能凭一条现有 median 假定真实速度。因此**只采用可解释的研究启发式，不声称拟合真人或从笔画名称测出笔压**。

参考（论文信息，不复制插图或全文）：

- Plamondon, R. (1993), *Looking at handwriting generation from a velocity control perspective*, Acta Psychologica 82, 89–101. https://doi.org/10.1016/0001-6918(93)90006-D
- Plamondon & Guerfali (1998), *The 2/3 power law: When and why?*, Acta Psychologica 100, 85–96. https://pubmed.ncbi.nlm.nih.gov/9844558/
- Yang & Li (2009), *Animating the Brush-writing Process of Chinese Calligraphy Characters*, ICIS. https://doi.org/10.1109/ICIS.2009.183

## 算法：以已有行程时间为基准的正权密度重参数化

在一个已核原始 stroke 的中线弧长 s∈[0,L] 上，原 motion.js 提供严格递增的累计时间曲线 T₀(s)，新的动作语义权重 w(s)>0：

T₁(s) = (∫₀ˢ w(u)dT₀(u)) / (∫₀ᴸ w(u)dT₀(u))

候选的实际曲线使用 T(s)=(1-α)T₀(s)+αT₁(s)，α=0.56 为目前研究参数。取样时 w(s) 被限制在 0.54—3.85；旧/新累计时间曲线是严格递增函数，故其正凸组合不会在转折时倒退、瞬移或产生内部冻结停顿。它只改变同一 source median 的推进时刻。

为避免少数复杂笔画被大幅扭曲，对每笔在 161 个固定时刻测量运动位置相对原版的最大归一化偏移；不得超过 **12.5%**。超过则连续降低 α，仍超限直接回退原版。绝不靠改轨迹坐标绕过限制。

只对细笔名 **reviewed** 的笔画考虑动作类别：

- 横、竖、提：较平稳行笔、有限起笔接触和收笔减速；
- 点：轻触起笔、点画内部适度快慢与提笔；
- 撇、捺：较快行笔与有限收锋；
- 折：从原**source median** 按折角检测中段有效转折，候选折前制动、连续转锋；
- 钩：只有当源 median 的**后段**存在有效转折才候选“钩前制动—短促出钩”；折钩允许较早折点加后段钩点；
- 没有 reviewed 名称的14个主项、没有清晰折点的名义折/钩，或者不能安全控制运动漂移的笔画，严格回退为原版。**笔画名称审核≠动作审核**。

默认参数不是人体实测物理系数；速度改变时仍保留原笔画总时长、读音/笔画名源政策。时间轴、倍率、拖动、切字、17笔龠与PDF续页不改。

## 工程质量门槛（实验可上线 ≠ 教学可接受）

1. Node：9字40笔的轮廓/median JSON byte-level 不变、命名审查守门、折钩不臆造事件、候选严格单调、0与100%端点一致、全局倍率与归一化模型独立；异常参数 fail-closed。
2. A3 pack Node / Browser：全201字同源；A3.5 在两个 StrokePlayer 中完整加载1045笔；每笔源轮廓 path d 与正式 PDF 打包源一致；笔间停顿/时长不变；未审核细笔名无语义推断。
3. Chromium：9个代表笔画 × 6 时点 × 2侧的54对真实渲染帧；A/B各自已绘红像素不消失、时间轴同步、笔尖持续、候选确实有可见运动差异；另以7笔 ×3个匹配弧长点核实墨迹相同，不允许通过不同字体、不同涂墨模型伪造“改进”；17笔龠和390px小屏继续检查。
4. A1 + Book 对 PR 精确 HEAD 的CI通过、合并，并且同一合并SHA的Pages Configure/Upload/实际 Deploy成功后，只宣布“**研究 A/B 上线**”。正式201字播放默认仍保持A3基线。
5. 最终是否切换B为默认，须用户/书法老师在定格+动画上明确作视觉认可，不能凭自动指标/论文模型推定改进已被认可。
