/* P2.2a — conservative engineering-only whole-character stroke-order match.
 * The published PDF-backed medians are a source reference, NOT measured
 * handwriting or teaching-approved trajectories. An uncertain verdict is
 * preferable to falsely asserting a learner wrote correctly/incorrectly.
 *
 * Inspired by general endpoint, shape and direction criteria used by Chinese
 * stroke practice libraries (e.g. Hanzi Writer), not a copy of their engine.
 */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.ZitieStrokeOrderCheck=api;
})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const VERSION='p22a-conservative-geometry-v1';
 const finite=x=>typeof x==='number'&&Number.isFinite(x);
 const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
 function curveLength(a){
   let n=0;for(let i=1;i<a.length;i++)n+=dist(a[i-1],a[i]);
   return n;
 }
 function resample(points,n=24){
   if(!Array.isArray(points)||points.length<2||n<2)throw Error('Bad polyline');
   const curve=points.map(p=>Array.isArray(p)?[p[0],p[1]]:[p.x,p.y]);
   if(!curve.every(p=>p.every(finite)))throw Error('Nonfinite stroke points');
   const lengths=[0];
   for(let i=1;i<curve.length;i++)
     lengths.push(lengths.at(-1)+dist(curve[i],curve[i-1]));
   const total=lengths.at(-1);
   if(total<.01)throw Error('Degenerate curve');
   const output=[];let k=1;
   for(let i=0;i<n;i++){
     const target=total*i/(n-1);
     while(k<curve.length-1&&lengths[k]<target)k++;
     const gap=lengths[k]-lengths[k-1];
     const t=gap>0?(target-lengths[k-1])/gap:0;
     output.push([
       curve[k-1][0]+t*(curve[k][0]-curve[k-1][0]),
       curve[k-1][1]+t*(curve[k][1]-curve[k-1][1])
     ]);
   }
   return output;
 }
 function compare(actual,reference){
   const a=resample(actual),b=resample(reference);
   const start=dist(a[0],b[0])/1024;
   const end=dist(a.at(-1),b.at(-1))/1024;
   let aligned=0;
   for(let i=0;i<a.length;i++)aligned+=dist(a[i],b[i])/1024;
   aligned/=a.length;
   const al=curveLength(a),bl=curveLength(b);
   const ratio=al/bl;
   const lengthPenalty=Math.abs(Math.log(ratio));
   // Absolute source coordinates are essential: strokes must be matched to
   // actual character locations, not only to shape after free translation.
   const score=.28*start+.28*end+.44*aligned+
     .025*Math.min(5,lengthPenalty);
   const plausible=score<=.098&&start<=.19&&end<=.19&&
     aligned<=.12&&ratio>=.32&&ratio<=2.8;
   return {score,start,end,aligned,lengthRatio:ratio,plausible};
 }
 function assignment(costs){
   const n=costs.length;
   if(n===0||n>18||costs.some(row=>row.length!==n))
     throw Error('Assignment requires 1–18 complete strokes');
   const total=1<<n;
   const dp=new Float64Array(total);
   const parent=new Int32Array(total);
   const selected=new Int8Array(total);
   dp.fill(Infinity);dp[0]=0;
   // Bitcount precomputation: each subset mask records which source strokes
   // have already been assigned to the first popcount(mask) user strokes.
   const count=new Uint8Array(total);
   for(let mask=1;mask<total;mask++)
     count[mask]=count[mask>>1]+(mask&1);
   for(let mask=0;mask<total-1;mask++){
     const base=dp[mask];
     if(!Number.isFinite(base))continue;
     const i=count[mask];
     for(let j=0;j<n;j++){
       if(mask&(1<<j))continue;
       const next=mask|(1<<j),value=base+costs[i][j].score;
       if(value<dp[next]){
         dp[next]=value;parent[next]=mask;selected[next]=j;
       }
     }
   }
   const matched=new Array(n);
   let mask=total-1;
   for(let i=n-1;i>=0;i--){
     matched[i]=selected[mask];mask=parent[mask];
   }
   return {matched,total:dp[total-1]};
 }
 function evaluate(glyph,recorded){
   if(!glyph||!Array.isArray(glyph.strokes)||!glyph.strokes.length||
      !Array.isArray(recorded))throw Error('Missing source or actual handwriting');
   const n=glyph.strokes.length,m=recorded.length;
   const base={matcherVersion:VERSION,referenceStatus:'engineering_preview_unreviewed',
     total:n,written:m,autoScoring:false};
   if(m<n)return {...base,status:'incomplete',message:
     '已写 '+m+'/'+n+' 笔，笔画数量不足，还不能判断完整笔顺。'};
   if(m>n)return {...base,status:'count_mismatch',message:
     '已写 '+m+' 笔，参考为 '+n+' 笔；请检查多写或断笔情况。'};
   if(n>18)return {...base,status:'uncertain',message:
     '笔画过多，当前模型暂时无法可靠判断笔顺。'};
   let scores;
   try{
     scores=recorded.map(r=>glyph.strokes.map(s=>
       compare(r.samples,s.median)));
   }catch(_){
     return {...base,status:'uncertain',message:
       '触点轨迹不完整，无法可靠判断笔顺，请尝试重写。'};
   }
   const best=assignment(scores);
   const identity=Array.from({length:n},(_,i)=>i);
   const observed=best.matched.map(i=>i+1);
   const allStrong=best.matched.every((target,i)=>{
     const chosen=scores[i][target];
     const other=scores[i].filter((_,j)=>j!==target)
       .reduce((lo,s)=>Math.min(lo,s.score),Infinity);
     // Exact/very-close matching is decisive even when a similar neighbor
     // exists, but close competitors must abstain rather than accuse.
     return chosen.plausible&&(n===1||other-chosen.score>=.018);
   });
   const ordered=best.matched.every((target,i)=>target===i);
   if(!allStrong)
     return {...base,status:'uncertain',observed,
       message:'轨迹与参考笔画有重叠或差异，暂时无法可靠判断笔顺；这不代表写错。',
       averageError:best.total/n};
   if(ordered)
     return {...base,status:'consistent',observed,
       message:'本次笔顺与参考顺序一致（工程轨迹匹配，非书法评分）。',
       averageError:best.total/n};
   const wrong=best.matched.flatMap((target,i)=>target!==i?
     [{writtenOrdinal:i+1,referenceOrdinal:target+1}]:[]);
   return {...base,status:'reordered',observed,mismatches:wrong,
     message:'疑似笔顺有误：第 '+wrong[0].writtenOrdinal+
       ' 次落笔更像参考第 '+wrong[0].referenceOrdinal+
       ' 笔。可以查看参考后重新练习。',
     averageError:best.total/n};
 }
 return {VERSION,compare,resample,assignment,evaluate};
});