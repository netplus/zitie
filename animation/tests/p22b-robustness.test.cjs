'use strict';
/*
 * P2.2b-1 OFFLINE SYNTHETIC AUDIT — NOT real handwriting accuracy.
 *
 * Read the same immutable PDF-derived medians used by P2.2a. Deterministic
 * transformations provide a counterexample/coverage inventory, not teacher-
 * labelled examples. No learner records, IndexedDB, network or telemetry.
 * This file is test-only: it does not change the production matcher.
 */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Matcher=require('../practice/order-check.js');

const ROOT=path.resolve(__dirname,'../..');
const PACK_PATH=path.join(ROOT,'build/a3/book-pack.js');
const SUITE_VERSION='p22b-synthetic-robustness-v1';
const STATUSES=['consistent','reordered','uncertain','incomplete','count_mismatch'];
const PREFIX='window.ZITIE_BOOK_PACK = ';
const FORMAL_PDF_SHA256='7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90';

function readPack(){
  const raw=fs.readFileSync(PACK_PATH,'utf8');
  assert.ok(raw.startsWith(PREFIX)&&raw.endsWith(';\n'),
    'Exact generated PDF-backed source pack required');
  const pack=JSON.parse(raw.slice(PREFIX.length,-2));
  assert.equal(pack.glyphs.length,201);
  assert.equal(pack.glyphs.reduce((n,g)=>n+g.strokes.length,0),1045);
  assert.equal(pack.publication.sha256,FORMAL_PDF_SHA256,
    'Audit must use the published, immutable v0.5.1 PDF source');
  assert.equal(new Set(pack.glyphs.map(g=>g.main_id)).size,201,
    'Each canonical glyph must have a unique main ID');
  for(const glyph of pack.glyphs){
    assert.match(glyph.source_sha256,/^[0-9a-f]{64}$/,
      'Missing glyph/source fingerprint');
    assert.equal(glyph.strokes.length,glyph.expected_stroke_count,
      'Unexpected stroke total for glyph '+glyph.character);
  }
  return pack;
}

function cloneStroke(glyph,referenceIndex,convert=(p)=>p){
  return glyph.strokes[referenceIndex].median.map((p,i)=>{
    const point=convert(p,i,referenceIndex,glyph);
    return {x:point[0],y:point[1]};
  });
}
function recorded(glyph,order,convert=(p)=>p){
  return order.map((j,index)=>({
    index,status:'raw-captured',
    samples:cloneStroke(glyph,j,convert)
  }));
}
const indices=glyph=>glyph.strokes.map((_,i)=>i);
const swap=(a,i,j)=>{
  const b=a.slice();[b[i],b[j]]=[b[j],b[i]];return b;
};
function jitter(p,pointIndex,strokeIndex,glyph,amplitude){
  // Deterministic, bounded, independent of host time or random seed.
  const phase=glyph.main_id*.371+strokeIndex*1.93+pointIndex*2.47;
  return [p[0]+Math.sin(phase)*amplitude,
          p[1]+Math.cos(phase*.83)*amplitude];
}
function prepare(glyph,type){
  const order=indices(glyph),n=order.length;
  switch(type){
    case 'source_exact':
      return recorded(glyph,order);
    case 'translate_18':
      return recorded(glyph,order,p=>[p[0]+18,p[1]-12]);
    case 'jitter_8':
      return recorded(glyph,order,(p,i,j,g)=>jitter(p,i,j,g,8));
    case 'jitter_30':
      return recorded(glyph,order,(p,i,j,g)=>jitter(p,i,j,g,30));
    case 'sparse_vertices':
      return order.map((j,index)=>{
        const median=glyph.strokes[j].median;
        const samples=median.filter((_,i)=>
          i===0||i===median.length-1||i%2===0).map(([x,y])=>({x,y}));
        return {index,status:'raw-captured',samples};
      });
    case 'swap_first':
      return n<2?null:recorded(glyph,swap(order,0,1));
    case 'swap_last':
      return n<2?null:recorded(glyph,swap(order,n-2,n-1));
    case 'reverse_first':
      return recorded(glyph,order).map((r,i)=>i===0?
        {...r,samples:r.samples.slice().reverse()}:r);
    case 'duplicate_first':
      return n<2?null:recorded(glyph,
        order.map((j,i)=>i===n-1?0:j));
    case 'displaced_first':
      return recorded(glyph,order).map((r,i)=>i===0?
        {...r,samples:r.samples.map(p=>({x:p.x+350,y:p.y+260}))}:r);
    case 'omit_last':
      return recorded(glyph,order.slice(0,-1));
    case 'extra_last':
      return recorded(glyph,order.concat(n-1));
    default:
      throw Error('Unknown robustness scenario '+type);
  }
}

