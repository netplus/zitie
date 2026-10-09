'use strict';
const nodeTest=require('node:test');
const assert=require('node:assert/strict');
const Brush=require('../brush-union.js');
const Pen=require('../experiments/pen-contact.js');
const Gesture=require('../experiments/gesture-data.js');
const Timeline=require('../timeline.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const lookup=ch=>glyphs.find(g=>g.character===ch);
function stage(ch,index=0){
  const g=lookup(ch),stroke=g.strokes[index];
  const timeline=Timeline.buildTimeline(g);
  const p=Brush.makeProfile(stroke.median,null);
  return {glyph:g,stroke,motion:timeline.strokes[index].motion,
    descriptor:Gesture.lookup(g,index),profile:p};
}
function plan(ch,index=0){
  const s=stage(ch,index);
  return Pen.makePlan(s.stroke,s.profile,s.motion,s.descriptor);
}

nodeTest('experimental candidates are explicit source-index annotations, not teaching-reviewed claims',()=>{
  for(const [ch,idx,kind,vertex] of [
    ['一',0,'horizontal',undefined],
    ['口',1,'fold',6],
    ['水',0,'hook',5],
    ['月',1,'hook',8],
    ['火',0,'dot',undefined],
    ['龠',13,'fold',9]]){
    const s=stage(ch,idx);
    assert.equal(s.descriptor.kind,kind);
    assert.equal(s.descriptor.pivotVertex,vertex);
    assert.equal(s.descriptor.reviewed,false);
    assert.equal(s.descriptor.source,'engineering_heuristic_only');
    assert.equal(s.motion.kind,'inferred_kinematic_heuristic_not_measured');
  }
  assert.equal(Gesture.lookup(lookup('火'),1).kind,'generic');
});

nodeTest('source contours and medians stay immutable across all 40 original strokes',()=>{
  for(const g of glyphs){
    const before=JSON.stringify(g.strokes);
    const timeline=Timeline.buildTimeline(g);
    assert.equal(timeline.strokes.length,g.expected_stroke_count);
    for(let i=0;i<g.strokes.length;i++){
      const p=Brush.makeProfile(g.strokes[i].median,null);
      const entry=Pen.makePlan(g.strokes[i],p,timeline.strokes[i].motion,
        Gesture.lookup(g,i));
      assert.equal(entry.kind,'synthetic_contact_experiment_not_measured');
      assert.equal(entry.sourceDirectionModified,false);
      assert.equal(entry.measuredPressure,false);
      assert.ok(Math.abs(entry.length-Timeline.polylineLength(g.strokes[i].median))<1e-6);
    }
    assert.equal(JSON.stringify(g.strokes),before,
      'the contact simulation mutated canonical data in '+g.character);
  }
});

nodeTest('stamp arrival is ordered, future stamps cannot appear before the nib reaches them',()=>{
  for(const [ch,idx] of [['一',0],['口',1],['水',0],['月',1],['火',0],['龠',13]]){
    const p=plan(ch,idx),samples=p.samples;
    assert.ok(samples.length>2&&samples.length<=501);
    assert.equal(samples[0].distance,0);
    assert.ok(Math.abs(samples.at(-1).distance-p.length)<1e-6);
    for(let i=1;i<samples.length;i++){
      const a=samples[i-1],b=samples[i];
      assert.ok(b.distance>a.distance);
      assert.ok(b.progress>a.progress);
      assert.ok(Math.abs(b.angle-a.angle)<=.190001,
        'virtual nib abruptly flipped at sample '+i+' for '+ch);
      assert.ok(Math.abs(b.pressure-a.pressure)<.24);
    }
    let old=-1;
    for(let t=0;t<=1000;t++){
      const snap=Pen.snapshot(p,t/1000);
      assert.ok(snap.count>=old,'painted prefix shrank');
      old=snap.count;
      if(t===0){assert.equal(snap.count,0);assert.equal(snap.state,'pending');}
      if(t===1000)assert.equal(snap.count,samples.length);
      if(t>0){
        assert.ok(snap.head&&snap.head.rx>0&&snap.head.ry>0);
        assert.ok(samples[snap.stampIndex].distance<=snap.distance+1e-7);
      }
    }
  }
});

nodeTest('pressure is an independent, bounded contact function, never inferred as inverse velocity',()=>{
  for(const ch of ['一','口','水','月','火','龠']){
    const s=plan(ch,ch==='口'?1:ch==='月'?1:ch==='龠'?13:0);
    assert.ok(s.samples.every(p=>p.pressure>=0&&p.pressure<=1));
    assert.ok(s.samples.every(p=>p.rx>=.6&&p.ry>=.45));
    const inking=s.samples.find(p=>p.progress>.42&&p.progress<.58);
    assert.ok(inking);
    assert.ok(s.samples.at(-1).pressure<inking.pressure,
      'pen contact should relax at source end in experimental model');
  }
  assert.ok(plan('一').samples[4].pressure>plan('一').samples[0].pressure);
});

nodeTest('source-located folds and hooks have distinct semantic events on one continuous median',()=>{
  const mouth=plan('口',1);
  const water=plan('水',0);
  const moon=plan('月',1);
  const complex=plan('龠',13);
  for(const entry of [mouth,water,moon,complex]){
    assert.ok(entry.pivot>0&&entry.pivot<entry.length);
    const atPivot=Pen.phaseAtDistance(entry,entry.pivot);
    assert.equal(atPivot,'pivot');
    assert.equal(Pen.phaseAtDistance(entry,0),'touch');
    assert.equal(Pen.phaseAtDistance(entry,entry.length),'lift');
  }
  assert.ok(water.samples.some(p=>p.phase==='flick'));
  assert.ok(moon.samples.some(p=>p.phase==='flick'));
  assert.ok(!mouth.samples.some(p=>p.phase==='flick'));
  assert.ok(!complex.samples.some(p=>p.phase==='flick'));
  assert.ok(water.samples.some(p=>p.phase==='brake')||
    water.samples.some(p=>p.phase==='pivot'));
});

nodeTest('rotation is eased in orientation space but the source path point never moves',()=>{
  const s=stage('口',1);
  const p=plan('口',1);
  for(const stamp of p.samples){
    const orig=Pen.pointAt(s.profile.stations,stamp.distance);
    const delta=Math.hypot(stamp.x-orig.x,stamp.y-orig.y);
    assert.ok(delta<=9.00001,
      'appearance-only source normal bias should stay within a bounded contact distance');
  }
  const turnSample=p.samples.find(x=>x.phase==='pivot');
  assert.ok(turnSample);
  const a=p.samples[0].angle,b=p.samples.at(-1).angle;
  assert.ok(Math.abs(a-b)>.25,'orientation must be able to change across a fold');
});

nodeTest('synthetic dots and hook terminals model different contact schedules',()=>{
  const dot=plan('火',0),hook=plan('水',0),line=plan('一',0);
  const at=p=>Pen.pressureAt(p,p.length*.98);
  assert.ok(at(hook)<at(line),'hook should taper more than horizontal stroke');
  assert.ok(at(dot)<at(line),'dot should release contact rather than draw a long line');
});

nodeTest('invalid model options and candidate source vertices fail closed',()=>{
  const s=stage('口',1);
  assert.throws(()=>Pen.makePlan(s.stroke,s.profile,s.motion,
    {...s.descriptor,pivotVertex:999}),/Invalid candidate/);
  assert.throws(()=>Pen.makePlan(s.stroke,s.profile,s.motion,s.descriptor,
    {spacing:-3}),/Unsupported/);
  assert.throws(()=>Pen.makePlan(s.stroke,s.profile,s.motion,s.descriptor,
    {maxStamps:2}),/budget/);
  assert.throws(()=>Pen.snapshot(null,.5),/Invalid/);
  assert.throws(()=>Pen.snapshot(plan('一'),NaN),/Invalid/);
});


nodeTest('source-fit repair catches up smoothly behind the synthetic nib; zero onset and no mid-stroke gray tail',()=>{
  for(const [character,index] of [['一',0],['口',1],['水',0],['月',1],['火',0],['龠',13]]){
    const p=plan(character,index);
    let previous=-1,lagPrevious=Infinity;
    assert.equal(Pen.repairDistanceAt(p,0).distance,0);
    for(let i=0;i<=1000;i++){
      const t=i/1000;
      const state=Pen.repairDistanceAt(p,t);
      const tip=p.length*t;
      assert.ok(state.distance>=previous,'repair unexpectedly erased ink at '+t);
      assert.ok(state.distance<=tip+1e-8,'reference repair painted ahead of pen at '+t);
      assert.ok(state.lag<=lagPrevious+1e-8,'trailing ink repair moved backward at '+t);
      assert.ok(state.spatialProgress>=0&&state.spatialProgress<=1);
      previous=state.distance;lagPrevious=state.lag;
    }
    assert.equal(Pen.repairDistanceAt(p,1).distance,p.length);
    assert.ok(Pen.repairDistanceAt(p,.995).spatialProgress>.993,
      'tail recovery must nearly complete by 99.5% of pen distance');
    const lagBound=Math.max(18,Math.min(48,p.length*.055));
    assert.ok(Pen.repairDistanceAt(p,.5).distance>=
      Math.max(0,p.length*.5-lagBound)-1e-6,
      'reference-width repair must stay within its documented absolute lag');
  }
});

nodeTest('pressure and local ellipse remain independent from source-outline coverage recovery',()=>{
  const p=plan('一');
  const probe=.25;
  const original=Pen.snapshot(p,probe);
  const repair=Pen.repairDistanceAt(p,probe);
  assert.equal(original.distance,p.length*probe);
  assert.ok(repair.distance<original.distance);
  assert.equal(original.head.rx,p.samples[original.stampIndex].rx);
  assert.equal(p.kind,'synthetic_contact_experiment_not_measured');
  assert.throws(()=>Pen.repairDistanceAt(p,-Infinity),/Invalid/);
  assert.throws(()=>Pen.repairDistanceAt(p,.25,{lag:-1}),/Unsupported/);
  assert.throws(()=>Pen.repairDistanceAt(p,.25,{settleAt:1}),/Unsupported/);
});
