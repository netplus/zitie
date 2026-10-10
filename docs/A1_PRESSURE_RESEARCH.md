# A1.5 — Evidence-led pen-pressure research and stable-renderer experiment

2026-10-10 · [Issue #101](https://github.com/netplus/zitie/issues/101)

## Decision and scope

User prefers the **A1.3 stable round-brush/player** over the A1.4 ellipse-contact experiment. Keep the stable painter, its source outlines, medians, stroke order, kinematic timeline and source-front-aligned round cursor unchanged. Add a separate pressure **demonstration** in an opt-in A/B page only. Synthetic normalized intensity is **not** measured pressure, absolute force, an empirically fitted coefficient, or teaching approval.

## Data sources — distinguish *availability* from *license*

| Source | Channels / relevance | Legal/access boundary | Current use |
|---|---|---|---|
| [CASIA-onDo](https://nlpr.ia.ac.cn/databases/CASIA-onDo/index.html), CASIA/NLPR, ACPR 2021 | Chinese/English document strokes with X, Y, pressure, pen state, timestamp; 2,012 documents, 200 writers | Academic research requires an agreement; published site explicitly prohibits commercial use under that agreement and charges for commercial license. A download URL is **not** redistributable permission. | Format and domain reference; **no source files acquired** |
| [CASIA-OHFC](https://nlpr.ia.ac.cn/databases/CASIA-OHFC/), CASIA/NLPR | InkML channels X/Y/F/S/T, including pen-down/move/up; flowcharts and text, not a canonical Kaishu dataset | Academic-research agreement and no commercial reuse under the academic agreement | Format reference; **no files acquired** |
| [DCOH-120K](https://github.com/SCUT-DLVCLab/DCOH-120K), Li/Peng/Jin 2025 | 83,142 Chinese text lines and 39,398 English lines; samples store X, Y, stroke ID, timestamp, tilt X/Y and pressure | Must apply and receive approval; CC BY-NC-ND 4.0, noncommercial research and no derivative redistribution | Promising eventual pressure+tilt calibration; **not downloaded** |
| [SVC2004 Task 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6891754/) | X/Y, timestamp, pressure, azimuth, altitude, button state at 100Hz; signatures | Dataset-specific access terms require separate verification; signatures do not represent elementary handwritten Chinese strokes | Potential signal-processing crosscheck only; not used to fit Chinese gesture priors |
| [CASIA-OLHWDB](https://nlpr.ia.ac.cn/databases/handwriting/Online_database.html) | Online isolated character POT records specify x/y and delimiters | Do **not** infer an F/pressure channel absent from the documented POT format | No pressure training from this dataset |

**Policy**: The public repo contains *zero* third-party raw pressure samples and no claims of empirically fitted pressure values. A later data-import/calibration phase needs a license review, provenance by device/writer, format inspection and train/validation/test separation. The optional lab works offline on our existing nine packaged glyphs and contains only **synthetic** pressure.

## Paper/implementation review

1. **Schomaker & Plamondon (1990),** *The Relation between Pen Force and Pen-Point Kinematics in Handwriting*, Biological Cybernetics, DOI [10.1007/BF00203451](https://doi.org/10.1007/BF00203451). Pressure–kinematic coherence was often low in cursive handwriting; speed is **not** a uniquely valid pressure ground truth.
2. **Gatouillat et al. (2017),** *Analysis of the pen pressure and grip force signal during basic drawing tasks*, Computers in Biology and Medicine 87:124–131, DOI [10.1016/j.compbiomed.2017.05.020](https://doi.org/10.1016/j.compbiomed.2017.05.020). In its studied drawing tasks, changing speed/timing did not significantly change normal pen force. Thus do **not** map pressure = 1/velocity.
3. **Wong & Ip (2000),** *Virtual brush: a model-based synthesis of Chinese calligraphy*, Computers & Graphics 24(1):99–113, DOI [10.1016/S0097-8493(99)00141-7](https://doi.org/10.1016/S0097-8493(99)00141-7). Parameterized brush geometry/orientation/ink deposition are compelling for a real brush; **not** an algorithm to blindly replace fixed-source Kaishu outlines or use an elliptical pointer.
4. **Plamondon (2013),** [*The lognormal handwriter: learning, performing, and declining*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3867641/) explains velocity reconstruction in motor submovements, **not** direct pen pressure prediction. Our existing motion profile can remain an independent time-to-distance map.
5. **Perfect Freehand (MIT),** [source](https://github.com/steveruizok/perfect-freehand): `[x,y,pressure]` inputs, `simulatePressure=false` for measured pressure; pressure-aware thinning/tapering can be optional rendering concepts. Do not import package/source or override our canonical published font glyph path.

## A1.5 research-only pressure prior (not fitted)

We use **arc-length parameter** `s ∈ [0,1]`, not a velocity-derived pressure, and a gesture-specific smooth function. Write:

`P(s) = clamp(envelope(s) × (base + pivot_bump(s) + dot_bump(s) − release(s)), 0, 1)`

- Contact envelope: `smoothstep(s / onset)` at start and `smoothstep((1-s) / lift)` at end. Both zero at the exact endpoints.
- Base contact intensity: conservative regular pen (~0.52 dimensionless). It is a subjective visualization parameter, **not calibrated normal force**.
- Pivot: Gaussian local **additional** pressure for curated, explicitly unreviewed fold/hook candidate `pivotVertex`, from the immutable original median arclength. No source point moves.
- Hook flick/sweep: smoother release toward lift; dots use a modest midstroke bump. All gesture labels are explicitly `engineering_heuristic_only`.
- Retiming: use the existing `ZitieTimeline.frameAt` and its motion curve; `P(s)` is independent of `v(t)`. Changing the 0.5–3× display speed alters only the timeline clock, never pressure at the same source position.
- Visual effects **only**: B-side circle radius and an *unfilled non-white* outer ring respond to `P(s)`; numerical % and pressure-vs-position curve are visible. The exact red SVG ink and canonical source remain identical in both panels.

This architecture avoids the past flat-ribbon terminal-gap and moving-white-hole regressions. A percentage is **synthetic normalized contact effort**; it must not be labeled N, kPa or digitizer-measured percentage.

## A/B acceptance

- **6 glyphs:** 一 (horizontal), 口 (fold), 水 (vertical hook), 月 (fold hook), 火 (dot), 龠 (complex folds). Original A1.3 stable renderer is used twice; visual overlay is independent of SVG source mask.
- Automated node: 0 at contact absence, bounded 0–1, finite and smooth across dense fractional sampling, independent of playback multiplier, reproducible and deterministic, pivot candidate effects, immutable source data, no extra strokes or alternate direction.
- Browser QA: synchronize elapsed time, exact original `path d` and stroke counts, compare A/B **red pixel bitmap** at sampled frames with tip/ring excluded (no ink differences), no white overlay, no erased ink, pressure gauge/curve finite, start/end contact zero.
- Keep stable baseline 40-stroke pixel integrity, 2× DPR, full-book/manifest gates. Only after PR final-head checks pass may the experiment be deployed separately. Do **not** swap the standard player, fit proprietary data, or call this authentic handwriting dynamics.

## Later research (separate authorization)

Seek appropriately licensed handwriting traces and normalize raw pressure per device, writer and stroke (calibration needed; raw 0–1024 / 0–4096 units can differ). Compute pressure-position consistency, cross-writer variance, velocity/pressure correlation, phase-conditioned confidence intervals, and train/validation split. Calibrate `base`, `onset/lift`, `pivot bump` only if traces are verified comparable to Chinese primary-school regular-pen writing. If calibration is not justified, retain a clearly labeled demonstration rather than fabricate certainty.
