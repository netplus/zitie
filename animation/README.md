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
