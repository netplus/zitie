# A1.2.1 — Glyph gallery and fine progressive writing

Review date 2026-10-09 · feedback [Issue #82](https://github.com/netplus/zitie/issues/82).

## Root cause and evidence

- Previous index.html used a single native glyph select. It was awkward with nine samples and unscalable to the future 201-item library.
- Previous player.js revealed all glyphs with a globally fixed 170-unit, round-capped median brush. At tiny progress, that round cap could expose a large region; thin hooks/folds looked blunt or popped.
- Canonical stroke outlines, median ordering, byte-identical final SVG paths, 201 item IDs and source field restrictions remain authoritative inputs, not targets for modification.

## Gallery redesign

- Searchable, clickable glyph tiles instead of the native dropdown. Search by character, batch, stroke count, canonical main ID or a verified fine-stroke name. Filters for B01/B02/B21.
- Screen-reader pressed state, empty-result clear, previous/next glyph, responsive layout and shortcuts (Space play/pause, A/D glyph navigation, R restart).
- Unified scrubbable slider queries the original elapsed-time model; all existing single-stroke and playback commands retain their meaning.
- The gallery includes nine **engineering samples**, not the whole 201-item material catalog. No runtime CDN, external fonts, server or analytics.

## Improved SVG progressive mask

1. Linearly resample *unchanged vendor median segments* at approximately 13 source units. Preserve every original corner and hook vertex; never smooth canonical direction without evidence.
2. At each station probe the exact original SVG filled outline with the geometry hit-test API, moving perpendicular in both directions and measuring the local left/right extent independently. Add a small safety margin. The probe path must first be connected to the DOM.
3. Grow the SVG mask as a union of local swept quadrilaterals, stopping its forward edge at the centerline tip rather than exposing a fixed-radius circle ahead.
4. The red pixels remain a masked copy of the exact original filled contour. At stroke completion the mask is removed; the finished reference path is unchanged.
5. If fill hit testing is unsupported or a source endpoint lies just outside its contour, retain the original endpoint and record a visual-only fallback width. A fallback cannot be counted as reviewed teaching geometry.

## Quality and limitations

Automated testing covers 0%, 5%, 25%, 50%, 75%, 95% intermediate frames (with pen indicator hidden), nonzero onsets, monotonic raster pixel coverage, stroke-count invariants, exact final outline, search/filter/keyboard/timeline controls, glyph switching and mask cleanup. Pure unit tests inspect the local geometry and do not infer correctness from rendering alone.

**Source typographic outlines do not encode real pen pressure.** Acute turns, overlapping sections of one stroke, medians outside the silhouette, and last-frame coverage jumps still require **manual frame-by-frame review** and independently substantiated writing directions. Passing CI is not teaching approval or a two-browser visual acceptance.

Run: node --test animation/tests/timeline.test.cjs animation/tests/precision.test.cjs ; bash scripts/a1_browser_smoke.sh.

Keep the explicit status engineering_preview_unreviewed for all nine sample medians. Do not change released PDFs, archived manifest, normative source records or Issues #4/#77.
