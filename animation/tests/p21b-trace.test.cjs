'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');
const {TraceSession,normalizePoint,SOURCE_BOUNDS}=
  require('../practice/trace-session.js');
const {sampleEvents,PointerInput}=require('../practice/pointer-input.js');
const {TraceCanvas}=require('../practice/trace-canvas.js');
const html=fs.readFileSync(path.join(ROOT,'animation/book.html'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'animation/practice/practice.css'),'utf8');
const bridge=fs.readFileSync(path.join(ROOT,'animation/practice/practice-bridge.js'),'utf8');
const source=require('../practice/reference-stage.js');
const sample=(x,y,timeStamp,pressure=.5,tiltX=0,tiltY=0)=>
  ({x,y,timeStamp,pressure,tiltX,tiltY});

test('P2.1b raw source coordinates keep real positions, clock and pen provenance',()=>{
 assert.deepEqual(SOURCE_BOUNDS,{minX:0,maxX:1024,minY:-124,maxY:900});
 const t=new TraceSession();
 assert.equal(t.begin(14,'pen',sample(100,200,101.5,.22,12,-8)),true);
 assert.equal(t.begin(15,'touch',sample(1,1,101.6)),false,
   'Second finger cannot become an active brush');
 assert.equal(t.append(15,sample(500,500,105)),false);
 assert.equal(t.append(14,sample(110,210,110,.65,20,-10)),true);
 assert.equal(t.append(14,sample(120,220,110,.7,21,-12)),true,
   'Distinct coalesced positions at same timestamp must not disappear');
 assert.equal(t.append(14,sample(120,220,110,.7,21,-12)),false,
   'Exact duplicate point/time should not be stored twice');
 assert.equal(t.end(14,sample(130,230,117,.8,22,-11)),true);
 const points=t.getSamples();
 assert.equal(t.getState().phase,'review');
 assert.equal(t.getState().pointCount,4);
 assert.deepEqual(points.map(p=>p.tMs),[0,8.5,8.5,15.5]);
 assert.deepEqual(points.map(p=>[p.x,p.y]),[
   [100,200],[110,210],[120,220],[130,230]]);
 assert.equal(points[0].pressure,.22);
 assert.equal(points[0].pressureSource,'device-reported-unverified');
 assert.equal(points[0].tiltX,12);
 assert.equal(t.draft.status,'draft-not-accepted');
 assert.equal(t.draft.schemaVersion,1);
 assert.equal(Object.isFrozen(t.draft.samples[0]),true);
 assert.equal(t.getState().acceptedStrokes,0);
 assert.equal(t.begin(16,'touch',sample(300,300,125)),false,
   'Draft cannot silently get replaced before explicit reset');
 assert.equal(t.reset(),true);
 assert.equal(t.getState().phase,'ready');
 assert.equal(t.getSamples().length,0);
});

test('P2.1b cancel, lost capture, visibility and resize never accept ghost ink',()=>{
 const t=new TraceSession();
 assert.equal(t.begin(4,'touch',sample(10,10,500)),true);
 assert.equal(t.append(4,sample(11,11,510)),true);
 assert.equal(t.cancel(5,'other-pointer'),false);
 assert.equal(t.cancel(4,'pointercancel'),true);
 assert.equal(t.cancel(4,'lostpointercapture'),false,'Cancellation must be idempotent');
 assert.equal(t.getState().acceptedStrokes,0);
 assert.equal(t.getState().pointCount,0);
 assert.equal(t.getState().cancellations,1);
 assert.equal(t.getState().phase,'ready');
 assert.equal(t.begin(6,'mouse',sample(50,51,560)),true);
 assert.equal(t.cancel(6,'orientationchange'),true);
 assert.equal(t.getState().acceptedStrokes,0);
 assert.equal(t.getState().cancellations,2);
 assert.equal(t.draft,null);
});

test('P2.1b raw time, SVG bounds, fake pressure and sample cap are fail-safe',()=>{
 const t=new TraceSession({maxPoints:3});
 assert.equal(t.begin(1,'touch',sample(-50,1000,2000)),true);
 assert.equal(t.append(1,sample(1024,900,2004)),true);
 assert.equal(t.append(1,sample(900,0,2007)),true);
 assert.equal(t.append(1,sample(800,0,2010)),false);
 assert.equal(t.end(1,sample(700,0,2014)),true);
 assert.equal(t.draft.droppedSamples,2);
 assert.equal(t.draft.samples.length,3);
 assert.deepEqual([t.draft.samples[0].x,t.draft.samples[0].y],[0,900]);
 assert.equal(t.draft.samples[0].pressure,null,
   'Touch generic 0.5 must not be passed off as measured pen pressure');
 assert.equal(t.draft.samples[0].pressureSource,null);
 const p=normalizePoint(sample(200,0,55),50,0,'mouse');
 assert.equal(p.pressure,null);
 assert.equal(p.tiltX,null);
 assert.throws(()=>normalizePoint(sample(NaN,50,60),0,0,'pen'),/Nonfinite/);
 assert.throws(()=>new TraceSession({maxPoints:1}),/size limit/);
});

test('P2.1b coalesced pointer samples maintain event order and current endpoint',()=>{
 const mk=(timeStamp,x,id=9)=>({pointerId:id,timeStamp,clientX:x});
 const ev={pointerId:9,timeStamp:300,clientX:3,
   getCoalescedEvents:()=>[mk(299,2),mk(297,1),mk(301,4),mk(300,3,99)]};
 assert.deepEqual(sampleEvents(ev,true).map(v=>v.clientX),[1,2,3,4]);
 assert.deepEqual(sampleEvents(ev,false).map(v=>v.clientX),[3]);
 assert.equal(sampleEvents({...ev,getCoalescedEvents:()=>{throw Error('unsupported');}},true).length,1);
 assert.equal(typeof PointerInput,'function');
 assert.equal(typeof TraceCanvas,'function');
});

test('P2.1b browser and source stay separated with no remote/cloud persistence',()=>{
 assert.equal(source.SOURCE_TRANSFORM,'translate(0 900) scale(1 -1)');
 assert.match(html,/<canvas id="practiceInk" aria-label=/);
 assert.match(html,/src="\.\/practice\/trace-session\.js"/);
 assert.match(html,/src="\.\/practice\/pointer-input\.js"/);
 assert.match(html,/src="\.\/practice\/trace-canvas\.js"/);
 assert.match(html,/id="practiceReset"/);
 assert.match(css,/#practiceInk\{[^}]*touch-action:none/);
 assert.doesNotMatch(css,/body\{[^}]*touch-action:none/);
 assert.match(bridge,/new Trace\.TraceSession\(\)/);
 assert.match(bridge,/new Ink\.TraceCanvas\(surface,stage\.group/);
 assert.match(bridge,/new Input\.PointerInput\(/);
 assert.match(bridge,/noAutomaticScore:true,noPersistentWritingStorage:true/);
 for(const f of ['trace-session.js','trace-canvas.js','pointer-input.js','practice-bridge.js']){
   const src=fs.readFileSync(path.join(ROOT,'animation/practice',f),'utf8');
   const executable=src.replace(/\/\*[\s\S]*?\*\//g,'')
     .replace(/^\s*\/\/.*$/gm,'');
   assert.doesNotMatch(executable,/\bfetch\s*\(|\bindexedDB\b|\blocalStorage\b|XMLHttpRequest/i);
 }
});
