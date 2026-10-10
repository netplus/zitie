/* A1.5 research-only normalized pressure demonstration. No force telemetry.
 * Pressure is an independent spatial gesture prior, NOT deduced from speed.
 * The original A1.3 round ink mask, SVG paths, medians and time law remain
 * untouched. Curated pivot annotations are unreviewed engineering hypotheses.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePressureModel=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  const smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x);};
  const gauss=(x,mu,width)=>Math.exp(-.5*((x-mu)/width)**2);
  const kinds=new Set(['generic','horizontal','fold','hook','dot','sweep']);
  function makePlan(stroke,gesture={},options={}){
    if(!stroke||!Array.isArray(stroke.median)||stroke.median.length<2||
       !stroke.median.every(p=>Array.isArray(p)&&p.length===2&&p.every(finite)))
      throw Error('Invalid original median for pressure demonstration');
    const base=options.base??.52;
    const onset=options.onset??.058;
    const lift=options.lift??.105;
    const pivotGain=options.pivotGain??.23;
    if(![base,onset,lift,pivotGain].every(finite)||base<.2||base>.75||
       onset<.02||onset>.20||lift<.03||lift>.25||
       pivotGain<0||pivotGain>.35)
      throw Error('Unsupported synthetic pressure coefficients');
    const kind=gesture.kind??'generic';
    if(!kinds.has(kind))throw Error('Unknown experimental pressure gesture');
    const distances=[0];
    for(let i=1;i<stroke.median.length;i++){
      const a=stroke.median[i-1],b=stroke.median[i];
      distances.push(distances[i-1]+Math.hypot(b[0]-a[0],b[1]-a[1]));
    }
    const length=distances.at(-1);
    if(!finite(length)||length<=.01)throw Error('Degenerate source pressure path');
    let pivot=null;
    if(gesture.pivotVertex!==undefined){
      const i=gesture.pivotVertex;
      if(!Number.isInteger(i)||i<1||i>=stroke.median.length-1)
        throw Error('Invalid unreviewed pivot source index');
      pivot=distances[i]/length;
    }
    const pivotWindow=clamp(28/length,.035,.12);
    return {
      kind:'synthetic_pressure_independent_of_velocity_unfitted',
      base,onset,lift,pivotGain,gesture:kind,pivot,pivotWindow,length,
      measured:false,source:'engineering_heuristic_only',
      calibratedToDataset:false,forceUnit:null,
      sourceMedianModified:false,sourceInkModified:false,
      sourceStrokeCountModified:false
    };
  }
  function pressureAt(plan,progress){
    if(!plan||plan.kind!=='synthetic_pressure_independent_of_velocity_unfitted'||
       !finite(progress))throw Error('Invalid synthetic pressure evaluation');
    const s=clamp(progress,0,1);
    if(s===0||s===1)return 0;
    let level=plan.base;
    if(plan.pivot!==null){
      const gain=(plan.gesture==='hook'?1:plan.gesture==='fold'?.75:.45);
      level+=plan.pivotGain*gain*gauss(s,plan.pivot,plan.pivotWindow);
    }
    if(plan.gesture==='dot')level+=.16*gauss(s,.54,.22);
    if(plan.gesture==='horizontal')level+=.045*gauss(s,.89,.075);
    if(plan.gesture==='sweep')
      level-=.12*smooth((s-.62)/.38);
    if(plan.gesture==='hook'&&plan.pivot!==null)
      level-=.19*smooth((s-plan.pivot-.035)/Math.max(.045,1-plan.pivot-.035));
    const contact=smooth(s/plan.onset)*smooth((1-s)/plan.lift);
    return clamp(level*contact,0,1);
  }
  function phaseAt(plan,progress){
    if(!plan||!finite(progress))throw Error('Invalid pressure phase');
    const s=clamp(progress,0,1);
    if(s===0)return 'hover';
    if(s>=1)return 'released';
    if(s<plan.onset)return 'touch';
    if(s>1-plan.lift*.82)return 'lift';
    if(plan.pivot!==null&&Math.abs(s-plan.pivot)<=plan.pivotWindow*.78)
      return 'pivot';
    if(plan.gesture==='hook'&&plan.pivot!==null&&s>plan.pivot+plan.pivotWindow*.78)
      return 'flick';
    return 'travel';
  }
  function snapshot(plan,progress){
    const s=clamp(progress,0,1);
    return {progress:s,pressure:pressureAt(plan,s),phase:phaseAt(plan,s),
      measured:false,forceUnit:null,source:plan.source};
  }
  function curve(plan,count=192){
    if(!Number.isInteger(count)||count<8||count>1000)
      throw Error('Invalid synthetic pressure sampling count');
    return Array.from({length:count+1},(_,i)=>snapshot(plan,i/count));
  }
  return {makePlan,pressureAt,phaseAt,snapshot,curve,smooth};
});
