/* P2.2b-2 research only: direction-aware ABSTENTION, not stroke-order grading.
 * The original P2.2a matcher stays unmodified and runs first. An input stroke
 * with convincing REVERSE-direction evidence relative to its globally assigned
 * reference can only downgrade a confident result to uncertain; never accuse.
 * No production UI loads this experimental module.
 */
'use strict';
const Matcher=require('../practice/order-check.js');
const VERSION='p22b2-direction-guard-research-v1';
// Exploratory constants. Not calibrated on real learners; do not use in UI.
const OPTIONS=Object.freeze({minSourceStraightness:0.50,
  maxCosine:-0.65,minCostContrast:0.028,maxReverseFit:0.075,
  minCostImprovementRatio:1.45});
const norm=p=>Math.hypot(p[0],p[1]);
function metricsForStroke(samples,median){
  const a=Matcher.resample(samples),b=Matcher.resample(median);
  const av=[a.at(-1)[0]-a[0][0],a.at(-1)[1]-a[0][1]];
  const bv=[b.at(-1)[0]-b[0][0],b.at(-1)[1]-b[0][1]];
  let srcLength=0;
  for(let i=1;i<b.length;i++)srcLength+=
    Math.hypot(b[i][0]-b[i-1][0],b[i][1]-b[i-1][1]);
  const srcDisplacement=norm(bv),learnerDisplacement=norm(av);
  const straightness=srcDisplacement/srcLength;
  const cosine=learnerDisplacement>0&&srcDisplacement>0?
    Math.max(-1,Math.min(1,
      (av[0]*bv[0]+av[1]*bv[1])/(learnerDisplacement*srcDisplacement))):null;
  const forward=Matcher.compare(samples,median);
  const backward=Matcher.compare(samples,median.slice().reverse());
  const costContrast=forward.score-backward.score;
  const sourceDirectionObservable=Number.isFinite(straightness)&&
    straightness>=OPTIONS.minSourceStraightness&&cosine!==null;
  const reverseClearlyBetter=costContrast>=OPTIONS.minCostContrast&&
    backward.score<=OPTIONS.maxReverseFit&&
    forward.score>=backward.score*OPTIONS.minCostImprovementRatio;
  const directionalConflict=sourceDirectionObservable&&
    cosine<=OPTIONS.maxCosine&&reverseClearlyBetter;
  return {sourceDirectionObservable,sourceStraightness:straightness,
    cosine,forwardCost:forward.score,reverseCost:backward.score,
    costContrast,directionalConflict};
}
function evaluateCandidate(glyph,recorded){
  const baseline=Matcher.evaluate(glyph,recorded);
  const output={version:VERSION,baselineStatus:baseline.status,
    candidateStatus:baseline.status,policy:'conservative_abstain_only',
    conflicts:[],inspectedStrokes:0};
  // Baseline global source-to-learner assignment must be confident first;
  // never relabel an uncertain/count-mismatched stroke or infer correspondence
  // from the raw input ordinal.
  if(!['consistent','reordered'].includes(baseline.status))return output;
  if(!Array.isArray(baseline.observed)||
     baseline.observed.length!==recorded.length)return output;
  for(let i=0;i<recorded.length;i++){
    const ordinal=baseline.observed[i];
    const median=glyph.strokes[ordinal-1]?.median;
    if(!median)continue;
    let result;
    try{result=metricsForStroke(recorded[i].samples,median)}
    catch(_){return {...output,candidateStatus:'uncertain',
      reason:'unreadable_direction_geometry'};}
    output.inspectedStrokes++;
    if(result.directionalConflict)output.conflicts.push({
      writtenOrdinal:i+1,referenceOrdinal:ordinal,
      cosine:result.cosine,sourceStraightness:result.sourceStraightness,
      forwardCost:result.forwardCost,reverseCost:result.reverseCost,
      costContrast:result.costContrast
    });
  }
  if(output.conflicts.length){
    output.candidateStatus='uncertain';
    output.reason='strong_reverse_direction_evidence';
  }
  return output;
}
module.exports={VERSION,OPTIONS,metricsForStroke,evaluateCandidate};
