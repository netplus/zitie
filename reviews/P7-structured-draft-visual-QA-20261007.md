# P7 structured draft visual QA — 2026-10-07

Scope: PR #49 structured navigation/back-matter additions only. Same-agent review; not an independent second reviewer.

## Build under review

- source commit: `a0fec601f3cb8a8833e662cec57d3ef56293edd6`
- workflow run: `37564891335`
- artifact: `11457814109 zitie-p7-structured-draft-research`
- artifact digest: `sha256:3923aaafe54af8706c3b2e9722a1b6735d50363f56ef5d00b5839d21556e8af5`
- collection: `B01-B21_with_preface_toc_appendices_draft_A4.pdf`
- total pages: 276
- release status: still fail-closed / not released

## Actual visual review

Rendered the complete set of pages newly introduced by this P7 structure change at 170 dpi and viewed them all:

- pages 4-5: 2 TOC/navigation pages
- pages 264-269: 6 pages of the 201-main-radical index
- pages 270-271: 2 pages of the 32 teaching variant candidates
- pages 272-273: 2 pages of the historical V001-V027 regression subset
- pages 274-275: source/field-review summary and source ledger
- page 276: version/errata/release-status page

Result: **15/15 newly introduced pages passed visual QA**.

## Specific checks

- TOC page ranges are legible and unclipped.
- Main-radical index is now actually sorted by `main_id`: 001 through 201.
- Final main-index entry is `201 龠 / B21 / 261-263`.
- V001-V032 are all present in the teaching variant index.
- V001-V027 are all present in the historical regression subset.
- Source-ledger titles no longer use hard string truncation; long D01/D02/D03/D04/S09/A01 labels render fully without clipping.
- Version page still says formal release is 0 and `deliverables/releases/` remains empty.
- No newly introduced page showed clipping, overlap, black squares, or broken CJK glyphs in the reviewed render.

## Boundary

This record does **not**:
- re-adjudicate the semantic content of the existing 258 practice pages;
- upgrade any GF0011-2022 source-blocked field;
- archive the 276-page file into `deliverables/drafts/`;
- update the manifest;
- create a release candidate or formal release.

Existing P6 artwork/layout review plus current CI regeneration continue to cover the practice-page pipeline. This QA closes only the P7 navigation/back-matter visual-review gate for PR #49.
