/* P2.1b: genuine Chromium CDP Input.dispatchTouchEvent, not synthetic DOM events.
 * Node22 built-ins only. All endpoints are localhost; no runtime dependency.
 */
import {spawn} from 'node:child_process';
import {mkdtempSync,readFileSync,existsSync,rmSync,writeFileSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
const chromeBin=process.env.CHROME_BIN;
const target=process.env.P22H_TARGET||'http://127.0.0.1:18794/animation/book.html?id=77';
if(!chromeBin)throw Error('CHROME_BIN is required for real CDP input test');
const profile=mkdtempSync(join(tmpdir(),'zitie-p22h-edgios-cdp-'));
const EDGE_UA='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 EdgiOS/140.0.0.0';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const check=(v,msg)=>{if(!v)throw Error(msg);};
const browser=spawn(chromeBin,[
 '--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu',
 '--no-first-run','--remote-debugging-port=0','--remote-allow-origins=*',
 '--user-data-dir='+profile,'--window-size=440,920',
 '--user-agent='+EDGE_UA,target
],{stdio:'ignore'});
let ws=null,seq=0;
const pending=new Map();
async function until(fn){
 for(let n=0;n<120;n++){
  try{const value=await fn();if(value)return value;}catch(_){}
  await sleep(120);
 }
 throw Error('CDP readiness timeout');
}
async function connect(){
 const port=await until(()=>existsSync(join(profile,'DevToolsActivePort'))?
  Number(readFileSync(join(profile,'DevToolsActivePort'),'utf8').split('\n')[0]):null);
 const page=await until(async()=>{
  const response=await fetch('http://127.0.0.1:'+port+'/json/list');
  const list=await response.json();
  return list.find(x=>x.type==='page'&&x.webSocketDebuggerUrl);
 });
 ws=new WebSocket(page.webSocketDebuggerUrl);
 await new Promise((yes,no)=>{
  const timeout=setTimeout(()=>no(Error('WebSocket connection timeout')),12000);
  ws.addEventListener('open',()=>{clearTimeout(timeout);yes();},{once:true});
  ws.addEventListener('error',e=>{clearTimeout(timeout);no(e);},{once:true});
 });
 ws.addEventListener('message',event=>{
  let v;try{v=JSON.parse(String(event.data));}catch(_){return;}
  const item=pending.get(v.id);
  if(!item)return;
  clearTimeout(item.timer);pending.delete(v.id);
  if(v.error)item.reject(Error(JSON.stringify(v.error)));
  else item.resolve(v.result);
 });
}
function call(method,params={}){
 return new Promise((resolve,reject)=>{
  const id=++seq;
  const timer=setTimeout(()=>{
   pending.delete(id);reject(Error('CDP '+method+' timed out'));
  },20000);
  pending.set(id,{resolve,reject,timer});
  ws.send(JSON.stringify({id,method,params}));
 });
}
async function onPage(fn){
 const result=await call('Runtime.evaluate',{
  expression:'('+fn.toString()+')()',returnByValue:true,awaitPromise:true
 });
 if(result.exceptionDetails)
  throw Error('Browser evaluate: '+JSON.stringify(result.exceptionDetails));
 return result.result.value;
}
const touch=(type,points)=>call('Input.dispatchTouchEvent',{
 type,touchPoints:points.map(p=>({id:p.id??1,x:p.x,y:p.y,
  radiusX:3,radiusY:3,force:.6}))
});
try{
 await connect();
 await call('Page.enable');
 await call('Runtime.enable');
 await call('Emulation.setDeviceMetricsOverride',{
  width:390,height:844,deviceScaleFactor:3,mobile:true});
 await call('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:2});
 await until(()=>onPage(()=>document.documentElement.dataset.p22aReady===
   'whole-word-v1'&&window.ZITIE_A3_BOOK?.pack?.glyphs.length===201));
 const initial=await onPage(async()=>{
  const p=window.ZITIE_P22A,b=window.ZITIE_A3_BOOK;
  if(!navigator.userAgent.includes('EdgiOS/'))
   throw Error('Requested Edge iOS UA not applied');
  b.selectGlyph(77);
  if(!p.open())throw Error('Cannot open source practice');
  await p.whenReady();
  const x=p.getState();
  const g=document.querySelector('[data-practice-source-transform]');
  const median=b.getGlyph().strokes[0].median;
  const m=g.getScreenCTM();
  const path=median.map(([x,y])=>({
   x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f,id:1
  }));
  return {path,ready:x.ready,mode:x.input.edgeIOSNativeTouch,
   source:b.getGlyph().source_sha256,style:b.getPressureStyle(),
   sourcePoints:b.getGlyph().strokes.length};
 });
 check(initial.ready&&initial.mode&&initial.sourcePoints===4&&
  initial.path.length>=2,'EdgiOS fallback did not initialize: '+JSON.stringify(initial));
 await touch('touchStart',[initial.path[0]]);
 const began=await onPage(()=>{
  const s=ZITIE_P22A.getState().input;
  return {phase:s.phase,source:s.inputSource,fallback:s.touchFallbackStarts,
   handoffs:s.touchHandoffs,pointerStarts:s.edgePointerFallbackStarts};
 });
 check(began.phase==='drawing'&&began.source==='touch'&&
  began.fallback+began.handoffs===1,
  'Native CDP Edge touch never started: '+JSON.stringify(began));
 // The address bar may resize the visual viewport; unchanged drawing surface
 // geometry should not cancel this real touch.
 const sameResize=await onPage(()=>{
  window.dispatchEvent(new Event('resize'));
  return ZITIE_P22A.getState().input.phase;
 });
 check(sameResize==='drawing','Browser-toolbar resize canceled active Edge touch');
 for(const pt of initial.path.slice(1))await touch('touchMove',[pt]);
 await touch('touchEnd',[]);
 await sleep(120);
 const result=await onPage(async()=>{
  const p=ZITIE_P22A;await p.whenSaved();
  const s=p.getState(),written=p.getWritten();
  const ink=document.getElementById('practiceInk'),group=
    document.querySelector('[data-practice-source-transform]');
  const t=written[0]?.samples[0];
  const m=group.getScreenCTM(),pt={x:m.a*t.x+m.c*t.y+m.e,
    y:m.b*t.x+m.d*t.y+m.f};
  const r=ink.getBoundingClientRect();
  const x=Math.max(0,Math.min(ink.width-1,Math.round(
    (pt.x-r.left)*ink.width/r.width)));
  const y=Math.max(0,Math.min(ink.height-1,Math.round(
    (pt.y-r.top)*ink.height/r.height)));
  const px=ink.getContext('2d').getImageData(x,y,1,1).data;
  return {written:s.progress.writtenStrokes,save:s.saveStatus,
   sampleCount:written[0]?.samples.length,pointerType:written[0]?.pointerType,
   inputSource:s.input.inputSource,phase:s.input.phase,
   blue:px[2]>px[0]+65&&px[2]>px[1]+30&&px[3]>80,
   actualInk:p.getInkMetrics().confirmedStrokes,
   sourceHash:ZITIE_A3_BOOK.getGlyph().source_sha256,
   noCapture:s.input.captureFailures===0};
 });
 check(result.written===1&&result.sampleCount>=2&&
  result.pointerType==='touch'&&result.phase==='ready'&&result.blue&&
  result.actualInk===1&&result.sourceHash===initial.source,
  'Native Edge UA finger did not create one real blue stroke: '+JSON.stringify(result));
 const second=await onPage(()=>{
  const g=document.querySelector('[data-practice-source-transform]');
  const src=ZITIE_A3_BOOK.getGlyph().strokes[1].median;
  const m=g.getScreenCTM();
  return src.map(([x,y])=>({x:m.a*x+m.c*y+m.e,
     y:m.b*x+m.d*y+m.f,id:1}));
 });
 await touch('touchStart',[second[0]]);
 await touch('touchMove',[second[1]]);
 await touch('touchCancel',[]);
 const canceled=await onPage(()=>{
  const p=ZITIE_P22A,s=p.getState();
  return {written:s.progress.writtenStrokes,phase:s.input.phase,
   cancel:s.input.lastCancel,blue:p.getInkMetrics().confirmedStrokes};
 });
 check(canceled.written===1&&canceled.phase==='ready'&&
  canceled.cancel==='touchcancel'&&canceled.blue===1,
  'Canceled real touch incorrectly committed ghost stroke: '+JSON.stringify(canceled));
 // Integration check: the EdgiOS UA may emit ONLY Pointer Events (no
 // Touch Events). These synthetic DOM PointerEvents test that code path,
 // while the preceding CDP touch test uses genuine native touch injection.
 const pointerOnly=await onPage(async()=>{
  const practice=ZITIE_P22A,book=ZITIE_A3_BOOK;
  if(!practice.restart())throw Error('Cannot reset after native touch QA');
  await practice.whenSaved();
  const countersBefore=practice.getState().input;
  const g=document.querySelector('[data-practice-source-transform]');
  const m=g.getScreenCTM(),canvas=document.getElementById('practiceInk');
  const pts=book.getGlyph().strokes[0].median.map(([x,y])=>({
   x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f
  }));
  const dispatch=(type,pt)=>canvas.dispatchEvent(new PointerEvent(type,{
   bubbles:true,cancelable:true,pointerType:'touch',pointerId:922,
   isPrimary:true,button:0,clientX:pt.x,clientY:pt.y
  }));
  dispatch('pointerdown',pts[0]);
  for(const pt of pts.slice(1))dispatch('pointermove',pt);
  dispatch('pointerup',pts.at(-1));
  await practice.whenSaved();
  const s=practice.getState(),written=practice.getWritten();
  return {written:s.progress.writtenStrokes,
   starts:s.input.edgePointerFallbackStarts-
     countersBefore.edgePointerFallbackStarts,
   handoffs:s.input.touchHandoffs-countersBefore.touchHandoffs,
   samples:written[0]?.samples.length,
   ink:practice.getInkMetrics().confirmedStrokes};
 });
 check(pointerOnly.written===1&&pointerOnly.ink===1&&
  pointerOnly.samples>=2&&pointerOnly.starts>=1&&
  pointerOnly.handoffs===0,
  'EdgiOS pointer-only channel was silently discarded: '+
    JSON.stringify(pointerOnly));
 // Simulate Edge InPrivate/blocked IndexedDB *without fake pen data*. The
 // loader must report no persistence but keep the drawing Canvas usable.
 const failedStorage=await onPage(async()=>{
  const p=ZITIE_P22A;
  if(!p.close())throw Error('Could not close initial successful session');
  ZitiePracticeLocalStore.LocalPracticeStore.prototype.loadWithTimeout=
    ()=>Promise.reject(Error('Storage blocked by WebView'));
  if(!p.open())throw Error('Cannot reopen unsaved practice');
  await p.whenReady();
  const s=p.getState();
  return {ready:s.ready,storageUsable:s.storageUsable,
    message:document.getElementById('practiceSaved').textContent,
    written:s.progress.writtenStrokes};
 });
 check(failedStorage.ready&&!failedStorage.storageUsable&&
  failedStorage.written===0&&
  failedStorage.message.includes('本地存储受限'),
  'Blocked local storage prevented honest in-memory drawing: '+
    JSON.stringify(failedStorage));
 const result2=await onPage(()=>{
  const p=ZITIE_P22A,b=ZITIE_A3_BOOK;
  return {pack:b.pack.glyphs.length,strokes:b.pack.glyphs.reduce((n,g)=>
   n+g.strokes.length,0),readOnly:b.player.frontGuard===true,
   noUserUploads:!document.querySelector('form[action]')};
 });
 check(result2.pack===201&&result2.strokes===1045&&result2.readOnly,
  'Edge compatible input touched original PDF source');
 const metrics={result:'PASS',input:'CDP Input.dispatchTouchEvent',
  browserSimulation:'EdgiOS UA on Chromium, NOT physical iPhone Edge',
  nativeSingleTouch:true,preferredTouchWithoutDuplicates:true,
  toolbarResizeSurvived:true,canceledStrokeNotCommitted:true,
  blockedIndexedDBFailsOpen:true,actualBlueInk:true,
  pointerOnlyFallbackRecovered:true,
  sourceReadOnly:true,sourceCount:201,strokeCount:1045,
  initial,began,firstStroke:result,canceled,pointerOnly,failedStorage};
 mkdirSync(resolve('build/a1'),{recursive:true});
 writeFileSync(resolve('build/a1/p22h-edgios-touch-metrics.json'),
  JSON.stringify(metrics,null,2)+'\n');
 process.stdout.write('PASS P2.2h EdgiOS emulated CDP native touch: '+
  JSON.stringify(metrics)+'\n');
}finally{
 for(const item of pending.values())clearTimeout(item.timer);
 try{ws?.close();}catch(_){}
 browser.kill('SIGTERM');await sleep(130);
 try{rmSync(profile,{recursive:true,force:true});}catch(_){}
}
