'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const K=require('../experiments/regular-kaishu-model.js');
const P=require('../experiments/stroke-primitives.js');
const H=require('../experiments/hardpen-model.js');
global.window=global;require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const find=ch=>glyphs.find(g=>g.character===ch);
const trial=(ch,index)=>{const g=find(ch);return K.makePlan(g.strokes[index],g,index);};
const near=(a,b,eps=.001)=>Math.abs(a-b)<=eps;

test('original nine source characters and forty source strokes are read-only',()=>{
  assert.equal(glyphs.length,9);
  const before=JSON.stringify(glyphs),counts=[];
  let total=0,curated=0;
  for(const g of glyphs){
    counts.push(g.strokes.length);
    for(let i=0;i<g.strokes.length;i++){
      const plan=K.makePlan(g.strokes[i],g,i);total++;
      assert.equal(plan.originalMedian,g.strokes[i].median);
      assert.equal(plan.sourceStroke,g.strokes[i]);
      assert.equal(plan.sourceSourceJSONUnchanged,true);
      assert.equal(plan.structuralApproval,false);
      assert.equal(plan.kaishuStandardClaim,false);
      assert.equal(plan.reviewed,false);
      assert.equal(plan.sourceInkOutlineUsed,false);
      assert.equal(plan.usesBrushSourceArtwork,false);
      assert.equal(plan.geometry.sourceVertexDistances.length,
        plan.revisedControlPoints.length);
      assert.equal(plan.pathAt(0),'');
      assert.equal(plan.completePath,plan.pathAt(1));
      assert.ok(plan.geometry.length>1);
      assert.ok(plan.geometry.samples.every(p=>
        Number.isFinite(p.x)&&Number.isFinite(p.y)));
      if(plan.revisedSource.startsWith('curated_'))curated++;
    }
  }
  assert.deepEqual(counts,[1,2,2,4,3,3,4,4,17]);
  assert.equal(total,40);assert.ok(curated>=19);
  assert.equal(JSON.stringify(glyphs),before);
});

test('一 十 口 月: horizontal baseline slightly ascends with no source wave',()=>{
  for(const [character,index] of [['一',0],['十',0],
    ['口',2],['月',2],['月',3]]){
    const metrics=K.horizontalMetrics(trial(character,index));
    assert.ok(metrics.angleDeg>=1.0&&metrics.angleDeg<=5.0,
      character+' angle '+metrics.angleDeg);
    assert.ok(metrics.maxNormalDeviation<=5.0,
      character+' residual wave '+metrics.maxNormalDeviation);
    assert.ok(metrics.span>100);
  }
  const raw=find('一').strokes[0].median;
  const deviations=raw.map(p=>{
    const t=(p[0]-raw[0][0])/(raw.at(-1)[0]-raw[0][0]);
    return Math.abs(p[1]-(raw[0][1]+
      t*(raw.at(-1)[1]-raw[0][1])));
  });
  assert.ok(Math.max(...deviations)>20,'Original 一 source really is wavy');
  assert.ok(K.horizontalMetrics(trial('一',0)).maxNormalDeviation<3);
});

test('十 口 巾: supporting verticals, regular corners and square enclosure',()=>{
  for(const [ch,i,max] of [['十',1,2],['口',0,9],
    ['巾',0,9],['巾',2,3]]){
    const metric=K.verticalMetrics(trial(ch,i));
    assert.ok(metric.maxNormalDeviation<=max,
      ch+' vertical '+metric.maxNormalDeviation);
    assert.ok(Math.abs(metric.dx)<Math.max(24,metric.span*.065));
  }
  const fold=trial('口',1),p=fold.revisedControlPoints;
  assert.equal(fold.revisedFoldVertex,1);
  assert.ok(p[1][0]-p[0][0]>390);
  const rise=(p[1][1]-p[0][1])/(p[1][0]-p[0][0]);
  assert.ok(rise>.02&&rise<.08);
  assert.ok(p.at(-1)[1]-p[1][1]<-250);
  assert.ok(Math.abs(p.at(-1)[0]-p[1][0])<40);
  assert.ok(trial('口',0).geometry.samples[0].x+350<
    fold.revisedControlPoints[1][0]);
});

test('水 月 巾 hooks are short, directed and end in fine hardpen point',()=>{
  for(const [ch,index,limit] of [['水',0,.20],['月',1,.20],['巾',1,.23]]){
    const p=trial(ch,index),pts=p.revisedControlPoints;
    const k=p.revisedHookVertex;
    assert.ok(k!==null&&k>0&&k<pts.length-1);
    const root=pts[k],end=pts.at(-1),shaft=pts[0];
    const length=Math.hypot(root[0]-shaft[0],root[1]-shaft[1]);
    const tip=Math.hypot(end[0]-root[0],end[1]-root[1]);
    assert.ok(tip/length<limit,ch+' hook too long');
    assert.ok(end[1]>root[1],ch+' hook not raised');
    assert.ok(end[0]<root[0],ch+' hook not pointed left');
    assert.ok(p.widthRatioAt(1)<=.20);
  }
});

