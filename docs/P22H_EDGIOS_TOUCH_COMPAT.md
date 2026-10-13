# P2.2h — iPhone Edge tracing compatibility audit (candidate)

Date: 2026-10-13. Issue: [#163](https://github.com/netplus/zitie/issues/163).

## Report and evidence boundaries

On an iPhone, Edge reportedly cannot use the “整字临摹” touch writing feature while Chrome and Safari can. **This report does not specify whether opening the overlay fails or whether drawing is ignored, nor does it include an iOS/Edge version or event log.** The root cause is not independently confirmed.

Microsoft documents Edge for iOS historically using system WebKit/WKWebView (https://blogs.windows.com/msedgedev/2017/10/05/microsoft-edge-ios-android-developer/). WebKit has known touch/pointer-capture divergence, including https://bugs.webkit.org/show_bug.cgi?id=220196 and pointercancel during native gesture recognition (https://bugs.webkit.org/show_bug.cgi?id=193962). The original project assumed all direct touches would produce reliable pointer events.

## Source risks discovered (not asserted as reproduced Edge defects)

1. `pointer-input.js` has no fallback for `touchstart/touchmove/touchend` if the browser does not deliver pointer events on the real canvas, and it treats every viewport resize as an interrupted pen stroke.
2. `sourcePoint()` depended on a global `DOMPoint` / `matrixTransform`. Any unsupported WebView interop caused the first contact to be silently ignored.
3. `practice-bridge.js` disables writing until its IndexedDB read finishes. IndexedDB may be blocked/private or never settle; if so the page can appear ready to write while actually disabled.

## Safeguarded mitigation

- On the **iPhone/iPad Edge `EdgiOS/` UA only**, prefer genuine Touch Events for **one finger**. Preserve original Pointer Events for pen/mouse and for Safari/Chrome. Other browsers fall back to Touch Events only if no pointer session was started. Never synthesize a canonical outline or a "fake" scored stroke. Source points come only from actual touch/pointer client coordinates, through the original reference transform and TraceSession.
- Ignore the duplicate Pointer Events emitted alongside the chosen Edge touch stream. Never convert browser `pointercancel`, `touchcancel`, lost capture, or multiple simultaneous fingers to successful pointer-up.
- Convert client CSS pixels into source SVG coordinates using the analytically exact inverse affine `getScreenCTM()` (including rotation/scale/translation), without requiring global `DOMPoint`. Reject nonfinite or singular matrices.
- Do not discard a genuine Edge native touch when the browser address bar causes resize; still cancel `orientationchange` and disable/move/gesture states as before. Other browsers preserve prior resize-abort semantics when the canvas dimensions change.
- Bound only the **initial IndexedDB read** to 3.5 seconds; a blocked/unresponsive request degrades to honest **in-memory-only** writing with an unsaved warning and exit protection, never writes over an unverified existing local record. In-memory blue ink does not upload or persist elsewhere.
- If a WebView fails even to initialize the ink Canvas, restore the normal page and display an error rather than trapping the user inside the modal.
- Add `-webkit-touch-callout:none` to the ink Canvas only (not global text or buttons).

## Verification

- Node regression: exact matrix inverse without DOMPoint, touch route selection on EdgiOS vs Safari/CriOS/Android, one native touch / duplicate pointer suppression, touchcancel, multi-touch, orientation, stable-vs-resized viewport, pending storage timeout.
- Real Chromium CDP `Input.dispatchTouchEvent` with iPhone `EdgiOS` UA, 390×844: actual first source stroke blue pixel, exactly one written stroke, no ghost on cancel, toolbar-like resize handling, disabled storage explicitly reported while input remains enabled. **This is emulation, not native iPhone Edge.**
- Existing full Chromium CDP native Pointer Events/whole-word touch and persistence tests must remain unchanged and green.
- Exact feature-head A1/Chromium and Book integrity before merge, same-merge-SHA Pages Configure/Upload/Deploy afterward.
- The official PDF, 201/1045 source outlines, A3 nib/ink/pressure model, stroke-order checker, learner storage keys and data remain unchanged.

## Still required

After deployment, on the affected **physical iPhone Edge**, collect (without uploading raw writing data) the iOS version, Edge version, whether entering the overlay succeeds, whether the first touch produces a blue dot/line, whether the Saved status ever changes, and whether switching Safari/Edge on the same device reproduces. No physical Edge/WKWebView claim until this step passes.

## P2.2i follow-up: pointer-only coverage gap found on code retry

A subsequent source review found that the #164 EdgiOS user-agent branch dropped **every** finger `pointerdown` before checking whether any native `touchstart` actually arrived. If the real WKWebView supplies Pointer Events but not Touch Events, no stroke can start. This is a **proven logic dead zone**, not a proven explanation of the original physical-device report.

The revised approach starts actual Pointer Events immediately (including on Edge). If `touchstart` for that finger subsequently arrives, the in-progress source-coordinate session transitions in place to Touch Events; the original pointer capture is released, duplicate pointer move/up is ignored, and no second accepted stroke or cancellation is generated. If Touch Events never arrive, pointermove/up still finishes the existing stroke. If touchstart arrives first, the existing Touch Events route remains. Non-Edge Safari/Chrome, pen and mouse keep their previous channel choice. Multitouch still cancels.

Additional tests must exercise all three event-order families: pointer-only, pointer-first-then-touch, and touch-first-then-pointer; both duplicate suppression and the source geometry are unchanged. The native CDP touch verification is kept, and a separate **synthetic DOM PointerEvent** test under Edge UA covers pointer-only integration. The latter is deliberately not described as physical native iPhone Edge input.

Issue #163 remains open until the actual affected iPhone Edge (OS and Edge version recorded) confirms that ink appears and pen-up commits. If not, add on-device non-telemetric diagnostic output before any further speculative browser workarounds.
