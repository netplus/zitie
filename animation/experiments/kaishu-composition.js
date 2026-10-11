/* A2.4: cross-stroke composition analysis and opt-in guarded junction experiment.
 * Engineering candidate only. Stroke order, source medians/outlines, timing,
 * fonts, approved lesson records and published default are READ ONLY.
 * No automatic closure: a relation MUST be explicitly declared, bounded and
 * verified; unannotated gaps (especially the complex 龠) stay untouched.
 */
(function(root,factory){
  const K=typeof module==='object'&&module.exports?
    require('./regular-kaishu-model.js'):root.ZitieKaishuModel;
  const H=typeof module==='object'&&module.exports?
    require('./hardpen-model.js'):root.ZitieHardpenModel;
  const api=factory(K,H);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieKaishuComposition=api;
})(typeof window!=='undefined'?window:null,function(Kaishu,Hardpen){
  'use strict';
  const finite=Number.isFinite;
  const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
  const distance=(p,q)=>Math.hypot(q[0]-p[0],q[1]-p[1]);
  const point=p=>[p[0],p[1]];
  const round=n=>+n.toFixed(5);
  const drafts=Object.freeze({
    // The only opt-in edit in this first study. The right descending 捺 of
    // 水 has an unintentional centerline gap from its stem in A2.3.
    // This is a hypothesis for visual review, not a teaching prescription.
    77:Object.freeze([Object.freeze({
      id:'water-right-sweep-root',from:3,endpoint:'start',to:0,
      desiredGap:15,maxMove:24,maxDistance:44
    })])
  });
  const protectedGaps=Object.freeze({
    // An approaching stroke must not be connected just because two
    // centerlines happen to be near; protect this deliberate separation.
    77:Object.freeze(['2:end>0','1:start>0']),
    201:Object.freeze(['no-auto-snap-complex-components'])
  });
  function pointsOf(plan){
    const p=plan?.revisedControlPoints;
    if(!Array.isArray(p)||p.length<2||
       p.some(v=>!Array.isArray(v)||v.length!==2||!v.every(finite)))
      throw Error('A2.4 requires finite A2.3 control points');
    return p;
  }
  function validate(plans,width){
    if(!Array.isArray(plans)||!plans.length||plans.length>64||
       !finite(width)||width<12||width>42)
      throw Error('Invalid A2.4 glyph composition');
    plans.forEach(pointsOf);
  }
  function nearestOnPolyline(p,points){
    if(!Array.isArray(p)||p.length!==2||!p.every(finite)||
       !Array.isArray(points)||points.length<2)
      throw Error('Invalid A2.4 projection');
    let result=null;
    for(let k=1;k<points.length;k++){
      const a=points[k-1],b=points[k],vx=b[0]-a[0],vy=b[1]-a[1];
      const len2=vx*vx+vy*vy;
      if(len2<1e-8)continue;
      const t=clamp(((p[0]-a[0])*vx+(p[1]-a[1])*vy)/len2,0,1);
      const q=[a[0]+t*vx,a[1]+t*vy],d=distance(p,q);
      if(!result||d<result.distance)
        result={point:q,distance:d,segment:k-1,fraction:t};
    }
    if(!result)throw Error('Degenerate A2.4 target polyline');
    return result;
  }
  function cross(a,b,c,d){
    return (b[0]-a[0])*(d[1]-c[1])-
      (b[1]-a[1])*(d[0]-c[0]);
  }
  function strictCrossing(a,b,c,d){
    const abC=cross(a,b,a,c),abD=cross(a,b,a,d);
    const cdA=cross(c,d,c,a),cdB=cross(c,d,c,b);
    return abC*abD<0&&cdA*cdB<0;
  }
  function intersects(p,q){
    for(let i=1;i<p.length;i++)for(let j=1;j<q.length;j++)
      if(strictCrossing(p[i-1],p[i],q[j-1],q[j]))return true;
    return false;
  }
  function analyze(plans,{width=26}={}){
    validate(plans,width);
    const axes=plans.map(pointsOf),segments=[],endpoints=[],crossings=[];
    let xMin=Infinity,xMax=-Infinity,yMin=Infinity,yMax=-Infinity;
    let weightedX=0,weightedY=0,weightSum=0;
    for(let i=0;i<axes.length;i++){
      const pts=axes[i],model=plans[i];
      for(const p of pts){
        xMin=Math.min(xMin,p[0]);xMax=Math.max(xMax,p[0]);
        yMin=Math.min(yMin,p[1]);yMax=Math.max(yMax,p[1]);
      }
      for(let j=1;j<pts.length;j++){
        const a=pts[j-1],b=pts[j],length=distance(a,b);
        if(length<.001)continue;
        const w=typeof model.widthAt==='function'?
          model.widthAt((j-.5)/(pts.length-1)):width;
        const area=length*w;
        weightedX+=(a[0]+b[0])*.5*area;
        weightedY+=(a[1]+b[1])*.5*area;
        weightSum+=area;
        segments.push({stroke:i,segment:j-1,length});
      }
      for(const end of ['start','end']){
        const at=end==='start'?pts[0]:pts.at(-1);
        let nearest=null;
        for(let other=0;other<axes.length;other++)if(other!==i){
          const q=nearestOnPolyline(at,axes[other]);
          if(!nearest||q.distance<nearest.distance)
            nearest={stroke:other,...q};
        }
        endpoints.push({
          stroke:i,end,point:point(at),
          nearest,
          contact:nearest?nearest.distance<=width?
            'touch':nearest.distance<=width*1.75?'near-gap':'separate':
            'single-stroke'
        });
      }
    }
    for(let i=0;i<axes.length;i++)for(let j=i+1;j<axes.length;j++)
      if(intersects(axes[i],axes[j]))crossings.push([i,j]);
    const horizontals=[];
    for(let i=0;i<plans.length;i++){
      if(plans[i].semantics?.kind!=='heng')continue;
      const a=axes[i][0],b=axes[i].at(-1);
      horizontals.push({stroke:i,
        angleDeg:Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI,
        midY:(a[1]+b[1])*.5});
    }
    const spanX=xMax-xMin,spanY=yMax-yMin;
    const centroid=weightSum>0?[weightedX/weightSum,weightedY/weightSum]:
      [(xMin+xMax)/2,(yMin+yMax)/2];
    return {
      strokes:plans.length,segments:segments.length,
      bounds:{minX:xMin,maxX:xMax,minY:yMin,maxY:yMax,
        width:spanX,height:spanY},
      centroid,
      centerOffset:[(centroid[0]-(xMin+xMax)/2)/(spanX||1),
        (centroid[1]-(yMin+yMax)/2)/(spanY||1)],
      endpoints,crossings,horizontals,
      parallelSpreadDeg:horizontals.length>1?
        Math.max(...horizontals.map(v=>v.angleDeg))-
        Math.min(...horizontals.map(v=>v.angleDeg)):null,
      handwritingTeachingApproved:false
    };
  }
  function applyRelations(plans,relations,{width=26,protectedPairs=[]}={}){
    validate(plans,width);
    if(!Array.isArray(relations)||relations.length>100)
      throw Error('Invalid A2.4 declared junction relations');
    const draft=plans.map(p=>pointsOf(p).map(point)),results=[];
    const seen=new Set();
    for(const r of relations){
      if(!r||typeof r.id!=='string'||!r.id||
         !Number.isInteger(r.from)||!Number.isInteger(r.to)||
         r.from<0||r.to<0||r.from>=draft.length||
         r.to>=draft.length||r.from===r.to||
         !['start','end'].includes(r.endpoint)||
         ![r.desiredGap,r.maxMove,r.maxDistance].every(finite)||
         r.desiredGap<0||r.desiredGap>width||
         r.maxMove<0||r.maxMove>width*2||
         r.maxDistance<r.desiredGap||r.maxDistance>width*4)
        throw Error('Invalid A2.4 bounded junction declaration');
      const key=r.from+':'+r.endpoint+'>'+r.to;
      if(seen.has(key))throw Error('Duplicate A2.4 junction declaration');
      seen.add(key);
      if(protectedPairs.includes(key))
        throw Error('A2.4 attempted to close a protected intentional gap');
      const subject=draft[r.from],idx=r.endpoint==='start'?0:subject.length-1;
      const before=subject[idx],near=nearestOnPolyline(before,draft[r.to]);
      const d=near.distance,moving=Math.max(0,d-r.desiredGap);
      let status='already-satisfied';
      if(d>r.maxDistance||moving>r.maxMove+1e-6)
        status='unresolved-out-of-bounds';
      else if(moving>1e-6){
        const t=moving/d,next=[round(before[0]+(near.point[0]-before[0])*t),
          round(before[1]+(near.point[1]-before[1])*t)];
        const adjacent=subject[idx===0?1:idx-1];
        const turnBefore=[adjacent[0]-before[0],adjacent[1]-before[1]];
        const turnAfter=[adjacent[0]-next[0],adjacent[1]-next[1]];
        const dot=turnBefore[0]*turnAfter[0]+turnBefore[1]*turnAfter[1];
        const cosine=clamp(dot/(Math.hypot(...turnBefore)*
          Math.hypot(...turnAfter)||1),-1,1);
        if(next.some(v=>v<0||v>1024)||distance(next,adjacent)<width*.35||
           Math.acos(cosine)>Math.PI/7)
          status='unresolved-shape-guard';
        else{
          subject[idx]=next;
          status='applied';
        }
      }
      results.push({
        id:r.id,key,from:r.from,to:r.to,status,
        beforeDistance:round(d),
        afterDistance:round(nearestOnPolyline(subject[idx],draft[r.to]).distance),
        shift:round(distance(before,subject[idx]))
      });
    }
    return {points:draft,results,
      applied:results.filter(r=>r.status==='applied').length,
      unresolved:results.filter(r=>r.status.startsWith('unresolved')).length};
  }
  function makePlans(glyph,options={}){
    if(!glyph||!Array.isArray(glyph.strokes))
      throw Error('Missing A2.4 source glyph');
    const sourceBefore=JSON.stringify(glyph.strokes);
    const width=options.width===undefined?26:options.width;
    const base=glyph.strokes.map((s,i)=>Kaishu.makePlan(s,glyph,i,{width}));
    const rules=drafts[glyph.main_id]||[];
    const solved=applyRelations(base,rules,{
      width,protectedPairs:protectedGaps[glyph.main_id]||[]
    });
    const result=base.map((plan,i)=>{
      const pts=solved.points[i],old=pointsOf(plan);
      const changed=pts.some((p,j)=>distance(p,old[j])>1e-6);
      if(!changed)return {...plan,
        compositionApproved:false,compositionMethod:'source-preserved-a23',
        compositionAdjustments:[]};
      const motor=Hardpen.makePlan({median:pts},plan.semantics,{width});
      return {...plan,...motor,kind:'a24_junction_trial_not_certified',
        sourceStroke:glyph.strokes[i],originalMedian:glyph.strokes[i].median,
        originalSourceId:plan.originalSourceId,
        revisedControlPoints:pts,
        revisedSource:'bounded_relational_endpoint_adjustment',
        sourceSourceJSONUnchanged:true,structuralApproval:false,
        kaishuStandardClaim:false,hasStrokeMorphology:true,
        usesBrushSourceArtwork:false,
        widthRatioAt:plan.widthRatioAt,widthAt:plan.widthAt,
        compositionApproved:false,compositionMethod:'guarded-explicit-junction',
        compositionAdjustments:solved.results.filter(r=>r.from===i&&
          r.status==='applied')};
    });
    if(JSON.stringify(glyph.strokes)!==sourceBefore)
      throw Error('A2.4 touched immutable source stroke data');
    return result;
  }
  function compare(glyph,afterPlans){
    if(!glyph||!afterPlans||afterPlans.length!==glyph.strokes.length)
      throw Error('A2.4 comparison glyph mismatch');
    const before=glyph.strokes.map((s,i)=>Kaishu.makePlan(s,glyph,i));
    const after=afterPlans;
    return {
      before:analyze(before),after:analyze(after),
      declaredRelations:drafts[glyph.main_id]||[],
      protectedGaps:protectedGaps[glyph.main_id]||[],
      applied:after.flatMap(p=>p.compositionAdjustments||[]),
      needsHumanReview:true,
      isCertifiedRegularScript:false
    };
  }
  return {drafts,protectedGaps,nearestOnPolyline,strictCrossing,
    analyze,applyRelations,makePlans,compare};
});
