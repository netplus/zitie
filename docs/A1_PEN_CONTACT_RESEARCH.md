# A1.4 — Natural pen motion, contact dynamics, and stroke-gesture research

Status: **research and experiment specification**, not an implementation release or teaching approval.
Date: 2026-10-09. Issue: https://github.com/netplus/zitie/issues/88

## 0. Problem definition and immutable constraints

User feedback: after A1.2.3 eliminated sampled fill artifacts, the animation still looks artificial at 起笔、落笔、折、钩 and adjoining segments. Pixel-monotone source-clipped paint is **necessary, not sufficient** for believable handwriting.

Actual `main` source audit on 2026-10-09 (commit `72a1c40db4392a6d11ab27776e6a9add5a0e8ec0`):

- `animation/samples.js`: 9 offline primary radicals, 40 ordered strokes, final per-stroke SVG `outline` and **spatial** centerline `median` points, pinned to immutable drawing source. These spatial medians contain **NO pen timestamps, pen pressure, pen tilt, height, ink mass, physical nib or certified event positions**. Some fine-stroke names remain constrained by source policy; no blocked field may be restored.
- `animation/motion.js`: global quintic/linear onset/finish time warp plus local Gaussian curvature slowdowns, synthesized from unreviewed medians. This can simulate spatially nonuniform speed but has no explicit pen-down, contact settling, corner pivot, flick/release or pressure. One generic slowdown around a high-angle vertex cannot distinguish 横折 from 竖钩.
- `animation/brush-union.js`: thousands of pixels are revealed by the **monotone union of circular, locally width-estimated stroked median fragments**, clipped to exact source outline. All local nibs have symmetric round caps and no tilt/pressure-dependent contact ellipse or independent lift-off state.
- `animation/player.js`: one 8-unit radius red pen-tip indicator follows `frame.tip`; the mask is removed exactly at stroke finish. This produces convincing order and absence of missing red paint in the 9 glyphs but does **not** represent actual pen geometry; the tip should be a deformable contact footprint rather than an independent hovering circle.
- Source PDF and canonical data: 201 main radicals / v0.5.1 299-page PDF, release manifest, teaching-source-policy, evidence records and print QA are frozen. A1.4 must **not** edit them, silently smooth the original medians or mark source trajectories teaching-reviewed.

## 1. Highest-relevance research, with findings versus what it does *not* prove

| Rank | Evidence | Directly usable idea | Key limitation |
|---|---|---|---|
| 1 | Zhang Junsong, Zhang Youmiao, Zhou Changle, **"Simulating the Writing Process from Chinese Calligraphy Image"**, *Journal of Computer-Aided Design & Computer Graphics* 26(6), 963–972 (2014), https://www.jcad.cn/en/article/id/a148ab9a-9e96-43a5-bc11-563c871bb72b | Extract real calligraphic ink-footprint statistics; reconstruct writing by advancing a **sequence of brush-paper contact footprints along a trajectory**. Very close to our static outline + median material. | Describes a method, not a ready-to-invoke API; true footprint templates must be obtained, not invented as ground truth. |
| 2 | Wong & Ip, **"Virtual brush: a model-based synthesis of Chinese calligraphy"**, *Computers & Graphics* 24(1), 99–113 (2000), DOI 10.1016/S0097-8493(99)00141-7, https://scholars.cityu.edu.hk/en/publications/virtual-brush-a-model-based-synthesis-of-chinese-calligraphy/ | Parameterize brush angle, shape, bristles, pressure and ink deposition. Changing motion speed alone cannot give realistic strokes; **contact state** is independent. | Full 3D bristle/fluid mechanics is expensive and inappropriate for the first 2D offline SVG experiment. |
| 3 | Yang & Li, **"Animating the Brush-writing Process of Chinese Calligraphy Characters"**, IEEE/ACIS ICIS (2009), DOI 10.1109/ICIS.2009.183, https://doi.org/10.1109/ICIS.2009.183 | For *regular script* (楷书), choose control points and quantify animation parameters using character shape **plus calligraphy expert knowledge**. Semantic events are important. | Experts and labels are required to validate fold/hook behaviors; geometry-only labels may be wrong. |
| 4 | Plamondon (1993), **"Looking at handwriting generation from a velocity control perspective"**, *Acta Psychologica* 82:89–101, DOI 10.1016/0001-6918(93)90006-D, https://www.sciencedirect.com/science/article/pii/000169189390006D ; Plamondon et al. (2014), **"Recent developments in the study of rapid human movements with the kinematic theory"**, PRL 35:225–235, DOI 10.1016/j.patrec.2012.06.004, https://www.sciencedirect.com/science/article/abs/pii/S0167865512001924 | Handwriting speeds often consist of asymmetric bell-shaped **lognormal motor pulses**, with individual submovements possibly overlapping. A one-ease-per-canonical-stroke model is insufficient for a long折钩. | Fit parameters from **measured** trajectories with time; from our static medians, only use as a prior and mark parameters as synthetic. |
| 5 | Flash & Hogan, **"The coordination of arm movements: an experimentally confirmed mathematical model"**, *J Neurosci* 5:1688–1703 (1985), https://pmc.ncbi.nlm.nih.gov/articles/PMC6565116/ ; Plamondon & Guerfali (1998), **"The 2/3 power law: When and why?"**, DOI 10.1016/S0001-6918(98)00027-4 | Smoothness/jerk optimization and curvature-dependent slowing are defensible components of movement planning. | Smoothness and the curvature power law are **not universal** to all handwritten strokes; they do not encode when a nib contacts paper, pivots or flicks. |
| 6 | Wang et al., **"Hierarchical offline-to-online Chinese handwriting trajectory reconstruction via dual-domain priors"**, *Journal of King Saud University – Computer and Information Sciences* (published 2026-08-21), https://doi.org/10.1007/s44443-026-01050-5 | Keep outline structure and motion priors as **separate constraints**; writing motion cannot be inferred from glyph image alone. | Replacing existing normative strokes by a neural model introduces training cost, direction/order risk, weak generalization to stylized Kaishu and licensing questions. Useful research backdrop, not initial implementation. |

