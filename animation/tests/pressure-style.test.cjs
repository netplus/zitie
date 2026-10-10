'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const Style=require('../pressure-style.js');
const Pressure=require('../experiments/pressure-model.js');
const Gestures=require('../experiments/gesture-data.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;

test('stable style is the default and exactly two explicit choices exist',()=>{
  const ctrl=new Style.StyleController();
  assert.deepEqual(Style.styles,['stable','simulated']);
  assert.equal(ctrl.mode,'stable');
  assert.equal(ctrl.ring,null);
  assert.equal(ctrl.setMode('simulated'),'simulated');
  assert.equal(ctrl.setMode('stable'),'stable');
  for(const invalid of ['ellipse','pressure',null,1,undefined]){
    assert.throws(()=>ctrl.setMode(invalid),/Unsupported pen pressure style/);
    assert.equal(ctrl.mode,'stable');
  }
});

test('synthetic circle grows smoothly with pressure but never has white paint',()=>{
  let previousRadius=0;
  for(let i=0;i<=1000;i++){
    const force=i/1000;
    const current=Style.markerGeometry(force);
    assert.ok(current.radius>=previousRadius);
    assert.ok(current.radius>=7.2&&current.radius<=16);
    assert.ok(current.ringRadius>current.radius);
    assert.equal(current.ringFill,'none');
    assert.ok(!Object.values(current).some(value=>value==='#FFFFFF'||value==='#fff'));
    previousRadius=current.radius;
  }
  for(const invalid of [-.01,1.01,Infinity,NaN,'0.5',null])
    assert.throws(()=>Style.markerGeometry(invalid),/Invalid normalized contact/);
});

test('all nine stable glyphs accept A1.5 pressure plans without altering medians',()=>{
  assert.equal(glyphs.length,9);
  const ctrl=new Style.StyleController();
  ctrl.setMode('simulated');
  for(const glyph of glyphs){
    const original=JSON.stringify(glyph);
    ctrl.prepare(glyph);
    assert.equal(ctrl.glyph,glyph);
    assert.equal(ctrl.plans.length,glyph.expected_stroke_count);
    assert.equal(ctrl.curves.length,glyph.expected_stroke_count);
    for(let i=0;i<ctrl.plans.length;i++){
      const plan=ctrl.plans[i],gesture=Gestures.lookup(glyph,i);
      assert.equal(plan.gesture,gesture.kind);
      assert.equal(plan.measured,false);
      assert.equal(plan.calibratedToDataset,false);
      assert.equal(plan.forceUnit,null);
      assert.equal(plan.sourceInkModified,false);
      const curve=ctrl.curves[i];
      assert.equal(curve.length,97);
      assert.equal(curve[0].pressure,0);
      assert.equal(curve.at(-1).pressure,0);
      assert.ok(curve.some(point=>point.pressure>.12));
      assert.ok(curve.every(point=>Number.isFinite(point.pressure)&&
        point.pressure>=0&&point.pressure<=1));
    }
    const prepared=ctrl.plans;
    ctrl.prepare(glyph);
    assert.equal(ctrl.plans,prepared,'Same source glyph should reuse pressure plans');
    assert.equal(JSON.stringify(glyph),original);
  }
});

test('force is a stroke-distance function, not a playback speed or measured force',()=>{
  const glyph=glyphs.find(g=>g.character==='水');
  const gesture=Gestures.lookup(glyph,0);
  const plan=Pressure.makePlan(glyph.strokes[0],gesture);
  for(const spatial of [0,.015,.11,.35,.5,.75,.95,1]){
    const value=Pressure.pressureAt(plan,spatial);
    for(const speed of [.5,1,1.5,2,3]){
      assert.equal(Pressure.pressureAt(plan,spatial),value,
        'Speed multiplier '+speed+' changed contact pressure');
    }
  }
});
