'use strict';
/* P2.2b-2 diagnostic on 201 immutable PDF references, NOT human calibration.
 * Compare the actual shipping matcher (A) vs a research-only abstention (B).
 */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const Matcher=require('../practice/order-check.js');
const Direction=require('../experiments/stroke-direction-guard.js');
const FORMAL_PDF_SHA='7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90';
const PREFIX='window.ZITIE_BOOK_PACK = ';
const PACK=path.join(__dirname,'../../build/a3/book-pack.js');
function loadPack(){
  const raw=fs.readFileSync(PACK,'utf8');
  assert.ok(raw.startsWith(PREFIX)&&raw.endsWith(';\n'));
  const p=JSON.parse(raw.slice(PREFIX.length,-2));
  assert.equal(p.publication.sha256,FORMAL_PDF_SHA);
  assert.equal(p.glyphs.length,201);
  assert.equal(p.glyphs.reduce((s,g)=>s+g.strokes.length,0),1045);
  assert.equal(new Set(p.glyphs.map(g=>g.main_id)).size,201);
  for(const g of p.glyphs){
    assert.match(g.source_sha256,/^[a-f0-9]{64}$/);
    assert.equal(g.strokes.length,g.expected_stroke_count);
  }
  return p;
}
const indices=g=>g.strokes.map((_,i)=>i);
const jitter=(p,i,j,g,scale)=>{
  const phase=g.main_id*.371+j*1.93+i*2.47;
  return [p[0]+Math.sin(phase)*scale,p[1]+Math.cos(phase*.83)*scale];
};
function make(g,{reverse=[],order=indices(g),jitterScale=0,translate=[0,0],sparse=false}={}){
  return order.map((src,ordinal)=>{
    let points=g.strokes[src].median;
    if(reverse.includes(ordinal))points=points.slice().reverse();
    if(sparse)points=points.filter((p,i)=>i===0||i===points.length-1||i%2===0);
    return {index:ordinal,status:'raw-captured',samples:points.map((p,i)=>{
      const q=jitterScale?jitter(p,i,src,g,jitterScale):p;
      return {x:q[0]+translate[0],y:q[1]+translate[1]};
    })};
  });
}
const CHALLENGES=[
  {id:'canonical',kind:'valid',args:()=>({})},
  {id:'shift18',kind:'valid',args:()=>({translate:[18,-12]})},
  {id:'jitter8',kind:'valid',args:()=>({jitterScale:8})},
  {id:'jitter30',kind:'valid',args:()=>({jitterScale:30})},
  {id:'sparse',kind:'valid',args:()=>({sparse:true})},
  {id:'reverseFirst',kind:'reverse',args:()=>({reverse:[0]})},
  {id:'reverseLast',kind:'reverse',args:g=>({reverse:[g.strokes.length-1]})},
  {id:'reverseMid',kind:'reverse',args:g=>g.strokes.length>=3?({reverse:[Math.floor(g.strokes.length/2)]}):null},
  {id:'reverseAll',kind:'reverse',args:g=>({reverse:indices(g)})},
  {id:'reverseFirstJitter8',kind:'reverse',args:()=>({reverse:[0],jitterScale:8})},
  {id:'reverseFirstJitter30',kind:'reverse',args:()=>({reverse:[0],jitterScale:30})},
  {id:'reverseFirstShift18',kind:'reverse',args:()=>({reverse:[0],translate:[18,-12]})},
  {id:'swapFirst',kind:'wrong_order',args:g=>g.strokes.length<2?null:
     ({order:indices(g).map((k,i)=>i===0?1:i===1?0:k)})},
  {id:'swapLast',kind:'wrong_order',args:g=>g.strokes.length<2?null:
     ({order:indices(g).map((k,i)=>i===g.strokes.length-2?g.strokes.length-1:
      i===g.strokes.length-1?g.strokes.length-2:k)})}
];
const statuses=['consistent','reordered','uncertain','incomplete','count_mismatch'];
function run(pack){
  const rows=[];let total=0, newlyAbstained=0;
  const focus=[];
  for(const ch of CHALLENGES){
    const row={scenario:ch.id,kind:ch.kind,denominator:0,
      a:Object.fromEntries(statuses.map(s=>[s,0])),
      b:Object.fromEntries(statuses.map(s=>[s,0])),
      newAbstentions:0,violations:[],directionEvidence:[]};
    for(const glyph of pack.glyphs){
      const args=ch.args(glyph);
      if(args===null)continue;
      const input=make(glyph,args);
      const a=Matcher.evaluate(glyph,input);
      const b=Direction.evaluateCandidate(glyph,input);
      assert.equal(a.status,b.baselineStatus);
      row.denominator++;row.a[a.status]++;row.b[b.candidateStatus]++;total++;
      if(b.candidateStatus!==a.status){
        assert.ok(b.candidateStatus==='uncertain'&&
          ['consistent','reordered'].includes(a.status),
          'Experimental guard MUST be monotonic abstention-only');
        row.newAbstentions++;newlyAbstained++;
        if(row.directionEvidence.length<12){
          row.directionEvidence.push({glyphId:glyph.main_id,character:glyph.character,
            firstAffectedOrdinal:b.conflicts[0]?.writtenOrdinal,
            matchedReferenceOrdinal:b.conflicts[0]?.referenceOrdinal,
            conflict:b.conflicts[0]||null});
        }
      }
      if(ch.kind==='valid'&&b.candidateStatus!=='consistent')
        row.violations.push({glyphId:glyph.main_id,character:glyph.character,
          a:a.status,b:b.candidateStatus});
      if(ch.id==='reverseFirst'&&a.status==='consistent'){
        focus.push({glyphId:glyph.main_id,character:glyph.character,
          firstStrokeName:glyph.strokes[0].name,
          a:a.status,b:b.candidateStatus,
          evidence:b.conflicts[0]||null});
      }
      if(ch.kind==='wrong_order'&&a.status==='reordered'&&
        b.candidateStatus!=='reordered')row.violations.push({
          glyphId:glyph.main_id,character:glyph.character,
          a:a.status,b:b.candidateStatus});
    }
    rows.push(row);
  }
  return {version:Direction.VERSION,mode:'offline_synthetic_only',
    productionMatcherVersion:Matcher.VERSION,realLearnerSamples:0,
    teacherLabels:0,sourceSha256:pack.publication.sha256,
    sourceGlyphs:201,sourceStrokes:1045,total,additionalAbstentions:newlyAbstained,
    focusReverseFirst:focus,byScenario:rows};
}
test('P2.2b-2 direction A/B guard cannot accuse and preserves correct synthetic samples',()=>{
  const pack=loadPack();const report=run(pack);
  assert.equal(report.byScenario.length,14);
  assert.equal(report.total,2778);
  const exact=report.byScenario.find(x=>x.scenario==='canonical');
  assert.equal(exact.a.consistent,201);
  assert.equal(exact.b.consistent,201);
  for(const row of report.byScenario){
    assert.ok(row.denominator>0,'missing scenario '+row.scenario);
    assert.equal(Object.values(row.a).reduce((x,y)=>x+y,0),row.denominator);
    assert.equal(Object.values(row.b).reduce((x,y)=>x+y,0),row.denominator);
    assert.deepEqual(row.violations,[]);
  }
  assert.deepEqual(report.focusReverseFirst.map(x=>x.glyphId),[187,191,200],
    'Exact P2.2a source-locked known regression cases should be reproduced');
  for(const x of report.focusReverseFirst){
    assert.equal(x.a,'consistent');
    assert.equal(x.b,'uncertain','Known reversal must no longer be confidently accepted');
    assert.ok(x.evidence&&x.evidence.cosine<-0.65);
  }
  if(process.env.P22B2_REPORT_FILE){
    const file=path.resolve(process.env.P22B2_REPORT_FILE);
    fs.mkdirSync(path.dirname(file),{recursive:true});
    fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n');
  }
  console.log('P2.2b-2 synthetic A/B cases:',report.total);
  for(const row of report.byScenario)
    console.log('P2.2b-2',row.scenario,'n='+row.denominator,
      'A='+JSON.stringify(row.a),'B='+JSON.stringify(row.b),
      'newAbstentions='+row.newAbstentions);
  console.log('P2.2b-2 targeted:',JSON.stringify(report.focusReverseFirst));
});
module.exports={loadPack,run,make,CHALLENGES};
