/* A1.2.2 deterministic motor-inspired (not measured) pen timing.
 * Spatial points, their order and the stroke outlines remain unchanged.
 * Evidence: Flash/Hogan 1985 minimum-jerk motion and empirical
 * speed-curvature coupling (not universally applicable to handwriting).
 * This implementation provides pedagogical heuristic timing only.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieMotion=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const hypot=(x,y)=>Math.hypot(x,y);
  const defaults=Object.freeze({
    sampleStep:7, angleThreshold:0.30, turnStrength:2.2,
    minVelocityFactor:0.30, easeWeight:0.88, baseWindow:11,
    minTurnWindow:9, maxTurnWindow:48
  });
  function quintic(t) {
    t=clamp(t,0,1);
    return t*t*t*(10+t*(-15+6*t));
  }
  function ease(t,weight=defaults.easeWeight) {
    t=clamp(t,0,1);
    return (1-weight)*t+weight*quintic(t);
  }
  function validateOptions(config) {
    const o={...defaults,...config};
    if(!finite(o.sampleStep)||o.sampleStep<2||o.sampleStep>40 ||
       !finite(o.angleThreshold)||o.angleThreshold<0||o.angleThreshold>1.5 ||
       !finite(o.turnStrength)||o.turnStrength<0||o.turnStrength>8 ||
       !finite(o.minVelocityFactor)||o.minVelocityFactor<=0||o.minVelocityFactor>1 ||
       !finite(o.easeWeight)||o.easeWeight<0||o.easeWeight>1 ||
       !finite(o.baseWindow)||o.baseWindow<0||o.baseWindow>70)
      throw new Error('Invalid motion heuristic configuration');
    return o;
  }

  function segmentsOf(median){
    if(!Array.isArray(median)||median.length<2)throw new Error('Missing motion median');
    const segments=[];
    let total=0;
    for(let i=1;i<median.length;i++){
      const a=median[i-1],b=median[i];
      if(!Array.isArray(a)||!Array.isArray(b)||a.length!==2||b.length!==2||
         !a.every(finite)||!b.every(finite))throw new Error('Nonfinite motion median');
      const dx=b[0]-a[0],dy=b[1]-a[1],len=hypot(dx,dy);
      if(len<0.01)continue;
      segments.push({sourceIndex:i-1,start:total,end:total+len,len,dx:dx/len,dy:dy/len});
      total+=len;
    }
    if(total<0.01)throw new Error('Degenerate motion path');
    return {segments,total};
  }

  function findTurns(median,options={}) {
    const o=validateOptions(options);
    const {segments,total}=segmentsOf(median);
    const turns=[];
    for(let i=1;i<segments.length;i++){
      const before=segments[i-1],after=segments[i];
      if(before.sourceIndex+1!==after.sourceIndex)continue; // ignore degenerate vertices
      const dot=clamp(before.dx*after.dx+before.dy*after.dy,-1,1);
      const angle=Math.acos(dot);
      if(angle<o.angleThreshold)continue;
      const severity=clamp((angle-o.angleThreshold)/(Math.PI-o.angleThreshold),0,1);
      const window=clamp(o.baseWindow+Math.min(before.len,after.len)*0.32,
        o.minTurnWindow,o.maxTurnWindow);
      turns.push({distance:before.end,angle,severity,window,
        sourceVertex:after.sourceIndex});
    }
    return {turns,total};
  }

  function buildMotionProfile(median,options={}){
    const o=validateOptions(options);
    const {turns,total}=findTurns(median,o);
    const count=Math.max(2,Math.ceil(total/o.sampleStep));
    const distances=Array.from({length:count+1},(_,i)=>total*i/count);
    function speedFactor(d){
      let penalty=0;
      for(const turn of turns){
        const z=(d-turn.distance)/turn.window;
        if(Math.abs(z)<4)
          penalty+=o.turnStrength*turn.severity*Math.exp(-0.5*z*z);
      }
      return clamp(1/(1+penalty),o.minVelocityFactor,1);
    }
    // Normalize cumulative travel-time density: dt/ds = 1/v(s).
    const cumulative=new Array(distances.length).fill(0);
    for(let i=1;i<distances.length;i++){
      const a=distances[i-1],b=distances[i];
      cumulative[i]=cumulative[i-1]+(b-a)*
        (1/speedFactor(a)+1/speedFactor(b))/2;
    }
    const totalEffort=cumulative[cumulative.length-1];
    if(!finite(totalEffort)||totalEffort<=0)throw new Error('Invalid motion integration');
    const fractions=cumulative.map(x=>x/totalEffort);
    fractions[0]=0;fractions[fractions.length-1]=1;
    const profile={version:1,kind:'inferred_kinematic_heuristic_not_measured',
      length:total,turns,distances,fractions,options:o,effort:totalEffort};
    profile.progressAt=time=>progressAt(profile,time);
    profile.speedFactorAt=distance=>speedFactor(clamp(distance,0,total));
    profile.phaseAt=time=>phaseAt(profile,time);
    return profile;
  }
  function progressAt(profile,time){
    if(!finite(time))throw new Error('Nonfinite motion time');
    const t=clamp(time,0,1);
    if(t===0||t===1)return t;
    const target=ease(t,profile.options.easeWeight);
    const xs=profile.fractions,ds=profile.distances;
    let lo=0,hi=xs.length-1;
    while(lo+1<hi){
      const mid=(lo+hi)>>1;
      if(xs[mid]<target)lo=mid;else hi=mid;
    }
    const frac=(target-xs[lo])/(xs[hi]-xs[lo]);
    return clamp((ds[lo]+(ds[hi]-ds[lo])*frac)/profile.length,0,1);
  }
  function phaseAt(profile,time){
    const t=clamp(time,0,1);
    const distance=profile.length*progressAt(profile,t);
    if(t===1)return {tag:'finished',label:'落笔完成',pace:0};
    const dt=0.003;
    const d1=progressAt(profile,clamp(t-dt,0,1));
    const d2=progressAt(profile,clamp(t+dt,0,1));
    const pace=(d2-d1)/(clamp(t+dt,0,1)-clamp(t-dt,0,1));
    if(t<0.13)return {tag:'onset',label:'起笔渐快',pace};
    if(t>0.88)return {tag:'terminal',label:'收笔渐慢',pace};
    if(profile.turns.some(turn=>Math.abs(distance-turn.distance)<
       Math.max(8,turn.window*0.75) &&turn.severity>0.13))
      return {tag:'turn',label:'转折减速',pace};
    return {tag:'travel',label:'稳步行笔',pace};
  }
  return {defaults,quintic,ease,segmentsOf,findTurns,
    buildMotionProfile,progressAt,phaseAt};
});