# P2.2e — Reuse the blank space beneath pressure styles

2026-10-13. Tracks [Issue #157](https://github.com/netplus/zitie/issues/157).

## Verified cause

The source paper is a square up to 410 CSS pixels. The right-hand 220px pressure style control has content-defined height; in default Stable mode its pressure graph is intentionally hidden, leaving a visually large unused region below. In Simulated mode, the graph is shorter than the paper and leaves a smaller gap. This is not a missing pressure widget.

## Layout solution

The source paper keeps its original dimensions. The **existing sticky pressure controller remains compact** at the right top. Do not stretch the original controller to the full square height: its A3.8 sticky-scroll behavior depends on remaining free scroll space.

The right column now has a second, independent read-only guide immediately below the pressure controller. It shows the **second unchanged PDF-authored writing tip** and original **写完检查** as an optional reminder, with a native link to the unchanged complete authored tips. It never fabricates individual-stroke scoring or real physical pressure.

CSS Grid constrains both right-column rows to the paper's current square height; the guide has zero minimum height and clipped overflow when compact, so it cannot push the original playback controls out of first screen. Stable mode shows the completion check. Simulated mode prioritizes its telemetry and chart, using a shorter source note and omitting redundant completion check, which remains in the full source block.

Phones and narrow tablets up to 720px keep the already-reviewed pressure strip ABOVE the paper and **hide the redundant side guide**. The existing first source tip/full detailed tips remain. Short wide-screen heights under 700px use the pre-existing layout instead of squeezing in extra content.

## Verification

The new real Chromium test checks both Stable and Simulated in 1440×900, 1366×768, 1020×768, 800×900, 390×844 and 390×667, including the preserved A3.8 sticky pressure on scroll, unchanged real pressure curve, source text after selecting complex 鼻, and one-screen playback control positions. Existing A3.8/A3.9/P2.2c/P2.2d and P2.2a practice tests remain mandatory.

Scope explicitly excludes the 299-page released PDF, B01–B21 source data, all 201 glyphs/1045 medians, A3.6 ink front, A3.7 pressure simulation, learner blue stroke captures, IndexedDB, original matcher and font distribution.

Release gate: exact PR-head A1/Chromium and Book integrity must both complete successfully before merge. Verify actual GitHub Pages Configure, Upload and Deploy on the SAME main merge SHA before claiming live availability. iPadOS/Android stylus hardware certification is separate.
