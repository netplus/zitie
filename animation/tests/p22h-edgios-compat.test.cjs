'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {sourcePoint,edgeIOSPreferredTouch,PointerInput,geometryChanged}=
  require('../practice/pointer-input.js');
const {TraceSession}=require('../practice/trace-session.js');
const {LocalPracticeStore}=require('../practice/storage.js');

test('P2.2h: invert SVG source CTM exactly without DOMPoint/WebKit-only APIs',()=>{
 const old=global.DOMPoint;
 try{
  global.DOMPoint=undefined;
  const group={getScreenCTM:()=>({a:0,b:2,c:-2,d:0,e:300,f:400})};
  const p=sourcePoint({clientX:282,clientY:410,timeStamp:40,
    pressure:undefined},group);
  assert.ok(Math.abs(p.x-5)<1e-9&&Math.abs(p.y-9)<1e-9);
  assert.equal(p.timeStamp,40);
  assert.throws(()=>sourcePoint({clientX:1,clientY:1,timeStamp:9},{
    getScreenCTM:()=>({a:1,b:2,c:2,d:4,e:0,f:0})}),/Singular/);
  assert.throws(()=>sourcePoint({clientX:NaN,clientY:10,timeStamp:9},group),
    /Invalid/);
 }finally{global.DOMPoint=old;}
});

