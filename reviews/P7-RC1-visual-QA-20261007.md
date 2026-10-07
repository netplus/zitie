# P7 v0.4.0 RC1 visual QA — 2026-10-07

Scope: release-candidate rendering only. Same-agent QA; not an independent second reviewer.

## Candidate under review

- source commit: `37ecce8f0f8447d0405b0b1a342863f8e1e844a8`
- workflow run: `37569445886`
- artifact: `11460206893 zitie-p7-draft-and-rc1-research`
- artifact digest: `sha256:897bbbc80b432900b0d1cd5e19386a40cb796177240e5b065fde3b5d8b565d12`
- candidate file: `B01-B21_with_preface_toc_appendices_rc1_A4.pdf`
- pages: 276
- formal release: still 0

## Full-text preflight

The generated RC1 contains:
- 0 occurrences of `编写中`;
- 0 occurrences of `编写稿`;
- 0 occurrences of `前言初稿`;
- 3 candidate markers on the 3 preface pages;
- 258 candidate markers on the 258 practice pages;
- 261 `发布候选稿 RC1` markers total.

The source-blocked / conflict-fail-closed disclosure remains present, including the GF0011—2022 item-level boundary. The version page still states formal release is 0 and `deliverables/releases/` remains empty.

## Actual rendered-page review

Rendered at 150 dpi and actually viewed 16 representative pages:

`1, 3, 4, 5, 6, 238, 259, 260, 261, 263, 264, 269, 270, 273, 275, 276`.

These cover:
- candidate preface first/last pages;
- both TOC pages;
- a normal low-stroke practice page;
- B20 complex continuation pages;
- B21 龠 17-stroke first/last continuation pages;
- first/last 201-main-radical index pages;
- teaching variant index;
- historical V001—V027 table;
- source ledger;
- version/release-status page.

Result: **16/16 representative RC1 pages passed visual QA**. No obvious clipping, overlap, black squares, broken CJK glyphs, or candidate-label misplacement was observed.

## Inherited visual coverage

This RC1 review does not pretend to re-review every unchanged geometry page from scratch.

- The 258 practice pages were already fully rendered and visually reviewed in P6; RC1 changes the status label/preface mode, not stroke artwork geometry.
- The 15 P7 TOC/index/back-matter pages were already fully rendered and visually reviewed in the structured-draft QA.

References:
- `data/evidence/P6-full-book-layout-review-20261007.json`
- `reviews/P6-full-book-layout-review-20261007.md`
- `data/evidence/P7-structured-draft-visual-QA-20261007.json`
- `reviews/P7-structured-draft-visual-QA-20261007.md`

## Boundary

RC1 QA passing does not itself create a formal release. RC1 must still pass its target-HEAD CI and be archived as a release candidate before the final formal-release gate.
