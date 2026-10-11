'use strict';
// A2.4 engineering regression: audited glyph structure, bounded local joins,
// intentional gaps, no mutation and no pedagogical certification.
const test=require('node:test');
const assert=require('node:assert/strict');
const C=require('../experiments/kaishu-composition.js');
const K=require('../experiments/regular-kaishu-model.js');
global.window=global;require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const find=ch=>glyphs.find(g=>g.character===ch);
const basic=g=>g.strokes.map((s,i)=>K.makePlan(s,g,i));
const nearest=(p,plan)=>C.nearestOnPolyline(p,plan.revisedControlPoints).distance;

test('A2.4 nine original glyphs and forty source strokes remain read-only',()=>{
  const snapshot=JSON.stringify(glyphs);
  let strokes=0,changed=0;
  for(const g of glyphs){
    const before=basic(g),after=C.makePlans(g);
    const audit=C.compare(g,after);
    assert.equal(after.length,g.strokes.length);
    assert.equal(audit.isCertifiedRegularScript,false);
    assert.equal(audit.needsHumanReview,true);
    assert.equal(audit.before.strokes,after.length);
    assert.equal(audit.after.strokes,after.length);
    assert.deepEqual(C.makePlans(g).map(p=>p.revisedControlPoints),
      after.map(p=>p.revisedControlPoints));
    for(let i=0;i<after.length;i++){
      const p=after[i];
      assert.equal(p.sourceStroke,g.strokes[i]);
      assert.equal(p.originalMedian,g.strokes[i].median);
      assert.equal(p.kaishuStandardClaim,false);
      assert.equal(p.structuralApproval,false);
      assert.equal(p.compositionApproved,false);
      assert.equal(p.sourceInkOutlineUsed,false);
      assert.equal(p.usesBrushSourceArtwork,false);
      assert.equal(p.reviewed,false);
      assert.equal(p.completePath,p.pathAt(1));
      assert.ok(p.geometry.length>0);
      assert.ok(Number.isFinite(p.widthAt(.5)));
      strokes++;
      if(JSON.stringify(before[i].revisedControlPoints)!==
         JSON.stringify(p.revisedControlPoints))changed++;
    }
  }
  assert.equal(glyphs.length,9);
  assert.equal(strokes,40);
  assert.equal(changed,1,'Only the explicitly declared 水 joint is changed');
  assert.equal(JSON.stringify(glyphs),snapshot);
});

test('bounded 水 sweep-to-stem junction reduces physical hardpen ink gap',()=>{
  const g=find('水'),a=basic(g),b=C.makePlans(g);
  const pre=nearest(a[3].revisedControlPoints[0],a[0]);
  const post=nearest(b[3].revisedControlPoints[0],b[0]);
  assert.ok(pre>26&&pre<44,'Previous centerline detachment');
  assert.ok(post<=15.01&&post>=14.99,'Target centerline contact');
  const adj=b[3].compositionAdjustments;
  assert.equal(adj.length,1);
  assert.equal(adj[0].id,'water-right-sweep-root');
  assert.equal(adj[0].status,'applied');
  assert.ok(adj[0].shift>0&&adj[0].shift<=24);
  assert.ok(post<pre-15);
  assert.equal(b[3].widthAt(.5),a[3].widthAt(.5));
  assert.equal(JSON.stringify(b[0].revisedControlPoints),
    JSON.stringify(a[0].revisedControlPoints));
  // Do not automatically join the right-side 撇 tip (intentional separation).
  assert.deepEqual(b[2].revisedControlPoints,a[2].revisedControlPoints);
  assert.ok(nearest(b[2].revisedControlPoints.at(-1),b[0])>35);
});

test('nearest projection works on segments and catches degenerate geometry',()=>{
  const q=C.nearestOnPolyline([5,7],[[0,0],[10,0]]);
  assert.deepEqual(q.point,[5,0]);
  assert.equal(q.distance,7);
  assert.equal(q.segment,0);
  assert.equal(q.fraction,.5);
  assert.throws(()=>C.nearestOnPolyline([NaN,2],[[0,0],[10,0]]));
  assert.throws(()=>C.nearestOnPolyline([2,2],[[1,1],[1,1]]));
  assert.equal(C.strictCrossing([0,0],[4,4],[0,4],[4,0]),true);
  assert.equal(C.strictCrossing([0,0],[4,0],[0,3],[4,3]),false);
  assert.equal(C.strictCrossing([0,0],[4,0],[4,0],[4,4]),false);
});

test('A2.4 constraint solver is fail-closed and preserves input arrays',()=>{
  const g=find('水'),input=basic(g),before=JSON.stringify(
    input.map(p=>p.revisedControlPoints));
  const rule={id:'candidate',from:3,endpoint:'start',to:0,
    desiredGap:15,maxMove:4,maxDistance:44};
  const unresolved=C.applyRelations(input,[rule]);
  assert.equal(unresolved.applied,0);
  assert.equal(unresolved.unresolved,1);
  assert.equal(unresolved.results[0].status,'unresolved-out-of-bounds');
  assert.deepEqual(unresolved.points[3],input[3].revisedControlPoints);
  assert.throws(()=>C.applyRelations(input,[{
    ...rule,from:2,endpoint:'end',maxMove:24
  }],{protectedPairs:['2:end>0']}),/protected/);
  assert.throws(()=>C.applyRelations(input,[{
    ...rule,to:3
  }]),/Invalid/);
  assert.throws(()=>C.applyRelations(input,[rule,rule]),/Duplicate/);
  assert.throws(()=>C.applyRelations(input,[{
    ...rule,desiredGap:Infinity
  }]),/Invalid/);
  assert.equal(JSON.stringify(input.map(p=>p.revisedControlPoints)),before);
});

test('structural metrics cover balance, crossings and horizontal alignment',()=>{
  for(const ch of ['口','月','水','龠']){
    const g=find(ch),plans=C.makePlans(g),m=C.analyze(plans);
    assert.equal(m.strokes,g.strokes.length);
    assert.equal(m.endpoints.length,plans.length*2);
    assert.ok(m.segments>=plans.length);
    assert.ok(m.bounds.width>0&&m.bounds.height>0);
    assert.ok(m.centroid.every(Number.isFinite));
    assert.ok(m.centerOffset.every(v=>Number.isFinite(v)&&Math.abs(v)<=.5));
    assert.ok(m.endpoints.every(e=>e.nearest&&e.nearest.stroke!==e.stroke));
    assert.equal(m.handwritingTeachingApproved,false);
  }
  const mouth=C.analyze(C.makePlans(find('口')));
  assert.ok(mouth.endpoints.some(e=>e.contact==='touch'));
  const month=C.analyze(C.makePlans(find('月')));
  assert.equal(month.horizontals.length,2);
  assert.ok(month.parallelSpreadDeg<2);
  const complex=C.compare(find('龠'),C.makePlans(find('龠')));
  assert.equal(complex.applied.length,0);
  assert.equal(complex.needsHumanReview,true);
  assert.ok(complex.after.horizontals.length>=4);
});

test('per-stroke clocks, stroke order and all 9 drawing paths remain finite',()=>{
  for(const g of glyphs)for(const p of C.makePlans(g)){
    let previous=-1;
    for(let j=0;j<=40;j++){
      const t=j/40,s=p.stateAt(t),progress=p.progressAt(t);
      assert.ok(Number.isFinite(s.point.x)&&Number.isFinite(s.point.y));
      assert.ok(progress>=previous&&progress<=1);
      assert.ok(p.widthAt(progress)>0);
      previous=progress;
    }
  }
});
