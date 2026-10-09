/* A1 offline, deterministic stroke timeline. MIT-style project logic; drawing data separately licensed. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.ZitieTimeline = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  const finite = n => typeof n === 'number' && Number.isFinite(n);
  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

  function validateGlyph(glyph) {
    if (!glyph || !Number.isInteger(glyph.main_id) || glyph.main_id < 1 ||
        typeof glyph.character !== 'string' || [...glyph.character].length !== 1 ||
        !Array.isArray(glyph.strokes) || !glyph.strokes.length ||
        glyph.strokes.length !== glyph.expected_stroke_count ||
        typeof glyph.order_code !== 'string' ||
        glyph.order_code.length !== glyph.strokes.length ||
        typeof glyph.normative_ref !== 'string' ||
        !/^(B\d\d)\/[1-9]\d*$/.test(glyph.normative_ref)) {
      throw new Error('Invalid canonical glyph metadata');
    }
    if (glyph.trajectory_review_status !== 'engineering_preview_unreviewed' &&
        glyph.trajectory_review_status !== 'reviewed_per_stroke') {
      throw new Error('Trajectory audit status required');
    }
    glyph.strokes.forEach((s, i) => {
      if (!s || s.index !== i + 1 || typeof s.outline !== 'string' ||
          !/^\s*M\s/i.test(s.outline) || !/[zZ]\s*$/.test(s.outline) ||
          !Array.isArray(s.median) || s.median.length < 2 ||
          !s.median.every(p => Array.isArray(p) && p.length === 2 && p.every(finite)) ||
          typeof s.name_status !== 'string' ||
          !['reviewed', 'ordinal_only'].includes(s.name_status) ||
          (s.name_status === 'reviewed' && !s.name)) {
        throw new Error('Missing or incompatible stroke trajectory: ' + (i + 1));
      }
    });
    return true;
  }

  function polylineLength(points) {
    let n = 0;
    for (let i = 1; i < points.length; i++)
      n += Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
    if (!finite(n) || n < 0.01) throw new Error('Zero-length median');
    return n;
  }

  function pointAt(points, progress) {
    let remaining = polylineLength(points) * clamp(progress, 0, 1);
    for (let i = 1; i < points.length; i++) {
      const p = points[i - 1], q = points[i];
      const d = Math.hypot(q[0] - p[0], q[1] - p[1]);
      if (remaining <= d && d > 0) {
        const t = remaining / d;
        return [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t];
      }
      remaining -= d;
    }
    return points[points.length - 1].slice();
  }

  function buildTimeline(glyph, pauseMs = 260) {
    validateGlyph(glyph);
    if (!finite(pauseMs) || pauseMs < 0 || pauseMs > 5000) throw new Error('Invalid pause');
    let cursor = 0;
    const strokes = glyph.strokes.map((s, i) => {
      const length = polylineLength(s.median);
      const durationMs = finite(s.duration_ms) ?
        s.duration_ms : clamp(300 + length * 1.25, 550, 2600);
      if (durationMs < 100 || durationMs > 10000) throw new Error('Invalid duration');
      const startMs = cursor, endMs = startMs + durationMs;
      const gapMs = i === glyph.strokes.length - 1 ? 0 : pauseMs;
      cursor = endMs + gapMs;
      return { index: i, startMs, endMs, durationMs, pauseMs: gapMs, length };
    });
    return { strokes, totalMs: cursor, glyph };
  }

  function frameAt(timeline, value) {
    const elapsedMs = clamp(value, 0, timeline.totalMs);
    if (elapsedMs >= timeline.totalMs)
      return { elapsedMs, index: timeline.strokes.length - 1, progress: 1, phase: 'finished', tip: null };
    for (const s of timeline.strokes) {
      if (elapsedMs < s.endMs) {
        const progress = clamp((elapsedMs - s.startMs) / s.durationMs, 0, 1);
        return { elapsedMs, index: s.index, progress, phase: 'writing',
          tip: pointAt(timeline.glyph.strokes[s.index].median, progress) };
      }
      if (elapsedMs < s.endMs + s.pauseMs)
        return { elapsedMs, index: s.index, progress: 1, phase: 'pause', tip: null };
    }
    throw new Error('Non-contiguous timeline');
  }

  function strokeStart(timeline, index) {
    if (!Number.isInteger(index) || index < 0 || index >= timeline.strokes.length)
      throw new Error('Invalid stroke index');
    return timeline.strokes[index].startMs;
  }

  function strokeEnd(timeline, index) {
    strokeStart(timeline, index);
    return timeline.strokes[index].endMs;
  }

  return { validateGlyph, polylineLength, pointAt, buildTimeline, frameAt, strokeStart, strokeEnd, clamp };
});
