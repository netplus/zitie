'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const Brush=require('../brush-union.js');
const Gallery=require('../gallery.js');
const Timeline=require('../timeline.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const find=ch=>glyphs.find(g=>g.character===ch);

test('canonical gallery filters and wraps without changing any primary sample',()=>{
  assert.equal(glyphs.length,9);
  assert.deepEqual(Gallery.batches(glyphs),['B01','B02','B21']);
  assert.deepEqual(Gallery.filteredGlyphs(glyphs,'水').map(x=>x.character),['水']);
  assert.deepEqual(Gallery.filteredGlyphs(glyphs,'B02').map(x=>x.character),['火','水','月']);
  assert.deepEqual(Gallery.filteredGlyphs(glyphs,'横折','B01').map(x=>x.character),['口','巾']);
  assert.deepEqual(Gallery.filteredGlyphs(glyphs,'','B21').map(x=>x.character),['龠']);
  assert.equal(Gallery.filteredGlyphs(glyphs,'不存在').length,0);
  assert.equal(Gallery.neighbor(glyphs,201,1).character,'一');
  assert.equal(Gallery.neighbor(glyphs,1,-1).character,'龠');
});

test('median sampling follows every verified source vertex without inventing turns',()=>{
  const original=find('水').strokes[0].median;
  const before=JSON.stringify(original);
  const sampled=Brush.sampleMedian(original,8);
  assert.deepEqual([sampled[0].x,sampled[0].y],original[0]);
  assert.deepEqual([sampled.at(-1).x,sampled.at(-1).y],original.at(-1));
  assert.ok(sampled.length>original.length);
  assert.ok(Math.abs(sampled.at(-1).distance-Timeline.polylineLength(original))<1e-6);
  for(const p of original)
    assert.ok(sampled.some(x=>Math.abs(x.x-p[0])<1e-6&&Math.abs(x.y-p[1])<1e-6));
  for(let i=1;i<sampled.length;i++)
    assert.ok(sampled[i].distance>sampled[i-1].distance);
  assert.equal(JSON.stringify(original),before);
});

test('measured width depends on original contour, not one global radius',()=>{
  const filled=(x,y)=>x>=0&&x<=200&&Math.abs(y)<=17;
  const profile=Brush.makeProfile([[4,0],[196,0]],filled,{spacing:8,margin:4});
  assert.equal(profile.method,'outline-cross-section');
  assert.equal(profile.coverage,'independent-round-stroke-union');
  assert.ok(profile.sampledWithFill>8);
  assert.ok(profile.fallbackSamples<3);
  assert.ok(profile.segments.every(x=>x.width>=37&&x.width<=47));
  assert.equal(profile.segments.length,profile.stations.length-1);
  assert.ok(profile.segments.every(x=>/^\s*M [^Z]+ L [^Z]+$/.test(x.d)));
});

test('brush state is monotone in travelled arclength and preserves a growing prefix',()=>{
  const profile=Brush.makeProfile([[0,0],[100,0]],(x,y)=>x>=0&&x<=100&&Math.abs(y)<15);
  let previousDistance=-1,previousVisible=-1,previousScale=-1;
  assert.equal(Brush.stateAt(profile,0).visibleCount,0);
  assert.equal(Brush.stateAt(profile,0).active,-1);
  for(let n=0;n<=1000;n++){
    const p=n/1000,state=Brush.stateAt(profile,p);
    assert.ok(state.distance>=previousDistance,'distance decreased '+p);
    assert.ok(state.visibleCount>=previousVisible,'visible completed prefix decreased');
    assert.ok(state.contactScale>=previousScale,'initial brush contact shrank');
    assert.ok(state.active>=-1&&state.active<profile.segments.length);
    assert.ok(state.tip.every(Number.isFinite));
    previousDistance=state.distance;
    previousVisible=state.visibleCount;
    previousScale=state.contactScale;
  }
  assert.equal(Brush.stateAt(profile,1).visibleCount,profile.segments.length);
  assert.equal(Brush.stateAt(profile,1).active,-1);
});

test('early paint contact grows gently, never with a full-size stationary disk at zero',()=>{
  const profile=Brush.makeProfile([[0,0],[500,0]],null);
  assert.equal(profile.method,'fallback-no-fill-API');
  assert.equal(profile.sampledWithFill,0);
  const a=Brush.stateAt(profile,0);
  const b=Brush.stateAt(profile,.01);
  const c=Brush.stateAt(profile,.04);
  assert.equal(a.contactScale,0);
  assert.ok(b.contactScale>0&&b.contactScale<1);
  assert.equal(c.contactScale,1);
  assert.ok(a.visibleCount<=b.visibleCount&&b.visibleCount<=c.visibleCount);
});

test('all nine source-backed glyphs retain exact stroke count and source median geometry',()=>{
  for(const g of glyphs){
    const raw=JSON.stringify(g.strokes);
    assert.equal(Timeline.validateGlyph(g),true);
    const tl=Timeline.buildTimeline(g);
    assert.equal(tl.strokes.length,g.expected_stroke_count);
    for(const stroke of g.strokes){
      const profile=Brush.makeProfile(stroke.median,null);
      assert.ok(profile.length>0);
      assert.ok(profile.segments.length>=1);
      assert.equal(profile.coverage,'independent-round-stroke-union');
      assert.ok(profile.segments.every(seg=>Number.isFinite(seg.width)&&seg.width>0));
      assert.equal(Brush.stateAt(profile,0).distance,0);
      assert.equal(Brush.stateAt(profile,1).distance,profile.length);
    }
    assert.equal(JSON.stringify(g.strokes),raw,'source stroke or median unexpectedly changed');
  }
});

test('invalid medians fail closed rather than synthesizing incorrect stroke direction',()=>{
  assert.throws(()=>Brush.sampleMedian([]),/Invalid/);
  assert.throws(()=>Brush.sampleMedian([[1,1],[1,1]]),/Zero length/);
  assert.throws(()=>Brush.sampleMedian([[1,1],[NaN,2]]),/Nonfinite/);
  assert.throws(()=>Brush.makeProfile([[0,0],[30,0]],null,{margin:100}),/Invalid/);
  assert.throws(()=>Brush.stateAt(null,.4),/Invalid/);
  assert.throws(()=>Brush.stateAt(Brush.makeProfile([[0,0],[50,0]],null),NaN),/Invalid/);
});

test('folds, hooks and complex strokes stay continuous without sub-stroke multiplication',()=>{
  for(const [glyph,index] of [['口',1],['水',0],['月',1],['龠',13]]){
    const entry=find(glyph),source=entry.strokes[index];
    const profile=Brush.makeProfile(source.median,null);
    assert.equal(profile.segments.length+1,profile.stations.length);
    assert.ok(profile.stations.length>source.median.length);
    for(let i=1;i<profile.segments.length;i++){
      const prior=profile.segments[i-1],cur=profile.segments[i];
      assert.ok(Math.abs(prior.x1-cur.x0)<1e-6);
      assert.ok(Math.abs(prior.y1-cur.y0)<1e-6);
      assert.ok(Math.abs(prior.end-cur.start)<1e-6);
    }
  }
});


test('optical front cursor advances with ink but preserves the canonical median timeline',()=>{
  for(const [char,index] of [['口',1],['水',0],['月',1],['龠',13]]){
    const stroke=find(char).strokes[index],before=JSON.stringify(stroke);
    const profile=Brush.makeProfile(stroke.median,null);
    const guide=Brush.makeVisualFrontier(profile);
    assert.equal(guide.sourceMedianUntouched,true);
    assert.equal(guide.kind,'optical_ink_frontier_cursor_not_normative_or_physical_pen');
    assert.equal(Brush.visualFrontAt(guide,0).lead,0);
    let previous=-1;
    for(let i=0;i<=250;i++){
      const t=i/250,f=Brush.visualFrontAt(guide,t);
      assert.ok(f.distance>=previous-1e-8,
        char+': optical cursor travelled backwards');
      assert.ok(f.distance+1e-8>=profile.length*t,
        char+': marker lags its own canonical median');
      assert.ok(f.lead<=guide.maxLead+1e-8,
        char+': unbounded optical anticipation');
      assert.ok(f.tip.every(Number.isFinite));
      previous=f.distance;
    }
    assert.ok(Math.abs(Brush.visualFrontAt(guide,1).distance-profile.length)<1e-6);
    assert.equal(JSON.stringify(stroke),before,'Optical guide changed source medians');
  }
});

test('normal short strokes keep the original cursor and drawing semantics',()=>{
  const glyph=find('一'),stroke=glyph.strokes[0],raw=JSON.stringify(stroke);
  const profile=Brush.makeProfile(stroke.median,null);
  assert.deepEqual(Brush.pointAtDistance(profile,0),stroke.median[0]);
  assert.deepEqual(Brush.pointAtDistance(profile,profile.length),stroke.median.at(-1));
  assert.equal(JSON.stringify(stroke),raw);
  assert.throws(()=>Brush.makeVisualFrontier(profile,{probeStep:0}),/Invalid/);
  assert.throws(()=>Brush.visualFrontAt(null,.5),/Invalid/);
});
