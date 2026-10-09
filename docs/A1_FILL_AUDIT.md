# A1.2.3 — artifact-resistant progressive ink geometry

2026-10-09 · feedback [#86](https://github.com/netplus/zitie/issues/86) · branch `feat/a1-robust-stroke-fill`

## Root-cause audit of the actual vA1.2.2 code

1. `animation/ink-brush.js` assembled many normal-offset filled quadrilaterals in **one** SVG `<path>`, and animated by replacing its list of polygons. At source-median corners, differing local tangent normals can produce nonconvex/crossed facets, abrupt changes in winding, holes and jagged edges. An SVG fill mask is not a geometric union primitive for self-intersecting quads. Simple red-pixel *counts* cannot reveal pixels disappearing at one location while appearing at another.
2. `animation/player.js` used a bounded but abruptly expanding extra terminal circle over the last 1.8% of arclength. When source median endpoints deviate from the wide typographic silhouette, this could uncover wedge-shaped terminal areas ahead of the intended progression, notably near hooks. This patch is **removed**, not retuned.
3. The existing 0/5/25/50/75/95% checks confirmed coarse area growth but did **not** ensure per-pixel set inclusion or absence of isolated patches across an individual fold/hook.

## Checked upstream implementation and graphics standards

- Hanzi Writer MIT SVG renderer: `src/renderers/svg/StrokeRenderer.ts` at https://github.com/chanind/hanzi-writer/blob/master/src/renderers/svg/StrokeRenderer.ts . It paints the median as a round-ended SVG **stroke**, clipped by the exact filled source-outline `<clipPath>`, instead of projecting and uniting filled polygon offsets.
- W3C SVG strokes: https://www.w3.org/TR/svg-strokes/ and MDN https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-linejoin specify round joins and cap semantics. We reuse the **rendering principle**, not a new normative stroke dataset or license assertion.
- Original `strokes[]` remain immutable filled silhouettes and `medians[]` immutable ordered centerlines, pinned to the existing upstream Hanzi Writer data commit. The legacy PDF and existing review evidence are not modified.

## Replacement algorithm: source-constrained monotone brush union

1. Resample each original median at 8 source coordinate units, retaining *all original vertices in sequence*. Probe original SVG filled path on both sides of each local normal via `isPointInFill()`. The measurement determines a bounded local contact radius. Unsupported points borrow *width only* from the nearest valid cross section and remain explicitly visual-only fallbacks.
2. Create independent white **round-capped SVG stroked line paths**, one between each adjacent pair of resampled median stations. Paths share endpoints; overlapping alpha-mask fragments are composited via **source-over union**, with no common winding fill rule or polygon self-intersection. The actual red drawing is still the exact original stroke outline, multiplied by this mask.
3. At normalized spatial progress `p`, paint the complete prefix of these fixed brush segments and only the corresponding prefix of the next active segment. Reverse scrubbing removes now-excluded prefix fragments. A small monotonically increasing contact-width ramp over the first ~2.2% of travel avoids the start-frame full-radius ink disk. There is **no separate terminal circle**.
4. The current brush front is driven by the same `timeline.js` / `motion.js` elapsed-time-to-arclength mapping as the pen indicator. No new pen strokes, changed directions, fabricated medians, altered stroke order or independent animation clocks.
5. When the original stroke finishes, render its **verbatim filled reference outline** directly (as before), never a redrawing reconstructed from the brush. Final vector geometry and canonical step count are byte-identical.

Math: for ordered median sections `S_i` and source outline `O`, the intermediate visible glyph is `O ∩ ⋃_{i in completed} Tube(S_i,r_i) ∪ Tube(prefix(S_active),r_active)`. Contact width scales monotonically with progress during onset; previously painted sections and their radii never shrink. Therefore in the ideal continuous SVG alpha-mask model, `Ink(p1) ⊆ Ink(p2)` for `p1 <= p2`. Browser rasterization, alpha thresholding, and source-median path anomalies must still be tested independently.

## Independent acceptance gates

- Node: deterministic ordered median sampling, local contour-radius source references, 9 glyphs / 40 unchanged stroke records, no discrete extra stroke for hooks, monotonic `visibleCount`, `contactScale` and progress with reverse seek/reset.
- Headless Chromium: rasterize the **actual visible red SVG pixels** at dense progress fractions on every source-backed sample. Check previous red pixels do not disappear, no detached large components, no red ink at 0%, unchanged exact reference outline and a quantitatively bounded change between 99.5% and the full target contour. This improves on merely comparing total red-pixel counts.
- Record per-glyph/per-stroke diagnostics and a browser screenshot sheet under `build/a1` in Actions. A Chrome check is necessary but not sufficient for WebKit/Firefox or human aesthetics.
- Performance: stationary masks and brushes are created once at glyph selection; at each frame, only changed prefix display attributes and one short active segment change. The algorithm is still a DOM-heavy prototype; 201-source coverage requires further profile/performance validation before distribution.
- Source medians still need **independent teaching direction evidence**. The user-supplied abnormal fill report is a graphics defect, not justification to change verified normative stroke order or silently edit source trajectories.

## Boundaries

All original 201 primary radicals, 9 offline prototypes, speed buttons, local nonuniform motion, source fail-closed Issue #4, v0.5.1 formal PDF and immutable release manifest remain untouched. No fonts are packaged in the browser application. This stage is **not** a new static copybook release.

Independent pixel-based QA results and final merged commit/Pages deployment must be recorded as observed, not predeclared.