### Special attention to pressure versus speed

- Wann & Nimmo-Smith (1991), **"The control of pen pressure in handwriting: A subtle point"**, https://doi.org/10.1016/0167-9457(91)90005-I, studies axial pen pressure **synchronously with xy trajectory** and shows contact/friction interplay. A naive `pressure = const / speed` rule is not justified.
- Gatouillat et al. (2017), https://doi.org/10.1016/j.compbiomed.2017.05.020, found drawing-quality changes under different timing/speed tasks without corresponding simple universal changes in measured tip normal force. The pressure and motion channels should be separately tunable.
- Pen-down and nib lift are *states*, not an extrapolated circular cap.

## 2. Open-source implementations actually inspected (no source copied)

### Tegaki (MIT; worth an isolated technical spike)

Repository: https://github.com/gkurt/tegaki
Technical docs: https://tegaki.ink/guides/generating/ and https://tegaki.ink/guides/rendering/

Read concrete source:
- `packages/generator/src/geometry/strokes.ts`: continuation scoring from direction, width and offset; degree-two sharp junctions stay a **single** brush stroke, while multiarm crossings need a matching rule. Our canonical stroke count must remain fixed, but this provides meaningful junction handling for contact state.
- `packages/renderer/src/core/pressure.ts`: pressure mixes each point's source width with mean width. It **does not** assert that velocity uniquely determines pressure.
- `packages/renderer/src/plugins/taper.ts`: separate start and end taper lengths; a single symmetric easing is inadequate.
- `packages/renderer/src/core/nib.test.ts`: extra **elliptical nib stamp** is painted only **when the pen reaches its attributed centerline position**; parameters include x/y offset, major/minor axes and rotation. Exactly the family of techniques needed for corners/terminal ink not covered by a circular cap.
- Its geometry pipeline describes **outline triangulation → chordal-axis / local width → spurs and corner nib stamps**; the raster alternative uses Zhang–Suen skeletonization and distance transforms. We already have canonical medians, so skip unreliable re-extraction; reuse *ideas* for inferring width and finding missing ink, never let this library silently reorder our strokes.

Licensing: library code is MIT, while the source glyph data remain separately subject to their own license. Any future vendored code must retain MIT copyright/permission notices. Current branch **does not vendor Tegaki code or ship its fonts**.

### Perfect Freehand (MIT; comparison baseline, not our primary renderer)

https://github.com/steveruizok/perfect-freehand
- Offers pressure-aware variable-width strokes with start/end taper, edge smoothing and stylus input; it can **simulate** pressure in absence of stylus data.
- It returns a new freehand outline; applying it directly as our final silhouette could violate the byte-identical source outline requirement. Evaluate only its **nib/contact heuristics** in a separate A/B experiment.
- Do not assume its synthetic pressure = actual pressure, especially for an expert Kaishu demonstration.

