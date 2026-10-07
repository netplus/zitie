# P7 formal v0.4.0 visual QA — 2026-10-07

Scope: final formal-release preflight PDF. Same-agent QA; not an independent second reviewer.

## Build under review

- source commit: `c52ce98fc80a598de9daa2654a0f51181eb7d072`
- workflow run: `37570728721`
- artifact: `11460508300 zitie-p7-draft-rc1-formal-preflight`
- artifact digest: `sha256:366c07f3177d86b3c1b7f0c8a0b3489c539dedbf90f0494158a51c6b99b42f18`
- formal PDF: `B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf`
- pages: 276
- bytes: 3,749,164
- SHA256: `ab3c23d7547872f4d0e2c128de397e9e89ed6de97b681876e2dff017ff5c4894`

## Full-text preflight

Verified on the generated formal PDF:
- `编写中`: 0
- `编写稿`: 0
- `前言初稿`: 0
- `发布候选稿 RC1`: 0
- 3/3 preface pages are labeled formal v0.4.0
- 258/258 practice pages carry the formal v0.4.0 publication label
- version page identifies current release as v0.4.0
- GF0011—2022 item-level source-blocked disclosure remains present
- `201 source_blocked_fail_closed` remains visible in back matter

## Actual rendered-page review

Rendered at 150 dpi and actually viewed:

`1, 3, 4, 5, 6, 238, 259, 260, 261, 263, 264, 269, 270, 273, 275, 276`.

These 16 pages cover:
- formal preface first/last pages
- both TOC pages
- ordinary practice layout
- B20 complex continuation
- B21 龠 17-stroke continuation
- first/last 201-main-radical index pages
- teaching variant index
- historical V001—V027 table
- source ledger
- version/current-release page

Result: **16/16 sampled formal pages passed visual QA**. No obvious clipping, overlap, black squares, broken glyphs, page-range drift, or publication-label placement error was observed.

## Inherited visual coverage

The formal rendering does not alter the reviewed stroke geometry:
- all 258 practice pages were fully layout-reviewed in P6;
- all 15 P7 navigation/back-matter pages were fully reviewed in the structured-draft QA;
- RC1 also received a representative final candidate QA.

This formal review checks the publication-mode differences and representative end-to-end pages; it does not falsely claim an independent second reviewer.

## Boundary

The PDF may be archived into `deliverables/releases/v0.4.0/` only after this evidence is on the target branch, target-HEAD CI succeeds, manifest release gates pass, and the release archival PR is merged. Existing fail-closed/source-blocked conclusions remain unchanged.
