# A1.3 — Optical cursor follows the stable round-brush ink frontier

**Release verification 2026-10-09:** [PR #99](https://github.com/netplus/zitie/pull/99) merged as `1ec9afb8b9f03657089cf61dd5551ed1fc0952ed`. Final proposed HEAD `40c5b9d43fdb622c132e0ed393f709b24ba0bde6` passed [A1 CI #37936426827](https://github.com/netplus/zitie/actions/runs/37936426827) and [Book CI #37936426822](https://github.com/netplus/zitie/actions/runs/37936426822); [Pages #37937065049](https://github.com/netplus/zitie/actions/runs/37937065049) completed Configure, Upload and Deploy on the merge SHA. At 512/1024 true SVG raster, 50 frames each: old red-ahead 1388/1370, new 429.51/411.51, no circle-on-gray samples, 40-stroke original ink suite unchanged. [Stable player](https://netplus.github.io/zitie/animation/). Human naturalness review is still open.

2026-10-09 · [Issue #98](https://github.com/netplus/zitie/issues/98)

## User-visible problem and selection

The experimental elliptical nib is **not** promoted. The preferred A1.2.3
stable round-brush renderer stays authoritative for visual source coverage.

The small red cursor has historically used the exact current canonical
median position, radius 8 source units. The actual stable brush paint is the
union of **round-capped** path fragments with half-width derived from the
source SVG contour. At a bend or hook, its painted footprint can run several
source units ahead of the median position. This is *not* inconsistent wall-clock
timing: both are evaluated from exactly the same `frame.progress`.

Attempting to replace all stable round masks by flat-ended local polygon
ribbons caused real Chrome regressions: an early disappearing pixel in 人
and a near-terminal 7.7% gap in 火 and 9.8% in a 龠 fold. Those trial masks
were **abandoned**, and none is part of this implementation. Image quality
is a hard gate, not something to trade for a synchronized dot.

## Stable algorithm: preserve ink; derive an optical frontier

The original `animation/player.js` mask continues to use unchanged
`Brush.makeProfile`/`Brush.stateAt`, white round-capped source-width
fragments and the same monotone source-clipped red SVG reveal. All frame
timings and source medians/outline `d` values remain unchanged.

`Brush.makeVisualFrontier(profile)` derives a separate, deterministic
**visual indicator** path by reusing the already available segment footprints:

1. At distance `d`, only fully settled segments and the partial active segment
   may contribute to the original round-cap union. Honor the original
   onset width/contact scale.
2. Probe positions **ahead along the original ordered median**, never a
   synthesized writing direction. Measure contiguous contact with the
   actually eligible round capsules; stop at the first uncovered probe.
   The maximum anticipation is 96 SVG source units.
3. Build a monotone arrival map from spatial distance to the first-order
   optical ink frontier. Take a prefix maximum and interpolate sampled values,
   so the visual marker never jumps backward after a bend.
4. Render the original same red circle at this optical contact position.
   It remains a small drawing-progress marker, **not** a calibrated physical
   ballpoint/brush nib or normative geometry input.

Selection is initially deliberately narrow: only strokes with a
previously reviewed name containing `折` or `钩` receive an optical
cursor correction. On other strokes the cursor remains exactly on
`timeline.frameAt(...).tip`. This is a rendering aid; it does not
change the pedagogical source state of any median.

### Coordinate semantics

- `frame.progress`, `frame.tip`, and `motion.phaseAt`: remain canonical
  engineering timeline coordinates (same as A1.2.3).
- `stateAt(profile,progress)`: retains the exact original dynamic brush mask.
- `visualFrontAt(frontier,progress)`: independently interpolates a monotone
  *appearance-only* circle position.
- `sourceStrokes`, PDFs, release manifest, font/licenses: never touched.

This mechanism differs from speeding up the pen or extrapolating its median:
it uses the known geometric paint footprints. It also differs from the
experimental ellipse in A1.4 (which remains opt-in and is **not** the default).

## Tests and acceptance

- Node regression: marker arclength is monotone, within the 96-unit bound,
  reaches the final median endpoint, and cannot rewrite source JSONs.
- Existing browser suite: offline UI, real SVG animation, 40-stroke
  384×384 exact monotone/outside-source/terminal-gap check, source-supported
  A1.4 opt-in regression and separate 2× DPR tests.
- Dedicated Chromium `stable-tip-frontier.html`: 5 representative
  strokes × 10 spatially consistent time samples, **same exact original red
  pixels**, compare the historical median marker against the new visible
  marker with the actual rasterized red footprint. Require no lead regression
  and several concrete corrections; archive all per-frame metrics.
- Final release gate: exact PR HEAD A1 + Book integrity CI, merge, then
  Pages deploy on the merge SHA.

## Limitations

The marker follows an *estimated centerline contact frontier* of the round
brush, not the supremum of every distant red pixel in the 2D outline. Sharp
folds or overlap may have unavoidable red side lobes that remain ahead of
the 8-unit circle. No measured physical pen pressure, tablet timestamps or
teacher-approved trajectories exist. Independent human viewing and
Firefox/WebKit/mobile-device inspection remain required.

The engineering target is a visibly more faithful synchronized **stable**
round-circle playback, not a claim of proven human handwriting kinetics.
