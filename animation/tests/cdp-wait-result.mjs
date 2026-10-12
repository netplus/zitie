/* Real-wall-clock Chromium smoke runner. IndexedDB is asynchronous and must
 * NOT be tested with Chrome's virtual-time-budget + immediate --dump-dom:
 * that can snapshot RUNNING while the IDB transaction is still outstanding.
 * Usage: node cdp-wait-result.mjs URL OUTPUT_HTML TIMEOUT_MS [SCREENSHOT_PNG]
 * Requires CHROME_BIN from browser-actions/setup-chrome; localhost only.
 */
import {spawn} from 'node:child_process';
import {mkdtempSync,existsSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {mkdirSync} from 'node:fs';

const [url,output,waitArg,screenshot]=process.argv.slice(2);
const chrome=process.env.CHROME_BIN;
const deadline=Number(waitArg||90000);
if(!url||!/^http:\/\/127\.0\.0\.1:\d+\/animation\/tests\/[a-z0-9-]+\.html$/.test(url)||
   !output||!chrome||!Number.isInteger(deadline)||deadline<1000||deadline>180000)
  throw Error('Use a localhost browser test URL, output path, and CHROME_BIN');
const profile=mkdtempSync(join(tmpdir(),'zitie-cdp-wait-'));
const browser=spawn(chrome,[
  '--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu',
  '--disable-background-timer-throttling','--disable-renderer-backgrounding',
  '--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0','--remote-allow-origins=*',
  '--user-data-dir='+profile,'--window-size=1560,1270',url
],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let ws=null,sequence=0;
const pending=new Map();
const start=Date.now();

async function until(fn){
  while(Date.now()-start<Math.min(deadline,18000)){
    if(browser.exitCode!==null)throw Error('Chromium exited before CDP ready');
    try{const value=await fn();if(value)return value;}catch(_){}
    await sleep(120);
  }
  throw Error('Chromium CDP readiness timed out');
}
function call(method,params={}){
  return new Promise((resolve,reject)=>{
    const id=++sequence;
    const timer=setTimeout(()=>{
      pending.delete(id);reject(Error('CDP '+method+' timed out'));
    },12000);
    pending.set(id,{resolve,reject,timer});
    ws.send(JSON.stringify({id,method,params}));
  });
}
async function evaluate(expression){
  const reply=await call('Runtime.evaluate',{
    expression,returnByValue:true,awaitPromise:false
  });
  if(reply.exceptionDetails)
    throw Error('Chrome evaluation error: '+JSON.stringify(reply.exceptionDetails));
  return reply.result?.value;
}
async function saveHtml(){
  const dom=await evaluate('document.documentElement.outerHTML');
  mkdirSync(dirname(resolve(output)),{recursive:true});
  writeFileSync(resolve(output),dom||'',{encoding:'utf8'});
}
try{
  const port=await until(()=>existsSync(join(profile,'DevToolsActivePort'))?
    Number(readFileSync(join(profile,'DevToolsActivePort'),'utf8').split('\n')[0]):null);
  const page=await until(async()=>{
    const resp=await fetch('http://127.0.0.1:'+port+'/json/list');
    const pages=await resp.json();
    return pages.find(p=>p.type==='page'&&p.webSocketDebuggerUrl);
  });
  ws=new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error('Chrome WebSocket open timeout')),10000);
    ws.addEventListener('open',()=>{clearTimeout(timer);resolve();},{once:true});
    ws.addEventListener('error',()=>{clearTimeout(timer);reject(Error('Chrome WebSocket error'));},{once:true});
  });
  ws.addEventListener('message',event=>{
    let data;try{data=JSON.parse(String(event.data));}catch(_){return;}
    const waiter=pending.get(data.id);
    if(!waiter)return;
    clearTimeout(waiter.timer);pending.delete(data.id);
    if(data.error)waiter.reject(Error(JSON.stringify(data.error)));
    else waiter.resolve(data.result);
  });
  await call('Runtime.enable');
  let final=null,progress=null;
  while(Date.now()-start<deadline){
    const frame=await evaluate('(()=>{const f=document.getElementById("demo");'+
      'const w=f?.contentWindow;const d=f?.contentDocument;'+
      'return {result:document.documentElement.dataset.result||null,'+
      'report:document.getElementById("result")?.textContent||null,'+
      'title:document.title,childReady:d?.documentElement?.dataset.p21cReady||null,'+
      'inputPhase:w?.ZITIE_P21C?.getState()?.input?.phase||null,'+
      'practiceReady:w?.ZITIE_P21C?.getState()?.ready||false,'+
      'saveStatus:w?.ZITIE_P21C?.getState()?.saveStatus||null};})()');
    progress=frame;
    if(frame?.result==='PASS'||frame?.result==='FAIL'){
      final=frame;break;
    }
    await sleep(180);
  }
  await saveHtml();
  if(screenshot){
    const image=await call('Page.captureScreenshot',{format:'png'});
    mkdirSync(dirname(resolve(screenshot)),{recursive:true});
    writeFileSync(resolve(screenshot),Buffer.from(image.data,'base64'));
  }
  if(!final)throw Error('Browser smoke timed out waiting for PASS/FAIL; state='+
    JSON.stringify(progress));
  if(final.result!=='PASS')throw Error('Browser smoke FAILED: '+
    String(final.report).slice(0,3500));
  process.stdout.write('PASS browser async CDP '+url+
    ' elapsedMs='+String(Date.now()-start)+'\n');
}finally{
  for(const entry of pending.values())clearTimeout(entry.timer);
  try{ws?.close();}catch(_){}
  browser.kill('SIGTERM');
  await sleep(120);
  try{rmSync(profile,{recursive:true,force:true});}catch(_){}
}
