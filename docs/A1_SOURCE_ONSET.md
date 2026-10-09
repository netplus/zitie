# A1.4.4 — true SVG start support and directional onset

2026-10-09 · [Issue #95](https://github.com/netplus/zitie/issues/95)

**Experimental B renderer only**; A1.2.3 stable player, normative source stroke data, released PDF and manifest unchanged.

## Root cause

The user's complaint has two independent parts. First, earlier revision hid the pen cursor by default because the cursor was a white-bordered ellipse that visually resembled a moving hole over the ink. The pen should remain visible; only its white-ring appearance was wrong.

Second, the source spatial median for 一 begins at `(121,393)`, *inside* the original filled vector glyph. It is not the leftmost drawing contact point. Synthetic pressure starts low, and even a no-lag symmetric round nib can miss the asymmetrical upper-left source contour for a brief moment before returning to fill it later. The earlier test only ensured monotonically increasing red pixels and pixels already 2% or 10% behind the median were covered; it did not establish the true support plane.

## Geometric calculation

In `source-onset.js`, compute the first nondegenerate source tangent `u` from original median points, and normal `n`. While the original filled SVG path is still connected, sample its Bézier boundary using `getTotalLength/getPointAtLength`. For each boundary point `P` in a bounded initial region project

- `s = dot(P - median[0], u)`
- `v = dot(P - median[0], n)`

The minimum projection `s_min` is the contour-supported start origin. In the actual source-backed Chrome run for 一 the contour point was approximately **(106.61,397.70)**, around **18.13 source units** before the first median vertex along initial tangent projection, including a small conservative margin. This is source SVG geometry, **not measured human pen contact**.

Direct contour-boundary sampling replaces the previous expensive 2D grid of repeated `isPointInFill` checks, but retains source-supported bounds and explicit fail-closed fallback. It does not rewrite the source points or infer a new stroke direction.

At pen distance `d` and normalized within-stroke time `t`, compute a monotonically advancing first-contact plane

`front(d,t) = s_min + (min(d,capEnd)-s_min) * smoothstep(min(t/landingTime,1))`.

The ink mask gains a projected oriented slab with tangent coordinate from `s_min` through `front` and normal coordinate within the computed local source-width envelope. The **unmodified original SVG filled outline** clips all brush/mask geometry. At 0% there is zero red ink; during onset the genuine cap gains ink from the actual source support point in the writing direction; after onset the front follows the existing immutable centerline distance. This is added by **union** to prior elliptical impression and source-width mask fragments, so no deposited ink is erased.

For safety this source-directional contact region is currently enabled only for curated, unreviewed A1 engineering `horizontal` candidates (the current 一 example), not all folded/hooked characters. It never changes canonical stroke order or tutorial-source status.

## Visible stylus restored

The B experimental pen guide now defaults to **visible**. It is a dark, stylus-shaped SVG marker, with a pointed tip at local (0,0) and **no white stroke or fill**. During first contact the visual tip travels from the newly measured source-supported start to the first original median point; afterwards it tracks existing pen motion. A direct toggle still allows hiding/showing this non-ink guide.

The guide is never used as an ink primitive. Browser pixel tests hide it when examining only deposited red ink, avoiding a false positive for out-of-outline pixels.

## Acceptance

- 45 Node tests including new source-geometry onset tests, strict positive/monotone tangent-front progression, original byte-identical source data, and existing 40-stroke stability checks.
- Real Chromium comparison of source glyph 一 at **512/768/1024** SVG raster sizes with early fractions beginning at 0.01% spatial travel. The independent pixel set test requires *every filled source pixel strictly behind the moving projection front* to have been painted, not just red-pixel-count monotonicity.
- Additional checks: 0% empty; no oversized first-frame blob; no previously red pixel lost; no red pixel outside original vector outline; exact final `path d`; all A/B six-glyph and 40-stroke stable checks retained.
- A dedicated 11-position source-relative A/B frame sheet **with B's visible dark stylus** is generated in Chromium for human picture review; no claims of teaching approval from numerical CI alone.
- Require **both final-HEAD A1 Chrome and Book integrity CI success**, merge, then independent GitHub Pages deployment success on merge commit.

The models still use synthetic pressure, no digitizer timestamp/force/tilt samples and unreviewed vendor motion directions. Firefox/WebKit and subjective calligraphy/Kaishu naturalness are separate review tasks (#88).
