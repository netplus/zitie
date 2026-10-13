'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');
const Whole=require('../practice/whole-progress.js');
const Matcher=require('../practice/order-check.js');
const Legacy=require('../practice/progress-controller.js');
const Storage=require('../practice/storage.js');
const {TraceSession}=require('../practice/trace-session.js');
const source=fs.readFileSync(path.join(ROOT,'build/a3/book-pack.js'),'utf8');
assert.ok(source.startsWith('window.ZITIE_BOOK_PACK = '),'Need exact generated PDF-backed pack');
const pack=JSON.parse(source.slice('window.ZITIE_BOOK_PACK = '.length,-2));
const water=pack.glyphs.find(x=>x.main_id===77);
const identity={glyphId:77,strokeCount:4,sourceHash:water.source_sha256,
 pdfHash:pack.publication.sha256};

function draftFromMedian(median,seed=0){
 const t=new TraceSession({maxPoints:8192});
 const item=(p,i)=>({x:p[0],y:p[1],timeStamp:1000+seed+i*10,
   pressure:.65,tiltX:5,tiltY:-4});
 assert.equal(t.begin(6+seed,'pen',item(median[0],0)),true);
 for(let i=1;i<median.length;i++)
   t.append(6+seed,item(median[i],i));
 t.end(6+seed,item(median.at(-1),median.length+1));
 return t.draft;
}
const recordedFromGlyph=(glyph,order=null)=>
  (order||glyph.strokes.map((_,i)=>i))
    .map((j,i)=>({samples:draftFromMedian(glyph.strokes[j].median,i*100).samples,
      index:i,status:'raw-captured'}));

test('P2.2a naturally lifted pen strokes enter one uninterrupted whole-word session',()=>{
 const c=new Whole.WholeWriting(identity);
 assert.equal(c.currentIndex,0);
 assert.equal(c.complete,false);
 assert.equal(c.append(null).ok,false);
 for(let i=0;i<4;i++){
   const v=c.append(draftFromMedian(water.strokes[i].median,i*150));
   assert.equal(v.ok,true);
   assert.equal(v.written,i+1);
   assert.equal(c.currentIndex,i+1);
   assert.equal(c.getWritten()[i].status,'raw-captured');
   assert.equal(c.getWritten()[i].index,i);
   assert.equal(c.complete,i===3);
 }
 assert.equal(c.append(draftFromMedian(water.strokes[0].median,999)).ok,false);
 assert.equal(c.getState().writtenStrokes,4);
 assert.equal(c.undo(),true);
 assert.equal(c.currentIndex,3);
 assert.equal(c.complete,false);
 assert.equal(c.append(draftFromMedian(water.strokes[3].median,777)).ok,true);
 assert.equal(c.complete,true);
 assert.equal(c.restart(),true);
 assert.equal(c.currentIndex,0);
 assert.equal(c.undo(),false);
});

test('P2.2a automatically identifies water correct order, swaps and incomplete writing',()=>{
 const correct=Matcher.evaluate(water,recordedFromGlyph(water));
 assert.equal(correct.status,'consistent',JSON.stringify(correct));
 assert.deepEqual(correct.observed,[1,2,3,4]);
 const swapped=Matcher.evaluate(water,recordedFromGlyph(water,[1,0,2,3]));
 assert.equal(swapped.status,'reordered',JSON.stringify(swapped));
 assert.deepEqual(swapped.observed,[2,1,3,4]);
 assert.ok(swapped.message.includes('第 1 次落笔'));
 const shuffled=Matcher.evaluate(water,recordedFromGlyph(water,[3,2,1,0]));
 assert.equal(shuffled.status,'reordered');
 const absent=Matcher.evaluate(water,recordedFromGlyph(water,[0,1,2]));
 assert.equal(absent.status,'incomplete');
 assert.equal(absent.written,3);
 const extra=Matcher.evaluate(water,recordedFromGlyph(water,[0,1,2,3,3]));
 assert.equal(extra.status,'count_mismatch');
 assert.equal(correct.autoScoring,false);
 assert.equal(correct.referenceStatus,'engineering_preview_unreviewed');
});

test('P2.2a blank, ambiguous, duplicated or badly displaced traces never become false correct',()=>{
 const ambiguous={strokes:[{median:[[100,300],[400,300]]},
    {median:[[100,300],[400,300]]}]};
 const both=[{samples:[{x:100,y:300},{x:400,y:300}]},
   {samples:[{x:100,y:300},{x:400,y:300}]}];
 const result=Matcher.evaluate(ambiguous,both);
 assert.equal(result.status,'uncertain',
   'Geometrically identical strokes cannot establish a reliable ordinal');
 const bogus=water.strokes.map((_,i)=>({samples:[
   {x:950-i*20,y:-100},{x:1000-i*20,y:-110}]}));
 assert.equal(Matcher.evaluate(water,bogus).status,'uncertain');
 const reversed=water.strokes.map((s,i)=>({
   index:i,samples:s.median.slice().reverse().map(([x,y])=>({x,y}))
 }));
 assert.notEqual(Matcher.evaluate(water,reversed).status,'consistent',
   'Reversed and displaced source strokes must not be confidently accepted');
});

