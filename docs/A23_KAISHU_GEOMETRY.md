# A2.3 — Professional hardpen regular-script geometry (楷书) candidate

2026-10-10 · [Issue #113](https://github.com/netplus/zitie/issues/113)

## Product correction

User feedback: the A2.2 ordinary rigid-nib animation is **too elementary, unprofessional and untidy**. The target is professional **硬笔楷书**, not merely a thin fixed-width pen. The legacy 毛笔（原版） renderer must remain fully available; A1.6's stable/synthetic-pressure selector is a separate concept. A2.3 is a **new opt-in comparison stage** while the last deployed hardpen remains unchanged.

### Verified geometric root cause

In `animation/samples.js`, the original Make Me a Hanzi / Hanzi Writer median for **一** is:

`[[121,393],[193,372],[417,402],[827,434],[920,401]]`.

It has over **20 SVG source units** of deviation from a straight line. Drawing that exact source median with a uniform 26-unit round-tip contact makes the hardpen look visibly wavy; velocity/pressure changes cannot repair this. Comparable artifacts include 口's sloping side walls, 十's drifting supporting vertical, 水's long, soft source hook and 月's compound hook pivot. Those source strokes are original artistic data and **not automatically a mature rigid-nib regular-script manuscript**.

A2.2 solved line-width constancy and monotone red-ink growth; **not** professional stroke regularity or the structure of the entire character.

## Evidence base: geometry is not the same as stroke order

- [河西学院语言文字网：硬笔书法28条法则](https://yywzw.hxu.edu.cn/info/1155/1097.htm) describes a subtly upward rightward 横, clear and straight supporting 竖, tapered 撇 and 捺, single continuous 横折 without two sharp corners or oversized pause, and brief upward-outward hook. This is a **pedagogical reference, not licensed machine-readable geometry**.
- [中国书法协会：钢笔楷书横画的写法](https://www.shufa.org.cn/xinshang/1024.html) explicitly distinguishes long/short horizontal hierarchy, restrained rising horizontal orientation, main stroke prominence and equally spaced horizontal sets.
- Open fonts such as [LXGW WenKai](https://github.com/lxgw/LxgwWenKai) (SIL OFL) may support an **independently licensed later visual/reference study**. Their outlines represent typographic forms rather than time-resolved hardpen trajectories. **No fonts, teacher samples, third-party vector outlines or copyrighted model coefficients were imported** into this prototype.
- Existing [A2 stroke motion research](A2_BASIC_STROKE_MODEL.md) motivates differentiating sources, semantic events, small local timing variation, nib behavior and geometrical control points rather than inferring genuine human movements from one completed image.

No numerical angle or point coefficient in A2.3 is claimed to come directly from those teaching sources. All such coefficients and the curated landmarks are **explicit engineering choices**. An independent teacher and/or an adequately licensed measured-pen trace dataset must still validate them.

## Model: source-preserving re-authoring of a DIFFERENT candidate skeleton

`animation/experiments/regular-kaishu-model.js` constructs a **new read-only derivative candidate** from the original glyph and stroke metadata. It NEVER edits the archived `stroke.median`, `stroke.outline`, character order, normative metadata or released A4 PDF.

- **横:** replace inconsistent brush median wiggles with a nearly straight guide and a gentle right-up ascent. A subtle sub-5-unit controlled arc is permitted; do not create multiple waves, and distinguish long from short by source/stroke role.
- **竖:** use a robust centerline estimate rather than following individual left-right perturbations; keep slight intended side inclination for enclosures but enforce structural verticality.
- **横折／横折钩:** split horizontal and vertical branches at one meaningful corner. Remove short *extra* zigzags before the turn. Prevent obvious angular doubling or accidental disconnected lines.
- **竖钩:** retain a long, mostly straight shaft and a **short** purposeful small hook, with a crisp terminal rather than a broad brush-style flourish.
- **撇／捺:** sample continuous visually smooth sweeps and add **small, purposeful gradual endpoint taper**. A 捺 may broaden very mildly before its terminal toe, but a standard rigid nib is not a traditional calligraphy brush. A source segment with hand-tremor wiggles must not be copied blindly.
- **点、其他复杂 strokes:** keep source-proportioned geometry and use conservative simplification/fallback when the primitive is not yet specifically reviewed.

Starting set includes handcrafted **engineering control points** for a small set of important source glyph/strokes: 一, 十, 人, 火, 口, 巾, 水, 月 and representative 龠 segments. All nine current experimental glyphs remain in their existing context. The non-curated strokes use simple semantic axis or curve geometry, but **none of these coordinates is promoted to normative educational evidence**.

The model passes revised points to the existing A2.2 `Hardpen.makePlan` to reuse the same strictly increasing clock and bounded movement; the absolute source duration, glyph selection and original stroke order remain untouched.

## Ink renderer: firm pen, not blunt tube and not 毛笔

`regular-kaishu-ink.js` uses the previously proven **immutable round-capped hardpen fragment union**. Each settled capsule has a deterministic width profile at its original source arclength, e.g.:

- 横 and vertical core widths close to 26 SVG units, with **very mild** regular-script emphasis at selected starts/finishes.
- 撇 and terminal 捺 gradually approach a fine tip; 捺's shoulder is only moderately wider, never a 2× or 3× brush stroke.
- 小钩 contracts progressively after the original structural change of direction.
- Gray completed/hint strokes use the **same per-fragment widths** as actual red ink. Completed red fragments never change or retract when the active short segment advances, preventing the former 口-corner one-pixel erasure.
- User-visible pressure values, if later enabled, remain synthetic and are not equated to pen width or force in Newtons.

Default width is still nominal **SVG source coordinates**, not 0.5mm actual metal nib dimensions. Preserve original contact, paper grid and no-source-dataset status.

## A/B and review conditions

**A** = existing published A2.2 hardpen renderer with original wavering medians and 26-unit monoline stroke.
**B** = experimental regular-script geometry and modest tapered width profiles, **same original character/stroke timeline**, 9 glyphs, no added stroke or changed lesson metadata.

Preview page: `animation/experiments/regular-kaishu-lab.html`. New helper modules are isolated in `animation/experiments`; A1.3 `player.js`, `motion.js`, `brush-union.js`, `timeline.js`, `samples.js`, the published A2.2 `hardpen-stage.js` and the user-requested **hardpen default / original brush option** are all retained unchanged.

### Automated acceptance

- **Node all 40 strokes**: source bytes/locations unchanged; horizontal angle bounded **1–5 degrees** and max variation <=5 units for five representative strokes; supporting vertical residual variation tightly constrained; 口 fold squareness, 水/月/巾 short hooks, no artificial extra double pivot; widths continuous/bounded, fine tips on 撇/捺/钩; strictly monotone temporal distance and all finite source-space positions.
- **Chromium all 9 glyphs ×8 timepoints**: old and candidate render with one clock; candidate red ink **never shrinks**; no stray source-alpha masks or brush silhouettes; every completed candidate uses full ordered 40-stroke shape; B actually differs from A in the problematic glyphs; selected tip follows the current candidate path; 390px responsiveness; inspect the generated nine-glyph visual comparison sheet.
- **Integrity**: existing A1 40-source stroke masks, A1.6 two-style/two-tool selectors, previous hardpen 63-frame raster regression, A2.1 raw-stroke A/B, v0.5.1 299-page PDF/manifest, 201 reviewed-source records retain their original state.
- **No silent promotion**: candidate geometric checks alone are *not sufficient* to certify "工整、专业、标准楷书". A continuous screenshot review and a knowledgeable handwriting teacher's stroke-by-stroke assessment must precede changing the deployed hardpen default. Initially publish **an opt-in laboratory**, not an unreviewed replacement.

Future A2.4: independent layout/structure calibration across more complex glyphs; review stroke widths, entry/terminal kinematics, dominant/secondary stroke hierarchy, inter-stroke spacing and consistent body-center; compare to rights-cleared regular-script measured rigid-pen templates. This is where a truly professional rather than merely tidier look must be established.
