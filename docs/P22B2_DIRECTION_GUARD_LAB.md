# P2.2b-2 — Source-locked direction abstention A/B (research only)

Tracks [#151](https://github.com/netplus/zitie/issues/151) after [#150](https://github.com/netplus/zitie/pull/150). **Only an offline diagnostic; not production handwriting scoring or teacher validation.** No change to published PDF, reference strokes, A3 animations, brush pressure, main UI, original matcher, or IndexedDB.

## Exactly identified failures

The actual [P2.2b-1 QA artifact](https://github.com/netplus/zitie/actions/runs/38338826144/artifacts/11785761712) and direct re-execution of the original `order-check.js` locate these source-perfect first-stroke reversals:

| Glyph | Stroke | Median vertex count | Source endpoint distance | Baseline reversed score | Baseline result |
|---|---|---:|---:|---:|---|
| 首 (187) | 点 | 3 | 121.66 | 0.09399 | `consistent` |
| 高 (191) | 点 | 3 | 122.32 | 0.09438 | `consistent` |
| 鼻 (200) | 撇 | 4 | 106.89 | 0.08427 | `consistent` |

The original P2.2a geometry score divides position errors by the **fixed 1024-unit canvas**; short strokes can remain below its `0.098` plausibility gate even if written back-to-front. Lowering a global threshold could make proper short strokes falsely fail. Direction within a stroke is not proof of the **between-stroke order**, so the candidate **abstains** rather than accuses.

## Independent research model

`animation/experiments/stroke-direction-guard.js` is Node-only and never loaded by the practice page. It first calls the real global matcher to obtain actual assigned reference ordinals; it **does not** assume the learner's nth pen-down matches the reference nth stroke. It analyzes only confidently matched `consistent` or `reordered` results.

For each matched trace: arc-length resample; compare input-to-reference endpoint direction cosine; measure reference straightness as endpoint displacement / reference arclength; compare normal and reversed median fits using unchanged original `Matcher.compare`.

A confident direction conflict requires **all** of these independent signals: reference straightness >= 0.50, cosine <= -0.65, forward-minus-reverse cost >= 0.028, reverse fit <= 0.075 and forward cost >= 1.45 times reverse cost. B can only change a confident status to `uncertain`, never to `reordered`. All constants are **exploratory and not calibrated on learners**.

[Hanzi Writer's quiz documentation](https://hanziwriter.org/docs.html) distinguishes backwards strokes with an `acceptBackwardsStrokes` option (default false), but neither its implementation nor any handwriting data was copied. [Two-layer bipartite stroke matching research](https://doi.org/10.1016/j.future.2017.09.074) offers separate context for stroke assignment; neither source establishes the thresholds above.

## Reproducible diagnostic

After building the PDF-source-locked A3 pack, run:

```sh
P22B2_REPORT_FILE=build/a1/p22b2-direction-metrics.json \
  node --test animation/tests/p22b-direction-lab.test.cjs
```

The complete 201-glyph / 1045-stroke source produces 14 scenarios, **2,778 synthetic whole-character examples**.

| Scenario | Shipping A | Experimental B |
|---|---|---|
| Exact, shifted, ±8/±30 jitter, sparse correct-order input | 1005/1005 `consistent` | 1005/1005 `consistent` |
| First/last adjacent swaps | 392/392 `reordered` | 392/392 `reordered` |
| First stroke reversed | 3 accepted, 198 uncertain | 0 accepted, 201 uncertain |
| Last stroke reversed | 1 accepted, 200 uncertain | 0 accepted, 201 uncertain |
| Middle stroke reversed (n >= 3) | 6 accepted, 169 uncertain | 0 accepted, 175 uncertain |
| All strokes reversed | 0 accepted, 201 uncertain | unchanged |
| First stroke reversed + jitter 8 / 30 | 2 + 2 accepted | 0 + 0 accepted |
| First stroke reversed + translation | 3 accepted | 0 accepted |

Relative to shipping A, B **downgrades 17 synthetic reversed inputs to uncertainty**, preserving all 1,005 synthetic correct-order controls and 392 reference swaps. These are *synthetic invariants*, not real-world accuracy/false-positive percentages. Report metadata contains only source glyph IDs, outcome counts, direction metrics and limited examples; no real learner samples, pen-point arrays or remote analytics.

The CI tests pin official PDF SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`, 201 glyphs, 1045 strokes, and verify monotonic abstention only. The JSON report is published as a short-lived QA artifact at `build/a1/p22b2-direction-metrics.json`, not exposed to learners or bundled as handwriting records.

## Next gate (NOT done)

Production adoption requires explicitly consented, independently teacher-labelled handwriting, participant-separated evaluation and additional short-dot / unconventional handwriting sampling; assess false accusation, incorrect acceptance and abstention by stroke type and device. See [calibration governance](P22B_STROKE_ORDER_CALIBRATION.md). No real device or teacher validation is claimed. Issue #151 stays open until that stage.