test('P2.2a exact PDF input medians across all 201 source glyphs never yield false swapped-order result',()=>{
 assert.equal(pack.glyphs.length,201);
 let consistent=0,totalStrokes=0;
 for(const glyph of pack.glyphs){
   const result=Matcher.evaluate(glyph,recordedFromGlyph(glyph));
   assert.ok(['consistent','uncertain'].includes(result.status),
     'Exact canonical trajectory must not be called reversed: '+glyph.character+
       ' '+JSON.stringify(result));
   consistent+=result.status==='consistent';
   totalStrokes+=glyph.strokes.length;
 }
 assert.equal(totalStrokes,1045);
 assert.equal(consistent,201,
   'Source-perfect strokes should all be confidently matched in a self-consistency oracle');
});

test('P2.2a snapshot recovery validates raw source and imports old P2.1c records without fabricating verification',()=>{
 const old=new Legacy.PracticeProgress(identity);
 for(let i=0;i<2;i++)assert.equal(
   old.accept(draftFromMedian(water.strokes[i].median,i*10)).ok,true);
 const previous=old.snapshot();
 const c=new Whole.WholeWriting(identity);
 assert.equal(c.restore(previous),true);
 assert.equal(c.currentIndex,2);
 assert.equal(c.legacyImported,true);
 assert.equal(c.getWritten()[0].status,'raw-captured');
 c.append(draftFromMedian(water.strokes[2].median,150));
 const snapshot=c.snapshot();
 assert.equal(snapshot.schemaVersion,2);
 assert.equal(snapshot.legacyImported,true);
 const reopened=new Whole.WholeWriting(identity);
 assert.equal(reopened.restore(JSON.parse(JSON.stringify(snapshot))),true);
 assert.equal(reopened.currentIndex,3);
 assert.equal(reopened.legacyImported,true);
 const before=JSON.stringify(reopened.snapshot());
 const tryBad=mutate=>{
   const x=JSON.parse(JSON.stringify(snapshot));mutate(x);
   assert.equal(reopened.restore(x),false);
   assert.equal(JSON.stringify(reopened.snapshot()),before);
 };
 tryBad(x=>{x.sourceHash='f'.repeat(64)});
 tryBad(x=>{x.glyphId=99});
 tryBad(x=>{x.written[0].index=2});
 tryBad(x=>{x.written[1].status='userConfirmed'});
 tryBad(x=>{x.written[1].samples[0].x=-10});
 tryBad(x=>{x.schemaVersion=5});
 reopened.restart();
 assert.equal(reopened.legacyImported,false);
});

test('P2.2a local storage accepts schema v2 but retains P2.1c v1 read compatibility',async()=>{
 const s=new Storage.LocalPracticeStore({dbName:'no-indexeddb-unit'});
 const whole=new Whole.WholeWriting(identity);
 whole.append(draftFromMedian(water.strokes[0].median));
 assert.equal(whole.snapshot().schemaVersion,2);
 await assert.rejects(s.save(whole.snapshot()),/IndexedDB unavailable/);
 await assert.rejects(s.save({schemaVersion:2,...identity,revision:1}),
   /Refuse to save unversioned/);
 assert.ok(Storage.makeKey(identity).includes('77'));
});

test('P2.2a HTML has no per-stroke confirmation and preserves read-only source/UI contracts',()=>{
 const html=fs.readFileSync(path.join(ROOT,'animation/book.html'),'utf8');
 const bridge=fs.readFileSync(path.join(ROOT,'animation/practice/practice-bridge.js'),'utf8');
 assert.doesNotMatch(html,/id="practiceAccept"/);
 assert.doesNotMatch(html,/确认这一笔/);
 for(const removed of ['practiceClearPrompt','practiceClearYes','practiceClearNo']){
   assert.doesNotMatch(html,new RegExp('id="'+removed+'"'),
     'No confirmation UI for immediate whole-character restart');
 }
 assert.match(bridge,/restart\.addEventListener\('click',restartAll\)/);
 assert.doesNotMatch(bridge,/requestRestart\s*\(/);
 assert.match(html,/id="practiceOrderResult"/);
 assert.match(html,/src="\.\/practice\/order-check\.js"/);
 assert.match(html,/src="\.\/practice\/whole-progress\.js"/);
 assert.match(bridge,/progress\.append\(session\.draft\)/);
 assert.match(bridge,/onInputChanged/);
 assert.match(bridge,/input\.reset\(\)/);
 assert.match(bridge,/Matcher\.evaluate/);
 assert.match(bridge,/localOnlyPersistence:true,continuousWriting:true/);
 assert.doesNotMatch(bridge,/\bXMLHttpRequest\b|\bfetch\s*\(/);
});