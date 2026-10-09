## A1.5 模拟笔压研究及稳定版 A/B（候选实验）

根据用户反馈，继续以 A1.3 稳定圆头笔迹为准，不用椭圆笔尖代替。独立增加[稳定版 vs 模拟用力 A/B 预览](experiments/pressure-lab.html)：A、B 两侧使用同一真实SVG原轮廓、原始中心线、原填充并集和同一时间轴；**只有 B 的小圆圈接触程度、可选无白圈轮廓和压力曲线变化**，对照原墨迹必须逐像素完全一致。模拟压力是 0–1 合成强度，非力传感器实测/人体标定，且不把速度误当压力。研究数据授权边界、论文和算法详见 [A1.5研究记录](../docs/A1_PRESSURE_RESEARCH.md)、[Issue #101](https://github.com/netplus/zitie/issues/101)。实际发布要经过最终 A1 Chrome/Book CI、PR 合入与 Pages 部署；当前不要称上线。

---

## A1.3 稳定版圆圈与墨迹前缘同步（已合入并部署）

用户明确更偏好稳定版 A1.2.3 的圆头笔迹，后续不以椭圆笔尖取代它。本轮仅修复折、钩等笔画中“墨迹已经向前写，圆圈却仍落后”的视觉不同步：使用原圆头笔刷已经落墨的几何范围，计算单调递增的 **显示圆圈前缘**；中心线、笔速、原SVG填充、原始笔顺、墨迹逐帧测试全部保持稳定版原样。其几何是视觉指示而非真实笔尖压力和教学审核。详见[设计与回归](../docs/A1_STABLE_FRONTIER.md)、[Issue #98](https://github.com/netplus/zitie/issues/98)。[PR #99](https://github.com/netplus/zitie/pull/99) 已合入 `main`（`1ec9afb8b9f03657089cf61dd5551ed1fc0952ed`），最终 A1+Book CI 双通过，合并后的[GitHub Pages #37937065049](https://github.com/netplus/zitie/actions/runs/37937065049)已完成真实部署。[稳定版在线体验](https://netplus.github.io/zitie/animation/)已包含此修复。数值测试不等于独立教师审定。

---

## A1.4.4 真轮廓起笔与深色笔尖

A1.4 B侧不再假定原 median 首点就是字形起点，而是沿真实原始 SVG 轮廓寻找切向支撑点，先沿源方向显露左侧起笔轮廓，再进入原有笔内进度。恢复默认可见的深色笔尖，避免以前白圈造成移动空洞错觉。A/B 质量测试包括 512/768/1024px 的真实浏览器起笔投影检查和11组带笔尖关键帧。详见 [技术说明](../docs/A1_SOURCE_ONSET.md)。稳定版和正式字帖均不受影响。

---

## A1.4.3 起笔覆盖修复（实验版）

对“一”左上笔头延迟填红的反馈，实验性 source-fitted 补全由起笔固定延迟
改为初段随笔尖同步，笔刷宽度平滑压下，再逐渐切换正常行笔延迟；
新增早期3–5%空间进度的512/768/1024三分辨率逐像素源轮廓检验。
详见 [A1.4 实验说明](../docs/A1_PEN_CONTACT_EXPERIMENT.md) 与
[Issue #93](https://github.com/netplus/zitie/issues/93)。
仅影响独立实验 B 模型，默认 A1.2.3 保持不变。

---

## A1.4 独立笔尖 A/B 实验（不替换稳定播放器）

另有[六个部首的可变接触椭圆笔尖实验](experiments/pen-lab.html)，左侧直接使用 A1.2.3 稳定渲染器，右侧采用合成笔压/倾角与明确标注的折前驻留、短促出钩微时序；两个版本使用相同原始中心线、笔顺、最终原轮廓和统一 elapsed time。详见[实验说明与测试](../docs/A1_PEN_CONTACT_EXPERIMENT.md)和 [Issue #88](https://github.com/netplus/zitie/issues/88)。仅当独立 CI 与 Pages 部署完成后才认为线上可用；**合成动作参数不代表真实笔压或教学审核。**

---

## A1.4 工程研究，不更改当前播放器

已检查 [2014 静态书法恢复动画、2000 虚拟笔刷、Sigma–lognormal 手写动力学、2026 中文手写研究，以及 Tegaki/Perfect Freehand 的真实实现](../docs/A1_PEN_CONTACT_RESEARCH.md)，提出“笔内子动作规划 → 压力/接触状态 → 椭圆笔尖印迹累积”的实验架构。该设计尚未部署、参数未经实测，不改写 source medians、normative order 或已发布页面。详见 [Issue #88](https://github.com/netplus/zitie/issues/88)。

---

# A1.2.3 墨迹渲染修复（按来源轮廓裁剪的连续笔刷）

替换了旧的自交法向四边形遮罩与收笔补丁，采用独立圆头笔迹片段的递增并集，确保已显示墨迹不因填充规则而消失，并只显露原有 SVG 轮廓内的部分。保持已有位置自适应笔速与 0.5×～3× 按钮。逐像素集包含校验及真实 Chrome 关键帧复核见[填充算法设计](../docs/A1_FILL_AUDIT.md)。全部轨迹仍属于工程预览，教学方向不因渲染修复而获得规范背书。

---

# A1.2.2 分阶段笔速与直接倍率按钮

播放器现在按实际 medians 的距离和几何转折生成可复验的**位置→时间非线性映射**；直行相对较快，起收笔与明显折转处减速。全局速度按钮可直接点击 0.5×/1×/1.5×/2×/3×，不会重置笔内速度节奏。笔迹遮罩以更密的局部宽度采样和收敛的笔尖前沿绘制；原始最终轮廓字节不改。研究来源、公式、可调整常数、验证门槛和非实测免责声明：[A1 Motion](../docs/A1_MOTION.md)。

---

# A1.2.1 交互与笔迹精细度改进

播放器新增点击式主部首字形卡片、按批次筛选和搜索（汉字、规范已核细笔名、批次、主项ID）、逐字切换和可拖动时间轴，保持完整播放控制与离线部署。原固定170单位圆头遮罩已替换为根据原始填充轮廓测量局部左右宽度、沿未经修改的中心线推进的 SVG 渐进遮罩；最终完成状态严格复用原矢量。**此项属于图形呈现优化，不提供新增的规范审核或真实毛笔力度数据。** 参见 [A1.2.1 设计与 QA](../docs/A1_UX_PRECISION.md)。

---

# A1 experimental offline SVG stroke animation

**Browser preview:** [Official GitHub Pages demo](https://netplus.github.io/zitie/animation/) (deployed successfully on 2026-10-09, [run #37880818335](https://github.com/netplus/zitie/actions/runs/37880818335)). See [hosting notes](../docs/A1_PREVIEW.md). This engineering preview remains unapproved for pedagogical trajectory correctness.

**Open `animation/index.html` directly in a modern browser**, including via `file://`. No server, npm dependency, internet access or separate font is needed. Choose from nine authentic primary radicals, play/pause, replay, previous/next, single-stroke repeat, speed adjustment and show-full-shape.

The red stroke is the **actual existing filled SVG outline** revealed along the vendor's ordered **median writing path**; the final full silhouette is never approximated by the mask. Future outlines are pale gray, earlier strokes dark gray. One deterministic timeline drives all controls.

**Engineering prototype only** — the source medians are structurally present, but their starts, pen directions, folds and hooks are **not yet independently teaching-reviewed**. Do not market this as validated writing instruction. Fine names are displayed only when the source policy allows them. See [A1 technical/audit design](../docs/A1_ANIMATION.md), [source notice](NOTICE.md), [reviewing Issue #79](https://github.com/netplus/zitie/issues/79) and [existing source gate #4](https://github.com/netplus/zitie/issues/4).

Smoke checks on a developer machine:

~~~sh
node --test animation/tests/timeline.test.cjs animation/tests/precision.test.cjs
bash scripts/a1_browser_smoke.sh
# After existing python scripts/acquire_vectors.py --batches B01 ... B21:
python scripts/a1_audit.py --require-all
~~~

The browser check needs Chrome/Chromium, Python 3, and a free localhost port. It opens only local assets and waits for real animation frames. Data materials are source-pinned to a fixed upstream revision; the 201 original JSONs are downloaded to `build/vectors/` by existing scripts, not checked into the Git tree. Nine packaged samples run offline.

*Classification*: 201 main radicals in the canonical book; 9 **playable engineering previews**; 0 **trajectory teaching approvals** as of A1.2. Future attached-form, comparison, recall and full-word position-migration assets must be counted separately.
