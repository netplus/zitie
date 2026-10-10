/* A2.2 rigid hardpen progressive ink:
 * Independent immutable ROUND-cap segments accumulate a monotone union.
 * A single growing SVG path can replace its previous round end cap with
 * a join at a pivot, causing a flickering erased pixel. Separate settled
 * capsules never lose previously painted coverage.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieHardpenInkUnion=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  const finite=n=>typeof n==='number'&&Number.isFinite(n);
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  const round=n=>Number(n.toFixed(5));
  const tag=(name,attrs={})=>{
    const el=document.createElementNS(NS,name);
    for(const [a,v] of Object.entries(attrs))el.setAttribute(a,String(v));
    return el;
  };
  const line=(a,b)=>'M '+round(a.x)+' '+round(a.y)+
    ' L '+round(b.x)+' '+round(b.y);
  function createRow(plan,width){
    if(!plan?.geometry?.samples?.length||!finite(width)||width<=0)
      throw Error('Invalid rigid nib source geometry');
    const basic={fill:'none','stroke-width':width,
      'stroke-linecap':'round','stroke-linejoin':'round',
      'pointer-events':'none'};
    const hint=tag('path',{...basic,d:plan.completePath,
      stroke:'#E1E4E7'});
    const finished=tag('path',{...basic,d:plan.completePath,
      stroke:'#5C6269'});
    const redGroup=tag('g',{'pointer-events':'none'});
    const stations=plan.geometry.samples;
    const fragments=stations.slice(1).map((station,i)=>{
      const part=tag('path',{...basic,d:line(stations[i],station),
        stroke:'#BD3945'});
      part.style.display='none';redGroup.append(part);
      return part;
    });
    const active=tag('path',{...basic,d:'',stroke:'#BD3945'});
    active.style.display='none';redGroup.append(active);
    redGroup.style.display='none';finished.style.display='none';
    return {hint,finished,redGroup,active,fragments,plan,
      previousVisibleCount:0};
  }
  function progressAt(row,progress){
    if(!row?.fragments||!finite(progress))
      throw Error('Invalid hardpen incremental progress');
    const stations=row.plan.geometry.samples;
    const len=row.plan.geometry.length,target=clamp(progress,0,1)*len;
    let lo=0,hi=stations.length;
    // Count completed segments (station 0 is not a segment).
    while(lo<hi){
      const mid=(lo+hi)>>1;
      if(stations[mid].distance<=target+1e-9)lo=mid+1;
      else hi=mid;
    }
    const visibleCount=Math.max(0,Math.min(row.fragments.length,lo-1));
    if(visibleCount>row.previousVisibleCount){
      for(let i=row.previousVisibleCount;i<visibleCount;i++)
        row.fragments[i].style.display='';
    }else if(visibleCount<row.previousVisibleCount){
      for(let i=visibleCount;i<row.previousVisibleCount;i++)
        row.fragments[i].style.display='none';
    }
    row.previousVisibleCount=visibleCount;
    if(progress>0&&visibleCount<row.fragments.length){
      const a=stations[visibleCount],b=stations[visibleCount+1];
      const fraction=clamp((target-a.distance)/(b.distance-a.distance),0,1);
      const endpoint={x:a.x+(b.x-a.x)*fraction,
        y:a.y+(b.y-a.y)*fraction};
      row.active.setAttribute('d',line(a,endpoint));
      row.active.style.display='';
    }else{
      row.active.style.display='none';
    }
    return {distance:target,visibleCount,
      segments:row.fragments.length};
  }
  function setWidth(row,width){
    if(!finite(width)||width<=0)throw Error('Invalid nib line width');
    for(const p of [row.hint,row.finished,row.active,...row.fragments])
      p.setAttribute('stroke-width',String(width));
  }
  return {createRow,progressAt,setWidth};
});
