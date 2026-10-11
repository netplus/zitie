'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const M=require('../motion.js');
const T=require('../timeline.js');
const A=require('../experiments/brush-gesture-model.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;
const select=ch=>glyphs.find(g=>g.character===ch);
const model=stroke=>A.buildPlan(stroke,M.buildMotionProfile(stroke.median));
const near=(a,b,tol=1e-8)=>Math.abs(a-b)<=tol;

test('A3.5 type names are hypotheses, only source-reviewed names allow classification',()=>{
  assert.equal(A.classify({name:'横折钩',name_status:'reviewed'}),'hook');
  assert.equal(A.classify({name:'竖钩',name_status:'reviewed'}),'hook');
  assert.equal(A.classify({name:'横折',name_status:'reviewed'}),'fold');
  assert.equal(A.classify({name:'横撇',name_status:'reviewed'}),'sweep');
  assert.equal(A.classify({name:'点',name_status:'reviewed'}),'dot');
  assert.equal(A.classify({name:'捺',name_status:'reviewed'}),'sweep');
  assert.equal(A.classify({name:'竖',name_status:'reviewed'}),'straight');
  assert.equal(A.classify({name:'竖钩',name_status:'ordinal_only'}),'unreviewed');
  const unreviewed={...select('一').strokes[0],name_status:'ordinal_only',name:null};
  const plan=model(unreviewed);
  assert.equal(plan.enabled,false);
  assert.equal(plan.reason,'ordinal_only_no_semantic_inference');
  assert.equal(plan.motion.kind,'inferred_kinematic_heuristic_not_measured');
});

test('known synthetic fold and hooked brush both preserve source path and use guarded turn events',()=>{
  const fold={name:'横折',name_status:'reviewed',median:[[0,0],[160,0],[160,-170]]};
  const hook={name:'竖钩',name_status:'reviewed',
    median:[[0,0],[0,-150],[0,-270],[-44,-301]]};
  const f=model(fold),h=model(hook);
  assert.equal(f.enabled,true);
  assert.equal(f.kind,'fold');
  assert.equal(f.events.length,1);
  assert.equal(f.events[0].type,'fold');
  assert.ok(near(f.events[0].distance,160));
  assert.equal(h.enabled,true);
  assert.equal(h.kind,'hook');
  assert.equal(h.events.at(-1).type,'hook');
  assert.ok(h.events.at(-1).position>.6);
  assert.equal(f.motion.length,M.buildMotionProfile(fold.median).length);
  assert.equal(h.motion.length,M.buildMotionProfile(hook.median).length);
  assert.equal(f.calibrated,false);
  assert.equal(h.reviewed,false);
  assert.equal(f.inkUnchanged,true);
  assert.equal(h.medianUnchanged,true);
  assert.equal(f.durationUnchanged,true);
  assert.equal(h.durationUnchanged,true);
});

test('ambiguous hook with no late source turn fails closed instead of inventing a pivot',()=>{
  const s={name:'竖钩',name_status:'reviewed',median:[[0,0],[0,-150],[0,-330]]};
  const plan=model(s);
  assert.equal(plan.enabled,false);
  assert.equal(plan.events.length,0);
  assert.equal(plan.reason,'ambiguous_turn_no_forced_semantic_pivot');
  assert.equal(plan.motion.kind,'inferred_kinematic_heuristic_not_measured');
  assert.equal(plan.calibrated,false);
});

test('all 9 canonical source samples keep 40 stroke outlines and immutable medians',()=>{
  let count=0,changed=0,reviewed=0;
  for(const g of glyphs){
    const raw=JSON.stringify(g);
    const baseline=T.buildTimeline(g);
    const candidate=T.buildTimeline(g);
    const plans=A.applyToTimeline(candidate);
    assert.equal(plans.length,baseline.strokes.length);
    assert.equal(candidate.totalMs,baseline.totalMs);
    for(let i=0;i<plans.length;i++){
      count++;
      const a=baseline.strokes[i],b=candidate.strokes[i];
      const plan=plans[i];
      if(plan.enabled)changed++;
      if(g.strokes[i].name_status==='reviewed')reviewed++;
      assert.equal(a.startMs,b.startMs);
      assert.equal(a.endMs,b.endMs);
      assert.equal(a.durationMs,b.durationMs);
      assert.equal(a.pauseMs,b.pauseMs);
      assert.equal(a.length,b.length);
      assert.ok(near(M.progressAt(a.motion,0),M.progressAt(b.motion,0)));
      assert.ok(near(M.progressAt(a.motion,1),M.progressAt(b.motion,1)));
      let prev=-1;
      for(let k=0;k<=150;k++){
        const t=k/150;
        const p=M.progressAt(b.motion,t);
        assert.ok(Number.isFinite(p)&&p>=0&&p<=1);
        if(k>0)assert.ok(p>prev,'A3.5 stalled/reversed source median');
        assert.ok(Math.abs(p-M.progressAt(a.motion,t))<=
          A.DEFAULT.maxProgressDrift+.000001);
        const point=T.pointAt(g.strokes[i].median,p);
        assert.ok(point.every(Number.isFinite));
        prev=p;
      }
    }
    assert.equal(T.frameAt(candidate,candidate.totalMs).phase,'finished');
    assert.equal(JSON.stringify(g),raw,'A3.5 changed canonical source glyph');
  }
  assert.equal(count,40);
  assert.ok(reviewed>=35);
  assert.ok(changed>=8,'A/B must create meaningful motion differences');
});

test('retiming is deterministic; globally selected speed must not rewrite time map',()=>{
  const source=select('水');
  const t=T.buildTimeline(source);
  const s=t.strokes[0],stroke=source.strokes[0];
  const a=A.buildPlan(stroke,s.motion);
  const b=A.buildPlan(stroke,s.motion);
  assert.deepEqual(a.events,b.events);
  assert.deepEqual(a.motion.fractions,b.motion.fractions);
  for(const rate of [.5,1,1.5,2]){
    const original=a.motion.progressAt(.47);
    const wallMs=s.durationMs*.47/rate;
    assert.ok(wallMs>0);
    assert.equal(a.motion.progressAt(.47),original);
  }
  const legacy=T.buildTimeline(source);
  assert.equal(legacy.strokes[0].motion.kind,
    'inferred_kinematic_heuristic_not_measured');
});

test('source-like anomalous coefficients and broken medians never silently produce motion',()=>{
  const median=[[0,0],[120,0]];
  const stroke={median,name:'横',name_status:'reviewed'};
  const src=M.buildMotionProfile(median);
  assert.throws(()=>A.buildPlan(stroke,src,{blend:2}),/coefficient/);
  assert.throws(()=>A.buildPlan(stroke,src,{pivotHold:-1}),/coefficient/);
  assert.throws(()=>A.buildPlan(stroke,src,{hookRelease:NaN}),/coefficient/);
  assert.throws(()=>A.buildPlan(stroke,{...src,fractions:[0,1]}),/source timing|source median|motion/i);
  assert.throws(()=>A.buildPlan(stroke,{...src,kind:'measured_human'}),/original median motion/);
  assert.throws(()=>A.applyToTimeline({strokes:[],glyph:{strokes:[stroke]}}),/complete original timeline/);
});
