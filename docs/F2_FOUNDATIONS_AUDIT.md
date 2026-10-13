# F2 — Foundations teaching geometry & QA (non-certified)

Status: **engineering geometry audit in progress; NOT handwriting-pedagogy certification**.

## Source hierarchy and negative claim

- [中华人民共和国教育部《汉语拼音方案》](https://www.moe.gov.cn/jyb_sjzl/ziliao/A19/195802/t19580201_186000.html): spellings, phonetic alphabet, diacritics and Pinyin-system basis.
- [教育部对“拼音书写笔顺是否有标准”的答复](https://www.moe.gov.cn/moe_879/moe_1252/s8447/201412/t20141204_179361.html): **国家目前没有统一的拼音字母笔顺标准**；可以参考拉丁字母一般书写习惯。Do not present F1 animation paths as official standard stroke order.
- [教育部对“小学拼音采用何种字母体”的答复](https://www.moe.gov.cn/moe_879/moe_1252/s8447/201412/t20141204_179278.html): elementary-school Pinyin handwriting favors a single-storey a/g style in the referenced teaching context. F1's hand-drawn `a`/`g` are representative shapes, not a font-specific norm.
- [教育部“小学汉语拼音教学特色”](https://www.moe.gov.cn/s78/A18/A18_ztzl/jnhypyfa/201805/t20180517_336341.html): distinguish `b/d` and `p/q`, promote accurate tone placement and `j/q/x/y` dot omission in applicable spelling.

The 23/24/16 primary-school teaching groupings do not override the wording of the original national scheme. Printed stroke direction for digits/Latin/Pinyin **still requires a selected edition of the learner's textbook and human review**. We do not infer a normative digit-writing order from geometry.

## Measured geometry baseline

- Published category counts are fixed at **26 letter pairs, 10 digits, 23 initials, 24 finals, 16 whole-reading syllables, six four-tone sets, eight words** = **113 stable IDs**.
- The current vectors contain **470 discrete SVG paths** at this source revision. A dedicated Node path parser samples cubic curves (101 points / cubic) and validates full composition and path-cell bounds across *all* items, not only first-page examples.
- Four-line guide coordinates are `14 / 47 / 83 / 117` on a 132-unit board. Engineering geometry uses up to 2.5 units tolerance near top/bottom; digital lettering overshoots are not interpreted as correct pedagogy. Numeral practice uses an approximately square 64-by-66 source grid; the separate A4 print grid spreads cells across the actual printable width.
- The F2 real Chromium review iterates all **113 entries at 1200px, 800px, and 390px**, checks ink path and canvas sizes, and builds every category's A4 rows. This is *automated rendering evidence*, not measured penmanship.
- Expected A4 classification: letters 7, numbers 3, initials 6, finals 6, syllables 4, tones 2, words 2 pages. Each item has three exercise rows; no user data is needed to print.
- **Discovered F2 regression gap**: original 390px F1 smoke covered short initials but not long word shapes. The F2 full-catalogue Chromium run recorded `#board` at **760px** and `document.scrollWidth=781px` inside a 390px view after opening long words. Root cause: `.boardBox` used an implicit auto-sized CSS grid track, allowing the inline 760px canvas width to become the grid track's min-content size. F2 fixes the *track sizing* with `grid-template-columns:minmax(0,1fr)` and `min-width:0` rather than hiding page overflow. The 390px all-entry browser gate now protects this case.

## Upcoming pedagogical review checklist

| Subject | Items to review | Status |
| --- | --- | --- |
| English letters | Capital/lowercase A–Z; shapes, proportions, writing order, case distinction | Needs textbook / teacher audit |
| Digits | `0–9`, including `1` base, `4` joints and `8` double-loop behavior | Needs human audit |
| Pinyin shape | Single-storey a/g; `b/d/p/q` and `n/m` visual discrimination; standard four-line occupied rows | Geometry checked; teaching review pending |
| Tone marks | `ī í ǐ ì` dot removal; `ǖ ǘ ǚ ǜ` keeps two dots; first/second/third/fourth tone | Encoding checked; printed visual review pending |
| Spelling | `j/q/x/y` + ü point omission where applicable; `iu/ui` tone position; whole-reading syllables | Language rules review pending |
| Layout | desktop/tablet/mobile board and real A4 printed page scale | Chromium QA; physical A4 print pending |
| Browser support | iOS Edge pointer/touch handoff, physical Safari/Chrome/Edge and touchscreen pen devices | F1.1 integration + device retest pending |

## Why all 470 paths are not being rewritten

Stroke paths currently have an **engineering-only** provenance, and the Ministry confirms no national Pinyin letter stroke-order sequence. Programmatically smoothing/reversing every path or changing glyph shapes without a named teaching style would produce *unjustified certainty*. We first establish stable geometry and explicit visual checks; any later geometry revision will have source rationale and side-by-side screenshots for human acceptance.

## Release governance

F2 is strictly additive to `animation/foundations/` tests and the QA workflow. It does not change F1 learning text, draw order, localStorage keys, browser touch handlers, 299-page v0.5.1 PDF, or any of the 201 Hanzi/1045 brush animation references. Require exact-head A1+Book CI and post-merge same-SHA Pages Deploy for shipping.

Related: [F2 issue #169](https://github.com/netplus/zitie/issues/169), [F1 design](F1_FOUNDATIONS_COPYBOOK.md).

## F2.2 — Per-entry learning cues (pending release gate)

F2.1 checked the physical geometry but did not tell learners *what to observe*. F2.2 supplies a **pure local, provenance-classified note** for each of the unchanged 113 entries. `animation/foundations/teaching.js` has three explicit cue categories: `spelling` (orthographic/tone rules), `recognition` (primary-school look-alike mnemonics), and `geometry` (non-certified engineering shape observations). A single concise tip appears beside the real practice grid; one short version is also included in each A4 printable item heading. No duplicate sidebar or persistent hint state.

### Rule references

- [MOE: 汉语拼音教学特色](https://www.moe.gov.cn/s78/A18/A18_ztzl/jnhypyfa/201805/t20180517_336341.html) — classroom b/d/p/q and n/m discrimination, omission of ü dots for specified y/j/q/x spellings, tone placement reminders.
- [GB/T 16159—2012 §6.5, hosted by MOE](https://www.moe.gov.cn/ewebeditor/uploadfile/2015/01/13/20150113091717604.pdf) — in `iu` / `ui`, tone mark is written over the **second letter**; tone on `i` removes the ordinary `i` dot. This is an orthographic rule, unlike the unregulated pen-motion stroke sequence.
- [MOE's Latin/Pinyin stroke-order clarification](https://www.moe.gov.cn/moe_879/moe_1252/s8447/201412/t20141204_179361.html) — no national unified Pinyin handwriting stroke-order standard.

### Coverage

- b/d: left/right position of stem/circle, p/q: which side has the descender; n/m: count humps; zh/ch/sh: two-letter combos; y/w recognition.
- Individual `ü`, `üe`, `ün`: retain double dots while practiced as final entries. `yu/yue/yuan/yun` whole syllables: explain y-related omission. `i` tone family `ī/í/ǐ/ì` omits i's dot; `ǖ/ǘ/ǚ/ǜ` retains ü diaeresis. `iu` and `ui` cue examples `liú` and `shuǐ` respectively.
- Generic fallback notes for every other English letter, digit, Pinyin initial/final, whole syllable and basic word. **No change** to glyph path, animation ordering, item key, data storage format, iPhone Edge input compatibility, original Hanzi PDF or A3 stroke data.

### Test gates

`animation/foundations/teaching.test.cjs` checks 113/113 notes, evidence classifications, high-risk pairs, i/ü tone exceptions and y-spelling. F2 full Chromium review checks every entry's actual onscreen tip and its printed A4 heading in 1200px/800px/390px viewports. Pages must bundle teaching.js locally and reject a missing file; independent F1 and F2.1 tests remain mandatory. The notes still require educator-facing terminology review, and physical A4 and iPhone Edge acceptance remain outstanding.
