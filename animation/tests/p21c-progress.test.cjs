'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');
const Progress=require('../practice/progress-controller.js');
const Storage=require('../practice/storage.js');
const {TraceSession}=require('../practice/trace-session.js');
const H='a'.repeat(64),P='b'.repeat(64);
const src={glyphId:77,strokeCount:4,sourceHash:H,pdfHash:P};
const penPoint=(x,y,timeStamp)=>({x,y,timeStamp,pressure:.62,tiltX:9,tiltY:-5});
function makeDraft(seed=0,type='pen'){
  const session=new TraceSession();
  const make=(x,y,t)=>type==='pen'?penPoint(x,y,t):
    {x,y,timeStamp:t,pressure:.5,tiltX:0,tiltY:0};
  assert.ok(session.begin(seed+1,type,make(seed+120,seed+300,100)));
  assert.ok(session.append(seed+1,make(seed+175,seed+285,110)));
  assert.ok(session.end(seed+1,make(seed+235,seed+245,120)));
  return session.draft;
}
test('P2.1c real drafts advance exactly one canonical stroke only on explicit confirm',()=>{
 const c=new Progress.PracticeProgress(src);
 assert.equal(c.currentIndex,0);
 assert.equal(c.accept(null).ok,false);
 for(let i=0;i<4;i++){
   const d=makeDraft(i*12);
   const old=JSON.stringify(d);
   const res=c.accept(d);
   assert.equal(res.ok,true);
   assert.equal(res.index,i);
   assert.equal(c.currentIndex,i+1);
   assert.equal(c.complete,i===3);
   assert.equal(JSON.stringify(d),old,'Raw trace must remain unmodified');
   assert.equal(c.getAccepted()[i].samples.length,3);
   assert.equal(c.getAccepted()[i].index,i);
   assert.equal(c.getAccepted()[i].status,'userConfirmed');
 }
 assert.equal(c.getState().acceptedStrokes,4);
 assert.equal(c.accept(makeDraft()).reason,'already-completed');
 assert.equal(c.undo(),true);
 assert.equal(c.currentIndex,3);
 assert.equal(c.complete,false);
 assert.equal(c.accept(makeDraft(99)).ok,true);
 assert.equal(c.complete,true);
 assert.equal(c.restart(),true);
 assert.equal(c.currentIndex,0);
 assert.equal(c.complete,false);
 assert.equal(c.undo(),false);
});
test('P2.1c reject taps, truncated traces, wrong order and impossible raw points',()=>{
 const c=new Progress.PracticeProgress(src);
 const original=makeDraft();
 assert.equal(Progress.validSamples(original.samples,'pen'),true);
 const copy={...original,samples:original.samples.map(x=>({...x}))};
 copy.samples[1].x=copy.samples[0].x;
 copy.samples[1].y=copy.samples[0].y;
 copy.samples[2].x=copy.samples[0].x;
 copy.samples[2].y=copy.samples[0].y;
 assert.equal(c.accept(copy).ok,false,'Zero-distance trail must not be accepted');
 assert.equal(c.accept({...original,droppedSamples:1}).ok,false);
 assert.equal(c.accept({...original,status:'skipped'}).ok,false);
 assert.equal(c.accept({...original,samples:[original.samples[0]]}).ok,false);
 assert.equal(c.accept({...original,samples:original.samples.map(p=>({...p,x:Infinity}))}).ok,false);
 assert.equal(c.accept({...original,samples:original.samples.map(p=>({...p,tMs:-1}))}).ok,false);
 assert.equal(c.accept({...original,samples:original.samples.map(p=>({...p,pressureSource:'synthetic'}))}).ok,false);
 assert.equal(c.currentIndex,0);
 assert.equal(c.getAccepted().length,0);
});
test('P2.1c checkpoint restores whole source-locked handwriting or none',()=>{
 const old=new Progress.PracticeProgress(src);
 old.accept(makeDraft(0));
 old.accept(makeDraft(9,'touch'));
 const snapshot=old.snapshot();
 const restored=new Progress.PracticeProgress(src);
 assert.equal(restored.restore(JSON.parse(JSON.stringify(snapshot))),true);
 assert.equal(restored.currentIndex,2);
 assert.equal(restored.getAccepted()[1].pointerType,'touch');
 assert.equal(restored.getAccepted()[1].samples[0].pressure,null);
 const tamper=mutate=>{
   const copy=JSON.parse(JSON.stringify(snapshot));
   mutate(copy);
   const current=JSON.stringify(restored.snapshot());
   assert.equal(restored.restore(copy),false);
   assert.equal(JSON.stringify(restored.snapshot()),current,
     'Invalid checkpoint must not partially overwrite good data');
 };
 tamper(x=>{x.sourceHash='f'.repeat(64);});
 tamper(x=>{x.pdfHash='f'.repeat(64);});
 tamper(x=>{x.glyphId=78;});
 tamper(x=>{x.strokeCount=3;});
 tamper(x=>{x.schemaVersion=2;});
 tamper(x=>{x.revision=1;});
 tamper(x=>{x.accepted[1].index=2;});
 tamper(x=>{x.accepted[0].status='automatic';});
 tamper(x=>{x.accepted[1].samples[1].x=2048;});
 tamper(x=>{x.accepted[1].samples[1].pressure=.5;});
 tamper(x=>{x.accepted[0].samples[1].tMs=-22;});
 tamper(x=>{x.accepted[0].samples=[];});
 tamper(x=>{x.accepted.push(snapshot.accepted[0],snapshot.accepted[0],snapshot.accepted[0]);});
 assert.equal(restored.getAccepted().length,2);
 const untouched=old.snapshot();
 untouched.accepted[0].samples[0].x=999;
 assert.notEqual(old.getAccepted()[0].samples[0].x,999);
 assert.equal(Object.isFrozen(old.getAccepted()[0].samples[0]),true);
});
test('P2.1c storage key partitions PDF revisions / glyphs, no cloud fallback',async()=>{
 const a=Storage.makeKey(src),b=Storage.makeKey({...src,glyphId:78});
 assert.notEqual(a,b);
 assert.notEqual(a,Storage.makeKey({...src,sourceHash:'c'.repeat(64)}));
 assert.notEqual(a,Storage.makeKey({...src,pdfHash:'d'.repeat(64)}));
 assert.throws(()=>Storage.makeKey({...src,pdfHash:'unknown'}),/source-locked/);
 const repo=new Storage.LocalPracticeStore({dbName:'test-no-browser'});
 await assert.rejects(repo.load(src),/IndexedDB unavailable/);
 await assert.rejects(repo.save(new Progress.PracticeProgress(src).snapshot()),/IndexedDB unavailable/);
 await assert.rejects(repo.remove(src),/IndexedDB unavailable/);
 const code=fs.readFileSync(path.join(ROOT,'animation/practice/storage.js'),'utf8');
 assert.doesNotMatch(code,/\bXMLHttpRequest\b|\bfetch\s*\(/);
 assert.doesNotMatch(code,/\blocalStorage\b/);
 assert.match(code,/this\.queue=result/);
});
test('P2.1c UI carries manual confirmation, safe exit, undo and no teacher scoring',()=>{
 const html=fs.readFileSync(path.join(ROOT,'animation/book.html'),'utf8');
 const bridge=fs.readFileSync(path.join(ROOT,'animation/practice/practice-bridge.js'),'utf8');
 const canvas=fs.readFileSync(path.join(ROOT,'animation/practice/trace-canvas.js'),'utf8');
 for(const name of ['practiceAccept','practiceUndo','practiceRestart',
   'practiceClearPrompt','practiceClearYes','practiceClearNo',
   'practiceLeavePrompt','practiceLeaveYes','practiceLeaveNo',
   'practiceSaved','practiceCompletion','practiceReturnCurrent']){
   assert.equal([...html.matchAll(new RegExp('id="'+name+'"','g'))].length,1,name);
 }
 for(const script of ['progress-controller.js','storage.js'])
   assert.ok(html.includes('src="./practice/'+script+'"'));
 assert.match(bridge,/progress\.accept\(session\?\.draft\)/);
 assert.match(bridge,/store\.save\(captured\)/);
 assert.match(bridge,/store\.load\(identity\(\)\)/);
 assert.match(bridge,/store\.remove\(identity\(\)\)/);
 assert.match(bridge,/noAutomaticScore:true,noPersistentWritingStorage:false/);
 assert.match(canvas,/getConfirmed/);
 assert.match(canvas,/for\(const stroke of confirmed\)/);
 assert.doesNotMatch(bridge,/XMLHttpRequest|\bfetch\s*\(/);
});
