/* A3.5 brush-motion laboratory: source-immutable, name-gated time warping.
 * Reuse published PDF stroke outlines/medians, the original brush ink
 * engine, pause durations and total clock. This changes ONLY where a
 * virtual nib is along an existing median at a given within-stroke time.
 *
 * Evidence boundary: Plamondon-style asymmetric velocity and local
 * curvature braking motivate constraints, NOT fitted neuromotor parameters.
 * Stroke names label research hypotheses; no capture/teaching approval.
 */
(function(root,factory){
  const Motion=typeof module==='object'&&module.exports?
    require('../motion.js'):root.ZitieMotion;
  const api=factory(Motion);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieA35BrushMotion=api;
})(typeof window!=='undefined'?window:null,function(Motion){
  'use strict';
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const gaussian=(x,center,width)=>Math.exp(-.5*((x-center)/width)**2);
  const DEFAULT=Object.freeze({
    blend:.56,
    onsetHold:.38,
    terminalHold:.50,
    pivotHold:1.60,
    hookRelease:.44,
    easeWeight:.83,
    maxProgressDrift:.125
  });
  function validate(config={}){
    const o={...DEFAULT,...config};
    for(const [key,min,max] of [
      ['blend',0,.85],['onsetHold',0,1.5],['terminalHold',0,1.5],
      ['pivotHold',0,4],['hookRelease',0,.7],
      ['easeWeight',.58,.95],['maxProgressDrift',.035,.19]
    ]){
      if(!finite(o[key])||o[key]<min||o[key]>max)
        throw Error('Invalid A3.5 research coefficient '+key);
    }
    return o;
  }
  function classify(stroke){
    if(!stroke||stroke.name_status!=='reviewed'||
       typeof stroke.name!=='string'||!stroke.name.trim())return 'unreviewed';
    const name=stroke.name;
    if(/钩/.test(name))return 'hook';
    if(/折|弯/.test(name))return 'fold';
    if(/点/.test(name))return 'dot';
    if(/撇|捺/.test(name))return 'sweep';
    if(/横|竖|提/.test(name))return 'straight';
    return 'generic';
  }
  function eventsOf(stroke,sourceMotion,kind){
    if(kind!=='hook'&&kind!=='fold')return [];
    const turns=sourceMotion.turns||[];
    const L=sourceMotion.length;
    const hits=turns.filter(t=>finite(t.distance)&&finite(t.angle)&&
      t.severity>.095&&t.distance>L*.12&&t.distance<L*.975);
    if(!hits.length)return [];
    const event=(type,turn)=>({
      type,distance:turn.distance,position:turn.distance/L,
      severity:turn.severity,angle:turn.angle,
      window:clamp(L*.043+turn.window*.35,12,52),
      sourceVertex:turn.sourceVertex,
      source:'geometry_candidate_not_teaching_evidence'
    });
    if(kind==='fold'){
      const pivot=hits.filter(t=>t.distance<L*.9)
        .sort((a,b)=>b.severity-a.severity)[0];
      return pivot?[event('fold',pivot)]:[];
    }
    // Hook release must be a LATE, non-trivial turn. Never invent a hook
    // vertex for a straight/ambiguous median merely because name says 钩.
    const late=hits.filter(t=>t.distance>L*.60)
      .sort((a,b)=>b.distance-a.distance)[0];
    if(!late)return [];
    const earlier=hits.filter(t=>t.distance<late.distance-
      Math.max(24,L*.10))
      .sort((a,b)=>b.severity-a.severity)[0];
    const result=[];
    if(earlier&&earlier.distance<L*.88)
      result.push(event('fold',earlier));
    result.push(event('hook',late));
    return result;
  }
  function buildPlan(stroke,sourceMotion,options={}){
    const o=validate(options);
    if(!stroke||!Array.isArray(stroke.median)||
       !sourceMotion||sourceMotion.kind!==
         'inferred_kinematic_heuristic_not_measured'||
       !Array.isArray(sourceMotion.distances)||
       !Array.isArray(sourceMotion.fractions)||
       sourceMotion.distances.length!==sourceMotion.fractions.length||
       sourceMotion.distances.length<3||
       !finite(sourceMotion.length)||sourceMotion.length<=.01)
      throw Error('A3.5 requires a validated, original median motion');
    const kind=classify(stroke);
    const L=sourceMotion.length;
    const xs=sourceMotion.distances;
    const src=sourceMotion.fractions;
    if(Math.abs(xs[0])>1e-8||Math.abs(xs.at(-1)-L)>1e-6||
       Math.abs(src[0])>1e-8||Math.abs(src.at(-1)-1)>1e-8)
      throw Error('A3.5 source motion has invalid endpoints');
    for(let i=1;i<xs.length;i++)
      if(xs[i]<=xs[i-1]||src[i]<=src[i-1])
        throw Error('A3.5 source timing is not strictly increasing');
    const events=eventsOf(stroke,sourceMotion,kind);
    const noop=(reason)=>({
      kind,events,enabled:false,reason,gestureName:stroke.name||null,
      calibrated:false,reviewed:false,sourceModified:false,
      durationUnchanged:true,medianUnchanged:true,inkUnchanged:true,
      motion:sourceMotion,maxDrift:0,
      phaseAt:(time)=>Motion.phaseAt(sourceMotion,time).label
    });
    if(kind==='unreviewed')return noop('ordinal_only_no_semantic_inference');
    if(kind==='generic')return noop('no_recognized_stroke_grammar');
    if((kind==='hook'||kind==='fold')&&!events.length)
      return noop('ambiguous_turn_no_forced_semantic_pivot');
    function density(d){
      let weight=1+o.onsetHold*gaussian(d,0,Math.max(10,L*.065));
      const terminal=(kind==='hook'?.26:kind==='sweep'?.28:
        kind==='dot'?.65:o.terminalHold);
      weight+=terminal*gaussian(d,L,Math.max(11,L*.065));
      if(kind==='dot')weight-=.18*gaussian(d,L*.50,Math.max(12,L*.20));
      for(const event of events){
        weight+=o.pivotHold*Math.max(.24,event.severity)*
          gaussian(d,event.distance-event.window*.19,event.window);
        if(event.type==='hook'){
          const release=Math.min(L*.995,event.distance+event.window*.89);
          weight-=o.hookRelease*
            gaussian(d,release,Math.max(11,event.window*.61));
        }
      }
      return clamp(weight,.54,3.85);
    }
    const cumulative=[0];
    for(let i=1;i<xs.length;i++){
      const dt=src[i]-src[i-1];
      const mid=(xs[i]+xs[i-1])/2;
      cumulative.push(cumulative[i-1]+dt*density(mid));
    }
    const sum=cumulative.at(-1);
    if(!finite(sum)||sum<=0)throw Error('Invalid A3.5 time integral');
    const retimed=cumulative.map(v=>v/sum);
    let chosenMotion=null,chosenDrift=Infinity;
    let mix=o.blend;
    // A/B candidate remains bounded relative to the published teaching
    // motion; each trial is a positive linear mix of monotone CDFs.
    for(let pass=0;pass<7;pass++,mix*=.67){
      const fractions=src.map((v,i)=>
        i===0?0:i===src.length-1?1:(1-mix)*v+mix*retimed[i]);
      if(fractions.some((v,i)=>!finite(v)|| (i>0&&v<=fractions[i-1])))
        throw Error('A3.5 retiming became non-monotonic');
      const motion={
        ...sourceMotion,
        fractions,
        options:{...sourceMotion.options,easeWeight:o.easeWeight},
        kind:'a35_brush_gesture_time_density_research_only'
      };
      motion.progressAt=t=>Motion.progressAt(motion,t);
      motion.phaseAt=t=>Motion.phaseAt(motion,t);
      let maxDrift=0;
      for(let k=0;k<=160;k++){
        const t=k/160;
        const delta=Math.abs(motion.progressAt(t)-
          Motion.progressAt(sourceMotion,t));
        maxDrift=Math.max(maxDrift,delta);
      }
      if(maxDrift<=o.maxProgressDrift+1e-9){
        chosenMotion=motion;
        chosenDrift=maxDrift;
        break;
      }
    }
    if(!chosenMotion)return noop('motion_drift_exceeded_fallback');
    return {
      kind,events,gestureName:stroke.name,enabled:true,
      reason:'source_only_time_reparameterization',motion:chosenMotion,
      calibrated:false,reviewed:false,sourceModified:false,
      durationUnchanged:true,medianUnchanged:true,inkUnchanged:true,
      maxDrift:chosenDrift,
      phaseAt:(time)=>{
        if(!finite(time))throw Error('Invalid A3.5 phase time');
        const t=clamp(time,0,1),p=chosenMotion.progressAt(t);
        const d=L*p;
        if(t<=.09)return '轻触起笔 · 提速';
        if(t>=.93)return kind==='hook'?'出钩收锋':'收笔提锋';
        for(const e of events){
          if(Math.abs(d-e.distance)<e.window*.88)
            return e.type==='hook'?'钩前制动 · 转锋':'折前制动 · 转锋';
          if(e.type==='hook'&&d>e.distance+e.window*.85&&
             d<e.distance+e.window*2.2)
            return '出钩提笔 · 短促行笔';
        }
        return kind==='dot'?'点画按提':'稳步行笔';
      }
    };
  }
  function applyToTimeline(timeline,options={}){
    if(!timeline||!Array.isArray(timeline.strokes)||
       !timeline.glyph||timeline.strokes.length!==timeline.glyph.strokes.length)
      throw Error('A3.5 requires a complete original timeline');
    const plans=[];
    for(let i=0;i<timeline.strokes.length;i++){
      const item=timeline.strokes[i];
      const plan=buildPlan(timeline.glyph.strokes[i],item.motion,options);
      item.motion=plan.motion;
      plans.push(plan);
    }
    return plans;
  }
  return {DEFAULT,validate,classify,eventsOf,buildPlan,applyToTimeline};
});
