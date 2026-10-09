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
