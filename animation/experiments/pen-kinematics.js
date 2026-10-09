/* A1.4 experimental gesture-aware motion retiming.
 * Same canonical single-stroke duration/time axis as the baseline, but
 * explicitly different location within the stroke: fold/pivot time is slowed,
 * annotated hook release moves faster, normal onset/ending stay eased.
 * A time-density model is used as an engineering prior. These are NOT
 * fitted sigma-lognormal coefficients nor measured human handwriting.
 */
(function(root,factory){
  const M=typeof module==='object'&&module.exports?
    require('../motion.js'):root.ZitieMotion;
  const api=factory(M);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePenKinematics=api;
})(typeof window!=='undefined'?window:null,function(Motion){
  'use strict';
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const gaussian=(d,center,width)=>Math.exp(-.5*((d-center)/width)**2);
  function makeTimeWarp(penPlan,sourceMotion,options={}){
    if(!penPlan||!finite(penPlan.length)||!sourceMotion||
       !Array.isArray(sourceMotion.fractions)||!Array.isArray(sourceMotion.distances)||
       sourceMotion.fractions.length!==sourceMotion.distances.length)
      throw Error('Invalid canonical source motion');
    const pivotHold=options.pivotHold??5.0;
    const flickBoost=options.flickBoost??.52;
    if(!finite(pivotHold)||pivotHold<0||pivotHold>12||
       !finite(flickBoost)||flickBoost<0||flickBoost>.85)
      throw Error('Unsupported experimental motion coefficients');
    const xs=sourceMotion.distances;
    const base=sourceMotion.fractions;
    const cumulative=[0];
    function density(distance){
      let weight=1;
      if(penPlan.pivot!==null){
        weight+=pivotHold*gaussian(distance,penPlan.pivot,penPlan.pivotWindow*.72);
        if(penPlan.gesture.kind==='hook'){
          const center=Math.min(penPlan.length*.94,
            penPlan.pivot+Math.max(18,penPlan.pivotWindow*.95));
          const width=Math.max(19,penPlan.length*.041);
          weight-=flickBoost*gaussian(distance,center,width);
        }
      }
      if(penPlan.gesture.kind==='dot')
        weight+=.9*gaussian(distance,0,Math.max(13,penPlan.length*.115));
      return clamp(weight,.25,13);
    }
    for(let i=1;i<xs.length;i++){
      const delta=base[i]-base[i-1];
      if(!finite(delta)||delta<=0)
        throw Error('Original motion samples are not strictly increasing');
      const mid=.5*(xs[i]+xs[i-1]);
      cumulative.push(cumulative[i-1]+delta*density(mid));
    }
    const end=cumulative.at(-1);
    if(!finite(end)||end<=0)throw Error('Invalid motion time integration');
    const normalized=cumulative.map(v=>v/end);
    normalized[0]=0;normalized[normalized.length-1]=1;
    function progressAt(time){
      if(!finite(time))throw Error('Nonfinite experimental time');
      const t=clamp(time,0,1);
      if(t===0||t===1)return t;
      const target=Motion.ease(t,sourceMotion.options.easeWeight);
      let lo=0,hi=normalized.length-1;
      while(lo+1<hi){
        const mid=(lo+hi)>>1;
        if(normalized[mid]<target)lo=mid;else hi=mid;
      }
      const a=normalized[lo],b=normalized[hi];
      const portion=(target-a)/(b-a);
      return clamp((xs[lo]+(xs[hi]-xs[lo])*portion)/penPlan.length,0,1);
    }
    function normalizedPace(time){
      const dt=.002;
      const a=clamp(time-dt,0,1),b=clamp(time+dt,0,1);
      return b>a?(progressAt(b)-progressAt(a))/(b-a):0;
    }
    return {
      kind:'research_only_substroke_time_density_not_measured',
      durationUnchanged:true,sourceStrokeCountUnchanged:true,
      distanceSamples:xs.slice(),timeSamples:normalized,
      sourceMotion,penPlan,
      densityAt:d=>density(clamp(d,0,penPlan.length)),
      progressAt,normalizedPace
    };
  }
  return {makeTimeWarp,gaussian};
});