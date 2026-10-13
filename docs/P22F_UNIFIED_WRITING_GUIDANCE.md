# P2.2f — Responsive deduplication of PDF-authored writing guidance

Status: 2026-10-13; implements [Issue #159](https://github.com/netplus/zitie/issues/159).

## Reconciled user feedback

The user repeatedly requested a writing-first lesson layout: readable author-backed guidance beside the paper, no dead space below the pressure panel, preserved simulated pressure curve, all playback controls in the initial laptop/phone viewport, and finally removal of the repeated full “02 字帖原有书写提示” at the bottom. The last redundant block repeated **every sentence** already shown in a first tip card and a side guide. Furthermore the side guide's old space-between stretching separated short sentences vertically, and the simulated-mode CSS clipped or hid the only local copy of the completion check.

Source audit of the official released v0.5.1 pack confirms **201/201 characters each has precisely two authored tips and one nonempty check**. There is no need to invent content or to drop any original teaching note.

## One visible complete reading path for each device and mode

- **All states:** first original source tip displayed prominently immediately below the square and next to current stroke/phase information. This sentence is **not** repeated anywhere in a long default block.
- **Wide desktop/Pad, stable pressure:** compact original sticky pressure controls stay beside the paper, followed by a readable, normal-flow side guide containing **only** the second original tip and the original **写完检查**. The guide is independently vertically scrollable if needed, rather than clipped or artificially spread to fill the paper.
- **Wide desktop/Pad, simulated pressure:** the full synthetic telemetry/curve remains visible. The side supplement is not squeezed into the tiny leftover region; instead the same second original tip and original check appear once in a compact continuation **below the original stroke navigator and PDF link**. This preserves A3.9's first visible stroke-jump button on a tall desktop.
- **Mobile / short viewports:** unchanged pressure strip above paper; first tip directly below paper; remaining original tip + check appear once in the same compact continuation below original stroke steps. No additional block pushes first-screen playback controls downward.
- The source tip's existing native anchor always targets the *actually visible* side guide or continuation, on glyph selection, viewport resize and pressure-mode switches. No hidden or dead anchors.
- Remove the numbered duplicate “02” section; rename the original stroke navigator “逐笔示范 · 点按笔画跳转”. Do not change any of its controls or the real PDF page link.

## Non-negotiable invariants

No edits to formal PDF 299 pages, source 201 glyphs/1045 SVG paths, B01–B21, A3.6 nib/ink frontier, A3.7/A3.8 pressure controller, A3.9 short-screen behavior, practice overlay, original learner blue traces, IndexedDB, matcher, restricted stroke labels, fonts or cloud synchronization.

## QA

Old P2.2c/P2.2d/P2.2e browser tests must be updated to the intentionally revised source-text contract; **no silent weakening** of first-screen controls, pointer-up capture or pressure-stickiness gates. Enhanced P2.2e real Chromium test verifies six viewports × stable/simulated, exact complementary source text and active link destination, with only one supplementary panel visible. Node contract verifies two-source-tip split and responsive CSS visibility. Before merge, exact PR HEAD A1/Chromium + Book-integrity completed/success. After merge, the same merge SHA Pages Configure, Upload and actual Deploy completed/success. Real iPad/Android stylus hardware acceptance remains separate.
