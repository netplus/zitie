'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const P=require('../experiments/stroke-primitives.js');
const T=require('../timeline.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const pick=(name,index)=>{const g=glyphs.find(g=>g.character===name);return {g,index,stroke:g.strokes[index]};};
const examples=[
  ['一',0,'heng'],['十',1,'shu'],['人',0,'pie'],
  ['口',1,'zhe'],['水',0,'gou'],['月',1,'zhe-gou'],
  ['龠',13,'zhe']
];
const dist=(a,b)=>Math.hypot(a.x-b[0],a.y-b[1]);

test('the five basic gesture families preserve validated stroke classification',()=>{
  assert.ok(P.categories.includes('heng')&&P.categories.includes('shu'));
  assert.ok(P.categories.includes('pie')&&P.categories.includes('gou'));
  assert.ok(P.categories.includes('zhe'));
  for(const [name,index,kind] of examples){
    const {g}=pick(name,index),s=P.semantics(g,index);
    assert.equal(s.kind,kind);
    assert.equal(s.reviewedTeachingTrajectory,false);
    assert.equal(s.source,'unreviewed_engineering_gesture_candidate');
  }
  assert.equal(P.semantics(pick('火',0).g,0).kind,'dian');
  assert.equal(P.semantics(pick('人',1).g,1).kind,'na');
  assert.ok(P.semantics(pick('水',1).g,1).kind==='generic',
    'Compound 横撇 requires separate reviewed action semantics');
});

test('curated hook/fold pivots remain EXACT original median vertices',()=>{
  for(const [name,index,kind] of examples){
    const {g,stroke}=pick(name,index);
    const sem=P.semantics(g,index),plan=P.makePlan(stroke,sem);
    const anchors=plan.geometry.sourceVertexDistances;
    for(const key of ['foldVertex','hookVertex']){
      if(sem[key]===undefined)continue;
      const pos=anchors[sem[key]]/plan.geometry.length;
      const sample=P.pointAt(plan,pos);
      assert.ok(dist(sample,stroke.median[sem[key]])<.00001,
        name+': derived curve lost canonical '+key);
      assert.ok(plan.geometry.corners.includes(sem[key]),
        name+': a semantic pivot was improperly rounded');
    }
    const phases=plan.events.map(e=>e.phase);
    if(kind.includes('zhe'))assert.ok(phases.includes('turn'));
    if(kind.includes('gou'))assert.ok(phases.includes('flick'));
  }
});

test('every source-backed stroke keeps all source knots, order and endpoints',()=>{
  for(const g of glyphs){
    const original=JSON.stringify(g.strokes);
    const tl=T.buildTimeline(g);
    for(let i=0;i<g.strokes.length;i++){
      const stroke=g.strokes[i],plan=P.makePlan(stroke,P.semantics(g,i));
      const samples=plan.geometry.samples,knots=plan.geometry.sourceVertexDistances;
      assert.equal(plan.canonicalStrokeOrderUnchanged,true);
      assert.equal(plan.fittedToHumanData,false);
      assert.equal(plan.sourceDirectionReviewed,false);
      assert.equal(plan.geometry.verification,'unit_test_unprobed');
      assert.equal(knots.length,stroke.median.length);
      assert.ok(dist(samples[0],stroke.median[0])<1e-8);
      assert.ok(dist(samples.at(-1),stroke.median.at(-1))<1e-8);
      for(let j=0;j<knots.length;j++)
        assert.ok(dist(P.pointAt(plan,knots[j]/plan.geometry.length),
          stroke.median[j])<1e-4,
          g.character+' stroke '+i+' lost median knot '+j);
      for(let j=1;j<samples.length;j++)
        assert.ok(samples[j].distance>samples[j-1].distance,
          'Non-monotone geometric arclength');
      assert.ok(plan.geometry.maxDeviation<=16.0001,
        'Geometric trajectory deviated too far from source');
      assert.equal(tl.strokes[i].durationMs>0,true);
    }
    assert.equal(JSON.stringify(g.strokes),original);
  }
});

test('action timings are monotone with distinct fold/hook dynamics',()=>{
  for(const [name,index,kind] of examples){
    const {g,stroke}=pick(name,index);
    const plan=P.makePlan(stroke,P.semantics(g,index));
    const map=plan.timing;
    assert.equal(map.progressAt(0),0);assert.equal(map.progressAt(1),1);
    let previous=-1,stepMax=0;
    for(let i=0;i<=1000;i++){
      const time=i/1000,s=map.progressAt(time);
      assert.ok(Number.isFinite(s)&&s>=previous&&s>=0&&s<=1,
        name+': time reversed');
      if(i>0)stepMax=Math.max(stepMax,s-previous);
      assert.ok(Number.isFinite(map.speedAt(time))&&map.speedAt(time)>=0);
      assert.ok(Number.isFinite(plan.stateAt(time).point.x));
      previous=s;
    }
    assert.ok(stepMax<.02,'Large trajectory discontinuity in '+name);
    for(let i=0;i<plan.events.length-1;i++)
      assert.ok(plan.events[i].s<=plan.events[i+1].s,
        'Out-of-order action grammar');
    for(const key of ['foldVertex','hookVertex']){
      if(plan.sem[key]===undefined)continue;
      const at=plan.geometry.sourceVertexDistances[plan.sem[key]]/
        plan.geometry.length;
      const clock=map.clockAt(at);
      assert.ok(Math.abs(map.progressAt(clock)-at)<.00005);
      assert.ok(map.speedDensityAt(at)>map.speedDensityAt(.45),
        name+': pivot should spend relatively more time per unit arclength');
    }
  }
});

test('straight, fall-off, fold and hook profiles have distinct time-density signatures',()=>{
  const plan=(name,index=0)=>{const {g,stroke}=pick(name,index);
    return P.makePlan(stroke,P.semantics(g,index));};
  const horizontal=plan('一'),vertical=plan('十',1),sweep=plan('人'),hook=plan('水');
  assert.notDeepEqual(horizontal.timing.timeTable,vertical.timing.timeTable);
  assert.ok(sweep.timing.speedDensityAt(.95)<sweep.timing.speedDensityAt(.30),
    'Falling stroke should gain relative speed toward release');
  assert.ok(hook.timing.hooks>.65,'Hook is near bottom of 水 stroke');
  assert.ok(hook.timing.speedDensityAt(hook.timing.hooks)>
    horizontal.timing.speedDensityAt(.70)+1.0,
    'The hook must visibly brake before flick');
});

test('source contour rejection falls back deterministically, no speculative outside smoothing',()=>{
  const {g,stroke}=pick('一',0),sem=P.semantics(g,0);
  const base=P.makePlan(stroke,sem);
  const reject=(x,y)=>Math.abs(x-stroke.median[0][0])<1e-6&&
    Math.abs(y-stroke.median[0][1])<1e-6;
  const blocked=P.makePlan(stroke,sem,reject);
  assert.equal(blocked.geometry.verification,'source_svg_fill_probe');
  assert.ok(blocked.geometry.rejectedSegments>0);
  assert.equal(blocked.sourceMedianUnchanged,true);
  assert.equal(JSON.stringify(stroke.median),JSON.stringify(g.strokes[0].median));
  assert.ok(base.geometry.samples.length>stroke.median.length);
  assert.throws(()=>P.makePlan(stroke,sem,undefined,
    {geometry:{maxOffset:100}}),/Invalid/);
  assert.throws(()=>P.makePlan(stroke,sem,undefined,
    {timing:{easeWeight:1.4}}),/Invalid/);
  assert.throws(()=>P.makePlan(null,sem),/Invalid/);
  assert.throws(()=>P.makePlan(stroke,{kind:'bad',
    reviewedTeachingTrajectory:false}),/unreviewed/);
});