test('P2.2h: Edge iOS touch preference is scoped (Safari, CriOS, Edge Android excluded)',()=>{
 assert.equal(edgeIOSPreferredTouch(
   'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) EdgiOS/140.0',true),true);
 assert.equal(edgeIOSPreferredTouch('Mozilla/5.0 (iPhone) CriOS/140.0',true),false);
 assert.equal(edgeIOSPreferredTouch('Mozilla/5.0 (iPhone) Version/18.0 Safari',true),false);
 assert.equal(edgeIOSPreferredTouch('Mozilla/5.0 (Android) EdgA/140.0',true),false);
 assert.equal(edgeIOSPreferredTouch('Mozilla/5.0 (iPad) EdgiOS/140.0',false),false);
});
function fixture(preferTouchInput){
 const w=global.window,d=global.document;
 const hooks=[],pressed=new Set();
 global.window={TouchEvent:class TouchEvent{},
  addEventListener:(name,handler)=>hooks.push(['window',name,handler]),
  removeEventListener:()=>{}};
 global.document={visibilityState:'visible',addEventListener:()=>{},
  removeEventListener:()=>{}};

 let rect={left:0,top:0,right:300,bottom:300,width:300,height:300};
 let changes=[],layoutCalls=0;
 const surface={
  addEventListener:(name,handler)=>hooks.push(['surface',name,handler]),
  removeEventListener:()=>{},
  getBoundingClientRect:()=>rect,
  setPointerCapture:id=>pressed.add(id),
  releasePointerCapture:id=>pressed.delete(id),
  hasPointerCapture:id=>pressed.has(id)
 };
 const session=new TraceSession();
 const group={getScreenCTM:()=>({a:1,b:0,c:0,d:1,e:0,f:0})};
 const input=new PointerInput({surface,group,session,preferTouchInput,
  onChange:x=>changes.push(x),onLayout:()=>layoutCalls++});
 const restore=()=>{input.destroy();global.window=w;global.document=d;};
 const ev=(identifier,x,y,timeStamp,type='single')=>({
  touches:type==='multi'?[{identifier},{identifier:identifier+1}]:
    [{identifier}],
  changedTouches:[{identifier,clientX:x,clientY:y}],
  timeStamp,cancelable:true,
  prevented:false,preventDefault(){this.prevented=true;}
 });
 const pe=(type,x,y,timeStamp,id=8)=>({pointerType:type,pointerId:id,
  clientX:x,clientY:y,timeStamp,isPrimary:true,button:0,cancelable:true,
  preventDefault(){}});
 return {input,session,hooks,ev,pe,pressed,changes,restore,
  resize:(next)=>{rect=next;input.onResize();},
  layout:()=>layoutCalls};
}
test('P2.2h: Edge preferred native touch records one stroke and rejects duplicate pointer events',()=>{
 const f=fixture(true);
 try{
  assert.ok(f.hooks.some(([at,name])=>at==='surface'&&name==='touchstart'));
  assert.ok(f.hooks.some(([at,name])=>at==='window'&&name==='touchmove'));
  f.input.down(f.pe('touch',10,12,100,8));
  assert.equal(f.session.active,null,'Edge touch PointerEvent should not preempt Touch Events');
  const start=f.ev(1,10,12,102);
  f.input.touchStart(start);assert.ok(start.prevented);
  assert.equal(f.session.active.pointerType,'touch');
  f.input.move(f.pe('touch',15,16,108,8)); // duplicate pointer ignored
  const move=f.ev(1,20,24,114);f.input.touchMove(move);
  assert.ok(move.prevented);
  f.input.up(f.pe('touch',20,24,116,8)); // duplicate pointerup ignored
  const end=f.ev(1,40,44,120);
  f.input.touchEnd(end);
  assert.ok(end.prevented);
  assert.ok(f.session.draft);
  assert.equal(f.session.draft.samples.length,3);
  assert.equal(f.session.draft.pointerType,'touch');
  assert.equal(f.session.draft.samples.at(-1).x,40);
  assert.equal(f.session.draft.samples.at(-1).pressure,null);
  assert.equal(f.input.getState().touchFallbackStarts,1);
  assert.deepEqual(f.changes,['down','move','up']);
 }finally{f.restore();}
});
test('P2.2h: Edge touch cancel, second finger and orientation never commit ghost ink',()=>{
 const f=fixture(true);
 try{
  f.input.touchStart(f.ev(4,10,10,20));
  f.input.touchMove(f.ev(4,30,30,35));
  f.input.touchCancel(f.ev(4,30,30,40));
  assert.equal(f.session.active,null);
  assert.equal(f.session.draft,null);
  assert.equal(f.input.getState().lastCancel,'touchcancel');
  f.input.touchStart(f.ev(4,10,10,100));
  f.input.touchStart(f.ev(5,20,20,110,'multi'));
  assert.equal(f.session.draft,null);
  assert.equal(f.input.getState().lastCancel,'multitouch');
  f.input.touchStart(f.ev(7,10,10,200));
  f.input.handlers.rotate();
  assert.equal(f.session.draft,null);
  assert.equal(f.input.getState().lastCancel,'orientationchange');
 }finally{f.restore();}
});
test('P2.2h: Safari pointer path remains authoritative; fallback can start if pointerdown absent',()=>{
 const f=fixture(false);
 try{
  f.input.down(f.pe('touch',10,10,10));
  assert.equal(f.input.getState().inputSource,'pointer');
  f.input.touchStart(f.ev(0,10,10,12));
  f.input.move(f.pe('touch',16,20,20));
  f.input.up(f.pe('touch',20,22,30));
  assert.equal(f.session.draft.samples.length,3);
  assert.equal(f.input.getState().touchFallbackStarts,0);
  f.input.reset();
  f.input.touchStart(f.ev(0,10,10,40));
  f.input.touchMove(f.ev(0,15,15,50));
  f.input.touchEnd(f.ev(0,20,20,60));
  assert.equal(f.session.draft.pointerType,'touch');
  assert.equal(f.input.getState().touchFallbackStarts,1);
 }finally{f.restore();}
});
test('P2.2h: viewport-only resize does not discard active touch; real desktop resize does',()=>{
 const e=fixture(true);
 try{
  e.input.touchStart(e.ev(1,10,10,100));
  e.resize({left:0,top:0,right:300,bottom:300,width:300,height:300});
  assert.equal(e.session.getState().phase,'drawing');
  e.resize({left:0,top:0,right:330,bottom:330,width:330,height:330});
  assert.equal(e.session.getState().phase,'drawing',
    'EdgiOS dynamic toolbar resize should not cancel real touch');
  assert.equal(e.layout(),2);
  e.input.touchEnd(e.ev(1,50,60,160));
  assert.equal(e.session.draft.samples.length,2);
 }finally{e.restore();}
 const ordinary=fixture(false);
 try{
  ordinary.input.down(ordinary.pe('pen',10,10,20));
  ordinary.resize({left:0,top:0,right:300,bottom:300,width:300,height:300});
  assert.equal(ordinary.session.getState().phase,'drawing');
  ordinary.resize({left:0,top:0,right:360,bottom:360,width:360,height:360});
  assert.equal(ordinary.session.getState().phase,'ready');
  assert.equal(ordinary.session.draft,null);
 }finally{ordinary.restore();}
});
test('P2.2h: pending IndexedDB read fails open rather than disabling the canvas forever',async()=>{
 const store=new LocalPracticeStore();
 store.load=()=>new Promise(()=>{}); // mimic indefinite WKWebView request
 await assert.rejects(store.loadWithTimeout({glyphId:1,pdfHash:'a'.repeat(64),
   sourceHash:'b'.repeat(64)},15),/timed out/);
 store.load=async()=>null;
 assert.equal(await store.loadWithTimeout({glyphId:1,pdfHash:'a'.repeat(64),
   sourceHash:'b'.repeat(64)},50),null);
});
