/* A2.3 professional hardpen Kaishu morphology using immutable capsules.
 * Deliberate small taper / corner weight is a pen's visible width *shape*,
 * NOT measured pressure and NOT a traditional brush alpha mask.
 * No partially drawn segment ever shrinks as the SVG timer advances.
 */
(function(root,factory){
  const Ink=typeof module==='object'&&module.exports?
    require('../hardpen-ink-union.js'):root.ZitieHardpenInkUnion;
  const api=factory(Ink);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieKaishuInk=api;
})(typeof window!=='undefined'?window:null,function(Ink){
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  const finite=Number.isFinite;
  const tag=(name,attrs={})=>{
    const el=document.createElementNS(NS,name);
    for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));
    return el;
  };
  function createRow(plan){
    if(typeof plan?.widthAt!=='function'||!plan.geometry?.samples)
      throw Error('Missing Kaishu candidate morphology');
    const row=Ink.createRow(plan,plan.width);
    const hint=tag('g',{'pointer-events':'none'});
    const finished=tag('g',{'pointer-events':'none'});
    const n=row.fragments.length;
    row.fragmentWidths=new Array(n);
    for(let i=0;i<n;i++){
      const segStart=plan.geometry.samples[i];
      const station=segStart.distance/plan.geometry.length;
      const width=+plan.widthAt(station).toFixed(5);
      if(!finite(width)||width<=0)throw Error('Nonfinite Kaishu pen width');
      const d=row.fragments[i].getAttribute('d');
      row.fragments[i].setAttribute('stroke-width',width);
      row.fragmentWidths[i]=width;
      for(const [group,color] of [
        [hint,'#E1E4E7'],[finished,'#5C6269']]){
        const p=tag('path',{d,fill:'none',stroke:color,
          'stroke-width':width,'stroke-linecap':'round',
          'stroke-linejoin':'round','pointer-events':'none'});
        group.append(p);
      }
    }
    finished.style.display='none';
    row.active.setAttribute('stroke-width',row.fragmentWidths[0]);
    row.hint=hint;row.finished=finished;
    row.isImmutableKaishuUnion=true;
    return row;
  }
  function progressAt(row,progress){
    if(!row?.isImmutableKaishuUnion)
      throw Error('Not a Kaishu irreversible ink row');
    const state=Ink.progressAt(row,progress);
    if(state.visibleCount<row.fragmentWidths.length)
      row.active.setAttribute('stroke-width',
        String(row.fragmentWidths[state.visibleCount]));
    return state;
  }
  function setBaseWidth(row,newBase){
    if(!row?.isImmutableKaishuUnion||!finite(newBase)||newBase<=0)
      throw Error('Invalid Kaishu contact base width');
    const original=row.plan.width;
    const factor=newBase/original;
    for(let i=0;i<row.fragments.length;i++){
      const width=row.fragmentWidths[i]*factor;
      row.fragments[i].setAttribute('stroke-width',width);
      row.hint.children[i].setAttribute('stroke-width',width);
      row.finished.children[i].setAttribute('stroke-width',width);
    }
    row.active.setAttribute('stroke-width',
      String(row.fragmentWidths[
        Math.min(row.previousVisibleCount,row.fragmentWidths.length-1)]*factor));
  }
  return {createRow,progressAt,setBaseWidth};
});
