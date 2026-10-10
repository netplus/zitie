# A2.2 — Hardpen-first UI, preserved brush and a shared writing clock

**Deployment verified (2026-10-10):** [PR #111](https://github.com/netplus/zitie/pull/111) merged as `ddd360f95872264fe74131c37b8275901fece769`. Its exact final HEAD `9f8d3e9947f0aeefda8910797cb6d752874d5ce8` passed [A1 Chromium #38040209141](https://github.com/netplus/zitie/actions/runs/38040209141) and [full Book integrity #38040209229](https://github.com/netplus/zitie/actions/runs/38040209229) **before merge**; [GitHub Pages #38040703826](https://github.com/netplus/zitie/actions/runs/38040703826) completed actual Configure/Upload/Deploy on the merged SHA. [**Main animation, hardpen default / original brush optional**](https://netplus.github.io/zitie/animation/). 69/69 Node tests; seven example glyphs ×nine Chrome frames of rigid nib, **zero vanished red pixels** after the cumulative-capsule fix and 56 form-distinct frames compared to the original brush silhouette; nine source-backed main-page glyphs ×seven Chrome frames, zero original brush red pixel mutations and zero rigid red pixel loss, four in-play tool swaps preserving timeline/speed and pressure-cue switching on both tools; 390px alignment passed. Browser screenshot/structured JSON audit archived in [A1 artifact #11664964365](https://github.com/netplus/zitie/actions/runs/38040100639/artifacts/11664964365). `Source medians` remain *unreviewed*; deployment success is not evidence of authentic human motion or calibrated steel nib diameter.

2026-10-10 · [Issue #110](https://github.com/netplus/zitie/issues/110)

## Product decision (explicit user correction)

The preferred target is **ordinary 钢笔／硬笔楷书**, not 毛笔 or a specialized flexible nib. The user also explicitly requested that **the existing 毛笔-style animation be kept**, but the main deployed interface should **default to hardpen**.

This changes the interpretation of the original A2 proposal: a stroke-specific *timing* curve applied to the already thick and tapered original SVG contours can still look like brush writing. We must therefore distinguish (1) a tool's contact and ink geometry, (2) the ordered skeletal movement, and (3) the time/pressure display model.

The published main screen has two **independent selectors**:

| Setting | Default | Other choice | Semantics |
|---|---|---|---|
| **书写工具** | **硬笔（默认）** | **毛笔（原版）** | Which ink renderer and movement style are shown |
| **笔压风格** | **稳定版** | **模拟笔压版** | Whether the small visual tip/force ring depicts synthetic contact — NOT a rewrite of the ink |

Switching writing tools does not change the selected glyph, playback time, selected stroke, rate or playing/pause state. The pressure style selection survives tool changes. Clicking 毛笔 reactivates the **existing A1.3 source-outline brush renderer** and its original optical-frontier marker; this legacy code is not replaced or deprecated. A1.5/A2.1 independent laboratories remain available as opt-in comparisons.

## Evidence, physical limits and no invented pressure data

- [The Goulet Pen Company — nibs explained](https://www.gouletpens.com/blogs/fountain-pen-blog/fountain-pen-nibs-explained) distinguishes regular firm, soft, and flex nibs. A flex nib separates tines under pressure and intentionally makes wider downstrokes; that is a distinct tool, **not** ordinary rigid-pen behavior.
- [The Pen Company — writing-robot extra-fine nib comparison](https://www.thepencompany.com/blog/expert-advice-product-reviews/extra-fine-fountain-pen-nibs-writing-robot-handwriting-comparison/) documents substantially different width variation among ostensibly similar fountain pens; its comparatively rigid nib changed width by roughly 0.04mm across tested pressure settings, whereas other samples varied more. The result supports keeping *normal* hardpen contact near-constant in our initial model, **not** asserting all steel pens have an identical width.
- [Fountain Pen Revolution (2026) — rigid vs flex nibs](https://fprevolutionusa.com/blogs/news/flex-nibs-vs-rigid-nibs-line-variation-explained) describes the design difference and confirms why intentionally pressure-widened flex writing should not be confused with everyday hardpen writing.
- [CASIA-onDo official corpus](https://nlpr.ia.ac.cn/databases/CASIA-onDo/index.html) records online writing X/Y, time, pen-state and pressure but must be separately rights-checked and its pen/device dynamics normalized before using coefficients. **No restricted handwriting corpus was downloaded or incorporated.**
- Minimum-jerk and Sigma–Lognormal literature previously examined in [A2 basic stroke research](A2_BASIC_STROKE_MODEL.md) motivate piecewise smooth motion and event segmentation. They do **not** provide parameter-free, uniquely correct hardpen handwriting motions from one final glyph.

The hardpen experiment uses source coordinates in an SVG 1024-unit plane and a default diameter of **26 SVG source units**, with a 21-unit thinner setting in the research lab. **No physical paper size or dpi-to-mm calibration exists**, so the UI must never describe these as actual 0.5mm, 0.38mm, etc. A rigid round nib naturally tends to nearly constant width; we represent that with a single line width and round caps. Decorative flex, angled nibs, traditional brush loading/dryness and pressure-driven width growth are explicitly excluded.

## Render architecture

### Hardpen stage (default)

`animation/experiments/hardpen-model.js` uses the original median *only as an unreviewed spatial scaffold*, preserving all original knots and intentional fold/hook vertices. It constructs a dense, bounded, piecewise cubic trajectory and reparameterizes it by computed arclength. Hardpen-specific timing has modest onset/terminal easing, short local fold/hook slowing, natural faster release for 撇/捺, and no brush-style lingering or exaggerated reverse entrance.

`animation/hardpen-stage.js` uses the shared `animation/hardpen-ink-union.js` renderer to paint the sampled candidate path as the **union of immutable, individual round-capped short line fragments** with the same source-unit width (26 by default). Previously painted fragments stay visible and unchanged; only the current partial segment advances. Rebuilding one large growing path caused a **one-pixel erased-ink artifact at 口's bend**, because a former end cap was converted to an SVG line join. This was discovered by the real-Chromium hardpen QA, and the renderer was corrected rather than relaxing the ink-loss gate. It still uses `SVG <path fill="none" stroke-width="26" stroke-linecap="round">` for each local piece, with no brush silhouette or source-alpha masks. Early and completed strokes use original-style light-gray/dark-gray line layers; current stroke is red. The displayed hardpen tip follows the candidate path. The canonical source glyph `outline` strings/medians/stroke order are never changed. The standalone A2.2 hardpen lab and the main default renderer **share this same incremental ink module**, avoiding divergent experiments.

### 毛笔 (selectable original)

The existing `ZitiePlayer.StrokePlayer` is kept intact, including its `Brush.makeProfile`, fixed-outline source masks, A1.3 optical cursor alignment, time law, all tests and full remaining original source glyph paths. The legacy A1.6 source red pixels are unchanged when selecting 毛笔 from the main screen.

### One timeline, two connected SVG layers

The existing original player is the **sole playback controller**. Its `onUpdate` drives the passive hardpen stage for the same source stroke at the same elapsed timestamp. Both SVG stages stay in the DOM and share viewBox/position; one is visually presented at a time, avoiding loss of SVG fill probing caused by detaching/display:none on the original source geometry. Tool changes only toggle CSS visibility, leaving the clock, source glyph and rate unchanged. No duplicate RAF playback loop is created.

The pressure model remains independent of written ink: in hardpen synthetic mode it shows a **smaller 4.5+3.5×P** round tip and a dark hollow pressure ring without widening the 26-unit line; in brush synthetic mode it retains the original larger visualization from A1.6. In both cases the pressure percentage is an **uncalibrated 0–1 heuristic**, not digitizer-measured force.

## Automated acceptance / veto

1. **Ordinary hardpen mechanics**, 7 representative glyphs at 63 early/middle/late browser frames: near-constant width; no inherited source alpha masks; no red ink loss; distinct red visual ink from the original source silhouette; no premature full-stroke appearance or stuck pointer; original glyph/PDF unchanged.
2. **Main page**, 9 original source-backed glyphs at 63 frames: hardpen default, preserved selectable brush and its original SVG source, **zero** hardpen red pixel disappearance, two SVGs exactly aligned at 390px, playing/elapsed/stroke/speed unchanged when switching tools during playback.
3. A1.6 force style works on **both** tools: brush stable state restores the original radius-8 white-edged dot; hardpen stable state restores a small no-white marker; simulated force ring is non-white and never modifies either pen's ink geometry.
4. Keep the historical A1 Chrome/controller, 40-stroke source-mask integrity, A1.3 optical cursor, A1.4 opt-in ellipse, A1.5 pressure lab and A2.1 gesture lab regressions. Explicitly switch to 毛笔 at the beginning of tests that historically assert the old source brush behavior.
5. Final proposed PR HEAD A1 animation + Book integrity CI must complete successfully; merge without force; verify actual GitHub Pages **Configure, Upload and Deploy** on merged SHA before calling hardpen default live.

## Important unfinished evidence

The vendor medians originate from conventional calligraphic artwork and have not been reconstructed from actual everyday rigid-pen recordings. Some starts, joins, proportions, sharp corners or flicks may still be pedagogically incorrect for hardpen despite flawless mathematical checks. Human specialist observation and licensed real hand-writing trajectory measurements are required before calling the model **verified hardpen calligraphy** or expanding from 9 experimental glyphs to all 201 normative characters.

This is a **hardpen-first user interface and visible research candidate**, not a claim that the handwriting model is scientifically or pedagogically complete.