const CASES=Object.freeze([
  {id:'source_exact',groundTruth:'correct_order',note:'Exact source oracle; not a person'},
  {id:'translate_18',groundTruth:'correct_order',note:'All strokes displaced (+18,-12)'},
  {id:'jitter_8',groundTruth:'correct_order',note:'Small synthetic vertex offsets'},
  {id:'jitter_30',groundTruth:'correct_order',note:'Larger synthetic vertex offsets'},
  {id:'sparse_vertices',groundTruth:'correct_order',note:'Synthetic sparse vertex sampling'},
  {id:'swap_first',groundTruth:'wrong_order',note:'Reference strokes 1 and 2 exchanged'},
  {id:'swap_last',groundTruth:'wrong_order',note:'Last two reference strokes exchanged'},
  {id:'reverse_first',groundTruth:'bad_direction',note:'First stroke reversed; order unchanged'},
  {id:'duplicate_first',groundTruth:'wrong_geometry',note:'Last stroke replaced with first'},
  {id:'displaced_first',groundTruth:'wrong_geometry',note:'First stroke displaced (350,260)'},
  {id:'omit_last',groundTruth:'missing_count',note:'One fewer stroke than reference'},
  {id:'extra_last',groundTruth:'extra_count',note:'One more stroke than reference'}
]);

function runAudit(pack){
  const byCategory=[];
  let cases=0,falseAccusations=0,falseAcceptances=0,abstentions=0;
  for(const definition of CASES){
    const result={...definition,denominator:0,
      outcomes:Object.fromEntries(STATUSES.map(k=>[k,0])),
      falseAccusations:0,falseAcceptances:0,
      abstentions:0,counterexamples:[]};
    for(const glyph of pack.glyphs){
      const input=prepare(glyph,definition.id);
      if(input===null)continue;
      const decision=Matcher.evaluate(glyph,input);
      assert.ok(STATUSES.includes(decision.status),
        'Unexpected matcher status: '+decision.status);
      assert.equal(decision.matcherVersion,Matcher.VERSION);
      assert.equal(decision.autoScoring,false);
      assert.equal(decision.referenceStatus,'engineering_preview_unreviewed');
      result.denominator++;
      result.outcomes[decision.status]++;
      cases++;
      const accused=definition.groundTruth==='correct_order'&&
        decision.status==='reordered';
      const accepted=definition.groundTruth!=='correct_order'&&
        decision.status==='consistent';
      if(accused){result.falseAccusations++;falseAccusations++;}
      if(accepted){result.falseAcceptances++;falseAcceptances++;}
      if(decision.status==='uncertain'){
        result.abstentions++;abstentions++;
      }
      // Export bounded metadata only; never raw stroke samples or timestamps.
      if((accused||accepted||decision.status==='uncertain')&&
          result.counterexamples.length<6){
        result.counterexamples.push({
          glyphId:glyph.main_id,character:glyph.character,
          strokeCount:glyph.strokes.length,outcome:decision.status
        });
      }
      // Invariants that can be established without human labels.
      if(definition.id==='source_exact')
        assert.equal(decision.status,'consistent',
          'Regression in source-perfect baseline for '+glyph.character);
      if(definition.groundTruth==='missing_count')
        assert.equal(decision.status,'incomplete',
          'Missing stroke must never receive a verdict');
      if(definition.groundTruth==='extra_count')
        assert.equal(decision.status,'count_mismatch',
          'Extra stroke must never receive an order verdict');
    }
    assert.ok(result.denominator>0,'No examples for '+definition.id);
    assert.equal(Object.values(result.outcomes).reduce((a,b)=>a+b,0),
      result.denominator);
    byCategory.push(result);
  }
  return {
    suiteVersion:SUITE_VERSION,sourceKind:'pdf_medians_synthetic_only',
    reportPurpose:'diagnostic_not_real_handwriting_validation',
    matcherVersion:Matcher.VERSION,
    publishedPdfSha256:pack.publication.sha256,
    sourceGlyphs:pack.glyphs.length,
    sourceStrokes:pack.glyphs.reduce((s,g)=>s+g.strokes.length,0),
    scenarioCount:CASES.length,caseCount:cases,
    falseAccusations, falseAcceptances,abstentions,
    realLearnerSamples:0,teacherLabels:0,
    productionThresholdsChanged:false,
    byCategory
  };
}

test('P2.2b-1: whole 201-glyph source-derived robustness inventory (diagnostic only)',()=>{
  const pack=readPack();
  const report=runAudit(pack);
  assert.equal(report.sourceGlyphs,201);
  assert.equal(report.sourceStrokes,1045);
  assert.equal(report.scenarioCount,12);
  assert.ok(report.caseCount>2000);
  assert.equal(report.byCategory.find(x=>x.id==='source_exact')
    .outcomes.consistent,201);
  assert.equal(report.byCategory.find(x=>x.id==='omit_last')
    .outcomes.incomplete,201);
  assert.equal(report.byCategory.find(x=>x.id==='extra_last')
    .outcomes.count_mismatch,201);
  assert.equal(report.realLearnerSamples,0);
  assert.equal(report.teacherLabels,0);
  // Deliberately NO synthetic-rate pass threshold: this is a measurement
  // baseline to be reviewed, not evidence to retune production scoring.
  if(process.env.P22B_REPORT_FILE){
    const output=path.resolve(process.env.P22B_REPORT_FILE);
    fs.mkdirSync(path.dirname(output),{recursive:true});
    fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n','utf8');
  }
  for(const row of report.byCategory){
    console.log('P2.2b synthetic',row.id,'n='+row.denominator,
      JSON.stringify(row.outcomes),
      'false-accusation='+row.falseAccusations,
      'false-accept='+row.falseAcceptances);
  }
  console.log('P2.2b JSON: source-perfect oracle 201/201; all other',
    'synthetic outcomes are diagnostic, NOT measured accuracy');
});

module.exports={prepare,runAudit,CASES,SUITE_VERSION};
