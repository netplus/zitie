# P2.2g — Production teaching defaults: 0.8× and simulated pressure

2026-10-13, [Issue #161](https://github.com/netplus/zitie/issues/161).

The user requested that the **main published 201-glyph A3 teaching page** open with slower animation (**0.8×**) and **模拟笔压版** selected.

## Exact behavior

- On initial `animation/book.html` load, default to 0.8× playback rate, with matching `aria-pressed` state. Keep 0.5×, 0.8×, 1×, 1.5× and 2× all selectable without switching the stroke source, silently seeking, or changing brush trajectories.
- Initialize the **page-level** A1.6 StyleController to simulated *before* selecting the canonical source glyph. Present the synthetic pressure controls and curve as active; retain the explicit "合成演示，非实测笔压" disclaimer, because simulated pressure is not hardware input.
- A direct change to stable or another speed is honored through glyph selection and user practice-overlay entry/exit. Restart changes the play position only. On a hard reload the documented defaults apply afresh. No localStorage or IndexedDB settings writes.
- Do **not** modify underlying A1.6 `StyleController` intrinsic stable constructor; previous experimental pages may depend on this stable baseline. Do **not** modify `StrokePlayer` speed validation or animation timebase. No pressure profile recalibration.
- Keep P2.2f's responsive source guidance: simulated pressure defaults to showing its supplemental note in the lower continuation, not in the side region, on large screens; the first hint stays near paper.

## Checks

- Node source contract and actual Chromium iframe test for 201/1045 source integrity, actual 0.8× player state + selected speed button, visible simulated curve, truthful pressure source, manual stable/1×/2× overrides, glyph navigation, full-word practice round-trip, reload resetting defaults, and UI under 1366×768 / 1020×768 / 800×900 / 390×844 / 390×667 (short phones may scroll).
- Update A3.7 pressure-raster/controls and A3.8 sticky panel browser expectations from old stable-default, without weakening the 12 frame ink identity checks. A3 book browser tests include the fifth speed; P2.2d 11 total playback/speed buttons and A3.9 first-screen visibility remain enforced.
- Formal 299-page PDF, 201 glyphs/1045 source strokes, nib frontier, original practice capture and IndexedDB remain immutable.
- Exact PR HEAD A1 real Chromium and Book integrity must complete/succeed before merging. After merging require actual same SHA GitHub Pages Configure/Upload/**Deploy** completed/success; real stylus hardware not certified.

## Raster-audit adjustment for simulated startup

A3.0 and A3.6 legacy Chromium tests previously hid the moving nib while pixel-counting **source ink**, but did not hide the separate simulated red **force-ring SVG circle**. With simulated pressure now the default, ring pixels could be mistaken for vanishing source pigment when the marker moves even though canonical masks/paths are unchanged. The raster helpers now **temporarily hide and restore both the nib and the simulated pressure ring** while measuring only source bitmap pixels; A3.7 independently continues to test the force ring and requires ink-identical stable/simulated output. No production rendering code or acceptance thresholds have been altered.
