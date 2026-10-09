/* A1.2.2 precision ink-reveal geometry, separate from the canonical timeline.
 * Profiles approximate painting only; they never modify or approve stroke medians.
 */
(function (root, factory) {
  const api=factory();
  if (typeof module==='object' && module.exports) module.exports=api;
  if (root) root.ZitieInkBrush=api;
})(typeof window!=='undefined' ? window:null,function(){
  'use strict';
  const hypot=(x,y)=>Math.hypot(x,y);
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  const round=v=>Number(v.toFixed(2));
  const lerp=(a,b,t)=>a+(b-a)*t;

  function sampleMedian(points,spacing=7) {
    if (!Array.isArray(points)||points.length<2||
        !Number.isFinite(spacing)||spacing<2||spacing>80)
      throw new Error('Invalid median or sample spacing');
    const out=[{x:points[0][0],y:points[0][1],distance:0}];
    let distance=0;
    for(let i=1;i<points.length;i++){
      const [ax,ay]=points[i-1],[bx,by]=points[i];
      const length=hypot(bx-ax,by-ay);
      if(!Number.isFinite(length))throw new Error('Invalid median segment');
      if(length<0.001)continue;
      const count=Math.ceil(length/spacing);
      for(let j=1;j<=count;j++){
        const t=j/count;
        out.push({x:lerp(ax,bx,t),y:lerp(ay,by,t),distance:distance+length*t});
      }
      distance+=length;
    }
    if(distance<0.01)throw new Error('Zero length median');
    for(let i=0;i<out.length;i++){
      const prev=out[Math.max(i-1,0)],next=out[Math.min(i+1,out.length-1)];
      let tx=next.x-prev.x,ty=next.y-prev.y;
      const size=hypot(tx,ty);
      if(size<0.001)throw new Error('Degenerate sampled median');
      tx/=size;ty/=size;
      out[i].nx=-ty;out[i].ny=tx;
    }
    return out;
  }

  function widthToContour(station,sign,contains,options={}) {
    const max=options.maxRadius||154;
    if(!contains(station.x,station.y))return null;
    const test=d=>contains(station.x+sign*station.nx*d,station.y+sign*station.ny*d);
    let lo=0,hi=3;
    while(hi<max&&test(hi)){lo=hi;hi=Math.min(max,hi*1.6);}
    if(test(hi))return max;
    for(let k=0;k<7;k++){
      const mid=(lo+hi)/2;
      if(test(mid))lo=mid;else hi=mid;
    }
    return lo;
  }

  function makeProfile(points,contains,options={}) {
    const stations=sampleMedian(points,options.spacing||7);
    const max=options.maxRadius||154;
    const margin=options.margin===undefined ? 6:options.margin;
    const fallback=options.fallbackRadius||72;
    let probed=0,misses=0;
    for(const s of stations){
      let left=null,right=null;
      if(typeof contains==='function'){
        try{
          left=widthToContour(s,1,contains,{maxRadius:max});
          right=widthToContour(s,-1,contains,{maxRadius:max});
        }catch(_){left=right=null;}
      }
      if(left===null||right===null){misses++;s.left=null;s.right=null;}
      else{
        probed++;
        s.left=clamp(left+margin,9,max+margin);
        s.right=clamp(right+margin,9,max+margin);
      }
    }
    // Vendor endpoints may extend just beyond the outline. Substitute only
    // brush width from the nearest measured cross-section, not point/direction.
    for(let i=0;i<stations.length;i++){
      const s=stations[i];
      if(s.left!==null)continue;
      let best=null,gap=Infinity;
      for(let j=0;j<stations.length;j++){
        const candidate=stations[j],diff=Math.abs(i-j);
        if(candidate.left!==null&&diff<gap){best=candidate;gap=diff;}
      }
      s.left=best?best.left:fallback;
      s.right=best?best.right:fallback;
    }
    // Smooth measured brush-width jitter only on locally aligned sections.
    // Never smooth median coordinates or join a genuine sharp fold/hook.
    const original=stations.map(p=>({left:p.left,right:p.right}));
    for(let i=1;i<stations.length-1;i++){
      const a=stations[i-1],b=stations[i],c=stations[i+1];
      const aligned=(a.nx*b.nx+a.ny*b.ny>0.96) &&
                    (b.nx*c.nx+b.ny*c.ny>0.96);
      if(!aligned)continue;
      b.left=original[i-1].left*0.2+original[i].left*0.6+
        original[i+1].left*0.2;
      b.right=original[i-1].right*0.2+original[i].right*0.6+
        original[i+1].right*0.2;
    }
    return {stations,length:stations[stations.length-1].distance,
      fullSegments:stations.slice(1).map((b,i)=>segmentGeometry(stations[i],b)),
      method:typeof contains==='function'?'outline-cross-section':'fallback-no-fill-API',
      sampledWithFill:probed,fallbackSamples:misses};
  }

  function segmentGeometry(a,b,softTip=false){
    const A=[round(a.x+a.nx*a.left),round(a.y+a.ny*a.left)];
    const B=[round(b.x+b.nx*b.left),round(b.y+b.ny*b.left)];
    const C=[round(b.x-b.nx*b.right),round(b.y-b.ny*b.right)];
    const D=[round(a.x-a.nx*a.left),round(a.y-a.ny*a.left)];
    const distance=hypot(b.x-a.x,b.y-a.y);
    if(distance<0.001)return '';
    if(!softTip)return 'M '+A.join(' ')+' L '+B.join(' ')+' L '+C.join(' ')+' L '+D.join(' ')+' Z';
    // At a partially written front, use a softly curved inward nib. The
    // control point lies *behind* the median tip; never unveil future ink.
    const retreat=Math.min(3.5,distance*0.34);
    const tip=[round(b.x-(b.x-a.x)*retreat/distance),
               round(b.y-(b.y-a.y)*retreat/distance)];
    return 'M '+A.join(' ')+' L '+B.join(' ')+' Q '+tip.join(' ')+' '+C.join(' ')+' L '+D.join(' ')+' Z';
  }

  function interpolateStation(a,b,distance){
    const t=clamp((distance-a.distance)/(b.distance-a.distance),0,1);
    let nx=lerp(a.nx,b.nx,t),ny=lerp(a.ny,b.ny,t);
    const norm=hypot(nx,ny);
    if(norm>0.001){nx/=norm;ny/=norm;}else{nx=a.nx;ny=a.ny;}
    return {x:lerp(a.x,b.x,t),y:lerp(a.y,b.y,t),distance,nx,ny,
      left:lerp(a.left,b.left,t),right:lerp(a.right,b.right,t)};
  }

  function revealPath(profile,progress){
    if(!profile||!Array.isArray(profile.stations)||profile.stations.length<2||
        !Number.isFinite(progress))throw new Error('Invalid progressive brush');
    const fraction=clamp(progress,0,1);
    if(fraction===0)return '';
    const cutoff=profile.length*fraction,all=profile.stations,chunks=[];
    for(let i=1;i<all.length;i++){
      const a=all[i-1],b=all[i];
      if(a.distance>=cutoff)break;
      const end=b.distance<=cutoff?b:interpolateStation(a,b,cutoff);
      chunks.push(end===b && profile.fullSegments ?
        profile.fullSegments[i-1] : segmentGeometry(a,end,true));
      if(b.distance>=cutoff)break;
    }
    return chunks.filter(Boolean).join(' ');
  }
  return {sampleMedian,widthToContour,makeProfile,revealPath,interpolateStation};
});