## 3. Empirical calibration candidates (verify license and access before use)

1. **CASIA-onDo** https://nlpr.ia.ac.cn/databases/CASIA-onDo/index.html : online Chinese/English document handwriting, each stroke includes `x,y, pressure, pen state, time`. Strongest input for phase transitions and nib contact if permitted; handwriting context/style differs from static source Kaishu.
2. **CASIA-OLHWDB** https://nlpr.ia.ac.cn/databases/handwriting/home.html : large Chinese online handwritten characters with trajectories; isolated-character records primarily encode `x,y` and stroke-end delimiting, so **do not assume timestamp/pressure** exists for all formats.
3. **Xu et al., 2026**, *Behavior Research Methods*, https://doi.org/10.3758/s13428-026-03001-4 : 42 Chinese speakers × 1200 handwritten characters; OpenHandWrite_Toolbox captures/analyses trajectory, stroke timing and some pressure attributes. Ground truth to infer distributions, not to copy annotations into our 201 canonical items automatically.
4. The Nature Communications 2026 study https://www.nature.com/articles/s41467-026-70536-7 records x/y/z, pressure and other dimensions; useful to check whether pen lifts are geometrically and temporally distinct. The task, sampling hardware and re-use rights must be reviewed.

**No raw handwriting datasets, handwriting samples, fonts or third-party code have been copied into zitie.**

## 4. A1.4 proposed three-layer engine (recommended approach)

Keep existing authoritative spatial geometry `O_i` (SVG path outline) and `M_i(s)` (ordered median), as well as the canonical stroke count/order.

### Layer A: motion planner (`motion.js` evolution)

Represent one source stroke as several **submovements** without changing canonical stroke identity. Candidate event types: `touch` (笔尖接触), `travel` (行笔), `brake` (折前制动), `pivot` (顿笔/转锋), `flick` (出钩), `lift` (提笔离纸).

Time-normalized scalar motion `s(t)` should remain monotone along the source median, but **speed and acceleration must be continuous except at explicitly labeled stationary pivots**. Candidate per-event speed curves: bounded overlap of lognormal pulses or a monotone Hermite/jerk-limited alternative if source data cannot support unique sigma-lognormal parameters.

Sigma-lognormal pulse (research *prior*, not estimated from our source):
`v_k(t) = D_k / [sigma_k sqrt(2 pi) (t-t0_k)] * exp(-(ln(t-t0_k)-mu_k)^2 / (2 sigma_k^2))` for `t>t0_k`.
Vector velocity uses overlapping directions from individual submovements. Preserve original median for progress-to-position mapping until a separately approved trajectory-refinement step.

**Do not** automatically classify a high-curvature corner as a hook, or force every hook to finish slower: hook release can be a short faster `flick` with simultaneous reduced contact, while a genuine fold can have `brake-pivot-travel`, all within one canonical stroke.

### Layer B: contact planner (new, orthogonal to motion)

At normalized source distance `s`, define synthetic contact state:
- `z(s)` / `touch(s)`: touching vs lifted (explicit, transitions near start/end);
- `p(s) ∈ [0,1]`: **normalized synthetic force/contact**, with independently controlled press/dwell/unpress; do not infer from inverse speed alone;
- `theta(s)` / `tilt(s)`: nib rotation (possibly with first-order angular lag at pivot);
- `a(s), b(s)`: ellipse axes, fitted from **existing stroke's contour cross sections** and limited by nib footprint constraints;
- `ink(s)`: optional optical deposition, **deferred** until realistic motion/contact is validated.

Contact should reach the paper before significant xy advance and withdraw gradually as the final flick moves; at a right-angle bend it can briefly stay in place while rotating and changing pressure.

### Layer C: source-clipped footprint renderer (new experimental renderer)

At each time `t` draw a pen-contact footprint:
`F(t) = ellipse(center=M_i(s(t))+offset(t), major=a(t), minor=b(t), angle=theta(t))`.

Visible red region:
`I_i(t) = O_i ∩ [union_{tau<=t} F(tau)]`.

Critical constraints:
- All intermediate paint remains inside `O_i`.
- Earlier paint never disappears; press/release alters **future** stamps, not already deposited ink.
- Each stamp has a bounded local time/position; cap/nozzle ink cannot leap to another arm merely because a wide circle overlaps it.
- For residual source silhouette pixels missed by physically plausible footprints, do not simply unmask the entire outline at 100%, causing a large jump. Evaluate **shape-referenced nib repair** as in Tegaki: infer small local ellipse stamps for terminals/corners with explicit arrival distances `s_stamp`. If residual is structurally substantial, flag **needs trajectory/contour review**, do not silently correct the canonical geometry.
- Keep exact original outline after completion.