test('stroke morphologies are restrained continuous Kaishu hardpen shapes',()=>{
  for(const [ch,index,kind] of [
    ['一',0,'heng'],['十',1,'shu'],['人',0,'pie'],
    ['人',1,'na'],['火',0,'dian'],['水',0,'gou'],
    ['口',1,'zhe']]){
    const p=trial(ch,index);
    assert.equal(p.semantics.kind,kind);
    const ratios=Array.from({length:201},(_,i)=>p.widthRatioAt(i/200));
    assert.ok(ratios.every(r=>r>=.13&&r<=1.25&&Number.isFinite(r)));
    assert.ok(ratios.some(r=>r!==ratios[0]));
    for(let i=1;i<ratios.length;i++)
      assert.ok(Math.abs(ratios[i]-ratios[i-1])<.06,
        ch+' sudden width jump at '+i+'/200');
    assert.ok(near(p.widthAt(.5),p.width*p.widthRatioAt(.5)));
  }
  for(const [ch,index] of [['人',0],['人',1],['水',0]])
    assert.ok(trial(ch,index).widthAt(1)<=6,ch+' blunt tip');
  assert.ok(trial('一',0).widthRatioAt(1)>.95);
  assert.ok(trial('一',0).widthRatioAt(1)<1.20);
});

test('all positions and widths finite, and motion monotone/deterministic',()=>{
  const before=JSON.stringify(glyphs);
  for(const g of glyphs)for(let i=0;i<g.strokes.length;i++){
    const a=K.makePlan(g.strokes[i],g,i);
    const b=K.makePlan(g.strokes[i],g,i);
    assert.deepEqual(a.revisedControlPoints,b.revisedControlPoints);
    assert.equal(a.completePath,b.completePath);
    let prev=-1;
    for(let k=0;k<=250;k++){
      const t=k/250,p=a.progressAt(t),state=a.stateAt(t);
      assert.ok(p>=prev&&p>=0&&p<=1&&Number.isFinite(p));
      assert.ok(state.point.x>=-20&&state.point.x<=1044);
      assert.ok(state.point.y>=-120&&state.point.y<=1000);
      assert.ok(Number.isFinite(a.widthAt(p)));
      prev=p;
    }
    assert.equal(a.progressAt(0),0);
    assert.equal(a.progressAt(1),1);
  }
  assert.equal(JSON.stringify(glyphs),before);
});

test('whole-character closure: 口 is closed, 月 bars meet both sides',()=>{
  const minDistance=(xy,plan)=>{
    let best=Infinity;
    for(const p of plan.geometry.samples)
      best=Math.min(best,Math.hypot(xy[0]-p.x,xy[1]-p.y));
    return best;
  };
  const left=trial('口',0),fold=trial('口',1),base=trial('口',2);
  const lowerLeft=left.revisedControlPoints.at(-1);
  const lowerRight=fold.revisedControlPoints.at(-1);
  const bottomLeft=base.revisedControlPoints[0];
  assert.ok(Math.hypot(lowerLeft[0]-bottomLeft[0],
    lowerLeft[1]-bottomLeft[1])<20,
    '口 bottom-left is not a joined endpoint');
  assert.ok(minDistance(lowerRight,base)<15,
    '口 bottom-right remains visibly open');
  const topLeft=left.revisedControlPoints[0];
  const topHorizontalStart=fold.revisedControlPoints[0];
  assert.ok(Math.hypot(topLeft[0]-topHorizontalStart[0],
    topLeft[1]-topHorizontalStart[1])<26,
    '口 top-left is disconnected');
  const monthLeft=trial('月',0),monthRight=trial('月',1);
  for(const index of [2,3]){
    const bar=trial('月',index);
    const start=bar.revisedControlPoints[0];
    const end=bar.revisedControlPoints.at(-1);
    assert.ok(minDistance(start,monthLeft)<18,
      '月 bar '+index+' left endpoint detached from left structure');
    assert.ok(minDistance(end,monthRight)<18,
      '月 bar '+index+' right endpoint detached from right structure');
  }
  const upper=K.horizontalMetrics(trial('月',2));
  const lower=K.horizontalMetrics(trial('月',3));
  assert.ok(Math.abs(upper.angleDeg-lower.angleDeg)<1,
    '月 repeated interior horizontals are not parallel');
});

test('bad source IDs and nonfinite morphology are rejected',()=>{
  const g=find('一'),s=g.strokes[0];
  assert.throws(()=>K.makePlan(null,g,0),/mismatch/);
  assert.throws(()=>K.makePlan(s,g,5),/mismatch/);
  const p=K.makePlan(s,g,0);
  assert.throws(()=>p.widthAt(NaN),/Nonfinite/);
  assert.throws(()=>p.widthAt(Infinity),/Nonfinite/);
  assert.throws(()=>K.horizontalMetrics(trial('十',1)),/Not a horizontal/);
  assert.throws(()=>K.verticalMetrics(trial('一',0)),/Not a vertical/);
  assert.equal(H.defaults.width,26);
  assert.equal(P.semantics(g,0).reviewedTeachingTrajectory,false);
});
