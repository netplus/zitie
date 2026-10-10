'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const H=require('../experiments/hardpen-model.js');
const P=require('../experiments/stroke-primitives.js');
const T=require('../timeline.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const examples=[['一',0,'heng'],['十',1,'shu'],['人',0,'pie'],
  ['口',1,'zhe'],['水',0,'gou'],['月',1,'zhe-gou'],['龠',13,'zhe']];
const glyph=name=>glyphs.find(g=>g.character===name);

test('rigid nib is explicitly not the old source silhouette or flex brush',()=>{
  const original=JSON.stringify(glyphs);
  let inspected=0;
  for(const g of glyphs){
    const duration=T.buildTimeline(g);
    for(let i=0;i<g.strokes.length;i++){
      const plan=H.makePlan(g.strokes[i],P.semantics(g,i));
      assert.equal(plan.genre,'ordinary_firm_nib_hardpen_kaishu');
      assert.equal(plan.sourceInkOutlineUsed,false);
      assert.equal(plan.sourceMedianUnchanged,true);
      assert.equal(plan.originalTeachingReviewUnchanged,true);
      assert.equal(plan.reviewed,false);
      assert.equal(plan.width,26);
      assert.equal(plan.options.width,26);
      assert.ok(duration.strokes[i].durationMs>0);
      assert.equal(plan.completePath,plan.pathAt(1));
      assert.equal(plan.pathAt(0),'');
      assert.match(plan.completePath,/^M [\d.-]+ [\d.-]+ L /);
      assert.equal(plan.completePath.includes(' C '),false,
        'Rigid nib must sample a continuous polyline without decorative filled blobs');
      inspected++;
    }
  }
  assert.ok(inspected>=35);
  assert.equal(JSON.stringify(glyphs),original);
});

test('hardpen motion retains every source centerline vertex and sharp fold/hook',()=>{
  for(const [character,index,kind] of examples){
    const g=glyph(character),sem=P.semantics(g,index),plan=H.makePlan(g.strokes[index],sem);
    assert.equal(sem.kind,kind);
    assert.equal(plan.geometry.sourceVertexDistances.length,
      g.strokes[index].median.length);
    const compare=(a,b)=>Math.hypot(a.x-b[0],a.y-b[1]);
    assert.ok(compare(plan.geometry.samples[0],g.strokes[index].median[0])<1e-6);
    assert.ok(compare(plan.geometry.samples.at(-1),g.strokes[index].median.at(-1))<1e-6);
    for(let k=0;k<g.strokes[index].median.length;k++){
      const progress=plan.geometry.sourceVertexDistances[k]/plan.geometry.length;
      const p=P.pointAt({geometry:plan.geometry},progress);
      assert.ok(compare(p,g.strokes[index].median[k])<1e-4);
    }
    for(const prop of ['foldVertex','hookVertex'])
      if(sem[prop]!==undefined)
        assert.ok(plan.geometry.corners.includes(sem[prop]));
  }
});

test('bounded natural rigid-tip velocity is strictly forward with no artificial dead stops',()=>{
  for(const [character,index] of examples){
    const g=glyph(character),plan=H.makePlan(g.strokes[index],P.semantics(g,index));
    let prev=-1,largestJump=0;
    const durations=[];
    for(let i=0;i<=1000;i++){
      const t=i/1000,p=plan.progressAt(t),state=plan.stateAt(t);
      assert.ok(Number.isFinite(p)&&p>=prev&&p<=1&&p>=0);
      assert.ok(Number.isFinite(state.point.x)&&Number.isFinite(state.point.y));
      assert.ok(Number.isFinite(state.normalizedSpeed)&&state.normalizedSpeed>=0);
      assert.ok(plan.densityAt(p)>=.7&&plan.densityAt(p)<=2.5);
      assert.ok(state.physicalPressureMeasured===false);
      if(i>0)largestJump=Math.max(largestJump,p-prev);
      if(i>0&&i<1000)assert.ok(state.normalizedSpeed>.05,
        'Hardpen motion froze during active stroke');
      prev=p;
      durations.push(state.phase);
    }
    assert.ok(largestJump<.01,'Abrupt current-frame position jump');
    assert.equal(plan.progressAt(0),0);
    assert.equal(plan.progressAt(1),1);
    assert.equal(plan.stateAt(1).contact,false);
    const events=plan.events;
    for(let i=1;i<events.length;i++)
      assert.ok(events[i].s>=events[i-1].s);
    assert.equal(events[0].phase,'contact');
    assert.equal(events.at(-1).phase,'done');
    assert.ok(!events.some(e=>/藏锋|蓄墨|回锋|毛笔/.test(e.label)));
  }
});

test('fold hook does not linger like a brush pivot and uses separate short exit',()=>{
  for(const [character,index] of [['口',1],['水',0],['月',1],['龠',13]]){
    const g=glyph(character),sem=P.semantics(g,index);
    const plan=H.makePlan(g.strokes[index],sem);
    assert.ok(plan.events.some(e=>e.phase==='pivot'));
    if(sem.hookVertex!==undefined){
      assert.ok(plan.events.some(e=>e.phase==='hookExit'));
      assert.ok(plan.hook!==null);
      assert.ok(plan.densityAt(plan.hook)>plan.densityAt(.4));
      assert.ok(plan.densityAt(Math.min(1,plan.hook+.06))<plan.densityAt(plan.hook),
        'Rigid short hook should release faster after turn');
    }
    if(sem.foldVertex!==undefined)
      assert.ok(plan.fold!==null&&plan.events.some(e=>e.phase==='foldApproach'));
  }
});

test('fine/regular uniform hardpen width changes neither geometry nor timing',()=>{
  const g=glyph('水'),sem=P.semantics(g,0),stroke=g.strokes[0];
  const fine=H.makePlan(stroke,sem,{width:21});
  const regular=H.makePlan(stroke,sem,{width:26});
  assert.equal(fine.width,21);assert.equal(regular.width,26);
  assert.deepEqual(fine.geometry.samples,regular.geometry.samples);
  assert.equal(fine.completePath,regular.completePath);
  for(const t of [0,.02,.1,.25,.5,.72,.91,1])
    assert.equal(fine.progressAt(t),regular.progressAt(t));
});

test('source motion is only a scaffold; invalid physical guesses fail closed',()=>{
  const g=glyph('水'),stroke=g.strokes[0],sem=P.semantics(g,0);
  assert.throws(()=>H.makePlan(stroke,sem,{width:0}),/Invalid/);
  assert.throws(()=>H.makePlan(stroke,sem,{width:48}),/Invalid/);
  assert.throws(()=>H.makePlan(stroke,sem,{foldBrake:4}),/Invalid/);
  assert.throws(()=>H.makePlan(stroke,{reviewedTeachingTrajectory:true}),/unreviewed/);
  assert.throws(()=>H.makePlan(null,sem),/unreviewed|median/i);
  assert.throws(()=>H.makePlan(stroke,sem).pathAt(NaN),/Invalid/);
  assert.throws(()=>H.makePlan(stroke,sem).progressAt(NaN),/Invalid/);
  assert.equal(H.defaults.width,26);
});
