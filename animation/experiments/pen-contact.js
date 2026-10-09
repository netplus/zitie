/* A1.4 virtual nib laboratory: deterministic synthetic contact footprints.
 * NO physical pen-pressure/time measurements and NO modified source geometry.
 * Source medians and reviewed SVG silhouette are always authoritative.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePenContact=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const TAU=Math.PI*2;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const finite=n=>typeof n==='number'&&Number.isFinite(n);
  const lerp=(a,b,t)=>a+(b-a)*t;
  const smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x);};
  const hypot=(x,y)=>Math.hypot(x,y);

  function pointAt(stations,distance){
    if(!stations?.length||!finite(distance))throw Error('Invalid stations/distance');
    const end=stations[stations.length-1].distance;
    const d=clamp(distance,0,end);
    let lo=0,hi=stations.length-1;
    while(lo+1<hi){
      const mid=(lo+hi)>>1;
      if(stations[mid].distance<d)lo=mid;else hi=mid;
    }
    const a=stations[lo],b=stations[hi];
    const t=(d-a.distance)/(b.distance-a.distance||1);
    return {x:lerp(a.x,b.x,t),y:lerp(a.y,b.y,t),distance:d,
      left:lerp(a.left,b.left,t),right:lerp(a.right,b.right,t),
      nx:lerp(a.nx,b.nx,t),ny:lerp(a.ny,b.ny,t)};
  }

  function pivotDistance(median,index){
    if(!Number.isInteger(index)||index<1||index>=median.length-1)
      throw Error('Invalid candidate gesture vertex');
    let length=0;
    for(let i=1;i<=index;i++)
      length+=hypot(median[i][0]-median[i-1][0],
                    median[i][1]-median[i-1][1]);
    return length;
  }

  function tangentAt(stations,d,window){
    const s=Math.max(3,window);
    const a=pointAt(stations,d-s),b=pointAt(stations,d+s);
    let dx=b.x-a.x,dy=b.y-a.y,mag=hypot(dx,dy);
    if(mag<1e-5){
      const c=pointAt(stations,d);
      dx=c.ny;dy=-c.nx;mag=hypot(dx,dy);
    }
    return [dx/mag,dy/mag];
  }

  function phaseAtDistance(plan,d){
    const length=plan.length;
    const start=length*.055,end=length*.945;
    if(d<=start)return 'touch';
    if(d>=end)return 'lift';
    if(plan.pivot!==null){
      const width=plan.pivotWindow;
      if(d>=plan.pivot-width&&d<=plan.pivot+width*.55)return 'pivot';
      if(plan.gesture.kind==='hook'&&d>plan.pivot+width*.55)
        return 'flick';
      if(d>=plan.pivot-width*1.7&&d<plan.pivot-width)return 'brake';
    }
    return 'travel';
  }

  function pressureAt(plan,d){
    const L=plan.length;
    const onset=smooth(d/Math.max(26,L*.055));
    const kind=plan.gesture.kind;
    const exitLength=Math.min(125,Math.max(36,L*(kind==='hook' ? .10 : kind==='dot' ? .13 : .09)));
    const exitStart=L-exitLength;
    const terminal=smooth((d-exitStart)/exitLength);
    const exitLoss=kind==='hook'?.88:kind==='sweep'?.76:kind==='dot'?.79:.61;
    let p=(.18+.82*onset)*(1-exitLoss*terminal);
    if(plan.pivot!==null){
      const z=(d-plan.pivot)/plan.pivotWindow;
      p+=.15*Math.exp(-z*z*.6);
    }
    return clamp(p,0,1);
  }

  function makePlan(stroke,profile,motion,gesture={},options={}){
    if(!stroke||!Array.isArray(stroke.median)||!profile?.stations?.length||
       !motion||!finite(profile.length)||profile.length<1)
      throw Error('Invalid source-backed pen plan');
    const step=options.spacing??5;
    const maxStamps=options.maxStamps??500;
    const tilt=options.tilt??.14;
    const ovality=options.ovality??.81;
    if(!finite(step)||step<2||step>24||
       !Number.isInteger(maxStamps)||maxStamps<2||maxStamps>2000||
       !finite(tilt)||Math.abs(tilt)>1.2||
       !finite(ovality)||ovality<.35||ovality>1.15)
      throw Error('Unsupported virtual nib parameters');
    const L=profile.length;
    const pivot=gesture.pivotVertex===undefined?null:
      pivotDistance(stroke.median,gesture.pivotVertex);
    if(pivot!==null&&(pivot<1||pivot>=L-1))
      throw Error('Candidate pivot outside source stroke');
    const plan={kind:'synthetic_contact_experiment_not_measured',
      gesture:{kind:gesture.kind??'generic',source:'engineering_heuristic_only',
        label:gesture.label??'通用接触'},
      length:L,sourceStrokeIndex:stroke.index,sourceLength:L,
      pivot,pivotWindow:Math.min(41,Math.max(14,L*.026)),
      measuredPressure:false,sourceDirectionModified:false,
      samples:[],motion};
    const count=Math.ceil(L/step);
    if(count>maxStamps)throw Error('Contact path exceeds bounded stamp budget');
    let priorAngle=null;
    for(let i=0;i<=count;i++){
      const d=L*i/count;
      const p=pointAt(profile.stations,d);
      const t=tangentAt(profile.stations,d,Math.min(34,Math.max(11,L*.019)));
      let angle=Math.atan2(t[1],t[0])+Math.PI*.5+tilt;
      if(priorAngle!==null){
        while(angle-priorAngle>Math.PI)angle-=TAU;
        while(angle-priorAngle<-Math.PI)angle+=TAU;
        // Rate-limit orientation *per traveled length*, never moving the
        // actual median. This represents finite rotation during a corner.
        const delta=clamp(angle-priorAngle,-.19,.19);
        angle=priorAngle+delta;
      }
      priorAngle=angle;
      const pressure=pressureAt(plan,d);
      const radius=clamp(Math.max(p.left,p.right),6,175);
      const contactFactor=.12+.88*pressure;
      const alongBias=clamp((p.left-p.right)*.12,-9,9);
      const normalMag=hypot(p.nx,p.ny)||1;
      const nx=p.nx/normalMag,ny=p.ny/normalMag;
      const rx=clamp(radius*1.10*contactFactor,0.6,165);
      const ry=clamp(radius*ovality*contactFactor,0.45,140);
      const stamp={
        distance:d,progress:d/L,x:p.x+nx*alongBias,
        y:p.y+ny*alongBias,angle,
        rx,ry,pressure,contact:pressure,
        phase:phaseAtDistance(plan,d),countSource:'measured_contour_width_only'
      };
      if(![d,stamp.x,stamp.y,angle,rx,ry,pressure].every(finite))
        throw Error('Nonfinite virtual nib stamp');
      plan.samples.push(stamp);
    }
    return plan;
  }

  function snapshot(plan,progress){
    if(!plan||!Array.isArray(plan.samples)||!finite(progress))
      throw Error('Invalid pen snapshot');
    const fraction=clamp(progress,0,1);
    const d=plan.length*fraction;
    // At 0%, no footprint has touched the surface.
    if(fraction===0)return {progress:fraction,count:0,distance:0,
      state:'pending',head:null,pressure:0,angle:0};
    let lo=0,hi=plan.samples.length;
    while(lo<hi){
      const mid=(lo+hi)>>1;
      if(plan.samples[mid].distance<=d+1e-8)lo=mid+1;
      else hi=mid;
    }
    const idx=Math.max(0,lo-1);
    const s=plan.samples[idx];
    // Prefer exact underlying median center (samples carry a bounded
    // appearance-only bias and must never replace canonical tip position).
    return {progress:fraction,count:lo,distance:d,state:phaseAtDistance(plan,d),
      head:{x:s.x,y:s.y,rx:s.rx,ry:s.ry,angle:s.angle},
      pressure:s.pressure,angle:s.angle,stampIndex:idx};
  }

  return {smooth,pointAt,pivotDistance,tangentAt,phaseAtDistance,
    pressureAt,makePlan,snapshot};
});