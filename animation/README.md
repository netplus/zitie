# A1 experimental offline SVG stroke animation

**Open \`animation/index.html\` directly in a modern browser**, including via \`file://\`. No server, npm dependency, internet access or separate font is needed. Choose from nine authentic primary radicals, play/pause, replay, previous/next, single-stroke repeat, speed adjustment and show-full-shape.

The red stroke is the **actual existing filled SVG outline** revealed along the vendor's ordered **median writing path**; the final full silhouette is never approximated by the mask. Future outlines are pale gray, earlier strokes dark gray. One deterministic timeline drives all controls.

**Engineering prototype only** — the source medians are structurally present, but their starts, pen directions, folds and hooks are **not yet independently teaching-reviewed**. Do not market this as validated writing instruction. Fine names are displayed only when the source policy allows them. See [A1 technical/audit design](../docs/A1_ANIMATION.md), [source notice](NOTICE.md), [reviewing Issue #79](https://github.com/netplus/zitie/issues/79) and [existing source gate #4](https://github.com/netplus/zitie/issues/4).

Smoke checks on a developer machine:

~~~sh
node --test animation/tests/timeline.test.cjs
bash scripts/a1_browser_smoke.sh
# After existing python scripts/acquire_vectors.py --batches B01 ... B21:
python scripts/a1_audit.py --require-all
~~~

The browser check needs Chrome/Chromium, Python 3, and a free localhost port. It opens only local assets and waits for real animation frames. Data materials are source-pinned to a fixed upstream revision; the 201 original JSONs are downloaded to \`build/vectors/\` by existing scripts, not checked into the Git tree. Nine packaged samples run offline.

*Classification*: 201 main radicals in the canonical book; 9 **playable engineering previews**; 0 **trajectory teaching approvals** as of A1.2. Future attached-form, comparison, recall and full-word position-migration assets must be counted separately.
