/* F1: independent Foundations book. Offline, no external fonts or services.
 * Vector trajectories are ENGINEERING EXAMPLES, not certified stroke order.
 */
(function(){
'use strict';
window.addEventListener('DOMContentLoaded',()=>{
  const model=window.ZitieFoundations;
  const $=id=>document.getElementById(id);
  const NS='http://www.w3.org/2000/svg';
  if(!model){$('lessonHint').textContent='基础字帖数据暂不可用。';return;}
  const state={
    group:model.groups[0],entry:null,rate:0.8,strokes:[],active:null,
    paths:[],elapsed:0,lastTime:0,raf:0,running:false,duration:0
  };
  const storagePrefix='zitie-foundations-f1:';
  const guide=$('guide'),canvas=$('ink'),board=$('board');
  const ctx=canvas.getContext('2d');
  const node=(type,attrs={})=>{
    const n=document.createElementNS(NS,type);
    for(const [key,value] of Object.entries(attrs))n.setAttribute(key,String(value));
    return n;
  };
  function setStatus(text){$('writeStatus').textContent=text;}
  function groupIndex(){return model.groups.indexOf(state.group);}
  function currentIndex(){return state.group.entries.findIndex(x=>x.id===state.entry.id);}
  function saveStrokes(){
    try{
      localStorage.setItem(storagePrefix+state.entry.id,JSON.stringify({
        version:1,strokes:state.strokes
      }));
      return true;
    }catch(_){return false;}
  }
  function loadStrokes(entry){
    try{
      const obj=JSON.parse(localStorage.getItem(storagePrefix+entry.id)||'null');
      if(!obj||obj.version!==1||!Array.isArray(obj.strokes))return [];
      if(obj.strokes.length>100)return [];
      return obj.strokes.filter(s=>Array.isArray(s)&&s.length>=1&&s.length<=1200&&
        s.every(p=>Array.isArray(p)&&p.length===2&&
          Number.isFinite(p[0])&&Number.isFinite(p[1])&&
          p[0]>=0&&p[0]<=1&&p[1]>=0&&p[1]<=1));
    }catch(_){return [];}
  }
  function appendGrid(root,comp,kind,offset=0,opacity=1){
    if(kind==='squares'){
      for(let x=0;x<comp.width;x+=76){
        const ox=offset+x;
        root.append(node('rect',{x:ox+6,y:17,width:64,height:66,
          fill:'none',stroke:'#dfc6cb','stroke-width':1.3,opacity}));
        root.append(node('path',{d:'M'+(ox+6)+' 50 H'+(ox+70)+
          ' M'+(ox+38)+' 17 V83',stroke:'#d5d5d5',
          'stroke-width':1,'stroke-dasharray':'3 4',opacity}));
      }
    }else{
      for(const [i,y] of [14,47,83,117].entries())
        root.append(node('path',{d:'M'+(offset-20)+' '+y+' H'+
          (offset+comp.width+20),stroke:i===2?'#cfabb2':'#d9c5ca',
          'stroke-width':i===2?1.6:1.1,opacity}));
    }
  }
  function path(stroke,offset,kind,attrs={}){
    const trans='translate('+(offset+stroke.x)+' 0)';
    return node('path',{d:stroke.d,transform:trans,fill:'none',
      'stroke-linecap':'round','stroke-linejoin':'round',...attrs});
  }
  function stopAnimation(){
    state.running=false;
    if(state.raf)cancelAnimationFrame(state.raf);
    state.raf=0;state.lastTime=0;
    $('demo').textContent='▶ 逐笔示范';
  }
  function drawFrame(ms){
    let rest=ms;
    for(const part of state.paths){
      const visible=Math.max(0,Math.min(1,(rest-100)/part.duration));
      part.el.setAttribute('stroke-dashoffset',String(part.length*(1-visible)));
      rest-=part.duration+115;
    }
  }
  function animate(time){
    if(!state.running)return;
    if(state.lastTime)state.elapsed+=Math.max(0,Math.min(90,time-state.lastTime))*state.rate;
    state.lastTime=time;
    drawFrame(state.elapsed);
    if(state.elapsed>=state.duration){
      state.running=false;state.raf=0;state.lastTime=0;
      $('demo').textContent='▶ 重新示范';return;
    }
    state.raf=requestAnimationFrame(animate);
  }
  function startDemo(restart=false){
    if(restart||state.elapsed>=state.duration){
      state.elapsed=0;drawFrame(0);
    }
    if(state.running){stopAnimation();return;}
    state.running=true;
    $('demo').textContent='Ⅱ 暂停示范';
    state.raf=requestAnimationFrame(animate);
  }
  function stage(item){
    stopAnimation();
    const comp=model.compose(item.text,state.group.kind);
    guide.replaceChildren();
    guide.setAttribute('viewBox','-24 0 '+(comp.width+48)+' 132');
    guide.setAttribute('aria-label',item.text+' 占格与书写工程示范');
    const w=Math.min(760,Math.max(260,(comp.width+48)*1.8));
    const h=Math.min(270,Math.round(w*132/(comp.width+48)));
    board.style.width=w+'px';
    board.style.height=Math.max(94,h)+'px';
    appendGrid(guide,comp,state.group.kind);
    state.paths=[];state.elapsed=0;state.duration=0;
    for(const st of comp.strokes){
      guide.append(path(st,0,state.group.kind,{
        stroke:'#aeb0b3','stroke-width':4.7,opacity:.55
      }));
      const over=path(st,0,state.group.kind,{
        stroke:'#b33b49','stroke-width':4.6
      });
      guide.append(over);
      const length=Math.max(1,over.getTotalLength());
      const duration=Math.max(250,Math.min(950,length*9));
      over.setAttribute('stroke-dasharray',String(length));
      over.setAttribute('stroke-dashoffset',String(length));
      state.paths.push({el:over,length,duration});
      state.duration+=duration+115;
    }
    drawInk();
  }
  function point(clientX,clientY){
    const r=canvas.getBoundingClientRect();
    if(!r.width||!r.height)return null;
    const x=(clientX-r.left)/r.width,y=(clientY-r.top)/r.height;
    if(!Number.isFinite(x)||!Number.isFinite(y))return null;
    return [Math.min(1,Math.max(0,x)),Math.min(1,Math.max(0,y))];
  }
  function drawInk(){
    const r=canvas.getBoundingClientRect();
    if(!r.width||!r.height)return;
    const ratio=Math.min(3,window.devicePixelRatio||1);
    const cw=Math.max(1,Math.round(r.width*ratio));
    const ch=Math.max(1,Math.round(r.height*ratio));
    if(canvas.width!==cw||canvas.height!==ch){canvas.width=cw;canvas.height=ch;}
    ctx.setTransform(cw/r.width,0,0,ch/r.height,0,0);
    ctx.clearRect(0,0,r.width,r.height);
    ctx.lineWidth=3.8;
    ctx.strokeStyle='#237fca';
    ctx.fillStyle='#237fca';
    ctx.lineJoin='round';ctx.lineCap='round';
    for(const points of state.strokes.concat(state.active?[state.active.points]:[])){
      if(!points.length)continue;
      ctx.beginPath();
      ctx.moveTo(points[0][0]*r.width,points[0][1]*r.height);
      for(let i=1;i<points.length;i++)
        ctx.lineTo(points[i][0]*r.width,points[i][1]*r.height);
      if(points.length===1){
        ctx.arc(points[0][0]*r.width,points[0][1]*r.height,2,0,Math.PI*2);
        ctx.fill();
      }else ctx.stroke();
    }
    $('undo').disabled=!state.strokes.length;
  }
  function begin(kind,id,x,y){
    if(state.active)return false;
    const p=point(x,y);
    if(!p)return false;
    state.active={kind,id,points:[p]};
    drawInk();
    return true;
  }
  function extend(x,y){
    if(!state.active)return;
    const p=point(x,y),arr=state.active.points;
    if(!p||arr.length>=1200)return;
    const prior=arr[arr.length-1];
    if(Math.hypot(p[0]-prior[0],p[1]-prior[1])>=.0015){
      arr.push(p);drawInk();
    }
  }
  function finish(x,y){
    if(!state.active)return;
    extend(x,y);
    const arr=state.active.points;
    state.active=null;
    if(state.strokes.length<100)state.strokes.push(arr);
    const saved=saveStrokes();
    drawInk();
    setStatus('已书写 '+state.strokes.length+' 笔'+
      (saved?' · 已保存在本机':' · 本机存储不可用，仅当前页面有效')+
      '；不自动判定笔顺。');
  }
  function cancel(){if(state.active){state.active=null;drawInk();}}
  canvas.addEventListener('pointerdown',e=>{
    if(e.isPrimary===false||(e.pointerType==='mouse'&&e.button!==0))return;
    if(!begin('pointer',e.pointerId,e.clientX,e.clientY))return;
    try{canvas.setPointerCapture(e.pointerId);}catch(_){}
    if(e.cancelable)e.preventDefault();
  });
  window.addEventListener('pointermove',e=>{
    if(!state.active||state.active.kind!=='pointer'||state.active.id!==e.pointerId)return;
    const events=typeof e.getCoalescedEvents==='function'?
      (function(){try{return e.getCoalescedEvents();}catch(_){return [];}})():[];
    for(const sample of events)extend(sample.clientX,sample.clientY);
    extend(e.clientX,e.clientY);
    if(e.cancelable)e.preventDefault();
  },true);
  window.addEventListener('pointerup',e=>{
    if(state.active?.kind==='pointer'&&state.active.id===e.pointerId){
      finish(e.clientX,e.clientY);
      if(e.cancelable)e.preventDefault();
    }
  },true);
  window.addEventListener('pointercancel',e=>{
    if(state.active?.kind==='pointer'&&state.active.id===e.pointerId)cancel();
  },true);
  canvas.addEventListener('lostpointercapture',e=>{
    if(state.active?.kind==='pointer'&&state.active.id===e.pointerId)cancel();
  });
  // Some iOS embedded engines fail to deliver Pointer Events on a canvas.
  // Ignore legacy Touch Events once a pointer session is active.
  canvas.addEventListener('touchstart',e=>{
    if(!state.active&&e.changedTouches.length===1){
      const t=e.changedTouches[0];
      begin('touch',t.identifier,t.clientX,t.clientY);
    }
    if(e.cancelable)e.preventDefault();
  },{passive:false});
  canvas.addEventListener('touchmove',e=>{
    if(state.active?.kind==='touch'){
      for(const t of e.changedTouches)if(t.identifier===state.active.id)
        extend(t.clientX,t.clientY);
    }
    if(e.cancelable)e.preventDefault();
  },{passive:false});
  canvas.addEventListener('touchend',e=>{
    if(state.active?.kind==='touch'){
      for(const t of e.changedTouches)if(t.identifier===state.active.id)
        finish(t.clientX,t.clientY);
    }
    if(e.cancelable)e.preventDefault();
  },{passive:false});
  canvas.addEventListener('touchcancel',cancel,{passive:false});
  window.addEventListener('blur',cancel);
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='hidden')cancel();
  });
  window.addEventListener('resize',()=>{
    cancel();drawInk();
  });
  function selectEntry(item){
    if(!item)return;
    stopAnimation();cancel();
    state.entry=item;
    state.strokes=loadStrokes(item);
    $('lessonHeading').textContent=item.text;
    $('groupLabel').textContent=state.group.name;
    $('lessonHint').textContent=item.meaning?item.meaning+' · '+state.group.hint:state.group.hint;
    let tip=state.group.key==='numbers'?
      '数字置于方格内，先看比例，再描红并独立练习。':
      '四线三格：辨认字母高低和占格，再跟随示范描摹。';
    if(item.text.includes('ü')||/[ǖǘǚǜ]/.test(item.text))
      tip+=' ü 的两个点要保留。';
    if(state.group.key==='tones')
      tip+=' 从左到右依次为一、二、三、四声；标调 i 去点。';
    if(state.group.key==='initials'&&['zh','ch','sh'].includes(item.text))
      tip+=' 这是两个字母组合，注意间距。';
    $('tipText').textContent=tip;
    stage(item);
    setStatus(state.strokes.length?
      '已恢复本机 '+state.strokes.length+' 笔 · 可以继续写或重新练习。':
      '在字格中直接书写；每次自然提笔记录一笔。');
    updateEntries();
    try{
      const url=new URL(window.location.href);
      url.searchParams.set('group',state.group.key);
      url.searchParams.set('item',item.id);
      history.replaceState(null,'',url);
    }catch(_){}
  }
  function updateEntries(){
    const container=$('items');
    container.replaceChildren();
    for(const item of state.group.entries){
      const button=document.createElement('button');
      button.type='button';
      button.setAttribute('aria-pressed',String(item.id===state.entry?.id));
      const strong=document.createElement('strong');
      strong.textContent=item.text;button.append(strong);
      if(item.meaning){
        const small=document.createElement('small');small.textContent=item.meaning;
        button.append(small);
      }
      button.addEventListener('click',()=>selectEntry(item));
      container.append(button);
    }
  }
  function selectGroup(group,selectedId){
    if(!group)return;
    cancel();
    state.group=group;
    $('groupCount').textContent=group.entries.length+' 项';
    $('catalogHint').textContent=group.hint;
    for(const b of $('tabs').querySelectorAll('button[data-group]'))
      b.setAttribute('aria-pressed',String(b.dataset.group===group.key));
    selectEntry(group.entries.find(x=>x.id===selectedId)||group.entries[0]);
  }
  function drawTabs(){
    for(const group of model.groups){
      const b=document.createElement('button');
      b.type='button';b.dataset.group=group.key;b.textContent=group.name;
      b.setAttribute('aria-pressed','false');
      b.addEventListener('click',()=>selectGroup(group));
      $('tabs').append(b);
    }
  }
  function worksheetSvg(comp,kind,mode){
    // Fix 1600:132 artwork proportions to A4 printable width / 15-mm row.
    // Subdivide the ENTIRE printable line; never center a short mini-SVG
    // which would leave most of the A4 page unused.
    const W=1600;
    const copies=comp.width>380?2:comp.width>220?3:
      comp.width>100?4:8;
    const cellWidth=W/copies;
    const svg=node('svg',{viewBox:'0 0 '+W+' 132',
      preserveAspectRatio:'xMidYMid meet',class:'printLine',
      'aria-label':mode+'：字帖练习格'});
    for(let i=0;i<copies;i++){
      const left=i*cellWidth;
      const x=left+(cellWidth-comp.width)/2;
      if(kind==='squares'){
        svg.append(node('rect',{x:left+2,y:11,width:cellWidth-4,
          height:106,fill:'none',stroke:'#e1cbd0',
          'stroke-width':1.1}));
        svg.append(node('path',{d:'M'+(left+2)+' 64 H'+
          (left+cellWidth-2)+' M'+(left+cellWidth/2)+
          ' 11 V117',stroke:'#ded6d6','stroke-dasharray':'4 5',
          'stroke-width':1}));
        // Number writing is centred within the larger worksheet cell.
        svg.append(node('rect',{x:x+6,y:17,width:64,height:66,
          fill:'none',stroke:'#ccb0b5','stroke-width':1.2}));
      }else{
        const lines=[14,47,83,117];
        for(let j=0;j<lines.length;j++)svg.append(node('path',{
          d:'M'+left+' '+lines[j]+' H'+(left+cellWidth),
          stroke:j===2?'#cda9b0':'#dfc7cb',
          'stroke-width':j===2?1.6:1.05
        }));
        if(i)svg.append(node('path',{d:'M'+left+' 14 V117',
          stroke:'#dedede','stroke-width':.8,
          'stroke-dasharray':'3 5'}));
      }
      if(mode==='blank')continue;
      for(const st of comp.strokes){
        svg.append(path(st,x,kind,{
          stroke:mode==='red'?'#b03a49':'#999da2',
          'stroke-width':4.5,opacity:mode==='red'?.85:.35
        }));
      }
    }
    return svg;
  }
  function makePrintPages(){
    const root=$('printRoot');root.replaceChildren();
    const entries=state.group.entries;
    for(let base=0;base<entries.length;base+=4){
      const page=document.createElement('section');
      page.className='printPage';
      const header=document.createElement('header');header.className='printHeader';
      const left=document.createElement('div');
      const h=document.createElement('h2');h.textContent='基础书写字帖 · '+state.group.name;
      const p=document.createElement('p');
      p.textContent='四线三格／数字方格 · 示范 → 描淡 → 独立书写';
      left.append(h,p);header.append(left);
      const num=document.createElement('small');
      num.textContent='第 '+(Math.floor(base/4)+1)+' / '+Math.ceil(entries.length/4)+' 页';
      header.append(num);page.append(header);
      for(const entry of entries.slice(base,base+4)){
        const article=document.createElement('article');article.className='printItem';
        const lineTitle=document.createElement('header');
        const title=document.createElement('h3');title.textContent=entry.text;
        lineTitle.append(title);
        if(entry.meaning){
          const small=document.createElement('small');small.textContent=entry.meaning;
          lineTitle.append(small);
        }
        article.append(lineTitle);
        const comp=model.compose(entry.text,state.group.kind);
        for(const mode of ['red','gray','blank'])
          article.append(worksheetSvg(comp,state.group.kind,mode));
        page.append(article);
      }
      const foot=document.createElement('p');foot.className='printNote';
      foot.textContent='独立绘制的工程字形示范，非已审核的规范笔顺；请结合学校教材核对。';
      page.append(foot);root.append(page);
    }
    return root.querySelectorAll('.printPage').length;
  }
  $('demo').addEventListener('click',()=>startDemo(false));
  $('replay').addEventListener('click',()=>{stopAnimation();startDemo(true);});
  $('speedButtons').addEventListener('click',e=>{
    const b=e.target.closest('button[data-rate]');
    if(!b)return;
    const r=Number(b.dataset.rate);
    if(![.5,.8,1,1.5].includes(r))return;
    state.rate=r;
    for(const button of $('speedButtons').querySelectorAll('button[data-rate]'))
      button.setAttribute('aria-pressed',String(Number(button.dataset.rate)===r));
  });
  $('undo').addEventListener('click',()=>{
    cancel();
    state.strokes.pop();const saved=saveStrokes();drawInk();
    setStatus('已保留 '+state.strokes.length+' 笔'+
      (saved?' · 本机自动保存':' · 本机存储不可用'));
  });
  $('clear').addEventListener('click',()=>{
    cancel();state.strokes=[];const saved=saveStrokes();drawInk();
    setStatus(saved?'已清空当前内容，可以立即重新练习。':'已清空当前页面笔迹。');
  });
  $('prev').addEventListener('click',()=>{
    const i=currentIndex(),all=state.group.entries;
    selectEntry(all[(i-1+all.length)%all.length]);
  });
  $('next').addEventListener('click',()=>{
    const i=currentIndex(),all=state.group.entries;
    selectEntry(all[(i+1)%all.length]);
  });
  $('print').addEventListener('click',()=>{
    if(state.active)cancel();
    makePrintPages();
    stopAnimation();
    window.print();
  });
  window.addEventListener('afterprint',()=>{$('printRoot').replaceChildren();});
  drawTabs();
  let initialGroup=model.groups[0],initialId=null;
  try{
    const q=new URLSearchParams(location.search);
    initialGroup=model.groups.find(x=>x.key===q.get('group'))||initialGroup;
    initialId=q.get('item');
  }catch(_){}
  selectGroup(initialGroup,initialId);
  // QA-only, read-only diagnostics. No learner profile, scores or data export.
  window.ZITIE_FOUNDATIONS={
    getCategory:()=>state.group.key,
    getEntry:()=>state.entry?.id,
    getSavedStrokeCount:()=>state.strokes.length,
    getRate:()=>state.rate,
    getPrintedPageCount:makePrintPages,
    selectGroup:key=>selectGroup(model.groups.find(x=>x.key===key))
  };
  document.documentElement.dataset.foundationsReady='f1';
});
})();
