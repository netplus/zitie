/* P2.1b: genuine Chromium CDP Input.dispatchTouchEvent, not synthetic DOM events.
 * Node22 built-ins only. All endpoints are localhost; no runtime dependency.
 */
import {spawn} from 'node:child_process';
import {mkdtempSync,readFileSync,existsSync,rmSync,writeFileSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
const chromeBin=process.env.CHROME_BIN;
const target=process.env.P21B_TARGET||'http://127.0.0.1:18786/animation/book.html?id=77';
if(!chromeBin)throw Error('CHROME_BIN is required for real CDP input test');
const profile=mkdtempSync(join(tmpdir(),'zitie-p21b-cdp-'));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const check=(v,msg)=>{if(!v)throw Error(msg);};
const browser=spawn(chromeBin,[
 '--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu',
 '--no-first-run','--remote-debugging-port=0','--remote-allow-origins=*',
 '--user-data-dir='+profile,'--window-size=1290,990',target
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
 await call('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:2});
 await until(()=>onPage(()=>document.documentElement.dataset.p21bReady===
  'raw-pointer-canvas'&&ZITIE_A3_BOOK?.pack?.glyphs.length===201));
 const setup=await onPage(async()=>{
  const book=ZITIE_A3_BOOK;book.selectGlyph(77);
  if(!ZITIE_P21B.open())throw Error('Immersive practice refused to open');
  await ZITIE_P21B.whenReady();
  const group=document.querySelector('[data-practice-source-transform]');
  const canvas=document.getElementById('practiceInk');
  const median=book.getGlyph().strokes[0].median;
  const points=median.map(([x,y])=>{
   const pt=new DOMPoint(x,y).matrixTransform(group.getScreenCTM());
   return {x:pt.x,y:pt.y,id:1};
  });
  return {points,boardWidth:canvas.getBoundingClientRect().width,
   sourceHash:book.getGlyph().source_sha256};
 });
 check(setup.points.length>=2&&setup.boardWidth>=300,
  'No usable PDF-source touch path');
 await touch('touchStart',[setup.points[0]]);
 const capture=await onPage(()=>{
  const s=ZITIE_P21B.getState().input;
  return {phase:s.phase,pointerId:s.activePointerId,
   captureFailures:s.captureFailures,
   captured:document.getElementById('practiceInk').hasPointerCapture(
     s.activePointerId)};
 });
 check(capture.phase==='drawing'&&capture.captured&&
   capture.captureFailures===0,'True touch pointer capture failed: '+JSON.stringify(capture));
 for(const pt of setup.points.slice(1))await touch('touchMove',[pt]);
 await touch('touchEnd',[]);
 await sleep(100);
 const trace=await onPage(()=>{
  const p=ZITIE_P21B,c=document.getElementById('practiceInk');
  const g=document.querySelector('[data-practice-source-transform]');
  const points=p.getWritten()[0]?.samples||[];
  const blueAt=pt=>{
   const loc=new DOMPoint(pt.x,pt.y).matrixTransform(g.getScreenCTM());
   const r=c.getBoundingClientRect();
   const x=Math.max(0,Math.min(c.width-1,Math.round(
     (loc.x-r.left)*c.width/r.width)));
   const y=Math.max(0,Math.min(c.height-1,Math.round(
     (loc.y-r.top)*c.height/r.height)));
   const rgba=c.getContext('2d').getImageData(x,y,1,1).data;
   return rgba[2]>rgba[0]+65&&rgba[2]>rgba[1]+32&&rgba[3]>80;
  };
  return {phase:p.getState().input.phase,points:points.length,
   painted:p.getInkMetrics().confirmedSamples,
   pointerType:points[0]?.pointerType,
   pressure:points[0]?.pressure,accepted:p.getState().input.acceptedStrokes,
   blueStart:blueAt(points[0]),blueEnd:blueAt(points.at(-1))};
 });
 check(trace.phase==='ready'&&trace.points>=2&&trace.painted===trace.points,
  'Real CDP touch failed to produce source-space ink: '+JSON.stringify(trace));
 check(trace.pointerType==='touch'&&trace.pressure===null&&
  trace.accepted===0,'Touch data falsely measured/grading completed: '+JSON.stringify(trace));
 check(trace.blueStart&&trace.blueEnd,'No real ink at CDP touched endpoints: '+JSON.stringify(trace));
 await call('Emulation.setDeviceMetricsOverride',{
  width:390,height:844,deviceScaleFactor:2,mobile:true});
 await sleep(270);
 const resized=await onPage(()=>{
  const p=ZITIE_P21B,c=document.getElementById('practiceInk');
  const g=document.querySelector('[data-practice-source-transform]');
  const trace=p.getWritten()[0].samples,pt=trace[0];
  const pixel=new DOMPoint(pt.x,pt.y).matrixTransform(g.getScreenCTM());
  const b=c.getBoundingClientRect();
  const x=Math.max(0,Math.min(c.width-1,Math.round(
    (pixel.x-b.left)*c.width/b.width)));
  const y=Math.max(0,Math.min(c.height-1,Math.round(
    (pixel.y-b.top)*c.height/b.height)));
  const rgba=c.getContext('2d').getImageData(x,y,1,1).data;
  return {width:innerWidth,dpr:devicePixelRatio,points:trace.length,
   painted:p.getInkMetrics().confirmedSamples,
   blue:rgba[2]>rgba[0]+65&&rgba[3]>80};
 });
 check(resized.width===390&&resized.dpr===2&&
  resized.points===trace.points&&resized.painted===trace.points&&resized.blue,
  'Mobile DPR/resize lost actual touch ink or model points: '+JSON.stringify(resized));
 mkdirSync(resolve('build/a1'),{recursive:true});
 const screenshot=await call('Page.captureScreenshot',{format:'png'});
 writeFileSync(resolve('build/a1/p22a-cdp-mobile-initial.png'),
  Buffer.from(screenshot.data,'base64'));
 await onPage(async()=>{
   if(!ZITIE_P22A.undo())throw Error('Could not undo first automatically recorded stroke');
   await ZITIE_P22A.whenSaved();
 });
 const second=await onPage(()=>{
  const g=document.querySelector('[data-practice-source-transform]');
  return ZITIE_A3_BOOK.getGlyph().strokes[0].median.slice(0,2)
    .map(([x,y])=>{
      const pt=new DOMPoint(x,y).matrixTransform(g.getScreenCTM());
      return {x:pt.x,y:pt.y,id:1};
    });
 });
 await touch('touchStart',[second[0]]);
 await touch('touchMove',[second[1]]);
 await touch('touchCancel',[]);
 const canceled=await onPage(()=>{
  const s=ZITIE_P21B.getState().input;
  return {phase:s.phase,count:s.pointCount,cancellations:s.cancellations,
   accepted:s.acceptedStrokes};
 });
 check(canceled.phase==='ready'&&canceled.count===0&&
  canceled.cancellations>0&&canceled.accepted===0,
  'Native browser touchCancel incorrectly committed partial stroke: '+JSON.stringify(canceled));

 const nativeConfirmed=[];
 for(let expected=0;expected<4;expected++){
   const tracePath=await onPage(()=>{
     const p=ZITIE_P21C;
     const stroke=ZITIE_A3_BOOK.getGlyph().strokes[p.getState().progress.currentIndex];
     const group=document.querySelector('[data-practice-source-transform]');
     return stroke.median.map(([x,y])=>{
       const xy=new DOMPoint(x,y).matrixTransform(group.getScreenCTM());
       return {x:xy.x,y:xy.y,id:1};
     });
   });
   await touch('touchStart',[tracePath[0]]);
   for(const point of tracePath.slice(1))await touch('touchMove',[point]);
   await touch('touchEnd',[]);
   const accepted=await onPage(async()=>{
     const p=ZITIE_P22A;
     await p.whenSaved();
     return {index:p.getState().progress.currentIndex,
       ink:p.getInkMetrics().confirmedStrokes,
       saved:p.getState().saveStatus,
       noConfirm:!document.getElementById('practiceAccept')};
   });
   check(accepted.index===expected+1&&accepted.ink===expected+1&&
     accepted.saved==='saved'&&accepted.noConfirm,
     'CDP lifted stroke did not auto-advance exactly once: '+
     JSON.stringify(accepted));
   nativeConfirmed.push(accepted);
 }
 const finished=await onPage(()=>{
   const p=ZITIE_P21C;
   return {complete:p.getState().progress.completed,
     strokes:p.getState().progress.writtenStrokes,
     order:p.getOrderCheck()?.status,
     ink:p.getInkMetrics().confirmedStrokes,
     lengths:p.getAccepted().map(s=>s.samples.length)};
 });
 check(finished.complete&&finished.strokes===4&&finished.ink===4&&
   finished.order==='consistent',
   'Full water character did not complete: '+JSON.stringify(finished));
 const full=await call('Page.captureScreenshot',{format:'png'});
 writeFileSync(resolve('build/a1/p22a-cdp-full-water.png'),
   Buffer.from(full.data,'base64'));
 await call('Page.reload',{ignoreCache:true});
 await until(()=>onPage(()=>document.documentElement.dataset.p21cReady===
   'guided-local-v1'&&ZITIE_A3_BOOK?.pack?.glyphs.length===201));
 const restored=await onPage(async()=>{
   const p=ZITIE_P21C;
   if(!p.open())throw Error('Practice failed to open after reload');
   await p.whenReady();
   return {count:p.getState().progress.writtenStrokes,
     complete:p.getState().progress.completed,
     ink:p.getInkMetrics().confirmedStrokes,
     lengths:p.getAccepted().map(s=>s.samples.length),
     save:p.getState().saveStatus,
     verdict:p.getOrderCheck()?.status,
     source:ZITIE_A3_BOOK.getGlyph().source_sha256};
 });
 check(restored.count===4&&restored.complete&&restored.ink===4&&
   restored.save==='restored'&&restored.verdict==='consistent'&&
   restored.source===setup.sourceHash&&
   JSON.stringify(restored.lengths)===JSON.stringify(finished.lengths),
   'Reload lost genuine touch traces: '+JSON.stringify(restored));
 const undone=await onPage(async()=>{
   const p=ZITIE_P21C;
   if(!p.undo())throw Error('Undo unavailable');
   await p.whenSaved();
   return {count:p.getState().progress.writtenStrokes,
     complete:p.getState().progress.completed,
     ink:p.getInkMetrics().confirmedStrokes,
     save:p.getState().saveStatus};
 });
 check(undone.count===3&&!undone.complete&&undone.ink===3&&
   undone.save==='saved','Undo after reload failed: '+JSON.stringify(undone));
 // Wrong sequence must be detected from actual physical touch locations,
 // not assumed to be ordinal because four pen lifts occurred.
 await onPage(async()=>{
   const p=ZITIE_P22A;
   p.restart();
   await p.whenSaved();
 });
 const swappedMapping=[1,0,2,3];
 for(const expected of swappedMapping){
   const tracePath=await onPage(()=>{
     const g=document.querySelector('[data-practice-source-transform]');
     const s=ZITIE_A3_BOOK.getGlyph().strokes[expected];
     return s.median.map(([x,y])=>{
       const pt=new DOMPoint(x,y).matrixTransform(g.getScreenCTM());
       return {x:pt.x,y:pt.y,id:1};
     });
   });
   await touch('touchStart',[tracePath[0]]);
   for(const pt of tracePath.slice(1))await touch('touchMove',[pt]);
   await touch('touchEnd',[]);
 }
 const wrong=await onPage(async()=>{
   const p=ZITIE_P22A;
   await p.whenSaved();
   return {status:p.getOrderCheck()?.status,
     observed:p.getOrderCheck()?.observed,
     written:p.getState().progress.writtenStrokes};
 });
 check(wrong.status==='reordered'&&
   JSON.stringify(wrong.observed)==='[2,1,3,4]'&&wrong.written===4,
   'A whole-water swap was incorrectly called correct: '+JSON.stringify(wrong));
 const result={result:'PASS',input:'CDP Input.dispatchTouchEvent',
  sourceHash:setup.sourceHash,boardCSSPixels:setup.boardWidth,
  capture,trace,resized,canceled,
  sourceReadOnly:true,automaticGrading:false,persistentStorage:true,
  nativeConfirmed,finished,restored,undone,wrong};
 writeFileSync(resolve('build/a1/p22a-cdp-whole-metrics.json'),
  JSON.stringify(result,null,2)+'\n');
 process.stdout.write('PASS P2.2a continuous CDP touch/reload/order: '+JSON.stringify(result)+'\n');
}finally{
 for(const item of pending.values())clearTimeout(item.timer);
 try{ws?.close();}catch(_){}
 browser.kill('SIGTERM');await sleep(130);
 try{rmSync(profile,{recursive:true,force:true});}catch(_){}
}
