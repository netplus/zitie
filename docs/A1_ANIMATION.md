# A1 — SVG stroke-writing animation (new stage, 2026-10-09)

## Scope and immutable boundary

A1 is a new, independent workstream following v0.5.1. The released 299-page PDF, delivery manifest, M1/M2/M3/Q1 history, 201 canonical IDs, and field-level fail-closed policy must remain byte-identical. The animation is **not** a release or amendment to the book. Issue #4 (normative source gaps) and #77 (physical printing) retain their own ownership and gates.

## A1.1 — Evidence from the actual repository

- Canonical order and fine strokes: `data/B01.json` through `data/B21.json` (201 unique `main_id`), `data/teaching-source-policy.json`, and field evidence under `data/evidence/`. For early batches, `stroke_names`/`order_code`; later batches, `stroke_order_review` and `fine_stroke_names_review`. Policy-blocked fine names are rendered as ordinal only.
- Source drawing: `scripts/acquire_vectors.py` pins Hanzi Writer / Make Me a Hanzi artwork at `68d10a4b21150cae5e1ebbd223eed289cf32d90c`, downloads per-character `build/vectors/XXXX.json` and records source SHA-256. Each vendor object includes `strokes[]` **filled, closed SVG outline paths** and `medians[]` **centerline polylines in matching order**. The repository does not track the full 201 original JSONs; they are fetched into the build cache.
- Artwork adaptation: `scripts/apply_artwork.py` applies **source-hash-pinned** overrides to `日/目/田` stroke 2 **including replacement medians**; `月` and true hooks are deliberately not globally modified. Our coverage audit uses the exact same function. Other source files stay unchanged.
- The printed page geometry in `scripts/build_batch.py` uses a fitting scale of `0.81 * grid_size / max(glyph_width,glyph_height)` and recenters the original paths in a square. SVG samples retain the vendor's 1024 coordinate system with `translate(0 900) scale(1 -1)`; the red/gray paths, median, clipping mask and pen are in that same original coordinate system. PDF cell dimensions are **not** hard-coded into the animator.
- P6 vector coverage record `data/evidence/P6-vector-material-coverage-20261007.json` reports **201/201 compatible stroke counts**, **0 missing**. This does **not** measure medians and is not trajectory approval. A1 tracks centerline material, per-stroke geometry, direction, and teaching acceptance in different counters.

## Technology decision

Use vanilla browser SVG and JavaScript. Compared with Canvas 2D, SVG retains the exact reviewed `path d` as a reusable final silhouette, offers responsive viewport scaling and accessibility, and supports clipping the fill with one animated median brush without rasterizing or erasing outlines. Unlike blindly animating the outline's path commands, the brush **travels along medians** in their point order, with a continuous polyline through internal folds and hooks. All playback commands operate on `animation/timeline.js` as the single elapsed-time model.

Renderer: every stroke has light-gray hint fill, earlier completed dark-gray fill, and a current red **exact source outline** clipped by a thick SVG path traveling along its median. The mask distance changes continuously; at the exact end of one stroke the red outline loses its clip and is identical to the source outline. On final completion all canonical paths are directly shown without clipping. A pen-tip indicator follows the arclength-interpolated median. No sprite/frame substitution, no outline-path-direction animation, no split of fold/hook into extra strokes.

**Known rendering risk**: a constant-width 170-unit brush can leave brief thin gaps at unusual wide terminals, or reveal neighboring parts of the *same stroke* a little early where they lie close together. The player uses the full original silhouette for a finished stroke, so the finished geometry is exact by construction; this does not certify intermediate revealed geometry. Quantitative mask/paint visual inspection and any per-stroke width/corner adaptation belong to the A1 trajectory review queue. Do not call source medians normative evidence on their own.

## Data contract (A1.2 engineering prototype)

`animation/samples.js` is a self-contained, offline JSON envelope embedded in a JS assignment (works with `file://` without `fetch`):

- `main_id`, `character`, `batch_id`, `normative_ref`, `expected_stroke_count`, `order_code`.
- `source_url` at the fixed immutable revision and `outline_review_status`.
- `trajectory_review_status = engineering_preview_unreviewed`: mandatory explicit status, never inferred from artwork_ready.
- For each ordered 1-based stroke: `outline`, `median: [[x,y],...]`, name and `name_status`. A production model may additionally carry the source raw SHA-256, start/end, turn-index annotations, per-stroke review links, review date, duration, pause, intended position/form, and blocking reason.
- The timeline derives start/end points from `median[0]`/`median[-1]`, turns from intermediate median points, and duration by median arc length (clamped to 550–2600 ms) with 260 ms pauses. There is one canonical elapsed time for all controls; player speed multiplies elapsed-time progression.
- Missing, invalid, degenerate or mismatched median arrays **block animation**. They are not synthesized from closed outline edges. Unreviewed fine stroke names are ordinal-only. These guards do not silently approve medians merely for being structurally valid.

### Nine representative offline samples

`一` (simple horizontal), `十` (horizontal/vertical), `人` (撇/捺), `火` (点、撇、捺), `口` (横折), `巾` (横折钩), `水` (竖钩), `月` (横折钩), and `龠` (17-stroke complex radical). These are all already part of B01/B02/B21. Their source point data and paths are stored as acquired; they are *engineering previews*, not new authoritative reviews.

## Acceptance gates

1. **Canonical**: `scripts/a1_audit.py` checks the 201 unique IDs, count/order, final outlines and medians from the pinned cached JSONs, applying three hash-checked terminal adaptations, and exact identity of all nine offline samples to the adapted source. A read-only JSON coverage report is emitted in `build/a1/coverage-report.json`.
2. **Behavioral**: `node --test animation/tests/timeline.test.cjs` verifies canonical sample metadata, mathematical interpolation, true folds/hooks as a single stroke, deterministic pause and final states, rejected missing data and source gates.
3. **Real browser**: `bash scripts/a1_browser_smoke.sh` runs a localhost server and headless Chrome against `animation/tests/browser-smoke.html`: actual requestAnimationFrame progression, partial clipped red fill, paused position, resume, restart, 3x speed, single replay, both step directions, exact final paths, and switching 1→17→4 strokes without stale clip IDs.
4. **Not yet an accepted teaching asset**: independently review each start point, direction, internal fold and hook, terminal coverage and intermediate mask at several progress points in at least two browsers; record reviewer/evidence, resolve structural issues. Do not promote any of the nine or 201 to teaching-approved solely on tests or prior PDF review.
5. **Shipping**: offline operation, full license notice, no fonts or normative PDF uploads. Future MP4/WebM, GIF, Flutter, variants and word migration are later tracks, not A1.2 prerequisites.

Run locally by opening `animation/index.html` directly (no server), or `python3 -m http.server` for the browser smoke harness. All resources referenced by the player are repository-relative and available offline.

## A1.3 onward

Audit 201 primary radicals across B01–B21 first, capture anomalies and fixed source hashes, then create a per-stroke trajectory review queue with source directions and stroke names. Separate other categories (variants, comparison/recollection, whole-word position migrations) in metrics; no counted overlap. Do not edit older normative evidence to make a trajectory appear approved. Source Issue #4 remains fail-closed.