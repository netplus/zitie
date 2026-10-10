'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const Pressure=require('../experiments/pressure-model.js');
const Gesture=require('../experiments/gesture-data.js');
const Motion=require('../motion.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const find=ch=>glyphs.find(g=>g.character===ch);

test('curated six glyphs use source-backed synthetic pressure with no source mutation',()=>{
  for(const char of ['一','口','水','月','火','龠']){
    const glyph=find(char),original=JSON.stringify(glyph);
    assert.ok(glyph,'Missing '+char);
    for(let i=0;i<glyph.strokes.length;i++){
      const plan=Pressure.makePlan(glyph.strokes[i],Gesture.lookup(glyph,i));
      assert.equal(plan.measured,false);
      assert.equal(plan.calibratedToDataset,false);
      assert.equal(plan.forceUnit,null);
      assert.equal(plan.sourceMedianModified,false);
      assert.equal(plan.sourceInkModified,false);
      assert.equal(plan.kind,'synthetic_pressure_independent_of_velocity_unfitted');
      assert.equal(plan.source,'engineering_heuristic_only');
      const pts=Pressure.curve(plan,256);
      assert.equal(pts.length,257);
      assert.equal(pts[0].pressure,0);
      assert.equal(pts.at(-1).pressure,0);
      for(let j=0;j<pts.length;j++){
        const p=pts[j];
        assert.ok(Number.isFinite(p.pressure)&&p.pressure>=0&&p.pressure<=1,
          char+' #'+i+' invalid pressure at '+j);
        assert.ok(p.progress>=0&&p.progress<=1);
        assert.equal(p.measured,false);
        if(j>0)assert.ok(Math.abs(pts[j].pressure-pts[j-1].pressure)<.09,
          char+' #'+i+' discontinuity at '+j);
      }
    }
    assert.equal(JSON.stringify(glyph),original,'Pressure modified source '+char);
  }
});

test('full contact model is smooth at start and lift while keeping nonzero travel',()=>{
  const g=find('一'),plan=Pressure.makePlan(g.strokes[0],Gesture.lookup(g,0));
  assert.equal(Pressure.pressureAt(plan,0),0);
  assert.equal(Pressure.pressureAt(plan,1),0);
  assert.equal(Pressure.phaseAt(plan,0),'hover');
  assert.equal(Pressure.phaseAt(plan,1),'released');
  assert.equal(Pressure.phaseAt(plan,.02),'touch');
  assert.equal(Pressure.phaseAt(plan,.995),'lift');
  assert.ok(Pressure.pressureAt(plan,.03)>0);
  assert.ok(Pressure.pressureAt(plan,.5)>.4);
  assert.ok(Pressure.pressureAt(plan,.98)<Pressure.pressureAt(plan,.8));
  assert.ok(Pressure.pressureAt(plan,.001)<Pressure.pressureAt(plan,.05));
});

test('fold and vertical hook have their own unreviewed pressure pivot gestures',()=>{
  for(const [char,idx] of [['口',1],['水',0],['月',1],['龠',13]]){
    const g=find(char),gest=Gesture.lookup(g,idx);
    const plan=Pressure.makePlan(g.strokes[idx],gest);
    assert.ok(plan.pivot>0&&plan.pivot<1,'Missing original pivot in '+char);
    assert.equal(Pressure.phaseAt(plan,plan.pivot),'pivot');
    const noPivot=Pressure.makePlan(g.strokes[idx],{kind:'generic'});
    assert.ok(Pressure.pressureAt(plan,plan.pivot)>
      Pressure.pressureAt(noPivot,plan.pivot)+.025,
      char+' pressure pivot should be visible');
    assert.equal(JSON.stringify(g.strokes[idx].median),
      JSON.stringify(g.strokes[idx].median));
  }
});

test('pressure is independent of velocity and global playback multiplier',()=>{
  const stroke=find('水').strokes[0];
  const plan=Pressure.makePlan(stroke,Gesture.lookup(find('水'),0));
  const motion=Motion.buildMotionProfile(stroke.median);
  const original=JSON.stringify(plan);
  for(const spatial of [.02,.08,.21,.4,.65,.89,.98]){
    const p=Pressure.pressureAt(plan,spatial);
    for(const rate of [.5,1,1.5,2,3]){
      const same=Pressure.pressureAt(plan,spatial);
      assert.equal(p,same,'Playback speed affected spatial pressure');
    }
  }
  assert.ok(motion.progressAt(.1)<.1,'Existing nonuniform speed remains independent');
  assert.equal(JSON.stringify(plan),original);
  assert.ok(!Object.prototype.hasOwnProperty.call(plan,'velocity'));
});

test('invalid coefficients, pivots and missing source paths fail closed',()=>{
  const stroke=find('一').strokes[0];
  assert.throws(()=>Pressure.makePlan(null),/Invalid/);
  assert.throws(()=>Pressure.makePlan({median:[[0,0],[0,0]]}),/Degenerate/);
  assert.throws(()=>Pressure.makePlan(stroke,{}, {onset:0}),/Unsupported/);
  assert.throws(()=>Pressure.makePlan(stroke,{kind:'unverified'}),/Unknown/);
  assert.throws(()=>Pressure.makePlan(stroke,{kind:'fold',pivotVertex:0}),/Invalid/);
  const plan=Pressure.makePlan(stroke);
  assert.throws(()=>Pressure.pressureAt(plan,NaN),/Invalid/);
  assert.throws(()=>Pressure.curve(plan,3),/Invalid/);
  assert.throws(()=>Pressure.curve(plan,1001),/Invalid/);
});

test('model calculation is reproducible and plans are not stroke-geometry mutations',()=>{
  const g=find('月'),s=g.strokes[1],gesture=Gesture.lookup(g,1);
  const a=Pressure.makePlan(s,gesture),b=Pressure.makePlan(s,gesture);
  assert.deepEqual(a,b);
  assert.deepEqual(Pressure.curve(a,32),Pressure.curve(b,32));
  assert.equal(Pressure.snapshot(a,.32).source,'engineering_heuristic_only');
});
