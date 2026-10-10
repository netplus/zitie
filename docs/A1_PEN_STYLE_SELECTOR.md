# A1.6 — Two pressure styles on the deployed stable animation page

2026-10-10 · [Issue #104](https://github.com/netplus/zitie/issues/104)

## Product behavior

The deployed `animation/index.html` player now offers a directly clickable **笔压风格** selector with exactly two modes.

| Setting | Default | Pen cursor | Original ink / timing |
|---|---|---|---|
| **稳定版** | Yes | Exact original 8-source-unit round marker; previous red fill and white edge | Unchanged A1.3 round-capped source-clipped union and deterministic motion |
| **模拟笔压版** | No | Same **existing corrected optical cursor position**; pressure-dependent round marker radius and non-white unfilled contact ring, with normalized contact % / semantic phase / position-pressure mini curve | Identical SVG red reveal, source medians, stroke order, playback timeline, arclength and speed |

Users select the mode **within the main page**, not by navigating to a different A/B URL. The choice remains active when selecting another character or operating seek, rewind, replay, pause, next stroke, show all and 0.5–3× speeds. Switching modes must not alter wall-clock position, playing state, chosen glyph, total duration or original mask. Opening a fresh page defaults to the proven stable style (no storage, permissions or external runtime dependencies).

## Implementation boundary

- `animation/pressure-style.js` is a presentation-only adapter attached **after** the existing `StrokePlayer.render()`, via its documented `onUpdate` callback. No edits to `animation/player.js`, `brush-union.js`, `motion.js`, `timeline.js` or packaged canonical `samples.js`.
- Its only stateful geometry is an optional SVG `circle` **outside** `<defs>` and outside all original stroke masks. Stable mode keeps no ring in the SVG tree.
- Reuse the reviewed-for-engineering A1.5 `ZitiePressureModel` spatial synthetic prior and unreviewed `ZitieGestureCandidates` pivot indices. The pressure algorithm is independent of velocity and cannot infer actual force.
- Synthetic cursor geometry matches the A1.5 side-by-side demo: inner radius `7.2 + 8.8 P(s)`, outer ring radius `radius + 4 + 5 P(s)`. No opaque white ring may be painted in simulated mode. At pen-up, pause between strokes and full completion, simulated pressure returns to zero and the outer ring disappears.
- The small curve shows `P(s)` over normalized *spatial arclength*, with an instantaneous indicator position. The 0–100% number is dimensionless synthetic contact intensity; it is **not** newtons, pressure sensor force or teacher-approved handwriting. Curve/circle intensity is not used as a final glyph fill mask.

A1.5's isolated lab remains separately available for side-by-side comparison but is no longer the only way to select simulated force. The earlier A1.4 variable-ellipse experiment remains research-only and is not part of either mode.

## Verification

- Node `animation/tests/pressure-style.test.cjs`: exactly two choices, stable initial default, strict input validation, monotonically increasing circular contact size and unfilled non-white halo, all nine original glyphs and complex strokes accepted without source edits, pressure independent of global speed.
- Real Chromium `animation/tests/pressure-style-smoke.html`: all 9 source-backed characters across 45 writing frames. Compare red-ink bitmaps and **exact SVG mask child markup** before/after style change. Assert zero mismatches, original stable circle restoration, no post-timeline force ring, unchanged elapsed/phase/speed/playing state, preserved mode on glyph navigation, keyboard-compatible button semantics and responsive 390px layout.
- Original 40-stroke pixel-integrity test, previous A1.3 optical cursor test at 512/1024px and A1.5 six-glyph 60-frame A/B pressure test must continue to pass. The new code is part of the existing `A1 animation checks` CI and the Pages release checks; source assets remain offline-compatible.
- Exact final PR HEAD A1+Book integrity checks, merge, and **successful Configure/Upload/Deploy** of GitHub Pages on the actual merge SHA are required before claiming production deployment. v0.5.1 299-page PDF, historical releases/manifest, 201 canonical teaching records and source policy are untouched.

## Scientific and pedagogical limits

See [A1 pressure evidence and licensing audit](A1_PRESSURE_RESEARCH.md). CASIA-onDo/OHFC and DCOH-120K have access/licensing restrictions. No raw third-party pressure samples were acquired or bundled. The visualization is an honest engineering illustration, not calibrated hand force and not an approved handwriting teaching motion. Empirical fitting, device normalization and naturalness evaluation remain independent future research.
