'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const Motion=require('../motion.js');
const Brush=require('../brush-union.js');
const Pen=require('../experiments/pen-contact.js');
const K=require('../experiments/pen-kinematics.js');
const Gestures=require('../experiments/gesture-data.js');
const Timeline=require('../timeline.js');
global.window=global;require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const find=c=>glyphs.find(g=>g.character===c);
function make(c,i){
  const glyph=find(c),stroke=glyph.strokes[i];
  const t=Timeline.buildTimeline(glyph);
  const motion=t.strokes[i].motion;
  const profile=Brush.makeProfile(stroke.median,null);
  const pen=Pen.makePlan(stroke,profile,motion,Gestures.lookup(glyph,i));
  return {pen,motion,warp:K.makeTimeWarp(pen,motion)};
}
function inverse(mapping,target){
  let lo=0,hi=1;
  for(let i=0;i<45;i++){
    const mid=(lo+hi)/2;
    if(mapping.progressAt(mid)<target)lo=mid;else hi=mid;
  }
  return (lo+hi)/2;
}
test('experimental retiming preserves the original duration and strictly advances on all 40 source strokes',()=>{
  for(const g of glyphs){
    for(let i=0;i<g.strokes.length;i++){
      const {pen,motion,warp}=make(g.character,i);
      assert.equal(warp.kind,'research_only_substroke_time_density_not_measured');
      assert.equal(warp.durationUnchanged,true);
      assert.equal(warp.sourceStrokeCountUnchanged,true);
      assert.equal(warp.progressAt(0),0);
      assert.equal(warp.progressAt(1),1);
      assert.ok(Math.abs(warp.penPlan.length-motion.length)<1e-6);
      let prev=-1;
      for(let n=0;n<=1000;n++){
        const t=n/1000,p=warp.progressAt(t);
        assert.ok(Number.isFinite(p));
        assert.ok(p>=prev,'experimental nib went backward in '+g.character);
        assert.ok(p>=0&&p<=1);
        prev=p;
      }
      assert.equal(warp.progressAt(1),1);
    }
  }
});
test('annotated mouth fold dwells locally longer than unchanged baseline',()=>{
  const {pen,motion,warp}=make('口',1);
  const pivot=pen.pivot/pen.length;
  const lo=Math.max(.01,pivot-.04),hi=Math.min(.99,pivot+.04);
  const baseWindow=inverse(motion,hi)-inverse(motion,lo);
  const labWindow=inverse(warp,hi)-inverse(warp,lo);
  assert.ok(labWindow>baseWindow*1.10,
    'local fold event should allocate visibly more wall time than stable baseline');
  assert.ok(warp.densityAt(pen.pivot)>warp.densityAt(pen.pivot-160));
});
test('hook releases speed up following the exact original source pivot without breaking the stroke',()=>{
  for(const [ch,index] of [['水',0],['月',1]]){
    const {pen,warp}=make(ch,index);
    assert.equal(pen.gesture.kind,'hook');
    const near=pen.pivot;
    assert.ok(warp.densityAt(near)>warp.densityAt(
      Math.min(pen.length*.94,near+Math.max(18,pen.pivotWindow*.95))),
    ch+' needs a short relative post-pivot flick');
    assert.ok(warp.normalizedPace(.6)>=0);
    assert.ok(warp.progressAt(.99)<1);
  }
});
test('isolated experimental warp never mutates original median, timeline or pressure plan',()=>{
  const source=JSON.stringify(glyphs.map(g=>g.strokes));
  for(const g of glyphs){
    const a=Timeline.buildTimeline(g);
    for(let i=0;i<g.strokes.length;i++){
      const {pen,motion,warp}=make(g.character,i);
      assert.deepEqual(warp.distanceSamples,motion.distances);
      assert.equal(warp.timeSamples.length,motion.fractions.length);
      assert.equal(pen.motion.kind,motion.kind);
    }
    assert.equal(a.totalMs,Timeline.buildTimeline(g).totalMs);
  }
  assert.equal(JSON.stringify(glyphs.map(g=>g.strokes)),source);
});
test('unapproved motion coefficients and bad timestamps cannot silently be used',()=>{
  const {pen,motion,warp}=make('口',1);
  assert.throws(()=>K.makeTimeWarp(pen,motion,{pivotHold:-1}),/Unsupported/);
  assert.throws(()=>K.makeTimeWarp(pen,motion,{flickBoost:1}),/Unsupported/);
  assert.throws(()=>warp.progressAt(NaN),/Nonfinite/);
  assert.throws(()=>K.makeTimeWarp(null,motion),/Invalid/);
});