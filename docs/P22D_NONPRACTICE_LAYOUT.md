# P2.2d — Non-practice A3 teaching homepage information hierarchy

Status: 2026-10-13; user request in Issue #155. This is a standalone **normal lesson view** redesign. The immersive P2.2a overlay, drawing input, 201-glyph PDF source and existing A3 renderer are out of scope.

## Previous page and diagnosis

Real P2.2c QA screenshot (1366×768 and 390×844) showed: historical research/old-version links dominate the mobile header; mobile hides the “临摹” label and leaves only a pen icon; PDF-authored source tips are cramped between stroke title and a phase label (ellipsized even when the paper is visible); controls are a dense flat row; B01–B21 batch chips wrap across multiple rows and compete with the teaching paper. The 201 character tiles occupy the most visually dominant section of the right rail.

## Revised hierarchy (only the A3 teaching page)

1. **Lesson-first header:** Short, recognizable brand and dataset provenance. Secondary experiments/old player are still reachable from a keyboard-accessible native “更多资源” disclosure, collapsed by default. Do not remove either external route.
2. **Hero teaching paper:** The current source glyph, pronunciation/provenance and an accent-colored explicit **开始临摹** button above the existing paper; previous/next glyph navigation stays adjacent. Mobile has a first-screen **选字** jump to its catalog. Keep SVG viewBox and native pressure-side/above writingStage structure entirely unchanged.
3. **Readable book-authored note:** Keep the original live stroke/phase label on row one, and present the *same* exact glyph.tips[0] in a full-width, two-line, linked “✎ 书写提示” card on row two. The entire original tips and check section remains below, reachable by its anchor. No invented, teacher-certified or pressure advice.
4. **Controls with intent:** Arrange play/restart/show-whole-character and previous/replay/next into a compact responsive grid, with speed as a secondary segment; all original IDs and event handlers retained. Preserve enough initial viewport for playback controls on 1366×768, 1020×768, 800×900 and 390×844, and honor the prior short-phone scrolling allowance.
5. **Calm searchable directory:** Keep all 201 source-backed tiles and existing search/filter semantics. Batch filters form one horizontally scrollable row rather than three vertically wrapped rows. Four larger columns on desktop and five on narrow phones. On ≤860px, clicking a glyph in the directory repositions the already updated teaching hero to view, avoiding manual upward scrolling. No new remote persistence, no extra UI modal.
6. **Responsive-only styles:** Separate main-layout.css overrides are scoped to normal page selectors. Existing practice.css overlay remains unchanged. The GitHub Pages static-site package must include the additional CSS; a green workflow without the CSS in _site is not deployment success.

## Acceptance

- Retain IDs/event semantics, every source glyph, original SVG pigment/front guard, stable/simulated pressure, existing PDF link, blue-pencil practice bridge, IndexedDB and whole-word order feedback.
- Node source/HTML/offline packaging contracts plus true Chromium QA, not DOM stubs.
- Measured screen coordinates and direct user events in 1440×900, 1366×768, 1020×768, 800×900, 390×844 and 390×667, including input/search/selected glyph scroll-back, pressure switching and authored hint sync. The compact A3.8/A3.9 and P2.2c regression gates must remain green or be revised only when the new user UX intentionally supersedes their geometry rule.
- Preserve older A3.9 mobile square width upper limit (≤272 CSS px) until browser evidence supports expanding it; this PR deliberately keeps the compact mobile board.
- Final **exact PR head** A1 Chromium + Book integrity success before merge. Then verify **the same main merge SHA** Pages Configure, Upload and actual Deploy all success. Inspect real screenshots for professional layout quality, not just numerical bounds.
- No font files, externally hosted resources or learner captures are distributed. iOS/Android Pad physical-device acceptance remains separate.
