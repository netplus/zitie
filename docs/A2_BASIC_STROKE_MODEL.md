# A2 — Basic-stroke grammar, motion geometry and cinematic handwriting

2026-10-10 · [Issue #107](https://github.com/netplus/zitie/issues/107)

## Why A1 is not enough

The user considers 横 (heng), 竖 (shu), 撇 (pie), 折 (zhe) and 钩 (gou) to be the essentials of Chinese writing and reports that the current writing animation still fails to express their character.

Source audit of `animation/timeline.js`, `motion.js`, `player.js`, `brush-union.js` and the A1.4/A1.5 studies reveals a **representation gap** rather than a frame-rate gap:

1. The A1.3 marker traverses piecewise-linear upstream `median` points. A curvature-aware quintic time warp changes *when* the point moves, not the interpolated path itself.
2. The same easing model governs all glyphs. Its `turn` tag cannot express the distinct contact, braking, turning, stored action, flick and lift events of composed strokes.
3. A1.6 normalized pressure affects the *appearance of the tip*; it does not certify either source writing geometry or human movement, nor does it change red ink. The A1.4 pressure ellipse was explicitly not preferred by the user.
4. A brush that draws the exact canonical SVG ink shape and a tip that follows a plausible human trajectory are **different physical/visual objects**. Altering the mask solely to chase an estimated hand motion has already caused empty ink and abrupt terminal-fill regressions in earlier experiments.

**Principle**: `Stroke = original source outline + reviewed/unreviewed medians + semantic action grammar + constrained kinematics + non-destructive source-ink reveal`. None of the source-derived medians is silently elevated to independent teaching review.

## Research inspection and usable insight

| Source | Evidence | Adopt, and important limitation |
|---|---|---|
| [Flash & Hogan (1985), *The Coordination of Arm Movements*](https://www.jneurosci.org/content/5/7/1688) | A minimum-jerk criterion explains many smooth planar movement patterns | Retain a smooth onset/end timing component, **not** smooth every fold corner away |
| [Plamondon et al. (2014), *Recent developments … Sigma–Lognormal model*](https://doi.org/10.1016/j.patrec.2012.06.004) | Motion can be decomposed into controlled overlapping submovements | Treat `touch / brake / pivot / flick / lift` as explicitly timed sub-actions; coefficients are **not fitted** to human data here |
| [Plamondon & Guerfali (1998), *2/3 power law: When and why?*](https://pubmed.ncbi.nlm.nih.gov/9844558/) | Speed is often coupled to geometric curvature | Not universal for all graphic movements. Use a bounded local penalty rather than claim exact human biomechanical law |
| [Wang et al. (2020), *Robot Calligraphy … Dynamic Brush Model*](https://arxiv.org/html/1911.08002v2) | Separate vector stroke decomposition, end-effector trajectory optimization and ink-footprint dynamics | Motivates future feedback-constrained rendering; its physically deformed brush is not a replacement for our preferred stable round-tip mask |
| [Wang et al. (2026), *Hierarchical offline-to-online Chinese handwriting trajectory reconstruction*](https://link.springer.com/article/10.1007/s44443-026-01050-5) | Separates stroke-level structural constraints from continuous vector reconstruction and kinetic priors | Architecture reference; model weights/datasets are **not** imported and reported comparisons do not certify our medians |
| [Wang et al. (2026), *Handwriting Trajectory Recovery via Autoregressive Ordered Stroke Instance Prediction*](https://arxiv.org/abs/2609.02251) | Order-first/stroke-continuity-first reconstruction can be more robust than holistic paths; sampling density affects metrics | Reinforces ordered stroke decomposition and fine-grained QA, not an excuse to infer missing teaching order |
| [Guo et al. (2025), *Brush Stroke-Based Writing Trajectory Control Model*](https://www.mdpi.com/2079-9292/14/15/3000) | Robotic brush stroke-level dynamic trajectory control | Brush physics, force sensing and feedback are not available in our original static SVG assets |

The project continues to use the pinned Hanzi Writer / Make Me A Hanzi outline and median data, with its existing Arphic license notice. Public materials are architectural references, not ingested training sets. A fundamentally different human-pen style cannot be reverse engineered uniquely from a static final glyph.

## A2.1 prototype: stroke semantics before spline fitting

Five initial **motion families**, not a claim that all other stroke types are normative subtypes:

| Primitive | Semantic actions to represent |
|---|---|
| 横 `heng` | Light touch → establish contact → sustained travel → controlled close and lift |
| 竖 `shu` | Establish vertical direction → steady long travel → stable terminal without sideways bounce |
| 撇 `pie` | Loaded starting segment → continuous falling/sweeping motion → gradually accelerating tapered release |
| 折 `zhe` | Approach → **brake before the original pivot** → retain a deliberate sharp angular direction change → reaccelerate |
| 钩 `gou` | Shaft travel → pre-hook storage/brake → change in direction → short flick → lift |
| `zhe-gou` | Compound **折 + 钩** with two distinct source-knot anchors and two local action windows |

**折 and 钩 are often *events* inside a compound stroke, not interchangeable isolated geometric classes.** A2 therefore stores explicit `foldVertex` and `hookVertex` indexes against **original vendor medians** for a small curated set (口 2, 巾 2, 水 1, 月 2, 龠 14). The indexes are labelled `unreviewed_engineering_gesture_candidate`. No algorithm reorders or renames the official source.

### 1. Curve geometry: preserve knots and corners

For each source median segment from `A` to `B`, construct a cubic curve using one-sided unit tangents:

`P(u) = (1-u)^3 A + 3(1-u)^2u C1 + 3(1-u)u^2 C2 + u^3 B`, where
`C1 = A + |B-A| T_out/3` and `C2 = B - |B-A| T_in/3`.

- On smooth interior points, share a tangent *direction* from the two source adjacent segments (G1-style intention, **not a claim of speed-matched C1 derivative**).
- At meaningful fold/hook vertices or large-angle turns, use distinct one-sided tangents and retain the original sharp corner.
- Compute discrete arc-length from dense samples (nominal 5 source units). Preserve *every exact median knot* in order; parameterize the experimental cursor by derived true arc-length rather than raw vertex count.
- Bound geometry displacement from the corresponding source segment (max 16 SVG units, more restrictive on short segments). In the browser, evaluate each candidate sample against the **connected original SVG filled outline** with `isPointInFill`. Reject suspect curved segments and use the original straight segment. Track fallback and residual out-of-source samples separately; if original vendor median itself escapes the contour, **flag**, never claim the algorithm corrected the source.
- This is *not* a new normative writing skeleton or an attempt to perfectly reproduce recorded handwriting. It is a deliberately constrained visual hypothesis.

### 2. Stroke-specific time density

Define strictly positive per-distance arrival cost:

`dt/ds = w(s) / integral[0..1] w(q)dq`, with `w(s)>0`.

The integral is sampled monotonically, then inverted after bounded quintic start/end easing. Fold anchors add a local slow-density Gaussian window; hook events combine pre-hook brake with a short decreased-density flick just after the original pivot; 撇/捺 have a relative velocity increase near release. Horizontal and vertical maintain distinct contact/terminal dwell envelopes. Those fields are **heuristic priors**; there is no measured sampling rate/pressure, no velocity fitted from real humans, and no assertion of the universal 2/3 power law.

Same fixed per-stroke duration and stroke order are retained. Temporal `progressAt(t)` stays in [0,1], is strictly increasing for finite 0<t<1, and reaches the exact original source endpoint. `clockAt(s)` inverts it for QA.

### 3. A/B laboratory architecture — original ink always authoritative

- A: published A1.3 stable `StrokePlayer` without modification.
- B: another **unmodified stable SVG mask renderer**, but re-timed to the experimental spatial progress at the same wall-clock fraction. Its tip *visualization only* is positioned on the constrained candidate curve and a subtle thin dashed centerline is optionally shown.
- B's true red brush remains driven by the original source medians; final source SVG filled silhouette is exact. This A2.1 phase is about validating dynamic skeleton hypotheses, **not** claiming a finished physically coupled new ink engine.
- Compare both at equal wall clock to see different actions. For exact ink integrity, compare B's raster to A at **matched source spatial arclength**, not simply at equal wall time. Both must match source red ink, so no abnormal fill holes can be hidden by the experiment.
- Show stroke phase, both positions, a normalized velocity comparison and source geometry rejection diagnostics. Keep the main A1.6 stable/synthetic-pressure selector completely unchanged.

## Representative geometry and QA

A/B selector covers: 一 (横), 十 (竖), 人 (撇), 口 (横折), 水 (竖钩), 月 (横折钩), 龠 (complex 横折). 巾 may be added for further multi-pivot validation.

**Node gates:** all nine existing source glyphs preserve source knots and original bytes, event positions are ordered, hard fold and hook anchors remain corners, derived arclength and time map are monotone/finite, wrong coefficients fail closed, all key strokes exhibit distinct kinetic density. Curve segment fallback must be deterministic and never invent geometry outside allowed offset.

**Real-browser gates:** connected-SVG contour probe used, 7 representative glyphs at several start/pivot/end timepoints, exact `outline d`, no extra canonical strokes, every accepted derived point stays source-contained or explicitly reports the original-source-blocked case, no runtime/nonfinite glitch; original red ink equals stable source ink at matched progress, 0 previously painted pixels vanish, source/final silhouette identical. Capture an A/B key-frame sheet for human naturalness assessment.

## Why not promote A2.1 immediately?

Even perfect geometric and CI scores do not establish that an inferred skeleton imitates hand technique. It remains an opt-in experiment until stroke-by-stroke specialist checks of the five primitives, dataset/pressure/velocity domain fit, and user aesthetic viewing. Automatic averaging can erase deliberate reverse entry, edge pressure, distinct fold angle and hook flick character. **The stable main player and released PDF/manifest/201 records must not change** in this phase.

Later A2.2 tasks: hand-reviewed source trajectory annotation, measured input (if permitted), richer hinge/flick curves and exact-source-front ink coupling with zero fill regressions. Later A2.3: select reviewed stroke families for main-player opt-in only after A2.2 data and human comparison pass.