An optional raster *arrival-time atlas* `T(x,y)` could be precomputed offline once per stroke as the earliest contact time of a footprint covering pixel `(x,y)`. Monotone reveal is threshold `T<=t`, clipped to `O_i`. This is an alternative optimized implementation of the same footprint union, not a new pen trajectory. SVG round fragments remain the stable fallback until visual/blur/performance QA proves otherwise.

## 5. Gesture exemplars (first six test glyphs)

| Example | Expected synthetic gesture stages | Specific failure to prevent |
|---|---|---|
| 一 — 横 | touch/press → travel → brake → release | Circle suddenly appears at first 2%; uniformly wide red snake; large last-frame contour snap |
| 口 — 横折 | travel → brake while still touching → pivot/rotate nib → travel | Instant 90-degree tangent/footprint jump, detached red triangle, artificial constant-speed corner |
| 水 — 竖钩 | vertical travel → brake at hook base → pivot → short **flick** with taper/lift | Every hook treated as slow stop; huge round cap; nib footprint rotates only after the pen leaves |
| 月 — 横折钩 | long horizontal → turn/pivot → vertical → flick/lift | Midstroke reversal or abrupt geometry, hook tip painted too early |
| 火 — 点/撇/捺 | dot contact footprint; sloping dynamic taper; independent stroke-phase labels | Dot treated as a long line; 撇/捺 terminal thickness copied from hook profile |
| 龠 — complex | many pen-down/lift cycles; test single-stroke local corner candidates | Cross-arm painting out of temporal order, excessive path nodes and mobile stutter |

Maintain source-policy fail-closed behavior: event labels above are engineering **candidate** states, not newly approved pedagogical stroke names.

## 6. Implementation options ranked

**Recommended**: retain zitie's small vanilla JS+SVG runtime and source data; add a separate experimental `pen-plan.js`/`nib-footprint.js` with sourced parameter defaults and source-outline clipping. Preserve baseline as the reference until A/B review passes.

**Second**: compare a minimal MIT Tegaki-derived nib/width rendering experiment on identical *canonical* median input; do not replace source stroke order or automatically run its font extraction pipeline. Check bundle size, future maintenance, source notices.

**Later only**: train end-to-end offline-to-online reconstruction against empirical handwriting or optimize lognormal parameters end-to-end from digitizer data. This demands paired input plus legal review, unbiased evaluation and care with Kaishu domain shift.

## 7. A/B acceptance specification — NOT currently passed

In a separate experiment page (do not overwrite `animation/index.html` or imply an official teaching release), render baseline A1.2.3 side by side with experimental pen-contact style for the six glyphs above.

- Deterministic shared elapsed time, stroke order, progress and speed buttons; same exact source outline, median arrays and source hash.
- Capture frames at time `0, 2, 5, 25, 50, 75, 95, 99, 100%` and denser local windows around each marked contact transition.
- Geometry guards: zero visible red pixels at t=0, **zero vanished previously rendered pixels**, zero outside `O_i`, no disconnected fragments, pen movement source-order monotone, no extra strokes, bounded terminal contour gap.
- Dynamics: plot `s(t), v(t), a(t), p(t), tilt(t)`; check continuous `v,p,theta` through phase boundaries (except deliberate still pivots), no sudden pressure/release radius changes, no negative/NaN.
- Style review: compare three independent questions (start/finish contact believability; turn/hook believability; overall naturalness), blinded A/B, expert review of each annotated event. A failed subjective review blocks default switch even if pixel tests pass.
- Browser/performance: Chromium first, then Firefox and WebKit where available; check desktop/mobile render frame time and retained SVG mask node counts. Do not promise 60fps without measurements.
- Source licensing and provenance: never redistribute fonts, never remove original Hanzi Writer ARPHIC license notice, no unapproved corpus copies.
- CI gates: baseline animation test stays green, experimental tests are named and separately reported; the official Pages preview remains A1.2.3 until the experimental renderer has explicit human acceptance.

## Decision

**Stop iterating the circular mask width or turn-slowdown constants as the main strategy.** The absence of nib contact state, stroke-gesture semantics and empirically informed microtiming is the likely cause of perceived artificial handwriting. Build the parametric pen-contact experiment first and preserve clear qualitative/quantitative acceptance gates before release.
