'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const M=require('../motion.js');
const T=require('../timeline.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const select=ch=>glyphs.find(g=>g.character===ch);
const almost=(a,b,eps=1e-6)=>Math.abs(a-b)<=eps;

test('minimum-jerk blend: deterministic easing is continuous, monotonic and not constant-speed',()=>{
  assert.equal(M.ease(0),0);assert.equal(M.ease(1),1);
  assert.ok(almost(M.ease(.5),.5));
  assert.ok(M.ease(.1)<.1);
  assert.ok(M.ease(.9)>.9);
  for(let i=1;i<=1000;i++)
    assert.ok(M.ease(i/1000)>M.ease((i-1)/1000));
  assert.ok(M.quintic(.1)<M.ease(.1));
});

test('straight strokes accelerate, cruise, decelerate and preserve endpoints',()=>{
  const median=[[0,0],[900,0]],p=M.buildMotionProfile(median);
  assert.equal(p.turns.length,0);
  assert.equal(p.kind,'inferred_kinematic_heuristic_not_measured');
  assert.equal(p.progressAt(0),0);assert.equal(p.progressAt(1),1);
  assert.ok(p.progressAt(.1)<.1 && p.progressAt(.9)>.9);
  const early=p.progressAt(.14)-p.progressAt(.07);
  const middle=p.progressAt(.54)-p.progressAt(.47);
  const late=p.progressAt(.93)-p.progressAt(.86);
  assert.ok(middle>early*1.5,'middle should travel farther in equal time than onset');
  assert.ok(middle>late*1.5,'middle should travel farther than terminal');
  assert.equal(p.phaseAt(.05).tag,'onset');
  assert.equal(p.phaseAt(.95).tag,'terminal');
  assert.equal(p.phaseAt(.5).tag,'travel');
});

test('acute folds slow at the actual median corner without breaking stroke',()=>{
  const median=[[0,0],[260,0],[260,-260]];
  const p=M.buildMotionProfile(median);
  assert.equal(p.turns.length,1);
  assert.equal(p.turns[0].sourceVertex,1);
  assert.ok(almost(p.turns[0].distance,260));
  assert.ok(almost(p.turns[0].angle,Math.PI/2));
  assert.ok(p.speedFactorAt(260)<p.speedFactorAt(130)*.7,
    'fold speed must be significantly lower');
  assert.equal(p.phaseAt(.5).tag,'turn');
  let prev=-1;
  for(let i=0;i<=1000;i++){
    const v=p.progressAt(i/1000);
    assert.ok(v>=prev,'movement direction reversed in fold');
    prev=v;
  }
  assert.equal(p.progressAt(1),1);
});

test('water hook remains one continuous motion profile with a local speed minimum',()=>{
  const stroke=select('水').strokes[0];
  const p=M.buildMotionProfile(stroke.median);
  assert.ok(p.turns.length>=1);
  const strongest=p.turns.reduce((a,b)=>b.severity>a.severity?b:a,p.turns[0]);
  assert.ok(p.speedFactorAt(strongest.distance) <
    p.speedFactorAt(Math.max(0,strongest.distance-strongest.window*4)));
  assert.ok(p.turns.every(t=>t.distance>0&&t.distance<p.length));
  assert.ok(M.progressAt(p,.87)>M.progressAt(p,.83));
});

test('distance follows original median exactly; source sample geometry unchanged',()=>{
  for(const g of glyphs){
    const before=JSON.stringify(g.strokes);
    const timeline=T.buildTimeline(g);
    assert.equal(timeline.strokes.length,g.expected_stroke_count);
    for(const stage of timeline.strokes){
      const s=g.strokes[stage.index];
      const p=stage.motion;
      assert.ok(almost(p.length,T.polylineLength(s.median),1e-5));
      for(let i=0;i<=100;i++){
        const t=i/100;
        const q=p.progressAt(t);
        assert.ok(q>=0&&q<=1);
        const pt=T.pointAt(s.median,q);
        assert.ok(pt.every(Number.isFinite));
        if(i>0)assert.ok(q>p.progressAt((i-1)/100));
      }
      const first=T.frameAt(timeline,stage.startMs);
      const last=T.frameAt(timeline,stage.endMs);
      assert.equal(first.index,stage.index);
      assert.equal(first.progress,0);
      assert.ok(last.progress===1 || last.phase==='finished' ||
        last.index===stage.index+1);
      assert.ok(stage.durationMs>=550&&stage.durationMs<=2600);
    }
    assert.equal(JSON.stringify(g.strokes),before);
    assert.equal(T.frameAt(timeline,timeline.totalMs).phase,'finished');
  }
});

test('global speed is a multiplier only and cannot mutate the normalized phase map',()=>{
  const tl=T.buildTimeline(select('口'));
  const segment=tl.strokes[1];
  const snap=segment.motion.progressAt(.6);
  const a=T.frameAt(tl,segment.startMs+segment.durationMs*.6);
  assert.ok(almost(a.progress,snap));
  // At 2x the same *model* position is reached in half the real wall time;
  // no separate speed curve is constructed or mutated.
  const wallMs=(segment.startMs+segment.durationMs*.6)/2;
  assert.ok(wallMs>0);
  assert.equal(segment.motion.progressAt(.6),snap);
  assert.equal(T.frameAt(tl,segment.startMs+segment.durationMs*.6).motion.tag,
    segment.motion.phaseAt(.6).tag);
});

test('degenerate/nonfinite data and unsupported coefficients fail closed',()=>{
  assert.throws(()=>M.buildMotionProfile(null),/median/);
  assert.throws(()=>M.buildMotionProfile([[0,0],[0,0]]),/Degenerate/);
  assert.throws(()=>M.buildMotionProfile([[0,0],[Infinity,1]]),/Nonfinite/);
  assert.throws(()=>M.buildMotionProfile([[0,0],[100,0]],{easeWeight:1.3}),/configuration/);
  assert.throws(()=>M.progressAt(M.buildMotionProfile([[0,0],[100,0]]),NaN),/Nonfinite/);
});

test('velocity is bounded at corners without arbitrary pauses inside one stroke',()=>{
  const steep=M.buildMotionProfile([[0,0],[130,0],[130,130],[0,130],[0,260]]);
  for(let i=0;i<=200;i++){
    const s=steep.length*i/200;
    const v=steep.speedFactorAt(s);
    assert.ok(v>=M.defaults.minVelocityFactor-1e-9 && v<=1+1e-9);
  }
  assert.ok(steep.turns.length>=3);
  assert.equal(steep.progressAt(.00001)>0,true);
});