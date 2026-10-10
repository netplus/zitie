/* A2.1 isolated basic-stroke grammar and constrained kinematic path.
 * A continuous geometric hypothesis, not normative stroke teaching evidence.
 * Source SVG d, source medians, stroke ordering, and published fill untouched.
 */
(function(root,factory){
  const M=typeof module==='object'&&module.exports?
    require('../motion.js'):root.ZitieMotion;
  const api=factory(M);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieStrokePrimitives=api;
})(typeof window!=='undefined'?window:null,function(Motion){
  'use strict';
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const length=(a,b)=>Math.hypot(b[0]-a[0],b[1]-a[1]);
  const lerp=(a,b,t)=>a+(b-a)*t;
  const gaussian=(s,mu,width)=>Math.exp(-.5*((s-mu)/width)**2);
  const atan=(a,b)=>Math.atan2(b[1]-a[1],b[0]-a[0]);
  const categories=Object.freeze(['heng','shu','pie','zhe','gou','zhe-gou','dian','na','generic']);
  // Curated engineering hypotheses, expressed as zero-based ORIGINAL
  // vendor median vertex indices. No derived trajectory approves these.
  const anchors=Object.freeze({
    '37:2':{foldVertex:6},          // 口 横折
    '40:2':{foldVertex:6,hookVertex:8}, // 巾 横折钩
    '77:1':{hookVertex:5},         // 水 竖钩
    '88:2':{foldVertex:5,hookVertex:8}, // 月 横折钩
    '201:14':{foldVertex:5}        // 龠 第14笔横折
  });
  const classify=name=>{
    switch(name){
      case '横':return 'heng';
      case '竖':return 'shu';
      case '撇':return 'pie';
      case '横折':return 'zhe';
      case '竖钩':return 'gou';
      case '横折钩':return 'zhe-gou';
      case '点':return 'dian';
      case '捺':return 'na';
      default:return 'generic';
    }
  };
  function semantics(glyph,index){
    const stroke=glyph?.strokes?.[index];
    if(!stroke||!Number.isInteger(glyph.main_id))
      throw Error('Missing source glyph for semantic stroke');
    const reviewed=stroke.name_status==='reviewed';
    const kind=reviewed?classify(stroke.name):'generic';
    const key=glyph.main_id+':'+(index+1);
    const config=reviewed?anchors[key]||{}:{};
    const count=stroke.median.length;
    for(const id of ['foldVertex','hookVertex']){
      if(config[id]!==undefined&&
         (!Number.isInteger(config[id])||config[id]<1||config[id]>=count-1))
        throw Error('Unreviewed pivot does not match source median: '+key);
    }
    return {kind,label:reviewed?stroke.name:'第'+(index+1)+'笔',
      source:'unreviewed_engineering_gesture_candidate',
      reviewedTeachingTrajectory:false,key,...config};
  }
  function cumulative(points){
    const dist=[0];
    for(let i=1;i<points.length;i++){
      const d=length(points[i-1],points[i]);
      if(!finite(d)||d<=.00001)throw Error('Degenerate source median segment');
      dist.push(dist.at(-1)+d);
    }
    return dist;
  }
  function cubic(a,b,c,d,t){
    const q=1-t,q2=q*q,t2=t*t;
    return [q2*q*a[0]+3*q2*t*b[0]+3*q*t2*c[0]+t2*t*d[0],
      q2*q*a[1]+3*q2*t*b[1]+3*q*t2*c[1]+t2*t*d[1]];
  }
  function unit(a,b){
    const d=length(a,b);return [(b[0]-a[0])/d,(b[1]-a[1])/d];
  }
  // A sharp fold retains TWO one-sided tangents. A small and genuinely
  // smooth curvature may use the same bisector on adjacent cubic pieces.
  function tangents(points,sem,angleLimit){
    const n=points.length,arr=[];
    for(let i=0;i<n;i++){
      const incoming=i?unit(points[i-1],points[i]):unit(points[0],points[1]);
      const outgoing=i<n-1?unit(points[i],points[i+1]):unit(points[n-2],points[n-1]);
      const dot=clamp(incoming[0]*outgoing[0]+incoming[1]*outgoing[1],-1,1);
      const corner=Math.acos(dot)>angleLimit||
        i===sem.foldVertex||i===sem.hookVertex;
      const sum=[incoming[0]+outgoing[0],incoming[1]+outgoing[1]];
      const mag=Math.hypot(...sum);
      const average=mag>1e-5?[sum[0]/mag,sum[1]/mag]:outgoing;
      arr.push({incoming:corner?incoming:average,
        outgoing:corner?outgoing:average,
        corner:i>0&&i<n-1&&corner,angle:Math.acos(dot),
        sourceVertex:i});
    }
    return arr;
  }
  function buildGeometry(points,sem,contains,options={}){
    const step=options.sampleStep??5;
    const angleLimit=options.angleLimit??.74;
    const maxOffset=options.maxOffset??16;
    if(!finite(step)||step<2||step>16||!finite(angleLimit)||
       angleLimit<.2||angleLimit>1.3||!finite(maxOffset)||
       maxOffset<2||maxOffset>40)
      throw Error('Invalid A2 constrained spline settings');
    const directions=tangents(points,sem,angleLimit);
    const samples=[{x:points[0][0],y:points[0][1],distance:0}];
    const vertexDistances=[0];
    let rejected=0,smoothed=0,sourceOutside=0,maxDeviation=0;
    for(let j=1;j<points.length;j++){
      const a=points[j-1],b=points[j],L=length(a,b);
      const inV=directions[j-1].outgoing,outV=directions[j].incoming;
      const p1=[a[0]+inV[0]*L/3,a[1]+inV[1]*L/3];
      const p2=[b[0]-outV[0]*L/3,b[1]-outV[1]*L/3];
      const count=Math.max(4,Math.ceil(L/step));
      const checked=[];
      const threshold=Math.min(maxOffset,Math.max(3,L*.11));
      let rejectedThis=false;
      for(let k=0;k<=count;k++){
        const t=k/count,p=cubic(a,p1,p2,b,t);
        const base=[lerp(a[0],b[0],t),lerp(a[1],b[1],t)];
        if(length(p,base)>threshold+1e-7||
           (typeof contains==='function'&&!contains(p[0],p[1])))
          rejectedThis=true;
        checked.push(p);
      }
      if(rejectedThis)rejected++;
      else smoothed++;
      for(let k=1;k<=count;k++){
        const t=k/count;
        const p=rejectedThis?[lerp(a[0],b[0],t),lerp(a[1],b[1],t)]:checked[k];
        const prev=samples.at(-1),delta=Math.hypot(p[0]-prev.x,p[1]-prev.y);
        if(delta<1e-10)continue;
        const deviation=length(p,[lerp(a[0],b[0],t),lerp(a[1],b[1],t)]);
        maxDeviation=Math.max(maxDeviation,deviation);
        if(typeof contains==='function'&&!contains(p[0],p[1]))
          sourceOutside++;
        samples.push({x:p[0],y:p[1],distance:prev.distance+delta});
      }
      vertexDistances.push(samples.at(-1).distance);
      const end=samples.at(-1);
      if(length([end.x,end.y],b)>1e-5)
        throw Error('Curved segment cannot preserve original source knot');
    }
    const total=samples.at(-1).distance;
    if(!finite(total)||total<=.01)throw Error('Invalid A2 curve length');
    return {samples,sourceVertexDistances:vertexDistances,
      length:total,smoothedSegments:smoothed,rejectedSegments:rejected,
      outsideSourceSamples:sourceOutside,maxDeviation,
      corners:directions.filter(x=>x.corner).map(x=>x.sourceVertex),
      verification:typeof contains==='function'?'source_svg_fill_probe':'unit_test_unprobed'};
  }
  function pointAt(plan,progress){
    if(!plan?.geometry?.samples||!finite(progress))
      throw Error('Invalid A2 trajectory sample');
    const arr=plan.geometry.samples;
    const d=clamp(progress,0,1)*plan.geometry.length;
    let lo=0,hi=arr.length-1;
    while(lo+1<hi){
      const mid=(lo+hi)>>1;
      if(arr[mid].distance<d)lo=mid;else hi=mid;
    }
    const a=arr[lo],b=arr[hi];
    const t=clamp((d-a.distance)/(b.distance-a.distance||1),0,1);
    const delta=Math.hypot(b.x-a.x,b.y-a.y);
    return {x:lerp(a.x,b.x,t),y:lerp(a.y,b.y,t),
      tangent:delta?[Math.atan2(b.y-a.y,b.x-a.x)]:[0],
      distance:d,progress:clamp(progress,0,1)};
  }
  function buildEvents(sem,geometry){
    const len=geometry.length,v=geometry.sourceVertexDistances;
    const events=[
      {phase:'touch',s:0,label:'触纸'},
      {phase:'settle',s:.045,label:'起笔定锋'},
      {phase:'travel',s:.085,label:'行笔'}
    ];
    const add=(phase,s,label)=>{
      if(!finite(s)||s<=0||s>=1)throw Error('Invalid A2 event anchor');
      events.push({phase,s,label});
    };
    if(sem.foldVertex!==undefined){
      const at=v[sem.foldVertex]/len;
      add('brake',clamp(at-.045,.06,.91),'折前制动');
      add('turn',at,'转锋');
      if(sem.kind==='zhe'||sem.kind==='zhe-gou')
        add('release',clamp(at+.035,.07,.97),'转后重新行笔');
    }
    if(sem.hookVertex!==undefined){
      const at=v[sem.hookVertex]/len;
      add('store',clamp(at-.03,.08,.94),'钩前蓄势');
      add('hook',at,'转腕起钩');
      add('flick',clamp(at+.038,.09,.975),'短促出锋');
    }
    if(sem.kind==='pie'||sem.kind==='na')
      add('taper',.78,'提锋渐出');
    if(sem.kind==='heng')add('finish',.90,'行笔收势');
    if(sem.kind==='shu')add('finish',.9,'竖末收锋');
    add('lift',.98,'提笔');
    events.push({phase:'done',s:1,label:'离纸'});
    events.sort((a,b)=>a.s-b.s);
    for(let i=1;i<events.length;i++)
      if(events[i].s<events[i-1].s)throw Error('A2 semantic events out of order');
    return events;
  }
  function buildTiming(sem,geometry,events,options={}){
    const count=options.count??256;
    const easeWeight=options.easeWeight??.73;
    if(!Number.isInteger(count)||count<80||count>600||
       !finite(easeWeight)||easeWeight<.2||easeWeight>.95)
      throw Error('Invalid A2 timing configuration');
    const n=count,v=geometry.sourceVertexDistances,L=geometry.length;
    const fold=sem.foldVertex!==undefined?v[sem.foldVertex]/L:null;
    const hook=sem.hookVertex!==undefined?v[sem.hookVertex]/L:null;
    const density=s=>{
      let d=1+.56*gaussian(s,.015,.035)+.42*gaussian(s,.985,.05);
      if(sem.kind==='heng')d+=.34*gaussian(s,.92,.055);
      if(sem.kind==='shu')d+=.24*gaussian(s,.94,.045);
      if(sem.kind==='pie'||sem.kind==='na')
        d-=.40*clamp((s-.62)/.38,0,1);
      if(sem.kind==='dian')
        d+=.35*gaussian(s,.35,.18);
      if(fold!==null)d+=2.6*gaussian(s,fold,.043);
      if(hook!==null){
        d+=2.8*gaussian(s,hook,.039);
        d-=.47*gaussian(s,Math.min(.96,hook+.065),.035);
      }
      return clamp(d,.42,7);
    };
    const distanceFractions=Array.from({length:n+1},(_,i)=>i/n);
    const accumulated=[0];
    for(let i=1;i<=n;i++){
      const s0=distanceFractions[i-1],s1=distanceFractions[i];
      accumulated.push(accumulated[i-1]+(s1-s0)*
        (density(s0)+density(s1))*.5);
    }
    const final=accumulated.at(-1);
    const normalized=accumulated.map(d=>d/final);
    normalized[0]=0;normalized[n]=1;
    function progressAt(t){
      if(!finite(t))throw Error('Invalid A2 clock');
      const time=clamp(t,0,1);
      if(time<=0)return 0;if(time>=1)return 1;
      const wanted=Motion.ease(time,easeWeight);
      let lo=0,hi=n;
      while(lo+1<hi){
        const m=(lo+hi)>>1;
        if(normalized[m]<wanted)lo=m;else hi=m;
      }
      const share=(wanted-normalized[lo])/
        (normalized[hi]-normalized[lo]);
      return clamp((lo+share)/n,0,1);
    }
    function clockAt(s){
      if(!finite(s))throw Error('Invalid A2 arc target');
      const p=clamp(s,0,1),idx=Math.min(n-1,Math.floor(p*n));
      const fraction=p*n-idx;
      const goal=lerp(normalized[idx],normalized[idx+1],fraction);
      let lo=0,hi=1;
      for(let i=0;i<35;i++){
        const mid=(lo+hi)*.5;
        if(Motion.ease(mid,easeWeight)<goal)lo=mid;else hi=mid;
      }
      return (lo+hi)*.5;
    }
    function speedAt(t){
      const delta=.0015;
      const lo=clamp(t-delta,0,1),hi=clamp(t+delta,0,1);
      return (progressAt(hi)-progressAt(lo))/(hi-lo||1);
    }
    return {kind:'a21_semantic_positive_density_not_measured',
      timeTable:normalized,distanceFractions,
      speedDensityAt:density,progressAt,clockAt,speedAt,
      folds:fold,hooks:hook,easeWeight,elapsedStrokeDurationUnchanged:true};
  }
  function makePlan(stroke,sem,contains,options={}){
    if(!stroke||!Array.isArray(stroke.median)||stroke.median.length<2||
       !stroke.median.every(p=>Array.isArray(p)&&p.length===2&&p.every(finite)))
      throw Error('Invalid A2 source median');
    if(!sem||!categories.includes(sem.kind)||
       sem.reviewedTeachingTrajectory!==false)
      throw Error('A2 requires unreviewed explicit semantic candidate');
    const source=stroke.median,rawDistances=cumulative(source);
    const geom=buildGeometry(source,sem,contains,options.geometry);
    const events=buildEvents(sem,geom);
    const timing=buildTiming(sem,geom,events,options.timing);
    function stateAt(t){
      const progress=timing.progressAt(t);
      const point=pointAt(plan,progress);
      let event=events[0];
      for(const candidate of events){
        if(candidate.s>progress)break;
        event=candidate;
      }
      return {progress,point,phase:event.phase,label:event.label,
        speed:timing.speedAt(clamp(t,0,1)),source:'engineering_preview_not_teaching_reviewed'};
    }
    const plan={kind:'a21_basic_stroke_grammar_candidate',
      sem,geometry:geom,events,timing,rawLength:rawDistances.at(-1),
      sourceMedianUnchanged:true,sourceOutlineUnchanged:true,
      canonicalStrokeOrderUnchanged:true,
      fittedToHumanData:false,sourceDirectionReviewed:false,
      movementDurationUnchanged:true};
    plan.stateAt=stateAt;
    return plan;
  }
  return {categories,anchors,classify,semantics,cumulative,tangents,
    buildGeometry,pointAt,buildEvents,buildTiming,makePlan,gaussian};
});
