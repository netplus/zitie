/* A1.2.3 — artifact-resistant progressive ink coverage.
 * Source outlines/medians are immutable drawing evidence, NOT an approval of
 * writing dynamics. Paint independent ROUND-CAPPED stroke segments into an SVG
 * alpha mask; their union cannot suffer even-odd cancellation, offset-polygon
 * intersections, or the arbitrary terminal-patch triangle of A1.2.2.
 */
(function(root,factory) {
  const api=factory();
  if(typeof module==='object' && module.exports)module.exports=api;
  if(root)root.ZitieInkBrushUnion=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const hypot=(x,y)=>Math.hypot(x,y);
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const finite=v=>Number.isFinite(v)&&typeof v==='number';
  const round=x=>Number(x.toFixed(3));

  function sampleMedian(points,spacing=8){
    if(!Array.isArray(points)||points.length<2||!finite(spacing)||
       spacing<2||spacing>80)throw new Error('Invalid median or sample spacing');
    const first=points[0];
    if(!Array.isArray(first)||first.length!==2||!first.every(finite))
      throw new Error('Invalid initial median point');
    const samples=[{x:first[0],y:first[1],distance:0}];
    let distance=0;
    for(let i=1;i<points.length;i++){
      const [a,b]=[points[i-1],points[i]];
      if(!Array.isArray(b)||b.length!==2||!b.every(finite))
        throw new Error('Nonfinite median point');
      const length=hypot(b[0]-a[0],b[1]-a[1]);
      if(length<1e-7)continue;
      const n=Math.ceil(length/spacing);
      for(let k=1;k<=n;k++){
        const t=k/n;
        samples.push({
          x:lerp(a[0],b[0],t),y:lerp(a[1],b[1],t),
          distance:distance+length*t
        });
      }
      distance+=length;
    }
    if(distance<0.01)throw new Error('Zero length median');
    for(let i=0;i<samples.length;i++){
      const prev=samples[Math.max(0,i-1)],next=samples[Math.min(samples.length-1,i+1)];
      let dx=next.x-prev.x,dy=next.y-prev.y,mag=hypot(dx,dy);
      if(mag<1e-7)throw new Error('Degenerate sampled median');
      dx/=mag;dy/=mag;
      samples[i].nx=-dy;samples[i].ny=dx;
    }
    return samples;
  }

  function widthToContour(s,side,contains,{maxRadius=165}={}){
    if(typeof contains!=='function'||!contains(s.x,s.y))return null;
    const inside=d=>contains(s.x+side*s.nx*d,s.y+side*s.ny*d);
    let lo=0,hi=3;
    while(hi<maxRadius&&inside(hi)){lo=hi;hi=Math.min(maxRadius,hi*1.6);}
    if(inside(hi))return maxRadius;
    for(let k=0;k<8;k++){
      const mid=(lo+hi)*0.5;
      if(inside(mid))lo=mid;else hi=mid;
    }
    return lo;
  }

  function makeProfile(points,contains,options={}){
    const samples=sampleMedian(points,options.spacing??8);
    const margin=options.margin??5;
    const fallbackRadius=options.fallbackRadius??76;
    const limit=options.maxRadius??165;
    if(!finite(margin)||margin<0||margin>32||
       !finite(fallbackRadius)||fallbackRadius<1||
       !finite(limit)||limit<8||limit>256)
      throw new Error('Invalid brush parameter');
    let measured=0,missing=0;
    for(const s of samples){
      let a=null,b=null;
      if(typeof contains==='function'){
        try{
          a=widthToContour(s,1,contains,{maxRadius:limit});
          b=widthToContour(s,-1,contains,{maxRadius:limit});
        }catch(e){a=b=null;}
      }
      if(a===null||b===null){missing++;s.left=s.right=null;}
      else{
        measured++;
        s.left=clamp(a+margin,4,limit+margin);
        s.right=clamp(b+margin,4,limit+margin);
      }
    }
    // Only brush radius may fall back. Never infer/reorder missing median data.
    let prior=null;
    for(let i=0;i<samples.length;i++){
      if(samples[i].left!==null){prior=samples[i];continue;}
      let nearest=null,gap=Infinity;
      for(let j=0;j<samples.length;j++){
        if(samples[j].left===null)continue;
        const d=Math.abs(i-j);
        if(d<gap){gap=d;nearest=samples[j];}
      }
      samples[i].left=nearest?nearest.left:fallbackRadius;
      samples[i].right=nearest?nearest.right:fallbackRadius;
    }
    // A small median-radius smoothing reduces width flicker on straight
    // sections. It never changes centerline, turns or source outline.
    const raw=samples.map(s=>({left:s.left,right:s.right}));
    for(let i=1;i<samples.length-1;i++){
      const a=samples[i-1],b=samples[i],c=samples[i+1];
      if(a.nx*b.nx+a.ny*b.ny<0.985||b.nx*c.nx+b.ny*c.ny<0.985)
        continue;
      b.left=0.2*raw[i-1].left+0.6*raw[i].left+0.2*raw[i+1].left;
      b.right=0.2*raw[i-1].right+0.6*raw[i].right+0.2*raw[i+1].right;
    }
    const coverSegments=[];
    for(let i=1;i<samples.length;i++){
      const a=samples[i-1],b=samples[i];
      const width=clamp(2*Math.max(a.left,a.right,b.left,b.right),8,2*(limit+margin));
      coverSegments.push({
        index:i-1,
        start:a.distance,end:b.distance,
        x0:a.x,y0:a.y,x1:b.x,y1:b.y,width,
        d:'M '+round(a.x)+' '+round(a.y)+' L '+round(b.x)+' '+round(b.y)
      });
    }
    if(!coverSegments.length)throw new Error('No brush coverage segments');
    const length=samples[samples.length-1].distance;
    return {
      stations:samples,segments:coverSegments,length,
      sampledWithFill:measured,fallbackSamples:missing,
      method:typeof contains==='function'?'outline-cross-section':'fallback-no-fill-API',
      coverage:'independent-round-stroke-union',
      // First 2% of travel grows actual brush contact monotonically
      // rather than revealing a full-radius disk at the first sample.
      onsetDistance:Math.min(24,Math.max(4,length*.022))
    };
  }

  function stateAt(profile,progress){
    if(!profile||!Array.isArray(profile.segments)||!profile.segments.length||
       !finite(progress))throw new Error('Invalid brush progress');
    const f=clamp(progress,0,1);
    const dist=profile.length*f;
    if(f===0)return {visibleCount:0,active:-1,partial:0,contactScale:0,
      distance:0,tip:[profile.segments[0].x0,profile.segments[0].y0]};
    let lo=0,hi=profile.segments.length;
    while(lo<hi){
      const m=(lo+hi)>>1;
      if(profile.segments[m].end<=dist+1e-9)lo=m+1;
      else hi=m;
    }
    const visibleCount=lo;
    const active=lo<profile.segments.length?lo:-1;
    const seg=profile.segments[active<0?profile.segments.length-1:active];
    const partial=active<0?1:clamp((dist-seg.start)/(seg.end-seg.start),0,1);
    const tip=active<0?[seg.x1,seg.y1]:
      [lerp(seg.x0,seg.x1,partial),lerp(seg.y0,seg.y1,partial)];
    const t=clamp(dist/profile.onsetDistance,0,1);
    const contactScale=t*t*(3-2*t);
    return {visibleCount,active,partial,contactScale,distance:dist,tip};
  }

  // A1.3: The RED round-capped ink trace is intentionally wider than the
  // source median. A small 8-unit cursor at the median can therefore lag
  // behind ALREADY VISIBLE INK on hooks, even though both share one clock.
  // Do not replace the stable ink algorithm or modify normative medians:
  // derive a distinct, deterministic *optical frontier indicator* position
  // from the exact source-width union stamps already used by the mask.
  function pointAtDistance(profile,distance){
    if(!profile?.stations?.length||!finite(distance))
      throw Error('Invalid stable frontier distance');
    const a=profile.stations,d=clamp(distance,0,profile.length);
    let lo=0,hi=a.length-1;
    while(lo+1<hi){
      const m=(lo+hi)>>1;
      if(a[m].distance<d)lo=m;else hi=m;
    }
    const p=a[lo],q=a[hi];
    const t=clamp((d-p.distance)/(q.distance-p.distance||1),0,1);
    return [lerp(p.x,q.x,t),lerp(p.y,q.y,t)];
  }
  function pointSegmentSquared(x,y,ax,ay,bx,by){
    const vx=bx-ax,vy=by-ay;
    const fraction=clamp(((x-ax)*vx+(y-ay)*vy)/(vx*vx+vy*vy||1),0,1);
    const dx=x-ax-fraction*vx,dy=y-ay-fraction*vy;
    return dx*dx+dy*dy;
  }
  function insideCurrentBrush(profile,state,x,y){
    // A settled local segment contributes its complete round cap. The active
    // partial contributes only through the current canonical median tip.
    // The same source-derived widths and starting-pressure scale are used
    // for the real SVG ink mask; future segments do not contribute.
    for(let j=state.visibleCount-1;j>=0;j--){
      const s=profile.segments[j];
      const scale=s.start<profile.onsetDistance?state.contactScale:1;
      const radius=s.width*.5*scale;
      if(x<Math.min(s.x0,s.x1)-radius||x>Math.max(s.x0,s.x1)+radius||
         y<Math.min(s.y0,s.y1)-radius||y>Math.max(s.y0,s.y1)+radius)
        continue;
      if(pointSegmentSquared(x,y,s.x0,s.y0,s.x1,s.y1)<=radius*radius)
        return true;
    }
    if(state.active>=0&&state.partial>0){
      const s=profile.segments[state.active],radius=s.width*.5*state.contactScale;
      if(pointSegmentSquared(x,y,s.x0,s.y0,state.tip[0],state.tip[1])<=radius*radius)
        return true;
    }
    return false;
  }
  function visibleFrontAtDistance(profile,distance,probeStep,maxLead){
    if(distance<=0)return 0; // No red at t=0.
    const state=stateAt(profile,distance/profile.length);
    const limit=Math.min(profile.length,distance+maxLead);
    let front=distance;
    // Only advance along CONTIGUOUS already-inked median points. This
    // prevents jumping across a gray segment to a later overlapping stroke.
    for(let next=distance+probeStep;next<=limit+1e-7;next+=probeStep){
      const [x,y]=pointAtDistance(profile,Math.min(next,limit));
      if(!insideCurrentBrush(profile,state,x,y))break;
      front=Math.min(next,limit);
    }
    return front;
  }
  function makeVisualFrontier(profile,options={}){
    if(!profile?.segments?.length||!finite(profile.length)||profile.length<=0)
      throw Error('Invalid optical frontier brush');
    const sampleStep=options.sampleStep??7;
    const probeStep=options.probeStep??2;
    const maxLead=options.maxLead??96;
    if(![sampleStep,probeStep,maxLead].every(finite)||
       sampleStep<3||sampleStep>32||probeStep<1||probeStep>10||
       maxLead<8||maxLead>140)
      throw Error('Invalid optical frontier settings');
    const n=Math.max(2,Math.ceil(profile.length/sampleStep));
    const entries=[];
    let last=0;
    for(let i=0;i<=n;i++){
      const distance=profile.length*i/n;
      const visible=i===0?0:i===n?profile.length:
        visibleFrontAtDistance(profile,distance,probeStep,maxLead);
      // The real rasterized union is append-only. A monotone envelope also
      // absorbs sub-sample aliasing around sharp source median pivots.
      last=clamp(Math.max(last,distance,visible),0,profile.length);
      entries.push({distance,front:last});
    }
    return {
      kind:'optical_ink_frontier_cursor_not_normative_or_physical_pen',
      sourceProfile:profile,entries,sourceMedianUntouched:true,
      maxLead,probeStep,sourceStrokeDurationUntouched:true
    };
  }
  function visualFrontAt(frontier,progress){
    if(!frontier?.entries?.length||!finite(progress))
      throw Error('Invalid optical cursor progression');
    const p=clamp(progress,0,1),d=frontier.sourceProfile.length*p;
    if(p===0)return {distance:0,lead:0,tip:pointAtDistance(frontier.sourceProfile,0)};
    const samples=frontier.entries;
    let lo=0,hi=samples.length-1;
    while(lo+1<hi){
      const mid=(lo+hi)>>1;
      if(samples[mid].distance<d)lo=mid;else hi=mid;
    }
    const a=samples[lo],b=samples[hi],t=clamp(
      (d-a.distance)/(b.distance-a.distance||1),0,1);
    const visualDistance=clamp(lerp(a.front,b.front,t),d,frontier.sourceProfile.length);
    return {distance:visualDistance,lead:visualDistance-d,
      tip:pointAtDistance(frontier.sourceProfile,visualDistance)};
  }

  return {sampleMedian,widthToContour,makeProfile,stateAt,
    pointAtDistance,makeVisualFrontier,visualFrontAt};
});