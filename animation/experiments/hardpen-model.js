/* A2.2 pen-first regular-script experimental motor model.
 * Targets a common firm/rigid fountain/gel pen contact, NOT brush/flex nib.
 * Uses original medians ONLY as unreviewed approximate stroke skeletons.
 * Source brush-style SVG outlines are *never* the rendered hard-pen ink.
 */
(function(root,factory){
  const P=typeof module==='object'&&module.exports?
    require('./stroke-primitives.js'):root.ZitieStrokePrimitives;
  const Motion=typeof module==='object'&&module.exports?
    require('../motion.js'):root.ZitieMotion;
  const api=factory(P,Motion);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieHardpenModel=api;
})(typeof window!=='undefined'?window:null,function(P,Motion){
  'use strict';
  const finite=n=>typeof n==='number'&&Number.isFinite(n);
  const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
  const gaussian=(p,c,w)=>Math.exp(-.5*Math.pow((p-c)/w,2));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const defaults=Object.freeze({
    width:26,spatialStep:4,geometricOffset:10,
    temporalResolution:360,easeWeight:.37,foldBrake:.76,
    hookBrake:.82,hookExit:.24,pressEase:.14,releaseEase:.16
  });
  const phaseLabels=Object.freeze({
    contact:'轻触纸面',travel:'稳定行笔',foldApproach:'折前轻缓',
    pivot:'笔尖转向',hookApproach:'钩前轻缓',hookExit:'简洁出钩',
    sweep:'自然行撇',lift:'提笔离纸',done:'书写完成'
  });
  function parameters(options={}){
    const o={...defaults,...options};
    if(!finite(o.width)||o.width<12||o.width>42||
       !finite(o.spatialStep)||o.spatialStep<2||o.spatialStep>12||
       !finite(o.geometricOffset)||o.geometricOffset<3||o.geometricOffset>20||
       !Number.isInteger(o.temporalResolution)||o.temporalResolution<120||
       o.temporalResolution>800||!finite(o.easeWeight)||o.easeWeight<.1||
       o.easeWeight>.65||!finite(o.foldBrake)||o.foldBrake<0||
       o.foldBrake>1.4||!finite(o.hookBrake)||o.hookBrake<0||
       o.hookBrake>1.4||!finite(o.hookExit)||o.hookExit<0||
       o.hookExit>.5||!finite(o.pressEase)||o.pressEase<0||
       o.pressEase>.6||!finite(o.releaseEase)||o.releaseEase<0||
       o.releaseEase>.6)
      throw Error('Invalid rigid-nib engineering settings');
    return o;
  }
  const lerpSample=(a,b,t)=>[
    lerp(a.x,b.x,t),lerp(a.y,b.y,t)
  ];
  function prefixAt(geometry,progress){
    if(!geometry?.samples?.length||!finite(progress))
      throw Error('Invalid hardpen path progress');
    const stations=geometry.samples,total=geometry.length;
    if(progress<=0)return '';
    const target=clamp(progress,0,1)*total;
    const strings=['M '+stations[0].x.toFixed(4)+' '+stations[0].y.toFixed(4)];
    for(let i=1;i<stations.length;i++){
      const a=stations[i-1],b=stations[i];
      if(b.distance<=target+1e-8)
        strings.push('L '+b.x.toFixed(4)+' '+b.y.toFixed(4));
      else{
        const part=clamp((target-a.distance)/(b.distance-a.distance),0,1);
        const p=lerpSample(a,b,part);
        strings.push('L '+p[0].toFixed(4)+' '+p[1].toFixed(4));
        break;
      }
    }
    if(strings.length===1)
      strings.push('L '+stations[0].x.toFixed(4)+' '+stations[0].y.toFixed(4));
    return strings.join(' ');
  }
  function makePlan(stroke,sem,options={}){
    if(!stroke?.median||!sem||sem.reviewedTeachingTrajectory!==false)
      throw Error('Hardpen study requires unreviewed median scaffold');
    const o=parameters(options);
    // Explicitly do NOT pass the historical brush-outline containment.
    // This study models the motion of a rigid pen in its own geometry.
    const base=P.makePlan(stroke,sem,null,{
      geometry:{sampleStep:o.spatialStep,maxOffset:o.geometricOffset,
        angleLimit:.70},
      timing:{count:160,easeWeight:.5}
    });
    const geometry=base.geometry,len=geometry.length;
    const vertices=geometry.sourceVertexDistances;
    const fold=sem.foldVertex===undefined?null:vertices[sem.foldVertex]/len;
    const hook=sem.hookVertex===undefined?null:vertices[sem.hookVertex]/len;
    function density(s){
      const t=clamp(s,0,1);
      let w=1+o.pressEase*gaussian(t,.025,.03)+
        o.releaseEase*gaussian(t,.985,.032);
      if(fold!==null)w+=o.foldBrake*gaussian(t,fold,.023);
      if(hook!==null){
        w+=o.hookBrake*gaussian(t,hook,.021);
        w-=o.hookExit*gaussian(t,Math.min(.973,hook+.041),.022);
      }
      // A small acceleration through the last third of a falling 撇/捺.
      if(sem.kind==='pie'||sem.kind==='na')
        w-=.19*Motion.quintic((t-.55)/.45);
      // Do not invent aggressive thick or slow brush-style termination.
      return clamp(w,.70,2.5);
    }
    const n=o.temporalResolution,distances=[0],effort=[0];
    for(let i=1;i<=n;i++){
      const x=(i-1)/n,y=i/n;
      distances.push(y);
      effort.push(effort[i-1]+(density(x)+density(y))/(2*n));
    }
    const total=effort[n],fractions=effort.map(x=>x/total);
    function progressAt(time){
      if(!finite(time))throw Error('Invalid hardpen time');
      const t=clamp(time,0,1);
      if(t===0||t===1)return t;
      const goal=Motion.ease(t,o.easeWeight);
      let lo=0,hi=n;
      while(lo+1<hi){
        const mid=(lo+hi)>>1;
        if(fractions[mid]<goal)lo=mid;else hi=mid;
      }
      const share=(goal-fractions[lo])/
        (fractions[hi]-fractions[lo]);
      return clamp((lo+share)/n,0,1);
    }
    function velocityAt(time){
      if(!finite(time))throw Error('Invalid hardpen velocity query');
      const t=clamp(time,0,1),d=.0015;
      const a=clamp(t-d,0,1),b=clamp(t+d,0,1);
      return (progressAt(b)-progressAt(a))/(b-a||1);
    }
    const events=[
      {phase:'contact',s:0,label:phaseLabels.contact},
      {phase:'travel',s:.035,label:phaseLabels.travel}
    ];
    if(sem.kind==='pie'||sem.kind==='na')
      events.push({phase:'sweep',s:.57,label:phaseLabels.sweep});
    if(fold!==null){
      events.push({phase:'foldApproach',
        s:clamp(fold-.032,.04,.90),label:phaseLabels.foldApproach});
      events.push({phase:'pivot',s:fold,label:phaseLabels.pivot});
      events.push({phase:'travel',s:Math.min(.985,fold+.035),
        label:phaseLabels.travel});
    }
    if(hook!==null){
      events.push({phase:'hookApproach',
        s:clamp(hook-.027,.05,.95),label:phaseLabels.hookApproach});
      events.push({phase:'pivot',s:hook,label:phaseLabels.pivot});
      events.push({phase:'hookExit',s:Math.min(.985,hook+.027),
        label:phaseLabels.hookExit});
    }
    events.push({phase:'lift',s:.988,label:phaseLabels.lift});
    events.push({phase:'done',s:1,label:phaseLabels.done});
    events.sort((a,b)=>a.s-b.s);
    function stateAt(time){
      const progress=progressAt(time);
      const point=P.pointAt({geometry},progress);
      let event=events[0];
      for(const e of events){if(e.s>progress)break;event=e;}
      return {progress,point,phase:event.phase,label:event.label,
        normalizedSpeed:velocityAt(time),contact:time<1&&progress>0,
        physicalPressureMeasured:false};
    }
    return {
      kind:'a22_unmeasured_rigid_nib_hardpen_kinematic_prior',
      genre:'ordinary_firm_nib_hardpen_kaishu',
      geometry,sourceStroke:stroke,
      sourceMedianUnchanged:true,sourceInkOutlineUsed:false,
      originalTeachingReviewUnchanged:true,reviewed:false,
      width:o.width,semantics:sem,options:o,
      fold,hook,events,densityAt:density,
      progressAt,velocityAt,stateAt,
      pathAt:progress=>prefixAt(geometry,progress),
      completePath:prefixAt(geometry,1)
    };
  }
  return {defaults,phaseLabels,parameters,prefixAt,makePlan};
});
