# P2.2b-1 — Offline stroke-order robustness audit (synthetic baseline)

Status: **engineering diagnostic**. Parent: [#149](https://github.com/netplus/zitie/issues/149). Based on merged P2.2a / [PR #148](https://github.com/netplus/zitie/pull/148). It does **not** claim genuine learner accuracy or teaching approval.

## Goal and scope

The current source-locked matcher reports one of \`consistent\`, \`reordered\`, \`uncertain\`, \`incomplete\`, or \`count_mismatch\`. A self-consistency test on 201 PDF-derived median paths and a few deliberately swapped strokes of 水 do not measure how it performs with variable handwriting. Before tuning the confidence gates, quantify what the current matcher does for a **fixed synthetic challenge set**.

This stage does **not** modify \`animation/practice/order-check.js\`, UI messages, source strokes, production confidence thresholds, on-device storage, brush animation, pressure styles, or the official 299-page v0.5.1 PDF.

Run the baseline after building the official A3 book pack:

\`\`\`sh
mkdir -p build/a1
P22B_REPORT_FILE=build/a1/p22b-robustness-metrics.json \
  node --test animation/tests/p22b-robustness.test.cjs
\`\`\`

CI stores the JSON report as \`a1-motion-frame-qa/build/a1/p22b-robustness-metrics.json\`. This report includes **no original/user captured point arrays**: only category totals, bounded glyph identifiers, characters, stroke counts, and machine outcomes. The CI suite reads the existing licensed source model but never imports practice IndexedDB or contacts a telemetry endpoint.

## Audited input and expected labels

All source cases are generated deterministically from the 201 characters and 1045 reference strokes of the current book pack. Each scenario has a *known synthetic operation*, not a teacher judgment about a real person's handwriting.

| Scenario | Operation | Ground truth for accounting |
|---|---|---|
| \`source_exact\` | Untouched source medians, original order | Correct-order baseline oracle |
| \`translate_18\` | Translate every coordinate (+18, −12) | Correct-order synthetic |
| \`jitter_8\` | Deterministic per-vertex perturbations up to 8 SVG units per axis | Correct-order synthetic |
| \`jitter_30\` | Larger deterministic perturbations up to 30 units per axis | Correct-order synthetic |
| \`sparse_vertices\` | Retain endpoints and every other source vertex | Correct-order synthetic |
| \`swap_first\` / \`swap_last\` | Exchange first/last adjacent reference strokes | Deliberate wrong-order synthetic; skip one-stroke glyphs |
| \`reverse_first\` | Reverse direction of the first stroke | Wrong direction, **not necessarily wrong stroke order** |
| \`duplicate_first\` | Replace last stroke with first stroke | Wrong geometry/repeated stroke, not an unequivocal order label |
| \`displaced_first\` | Displace one stroke by (+350, +260) | Wrong geometry, not an unequivocal order label |
| \`omit_last\` | Remove one completed stroke | Incomplete count; no order verdict permitted |
| \`extra_last\` | Append another completed stroke | Extra count; no order verdict permitted |

Potentially geometrically indistinguishable stroke swaps remain *ordered as swapped in this test* but the matcher should abstain when it cannot distinguish them. For \`reverse_first\`, \`duplicate_first\`, and \`displaced_first\`, \`consistent\` indicates a useful diagnostic blind spot, **not** an empirically measured stroke-order false acceptance. The report's \`falseAcceptances\` aggregation is therefore a broad **synthetic-invalid acceptance count**; use \`wrong_order\` rows specifically when discussing order false acceptance.

All audit outcomes are partitioned by scenario, with exact denominators and machine-status counts. A maximum of six representative metadata-only examples per category is retained to assist further examination. This is **not** a representative distribution of people's writing, and the counts cannot be translated into learner accuracy percentages.

## Safety and CI gates

Hard failures:
1. PDF source pack absent/malformed, number of glyphs not 201, source-stroke total not 1045, or a malformed publication SHA.
2. Any source-exact canonical input does not return \`consistent\` (the full baseline remains mandatory).
3. A missing-count case is not \`incomplete\`, or extra-count case is not \`count_mismatch\`.
4. Any unknown matcher status or invalid/missing metadata.

Synthetic perturbation rates are **diagnostic only** and deliberately have no arbitrary pass percentage. CI success means the audit runs and its **known invariants** hold, *not* that the matcher is reliable on humans. No threshold change can be justified from this CI alone.

## P2.2b-2: real data governance and calibration protocol (not performed)

Before any real-handwriting ingest:

- Obtain explicit, revocable and purpose-limited consent from each adult participant, and parent/guardian authorization plus age-appropriate assent for minors where required. Use a written retention period, deletion process, access controls and review of applicable child-data protection rules. Declining participation must not impair practice.
- Keep collection **opt-in, off by default, and independent of normal IndexedDB exercise records**. No stealth analytics, no automatic cloud synchronization, no identifiable student names, school, location, raw device IDs, advertising identifiers or full contact details in a public repository or CI artifact.
- Acquire a documented source and license for any external handwriting dataset before use. “Publicly downloadable” does **not** imply consent to redistribute, train on, or publish samples. Data and annotations must have verified compatible terms.
- Sample across Pad/phone/desktop hardware, finger/stylus/mouse, screen sizes, pressure availability, and writing proficiency. Do not train/evaluate on repeated traces from the same participant across partitions. Reserve a participant-separated, never-tuned-on held-out set.
- Two independent trained Chinese handwriting reviewers annotate **each stroke** (source correspondence, direction, start/end, segmentation, missing/extra, order) and whole-word outcome. Disagreements and unidentifiable strokes must be adjudicated by a third reviewer or marked ambiguous; never force a ground-truth order.
- Preserve stroke segmentation and real temporal sequence. A teacher's own pen-order judgment is separate from source-medium geometry; mistakes in the source reference are adjudication issues, not automatic learner errors.
- Bind each accepted sample to \`glyphId\`, \`sourceHash\`, \`pdfHash\`, matcher version, a pseudonymous consent/deletion token maintained in a separate access-controlled system, review status, capture setup, device category and sampling protocol. Do not publish raw traces as JSON under \`animation/\`, \`docs/\`, \`build/a1/\`, or GitHub Actions artifacts.

Metrics must include denominators, confidence intervals and an abstention matrix, separated by scenario and participant/device/character class:

- **False accusation rate**: of expert-confirmed correct-order attempts, percentage classified \`reordered\`; \`uncertain\` counts as an abstention, not a wrong accusation.
- **False order acceptance rate**: of expert-confirmed wrong-order attempts, percentage classified \`consistent\`; \`uncertain\` is not counted as acceptance.
- **Coverage / abstention rate**: proportions classified definitively (\`consistent\`/\`reordered\`) versus \`uncertain\`, for both expert-confirmed classes; count errors (\`incomplete\`, \`count_mismatch\`) are a *separate* segmentation outcome.
- **Conditional error among classified attempts**: report alongside unconditional errors to expose how abstention affects apparent accuracy. Use participant-clustered confidence intervals where samples are correlated.
- **Stroke-class analysis**: group by reviewed reference \`name_status==='reviewed'\` names (e.g., 横/竖/撇/捺/折/钩); use an explicit **unreviewed** group for restricted names. Never infer a name from unsupported source labels.

Proposed real-world acceptance must be written only **after** a statistically justified pilot, with separate false-acceptance, false-accusation and coverage targets and explicit teacher sign-off. No scores/exam judgments based on current synthetic metrics.

## P2.1d / P2.3 boundary

Real Apple Pencil/iPadOS, Android Pad, finger and palm rejection, pointer cancellation, cross-orientation, frame rates and device-specific IndexedDB behavior need separate hardware QA. Passing Chromium native CDP touch does not imply iOS/Android certification.

## External research (non-normative)

- Hanzi Writer publicly documents configurable quiz leniency and directional matching behavior: https://hanziwriter.org/docs.html
- The Hanzi Writer implementation and source-data licensing are distinct (MIT code versus Arphic-derived data): https://github.com/chanind/hanzi-writer

These references inform the **testing taxonomy** only; the project's official glyph data and P2.2a matcher remain unchanged. No external samples are copied or bundled.
