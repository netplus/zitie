/* A3.6 progressive-source-front guard for licensed PDF stroke medians.
 * Cap-based brush masks can paint past the nib at folds. Intersect the
 * original ink mask with a monotone source-arclength Voronoi partition:
 * a cell may reveal ink only after its ordered source station is reached.
 * This does not edit a stroke outline, median, clock or stroke order.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieInkFrontGuard=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const clip=(polygon,a,b,c)=>{
    if(polygon.length<3)return [];
    const result=[];
    let prev=polygon[polygon.length-1];
    let pv=a*prev[0]+b*prev[1]-c;
    for(const point of polygon){
      const v=a*point[0]+b*point[1]-c;
      if((v<0)!==(pv<0)){
        const den=pv-v;
        const t=den!==0?pv/den:.5;
        result.push([prev[0]+t*(point[0]-prev[0]),
                     prev[1]+t*(point[1]-prev[1])]);
      }
      if(v<=0)result.push(point);
      prev=point;pv=v;
    }
    return result;
  };
  const round=v=>+v.toFixed(4);
  function buildCells(profile,{bounds=[-256,-256,1280,1280]}={}){
    if(!profile||!Array.isArray(profile.stations)||profile.stations.length<2||
       !Array.isArray(bounds)||bounds.length!==4||!bounds.every(finite)||
       !(bounds[0]<bounds[2]&&bounds[1]<bounds[3]))
      throw Error('Invalid source-front guard input');
    const stations=profile.stations;
    if(stations.length>900)throw Error('Unsafe source-front station count');
    const cells=[];
    for(let i=0;i<stations.length;i++){
      const site=stations[i];
      if(![site.x,site.y,site.distance].every(finite)||
         (i>0&&site.distance<=stations[i-1].distance))
        throw Error('Non-monotonic source-front station');
      let polygon=[
        [bounds[0],bounds[1]],[bounds[2],bounds[1]],
        [bounds[2],bounds[3]],[bounds[0],bounds[3]]
      ];
      for(let j=0;j<stations.length;j++){
        if(j===i)continue;
        const other=stations[j];
        const a=other.x-site.x,b=other.y-site.y;
        const sq=a*a+b*b;
        if(sq<1e-8){
          // Exact revisits already have deposited ink from their FIRST
          // visit, so the earlier station owns the duplicate location.
          if(j<i){polygon=[];break;}
          continue;
        }
        const c=(other.x*other.x+other.y*other.y-
                 site.x*site.x-site.y*site.y)/2;
        polygon=clip(polygon,a,b,c);
        if(polygon.length<3)break;
      }
      const d=polygon.length<3?'': 
        'M '+polygon.map(p=>round(p[0])+' '+round(p[1])).join(' L ')+' Z';
      cells.push({distance:site.distance,outline:d,vertices:polygon.length});
    }
    return {kind:'source_arc_voronoi_progress_gate',cells,
      sourceMedianModified:false,sourceOutlineModified:false,
      nibClockModified:false,
      maxStationGap:Math.max(...stations.slice(1).map((s,i)=>
        s.distance-stations[i].distance))};
  }
  function visibleCount(guard,distance){
    if(!guard||!Array.isArray(guard.cells)||!finite(distance))
      throw Error('Invalid source-front visibility');
    if(distance<=0)return 0;
    let lo=0,hi=guard.cells.length;
    while(lo<hi){
      const mid=(lo+hi)>>1;
      if(guard.cells[mid].distance<=distance+1e-7)lo=mid+1;
      else hi=mid;
    }
    return lo;
  }
  return {buildCells,visibleCount};
});
