# P2.2c — Place writing tips in the active handwriting viewport

User-requested layout improvement, 2026-10-13. Tracks Issue #153. This is **presentation only**.

## Verified root cause and accepted design

In the published 201-glyph animation, the original “02 字帖原有书写提示” appears below the handwriting paper, playback controller, stroke-step buttons and PDF-page link. On laptop 1366×768 and 390×844 phone, it is off-screen during writing. In the immersive P2.2a overlay, the active ordinal/stroke label, generic pointer-up instruction and final conservative order verdict appear in an action panel **below the canvas**, which is especially difficult to use on portrait phones and tablets.

**Main A3 player:** Place a prominent “✎ 书写提示” source preview on the **existing progress row next to the drawn stroke**, showing exactly the first source-authored note (glyph.tips[0]); no paraphrase or new teaching claim. On narrow phones, truncate with ellipsis rather than wrapping the row and hiding controls. The link jumps to the original *full* teaching hint block, which still contains all tips and the unmodified “写完检查” (glyph.check). Both preview and full text refresh for every glyph selection.

**Immersive practice:** Relocate the existing practiceStrokeTitle and practiceStrokeHint **above** practiceBoard and its real blue Canvas. Add an exact first authored PDF hint in this visible guide. Move the same original practiceOrderResult there, so the conservative whole-word order result is visible beside the drawing when completed. Do not duplicate results or pretend that a whole-character note is a per-stroke validation. Leave undo, instant whole-word restart (no confirmation), local IndexedDB persistence, safe exit and brush reference unchanged.

**Layout and accessibility:** The practice guide and square canvas share matching responsive width limits; landscape budgets enough height for the guide. The main preview uses an existing row instead of introducing a tall banner. The preview is a keyboard-focusable native anchor with the complete source notes available as a title; the full original notes stay readable. The verdict retains role=status and aria-live=polite; no live region is added to the stroke title, avoiding redundant announcements during pointer movement.

## Regression and release gates

- Node: unique DOM IDs; preview precedes main controller, complete original tips/check preserved, current-stroke cue and result precede actual touch Canvas, no restored restart confirmation dialog.
- True Chromium in CI: main **1366×768, 1020×768, 820×1180, 390×844, 390×667**, with prominent source hint, nonoverlapping text, horizontal-scroll-free layout and old A3.9 playback/pressure controls still first-screen visible at previous required heights. Complex glyph 鼻 must refresh the exact long source tip/check.
- Practice **820×1180, 1180×820, 390×844, 390×667**, with the current reference and book hint above the square board within the first viewport; source coordinates/ink do not shift. Four genuine pointer strokes of 水 naturally advance without per-stroke confirmation, completed conservative verdict is above the paper and one-click restart remains immediate.
- Record structured QA dimensions and screenshots of the real published iframe, not mocked artwork.
- Exact PR final SHA A1 browser + Book integrity both completed/success before merge. Then verify GitHub Pages Configure, Upload and actual Deploy against that same merge SHA.

## Strict scope exclusions

No changes to published 299-page v0.5.1 PDF, B01–B21 teaching records, 201 glyphs/1045 original median paths or source manifest, original A3 brush/player/pressure/ink-front guard, stroke-order matching rules or isolated direction experiment, stored learner inputs, IndexedDB schema, or external font licenses. No tablet hardware certification is implied.
