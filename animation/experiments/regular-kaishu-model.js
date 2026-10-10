/* A2.3 professional regular-script HARDPEN geometry candidate, not a font.
 * The brush-derived source medians and SVG outlines are READ ONLY. The
 * A2.2 rigid nib is the reference control, not an approved 楷书 font.
 *
 * Standardization hypothesis: axis control, slight horizontal ascent,
 * straight vertical supports, distinct fold corners, short hooks,
 * continuous falling strokes with meaningful thin terminals, and balance.
 * Curated anchors below are ENGINEERING DRAFTS, not teacher reviews.
 */
(function(root,factory){
  const H=typeof module==='object'&&module.exports?
    require('./hardpen-model.js'):root.ZitieHardpenModel;
  const P=typeof module==='object'&&module.exports?
    require('./stroke-primitives.js'):root.ZitieStrokePrimitives;
  const api=factory(H,P);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieKaishuModel=api;
})(typeof window!=='undefined'?window:null,function(Hardpen,Primitive){
  'use strict';
  const finite=Number.isFinite;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const smooth=t=>{const x=clamp(t,0,1);return x*x*(3-2*x);};
  const distance=(a,b)=>Math.hypot(b[0]-a[0],b[1]-a[1]);
  const round=n=>+n.toFixed(5);
  // Stroke-specific *non-normative* anchor drafts based on the existing
  // silhouette/proportions. Do not copy them into source lesson records.
  const revisions=Object.freeze({
    '1:1': {points:[[122,389],[524,411],[919,431]],kind:'heng'},
    '6:1': {points:[[112,434],[523,455],[926,477]],kind:'heng'},
    '6:2': {points:[[506,812],[508,424],[508,18]],kind:'shu'},
    '12:1':{points:[[485,735],[477,616],[415,440],[282,258],[96,108]],kind:'pie'},
    '12:2':{points:[[479,481],[512,380],[656,223],[784,123],[926,105]],kind:'na'},
    '37:1':{points:[[279,571],[280,390],[300,180]],kind:'shu'},
    '37:2':{points:[[301,567],[731,592],[733,412],[710,208]],
      kind:'zhe',foldVertex:1},
    '37:3':{points:[[302,191],[513,203],[732,212]],kind:'heng'},
    '40:1':{points:[[269,559],[280,378],[273,225]],kind:'shu'},
    '40:2':{points:[[313,550],[736,583],[732,324],
      [715,282],[687,285],[665,308]],kind:'zhe-gou',
      foldVertex:1,hookVertex:3},
    '40:3':{points:[[500,802],[506,419],[508,22]],kind:'shu'},
    '77:1':{points:[[507,811],[507,479],[505,104],[498,79],
      [467,85],[427,126]],kind:'gou',hookVertex:3},
    '77:2':{points:[[146,494],[371,519],[389,490],[317,320],
      [210,202],[128,125]],kind:'generic',foldVertex:2},
    '77:3':{points:[[746,682],[727,628],[651,533],[596,455]],kind:'pie'},
    '77:4':{points:[[544,500],[570,420],[711,271],[825,208],[924,191]],kind:'na'},
    '88:1':{points:[[350,777],[380,614],[371,391],[282,184],[167,30]],kind:'pie'},
    '88:2':{points:[[416,766],[675,792],[678,487],
      [676,95],[660,65],[635,74],[605,110]],
      kind:'zhe-gou',foldVertex:1,hookVertex:4},
    '88:3':{points:[[376,541],[521,553],[677,566]],kind:'heng'},
    '88:4':{points:[[363,361],[515,377],[676,388]],kind:'heng'},
    '95:3':{points:[[460,761],[486,584],[468,359],[367,173],[185,51]],kind:'pie'},
    '95:4':{points:[[518,374],[621,242],[777,76],[915,47]],kind:'na'},
    '201:1':{points:[[462,837],[426,718],[342,594],[197,468],[104,425]],kind:'pie'},
    '201:2':{points:[[517,761],[623,640],[787,553],[921,542]],kind:'na'},
    '201:14':{points:[[264,262],[712,315],[715,86],
      [701,38],[673,46],[628,72]],kind:'zhe-gou',
      foldVertex:1,hookVertex:3}
  });
  const supported=Object.freeze(['heng','shu','pie','na','zhe','gou',
    'zhe-gou','dian','generic']);
  function dedupe(points){
    const out=[];
    for(const p of points){
      if(!Array.isArray(p)||p.length!==2||!p.every(finite))
        throw Error('Invalid Kaishu control anchor');
      const q=[round(p[0]),round(p[1])];
      if(!out.length||distance(out.at(-1),q)>.01)out.push(q);
    }
    if(out.length<2)throw Error('Kaishu skeleton degenerate');
    return out;
  }
  function horizontal(raw){
    const a=raw[0],b=raw.at(-1),dx=b[0]-a[0];
    if(dx<24)return raw.slice(); // no invented horizontal orientation
    const targetRise=clamp(b[1]-a[1],dx*.024,dx*.062);
    const lift=a[1]+targetRise;
    return [[a[0],a[1]],[(a[0]+b[0])*.5,
      (a[1]+lift)*.5+dx*.002],[b[0],lift]];
  }
  function vertical(raw){
    const first=raw[0],last=raw.at(-1),dy=first[1]-last[1];
    if(dy<20)return raw.slice();
    const sorted=raw.map(p=>p[0]).sort((a,b)=>a-b);
    const center=sorted[Math.floor(sorted.length/2)];
    const tilt=clamp(last[0]-first[0],-dy*.035,dy*.035);
    const finalY=Math.max(12,last[1]);
    return [[center-tilt*.5,first[1]],[center,
      (first[1]+finalY)*.5],[center+tilt*.5,finalY]];
  }
  function polyError(p,a,b){
    const len=distance(a,b);
    if(!len)return distance(p,a);
    const t=clamp(((p[0]-a[0])*(b[0]-a[0])+
      (p[1]-a[1])*(b[1]-a[1]))/(len*len),0,1);
    return distance(p,[lerp(a[0],b[0],t),lerp(a[1],b[1],t)]);
  }
  function simplify(raw,epsilon=12){
    if(raw.length<=2)return raw.slice();
    let max=-1,index=-1;
    for(let i=1;i<raw.length-1;i++){
      const err=polyError(raw[i],raw[0],raw.at(-1));
      if(err>max){max=err;index=i;}
    }
    if(max<=epsilon)return [raw[0],raw.at(-1)];
    return [...simplify(raw.slice(0,index+1),epsilon).slice(0,-1),
      ...simplify(raw.slice(index),epsilon)];
  }
  function inferredFold(raw,hooked){
    if(raw.length<4)return {points:raw.slice(),foldVertex:null,
      hookVertex:null};
    const dist=Primitive.cumulative(raw);
    const total=dist.at(-1);
    let best=0,pivot=1;
    for(let i=1;i<raw.length-1;i++){
      const left=raw[i-1],here=raw[i],right=raw[i+1];
      const a=[here[0]-left[0],here[1]-left[1]];
      const b=[right[0]-here[0],right[1]-here[1]];
      const dot=clamp((a[0]*b[0]+a[1]*b[1])/
        (Math.hypot(...a)*Math.hypot(...b)||1),-1,1);
      const turn=Math.acos(dot);
      const progress=dist[i]/total;
      const score=turn*(progress>.16&&progress<.76?1:.4);
      if(score>best){best=score;pivot=i;}
    }
    if(best<.35)return {points:simplify(raw),foldVertex:null,
      hookVertex:null};
    const a=raw[0],corner=raw[pivot],end=raw.at(-1);
    const rise=clamp(corner[1]-a[1],(corner[0]-a[0])*.015,
      (corner[0]-a[0])*.09);
    const fold=[corner[0],a[1]+rise];
    if(!hooked)
      return {points:dedupe([a,fold,
        [lerp(fold[0],end[0],.4),lerp(fold[1],end[1],.4)],end]),
        foldVertex:1,hookVertex:null};
    const straightEnd=[lerp(fold[0],end[0],.16),
      lerp(fold[1],end[1],.88)];
    const tip=[end[0],end[1]];
    return {points:dedupe([a,fold,straightEnd,tip]),
      foldVertex:1,hookVertex:2};
  }
  function chooseAnchors(stroke,glyph,index,sem){
    const key=glyph.main_id+':'+(index+1);
    const manual=revisions[key];
    if(manual){
      if(manual.kind!==sem.kind &&
         !(manual.kind==='zhe-gou'&&sem.kind==='zhe'))
        throw Error('Curated Kaishu primitive does not match source '+key);
      return {points:dedupe(manual.points),
        foldVertex:manual.foldVertex??null,
        hookVertex:manual.hookVertex??null,
        source:'curated_engineering_candidate_not_a_teaching_reference',
        key};
    }
    const raw=stroke.median,kind=sem.kind;
    if(kind==='heng')return {
      points:dedupe(horizontal(raw)),foldVertex:null,hookVertex:null,
      source:'axis_regularization_heuristic',key};
    if(kind==='shu')return {
      points:dedupe(vertical(raw)),foldVertex:null,hookVertex:null,
      source:'axis_regularization_heuristic',key};
    if(kind==='zhe'||kind==='zhe-gou'){
      const inferred=inferredFold(raw,kind==='zhe-gou');
      return {...inferred,source:'unreviewed_fold_inference',key};
    }
    if(kind==='pie'||kind==='na'){
      // RDP removes unwanted brush-source jitters without forcing a
      // polyline into a straight stroke; deliberate trajectories survive.
      return {points:dedupe(simplify(raw,12)),foldVertex:null,
        hookVertex:null,source:'low_curvature_sweep_heuristic',key};
    }
    return {points:dedupe(simplify(raw,9)),foldVertex:null,
      hookVertex:null,source:'source_skeleton_fallback_unreviewed',key};
  }
  function makePlan(stroke,glyph,index,options={}){
    if(!glyph?.strokes?.[index]||glyph.strokes[index]!==stroke)
      throw Error('Kaishu glyph/stroke provenance mismatch');
    const original=JSON.stringify(stroke);
    const baseSem=Primitive.semantics(glyph,index);
    if(!supported.includes(baseSem.kind))throw Error('Unsupported source stroke name');
    const chosen=chooseAnchors(stroke,glyph,index,baseSem);
    // Source medians and artwork remain untouched; only a DIFFERENT
    // candidate skeleton feeds the A2.2 hardpen dynamics.
    const modelSem={...baseSem,
      foldVertex:chosen.foldVertex??undefined,
      hookVertex:chosen.hookVertex??undefined};
    const virtual={median:chosen.points};
    const underlying=Hardpen.makePlan(virtual,modelSem,options);
    const avgWidth=underlying.width,kind=baseSem.kind;
    const hook=underlying.hook,fold=underlying.fold;
    function widthRatioAt(progress){
      if(!finite(progress))throw Error('Nonfinite Kaishu width position');
      const t=clamp(progress,0,1);
      let weight=1;
      if(kind==='heng'){
        weight=1-.055*Math.sin(Math.PI*t)+.06*smooth((t-.86)/.14);
      }else if(kind==='shu'){
        weight=1-.045*Math.sin(Math.PI*t);
        if(glyph.main_id===6&&index===1)
          weight*=1-.79*smooth((t-.79)/.21); // 悬针竖
      }else if(kind==='pie'){
        weight=1.08-.91*smooth((t-.24)/.76);
      }else if(kind==='na'){
        weight=.60+.61*smooth((t-.08)/.70);
        weight*=1-.86*smooth((t-.83)/.17);
      }else if(kind==='gou'||kind==='zhe-gou'){
        weight=1+(hook!==null?.10*Math.exp(-Math.pow((t-hook)/.035,2)):0);
        if(hook!==null){
          const releaseStart=Math.max(.57,hook-.12);
          weight*=1-.84*smooth((t-releaseStart)/(1-releaseStart));
        }
      }else if(kind==='dian'){
        weight=.64+.44*smooth(t/.62);
        weight*=1-.22*smooth((t-.78)/.22);
      }else if(kind==='zhe'){
        weight=1+(fold!==null?.08*Math.exp(-Math.pow((t-fold)/.06,2)):0);
      }else{
        weight=1-.06*Math.sin(Math.PI*t);
      }
      return clamp(weight,.13,1.25);
    }
    function widthAt(progress){return avgWidth*widthRatioAt(progress);}
    const result={...underlying,
      kind:'a23_regular_kaishu_heuristic_not_certified',
      sourceStroke:stroke,sourceSourceJSONUnchanged:true,
      kaishuStandardClaim:false,structuralApproval:false,
      source:'unreviewed_engineering_candidate',
      originalSourceId:chosen.key,originalMedian:stroke.median,
      revisedControlPoints:chosen.points,
      revisedFoldVertex:chosen.foldVertex,
      revisedHookVertex:chosen.hookVertex,
      revisedSource:chosen.source,
      widthRatioAt,widthAt,
      hasStrokeMorphology:true,usesBrushSourceArtwork:false};
    if(JSON.stringify(stroke)!==original)
      throw Error('Kaishu regularization changed original source');
    return result;
  }
  function horizontalMetrics(plan){
    if(plan.semantics.kind!=='heng')throw Error('Not a horizontal stroke');
    const path=plan.geometry.samples,a=path[0],b=path.at(-1);
    const dx=b.x-a.x;
    const slope=(b.y-a.y)/dx;
    let maxOffset=0;
    for(const p of path){
      const expected=a.y+(p.x-a.x)*slope;
      maxOffset=Math.max(maxOffset,Math.abs(p.y-expected));
    }
    return {slope,angleDeg:Math.atan(slope)*180/Math.PI,
      maxNormalDeviation:maxOffset,span:dx};
  }
  function verticalMetrics(plan){
    if(plan.semantics.kind!=='shu')throw Error('Not a vertical stroke');
    const path=plan.geometry.samples,a=path[0],b=path.at(-1);
    let maxOffset=0;
    for(const p of path){
      const t=(a.y-p.y)/(a.y-b.y||1);
      const expected=lerp(a.x,b.x,t);
      maxOffset=Math.max(maxOffset,Math.abs(p.x-expected));
    }
    return {span:a.y-b.y,dx:b.x-a.x,maxNormalDeviation:maxOffset};
  }
  return {revisions,makePlan,chooseAnchors,polyError,simplify,
    horizontal,vertical,inferredFold,horizontalMetrics,verticalMetrics};
});
