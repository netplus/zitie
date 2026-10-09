# A1.2.2 — Position-dependent handwriting rhythm and precise active ink

Date: 2026-10-09. Feedback tracking: https://github.com/netplus/zitie/issues/84 .

## Evidence and limits (NOT measured human handwriting)

1. Flash & Hogan (1985), Journal of Neuroscience, https://pmc.ncbi.nlm.nih.gov/articles/PMC6565116/ : some unconstrained point-to-point human arm movements show approximately bell-shaped velocity and smooth starts/ends, consistent with minimum-jerk optimization. This study does **not** prescribe a universal time function for every Chinese handwritten stroke.
2. Curvature/velocity: https://pmc.ncbi.nlm.nih.gov/articles/PMC4517202/ reports different exponents for different shapes, rather than one universal one-third law. Plamondon & Guerfali (1998), https://doi.org/10.1016/S0001-6918(98)00027-4 , specifically discuss where the 2/3 handwriting power relationship fails.
3. Chinese writing measurements: Xu et al. (2026), https://doi.org/10.3758/s13428-026-03001-4 , collects real pen stroke timing/trajectories; multidimensional pen-speed/pressure data are described in https://www.nature.com/articles/s41467-026-70536-7 . Such empirical measurements are not embedded in the repo's Hanzi Writer source JSON.
4. Our repository's immutable `strokes[]` contain final outlines and `medians[]` contain spatial coordinates in stroke order. There are **no per-point timestamps, forces, height, tilt, or true pen-pressure measurements**. Therefore the model below is a transparent, tunable **pedagogical heuristic**, not an actual person's writing recording, measured physical pen velocity, or normative proof of direction.

## One elapsed-time axis, two independent concepts of speed

- The original `animation/timeline.js` remains the sole playback timeline (one elapsed duration per stroke, with prior fixed inter-stroke pause). We do not split folded or hooked strokes into extra strokes, change order, fabricate medians, or alter final outlines.
- A per-stroke pure-data motion profile in `animation/motion.js` converts **time within the current stroke** to **distance along its original median**. The same progress drives red mask coverage and pen-tip position.
- The UI speed buttons (`0.5×`, `1×`, `1.5×`, `2×`, `3×`) only multiply wall-time progression through that same timeline; they **do not discard** turn deceleration or start/end pacing. The current selection uses `aria-pressed`, with visible selected state and keyboard focus safety.
- The UI's dynamic stage labels (起笔渐快、稳步行笔、转折减速、收笔渐慢) refer only to this inferred motion phase; they are not new fine-stroke-name approvals.

## A1 inferred time-to-arc-length model (v1)

1. Treat input medians as immutable connected polylines. Calculate each segment's arc length and tangent. Identify a turning vertex when neighboring tangents change direction by more than 0.30 radians, ignoring degenerate subsegments.
2. Compute a turn severity from the angle above threshold; create a local Gaussian travel-time penalty centered at that source vertex. The spatial speed factor is v(s) = clamp[ 1/(1 + 2.2 Σ severity_i exp(-0.5((s-s_i)/sigma_i)^2)), 0.30, 1 ]. Window sigma_i is 11 + 0.32 times the shorter adjacent segment, clamped to 9..48 source units. These numbers are **engineering defaults**, not empirical Chinese pen-speed constants.
3. Numerically integrate travel time density dt/ds = 1/v(s) along the *unmodified* median at about seven units per sample. Normalize cumulative time. Apply a start/end time warp E(t) = 0.12t + 0.88(10t^3 - 15t^4 + 6t^5), a blend of linear and minimum-jerk-like easing to avoid a completely stalled beginning. Invert the normalized cumulative time curve to determine current spatial progress.
4. `frameAt()` uses that progress to interpolate the original median's point; pause/restart/single-stroke/seek, multiplier changes, and end-frame states all reuse exactly the same elapsed-time source. The model's progress is strictly monotone and is 0/1 exactly at stroke start/end.
5. Turning slows but never pauses discontinuously, allowing a continuous pen direction through 横折、竖钩 and other composite single strokes. Exact final outline geometry is always drawn from the original reviewed `stroke.outline`.

## Visual refinements and tradeoffs

- `animation/ink-brush.js` uses more closely spaced pen-mask cross-sections (7 vs previous 13 source units) and smaller default contour margin (6 vs 8). This reduces coarse polygon artifacts and excessive adjacent ink.
- The left/right cross-section widths are lightly smoothed **only where successive normals remain aligned** (dot products above 0.96); no smoothing crosses a sharp angle, and **median point positions never move**.
- The last partial segment uses a slightly rounded, *inward/backward* leading nib edge instead of the previous blunt cut, with no forward mask projection past the current pen-tip.
- Earlier dark and future pale SVG layers remain separated; the final red/gray shape is the original unmodified silhouette, not the temporary pen-mask polygon.
- These techniques still cannot reconstruct real nib contact physics, uplift/press-force or brush angle. They may produce residual visual gaps at exotic terminals and must undergo sampled intermediate-frame review; testing does not grant teaching approval.

## Quality gates and continuation

- Pure tests: check start/end speed variation, mid-stroke movement, source-vertex turn location, lower local speed at right-angle fold and hook, strict monotonic progress, unchanged source bytes, correct total stroke counts, rejected missing data, and global multiplier independence.
- Browser: assert five accessible direct buttons, no select dropdown, accurate motion labels, phase-preserving speed switch, original gallery/search/keyboard/mobile functions, real SVG red-pixel growth at 0/5/25/50/75/95%, masks removed at 100% and exact source final `path d`.
- GitHub Pages is already enabled; deploy `motion.js` and all updated browser assets offline with the required source license. Verify the deployment job actually succeeded, not merely the animation unit tests.
- **Approval split:** engine/UX CI success does not mean the 9 medians are pedagogically reviewed. Keep `engineering_preview_unreviewed` and open trajectory review #79 / visual feedback #82. Maintain fail-closed #4 and physical-print #77, the 201-primary denominator, and all released PDF/manifest history.
