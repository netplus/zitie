/* A1.4.4 source-derived directional start-cap sweep.
 * Uses the original SVG filled silhouette (isPointInFill) and the FIRST
 * canonical median tangent. This is an opt-in VISUAL contact model for
 * reviewed horizontal stroke-type experiments, NOT normative movement data.
 * Never edits the source outline or source median coordinates.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieSourceOnset=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const hypot=(x,y)=>Math.hypot(x,y);
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x);};
  const round=v=>Number(v.toFixed(3));
  function makeStartCap(stroke,profile,contains,options={}){
    if(!stroke||!Array.isArray(stroke.median)||stroke.median.length<2||
       !profile?.stations?.length)throw Error('Invalid source start-cap geometry');
    // A source silhouette query is mandatory. Do NOT invent a cap if the
    // browser lacks SVG fill hit testing or the source is not connected.
    if(typeof contains!=='function')return null;
    const p0=stroke.median[0];
    const next=stroke.median.find((p,i)=>i>0&&hypot(p[0]-p0[0],p[1]-p0[1])>.01);
    if(!next)throw Error('Degenerate source start tangent');
    let dx=next[0]-p0[0],dy=next[1]-p0[1],mag=hypot(dx,dy);
    const u=[dx/mag,dy/mag],n=[-dy/mag,dx/mag];
    const capLength=clamp(Math.min(mag+24,profile.length*.13),42,112);
    const scanStep=options.scanStep??1.5;
    const lateralStep=options.lateralStep??3.0;
    const landingTime=options.landingTime??.014;
    if(!finite(scanStep)||scanStep<.5||scanStep>6||
       !finite(lateralStep)||lateralStep<.6||lateralStep>9||
       !finite(landingTime)||landingTime<.003||landingTime>.08)
      throw Error('Invalid source start contact settings');
    let span=68;
    for(const sample of profile.stations){
      if(sample.distance>capLength)break;
      span=Math.max(span,sample.left??0,sample.right??0);
    }
    span=clamp(span+23,82,184);
    const backward=clamp(span*1.15,48,126);
    const project=(s,t)=>[p0[0]+u[0]*s+n[0]*t,p0[1]+u[1]*s+n[1]*t];
    let first=null,hits=0,behind=Infinity;
    const outlinePath=options.outlinePath;
    const hasBoundarySampler=outlinePath&&
      typeof outlinePath.getTotalLength==='function'&&
      typeof outlinePath.getPointAtLength==='function';
    if(hasBoundarySampler){
      // Sampling the REAL SVG Bézier outline is much cheaper than making
      // thousands of isPointInFill requests across a 2D interior grid.
      // The boundary is the right place to measure the start support.
      const outlineLength=outlinePath.getTotalLength();
      if(!finite(outlineLength)||outlineLength<=0)
        throw Error('Invalid source SVG outline length');
      const count=Math.min(950,Math.max(90,Math.ceil(outlineLength/4.2)));
      for(let i=0;i<=count;i++){
        const p=outlinePath.getPointAtLength(outlineLength*i/count);
        const x=p.x,y=p.y;
        if(!finite(x)||!finite(y))continue;
        const px=x-p0[0],py=y-p0[1];
        const along=px*u[0]+py*u[1];
        const sideways=px*n[0]+py*n[1];
        if(along< -backward||along>0||Math.abs(sideways)>span)continue;
        hits++;
        if(along<behind){behind=along;first={x,y,s:along,normal:sideways};}
      }
    }else{
      // Geometry-library-independent unit-test fallback; browsers use
      // the outline sampler above to avoid blocking iframe init.
      for(let s=-backward;s<=0;s+=scanStep){
        for(let t=-span;t<=span;t+=lateralStep){
          const [x,y]=project(s,t);
          if(!contains(x,y))continue;
          hits++;
          if(s<behind){behind=s;first={x,y,s,normal:t};}
        }
      }
    }
    if(!first||!finite(behind))return null;
    const sourceStart=clamp(behind-(hasBoundarySampler?3:scanStep*1.6),-backward-3,0);
    const cap={
      kind:'source_contour_probed_directional_contact',
      sourceMedianStart:p0.slice(),
      sourceStartPoint:[first.x,first.y],
      sourceStart,capLength,span,landingTime,
      tangent:u,normal:n,hitSamples:hits,scanStep,
      supportMethod:hasBoundarySampler?'source-svg-boundary-arclength':'test-fill-grid',
      sourceDirectionModified:false,
      referenceMaskClipped:true
    };
    cap.pointAt=(s,t)=>project(s,t);
    return cap;
  }
  function sweepAt(cap,distance,timeProgress){
    if(!cap||!finite(cap.capLength)||!finite(distance)||!finite(timeProgress))
      throw Error('Invalid directional onset sweep');
    const t=clamp(timeProgress,0,1),d=clamp(distance,0,cap.capLength);
    if(t<=0)return {d:'',front:cap.sourceStart,contact:0,
      tip:cap.sourceStartPoint.slice()};
    const contact=smooth(t/cap.landingTime);
    // Reconstruct the contact face from the true source support plane,
    // moving forward along the immutable initial median tangent. At the
    // end of the landing phase it meets the current pen arclength exactly.
    const front=cap.sourceStart+(d-cap.sourceStart)*contact;
    const start=cap.sourceStart;
    if(front-start<1e-6)return {d:'',front,contact,
      tip:cap.sourceStartPoint.slice()};
    const a=cap.pointAt(start,-cap.span);
    const b=cap.pointAt(front,-cap.span);
    const c=cap.pointAt(front,cap.span);
    const e=cap.pointAt(start,cap.span);
    const fmt=p=>round(p[0])+' '+round(p[1]);
    const path='M '+fmt(a)+' L '+fmt(b)+' L '+fmt(c)+
      ' L '+fmt(e)+' Z';
    // The marker starts on the actual support point and approaches the
    // canonical first median point during the initial contact gesture.
    const markerTip=[
      lerp(cap.sourceStartPoint[0],cap.sourceMedianStart[0],contact),
      lerp(cap.sourceStartPoint[1],cap.sourceMedianStart[1],contact)
    ];
    return {d:path,front,contact,tip:markerTip};
  }
  return {makeStartCap,sweepAt,smooth};
});