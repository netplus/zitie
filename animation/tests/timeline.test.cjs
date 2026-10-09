'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const T = require('../timeline.js');
global.window = global;
require('../samples.js');
const pack = global.ZITIE_SAMPLES;
delete global.window;
const lookup = ch => pack.glyphs.find(g => g.character === ch);

test('offline bundle contains nine actual primary radicals, with an explicit unreviewed median gate', () => {
  assert.equal(pack.schema_version, 1);
  assert.equal(pack.review_state, 'trajectory_not_teaching_approved');
  assert.equal(pack.glyphs.length, 9);
  const ids = pack.glyphs.map(g => g.main_id);
  assert.equal(new Set(ids).size, 9);
  for (const g of pack.glyphs) {
    assert.equal(T.validateGlyph(g), true);
    assert.equal(g.trajectory_review_status, 'engineering_preview_unreviewed');
    assert.equal(g.outline_review_status, 'legacy_artwork_ready');
    assert.match(g.source_url, new RegExp(pack.source_revision));
  }
});

test('canonical batch data owns stroke counts, order and reviewed fine names', () => {
  const policy = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../data/teaching-source-policy.json')));
  const blocked = new Set(policy.rules.find(r => r.field === 'fine_stroke_names').main_ids);
  for (const g of pack.glyphs) {
    const book = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../data/' + g.batch_id + '.json')));
    const original = book.entries.find(e => e.main_id === g.main_id);
    assert.equal(original.character, g.character);
    const code = original.stroke_order_review?.order_code || original.order_code || original.order_code_candidate;
    const names = original.stroke_names || original.fine_stroke_names_review?.adjudicated_names;
    assert.equal(g.order_code, code);
    assert.equal(g.strokes.length, names.length);
    assert.equal(blocked.has(g.main_id), false);
    assert.deepEqual(g.strokes.map(s => s.name), names);
  }
});

test('one median per stroke; source geometry remains untouched in the timeline', () => {
  for (const g of pack.glyphs) {
    const before = JSON.stringify(g.strokes);
    const tl = T.buildTimeline(g);
    assert.equal(tl.strokes.length, g.expected_stroke_count);
    assert.ok(tl.totalMs > 0);
    assert.equal(JSON.stringify(g.strokes), before);
    for (const s of tl.strokes) {
      assert.ok(s.durationMs >= 550 && s.durationMs <= 2600);
      assert.ok(s.length > 0);
      assert.ok(s.endMs <= tl.totalMs);
    }
  }
});

test('arclength interpolation follows the input median rather than the closed SVG outline', () => {
  const hor = lookup('一').strokes[0].median;
  assert.deepEqual(T.pointAt(hor, 0), hor[0]);
  assert.deepEqual(T.pointAt(hor, 1), hor[hor.length - 1]);
  assert.ok(T.pointAt(hor, 0.65)[0] > T.pointAt(hor, 0.3)[0]);
  const tl = T.buildTimeline(lookup('十'));
  const first = T.frameAt(tl, tl.strokes[0].durationMs / 2);
  assert.equal(first.phase, 'writing');
  assert.ok(first.progress > 0 && first.progress < 1);
  assert.equal(first.index, 0);
  const second = T.frameAt(tl, T.strokeStart(tl, 1) + tl.strokes[1].durationMs / 2);
  assert.equal(second.index, 1);
  assert.ok(second.tip[1] < lookup('十').strokes[1].median[0][1]);
});

test('all pauses and final states form one deterministic timeline', () => {
  for (const g of pack.glyphs) {
    const tl = T.buildTimeline(g);
    for (const s of tl.strokes) {
      assert.equal(T.frameAt(tl, s.startMs).index, s.index);
      if (s.pauseMs) {
        const gap = T.frameAt(tl, s.endMs + s.pauseMs / 2);
        assert.equal(gap.phase, 'pause');
        assert.equal(gap.index, s.index);
        assert.equal(gap.progress, 1);
      }
    }
    const end = T.frameAt(tl, tl.totalMs);
    assert.equal(end.phase, 'finished');
    assert.equal(end.progress, 1);
    assert.equal(end.tip, null);
  }
});

test('turns and hooks remain inside single ordered strokes', () => {
  const fold = lookup('口').strokes[1].median;
  assert.ok(fold.some((p,i) => i>0 && p[0] > fold[0][0] + 350));
  assert.ok(fold.at(-1)[1] < fold[0][1] - 200);
  const hook = lookup('水').strokes[0].median;
  assert.ok(hook[4][1] < hook[0][1] - 600);
  assert.ok(hook.at(-1)[0] < hook[4][0] - 100);
  const turn = lookup('巾').strokes[1].median;
  assert.ok(turn[7][1] < turn[0][1]);
  assert.ok(turn.at(-1)[0] < turn[7][0] - 100);
  assert.equal(lookup('龠').strokes.length, 17);
});

test('corrupt, missing, zero-length and unreviewed-source-without-label inputs fail closed', () => {
  const copy = g => JSON.parse(JSON.stringify(g));
  let g = copy(lookup('一')); g.strokes[0].median = null;
  assert.throws(() => T.buildTimeline(g), /Missing or incompatible/);
  g = copy(lookup('一')); g.strokes[0].median = [[1,2],[1,2]];
  assert.throws(() => T.buildTimeline(g), /Zero-length median/);
  g = copy(lookup('一')); g.expected_stroke_count = 2;
  assert.throws(() => T.buildTimeline(g), /Invalid canonical/);
  g = copy(lookup('一')); delete g.trajectory_review_status;
  assert.throws(() => T.buildTimeline(g), /Trajectory audit status/);
  g = copy(lookup('一')); g.strokes[0].name_status = 'ordinal_only';
  assert.equal(T.validateGlyph(g), true);
});

test('out-of-range seek and speed boundaries are rejected', () => {
  const tl = T.buildTimeline(lookup('月'));
  assert.throws(() => T.strokeStart(tl, 4), /Invalid stroke/);
  assert.throws(() => T.strokeEnd(tl, -1), /Invalid stroke/);
  assert.throws(() => T.buildTimeline(lookup('月'), -1), /Invalid pause/);
  assert.equal(T.frameAt(tl, -400).elapsedMs, 0);
  assert.equal(T.frameAt(tl, tl.totalMs + 100).phase, 'finished');
});
