/* A2.2 independent fixed-width hardpen renderer. No brush-outline mask.
 * Original A1.6 player remains untouched; the B panel renders its own
 * ordered source-median-based motion using one uniform circular contact.
 */
window.addEventListener('DOMContentLoaded',function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const NS='http://www.w3.org/2000/svg';
  const source=window.ZITIE_SAMPLES.glyphs;
  const T=window.ZitieTimeline;
  const M=window.ZitieHardpenModel;
  const P=window.ZitieStrokePrimitives;
  const Ink=window.ZitieHardpenInkUnion;
  const Old=window.ZitiePlayer.StrokePlayer;
  const examples=[
    {char:'一',stroke:0,label:'横 · 一'},
    {char:'十',stroke:1,label:'竖 · 十'},
    {char:'人',stroke:0,label:'撇 · 人'},
    {char:'口',stroke:1,label:'折 · 口'},
    {char:'水',stroke:0,label:'钩 · 水'},
    {char:'月',stroke:1,label:'折钩 · 月'},
    {char:'龠',stroke:13,label:'复杂折 · 龠'}
  ];
  const baseline=new Old({svg:$('baselineStage')});
  const svg=$('hardpenStage');
  const tag=(name,attrs={})=>{
    const el=document.createElementNS(NS,name);
    for(const [key,value] of Object.entries(attrs))el.setAttribute(key,String(value));
    return el;
  };
  let current=null,glyph=null,plans=[],rows=[],tip=null,
    geometryGuide=null,elapsed=0,total=0,playing=false,
    lastTick=null,speed=1,width=26,showGuide=false,lastState=null;
  function background(){
    svg.replaceChildren();
    svg.setAttribute('viewBox','0 0 1024 1024');
    svg.append(tag('rect',{x:0,y:0,width:1024,height:1024,fill:'#FFFFFF'}));
    svg.append(tag('rect',{x:56,y:48,width:912,height:928,fill:'none',
      stroke:'#C9979B','stroke-width':2}));
    for(const [x1,y1,x2,y2] of [[512,48,512,976],[56,512,968,512]])
      svg.append(tag('line',{x1,y1,x2,y2,stroke:'#E2C9CD',
        'stroke-width':2,'stroke-dasharray':'12 12'}));
    const group=tag('g',{transform:'translate(0 900) scale(1 -1)'});
    svg.append(group);return group;
  }
  function attach(glyph){
    const group=background();
    const old=JSON.stringify(glyph.strokes);
    plans=glyph.strokes.map((s,i)=>M.makePlan(s,P.semantics(glyph,i),{width}));
    if(JSON.stringify(glyph.strokes)!==old)
      throw Error('Hardpen projection must not modify source glyph');
    rows=plans.map(plan=>Ink.createRow(plan,width));
    // Preserve role layering: gray future traces below finished traces
    // and all red incremental capsule segments.
    for(const row of rows)group.append(row.hint);
    for(const row of rows)group.append(row.finished);
    for(const row of rows)group.append(row.redGroup);
    geometryGuide=tag('path',{d:plans[current.stroke].completePath,
      stroke:'#237d8a','stroke-width':2,fill:'none',
      opacity:'.57','stroke-dasharray':'7 10','pointer-events':'none'});
    group.append(geometryGuide);
    tip=tag('circle',{cx:0,cy:0,r:5,fill:'#BD3945',
      stroke:'#BD3945','stroke-width':.7,'pointer-events':'none'});
    group.append(tip);
  }
  function speedGraph(){
    const canvas=$('velocityChart'),ctx=canvas.getContext('2d');
    const w=canvas.width,h=canvas.height,left=38,right=w-16,top=14,bottom=h-27;
    ctx.clearRect(0,0,w,h);ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);
    ctx.strokeStyle='#e5e8eb';ctx.lineWidth=1;
    for(let i=0;i<=3;i++){
      const y=top+(bottom-top)*i/3;
      ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();
    }
    const a=baseline.timeline.strokes[current.stroke].motion;
    const b=plans[current.stroke];
    for(const [fn,color] of [
      [t=>{
        const d=.002,lo=Math.max(0,t-d),hi=Math.min(1,t+d);
        return (a.progressAt(hi)-a.progressAt(lo))/(hi-lo||1);
      },'#9aa6af'],
      [t=>b.velocityAt(t),'#1b8190']]){
      ctx.beginPath();ctx.lineWidth=3.3;ctx.strokeStyle=color;
      for(let i=0;i<=200;i++){
        const t=i/200,x=left+(right-left)*t;
        const y=bottom-Math.min(3,fn(t))*(bottom-top)/3;
        if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);
      }
      ctx.stroke();
    }
    const stage=baseline.timeline.strokes[current.stroke];
    const t=Math.max(0,Math.min(1,(elapsed-stage.startMs)/stage.durationMs));
    ctx.strokeStyle='#b63b48';ctx.lineWidth=1.5;ctx.beginPath();
    ctx.moveTo(left+(right-left)*t,top);
    ctx.lineTo(left+(right-left)*t,bottom);ctx.stroke();
    ctx.font='13px system-ui';ctx.fillStyle='#677782';
    ctx.fillText('触纸',left,bottom+19);
    ctx.textAlign='right';ctx.fillText('离纸',right,bottom+19);
    ctx.textAlign='start';
  }
  function render(){
    if(!glyph||!current)return null;
    baseline.elapsed=elapsed;
    baseline.render();
    const frame=T.frameAt(baseline.timeline,elapsed);
    let activeState=null;
    for(let i=0;i<rows.length;i++){
      const row=rows[i],stage=baseline.timeline.strokes[i];
      const before=i<frame.index,after=i>frame.index;
      const finished=frame.phase==='finished'||before;
      const inProgress=!finished&&!after;
      row.finished.style.display=finished?'':'none';
      row.redGroup.style.display=inProgress?'':'none';
      if(inProgress){
        const clock=Math.max(0,Math.min(1,
          (elapsed-stage.startMs)/stage.durationMs));
        const state=row.plan.stateAt(clock);
        Ink.progressAt(row,state.progress);
        if(i===current.stroke)activeState=state;
      }
    }
    const stage=baseline.timeline.strokes[current.stroke];
    const time=Math.max(0,Math.min(1,
      (elapsed-stage.startMs)/stage.durationMs));
    const state=plans[current.stroke].stateAt(time);
    const active=frame.phase==='writing'&&frame.index===current.stroke&&
      state.progress>0&&state.progress<1;
    if(active){
      tip.setAttribute('cx',state.point.x.toFixed(5));
      tip.setAttribute('cy',state.point.y.toFixed(5));
      tip.style.display='';
    }else tip.style.display='none';
    geometryGuide.style.display=showGuide?'':'none';
    $('phase').textContent=frame.phase==='finished'?'已完成':
      frame.index<current.stroke?'待开始':
      frame.index>current.stroke?'已结束':state.label;
    $('oldProgress').textContent=Math.round(
      frame.index===current.stroke?frame.progress*100:
      frame.index>current.stroke?100:0)+'%';
    $('newProgress').textContent=Math.round(state.progress*100)+'%';
    $('widthStatus').textContent='恒定 '+width+' 单位';
    $('seek').value=total?Math.round(elapsed*1000/total):0;
    $('clock').textContent=(elapsed/1000).toFixed(2)+' / '+
      (total/1000).toFixed(2)+'s';
    $('play').textContent=playing?'Ⅱ 暂停':'▶ 同步播放';
    speedGraph();
    lastState={frame,selected:current,elapsed,
      hardProgress:state.progress,hardState:state,
      active,hardTip:active?[
        +tip.getAttribute('cx'),+tip.getAttribute('cy')]:null};
    return lastState;
  }
  function pause(){playing=false;lastTick=null;return render();}
  function seek(ms){
    if(!Number.isFinite(ms))throw Error('Invalid hardpen seek');
    playing=false;lastTick=null;elapsed=Math.max(0,Math.min(total,ms));
    return render();
  }
  function select(option){
    const found=typeof option==='string'?
      examples.find(v=>v.char===option):option;
    if(!examples.includes(found))throw Error('Unknown hardpen sample');
    current=found;glyph=source.find(v=>v.character===found.char);
    if(!glyph)throw Error('Missing original glyph');
    playing=false;lastTick=null;
    baseline.setGlyph(glyph);
    attach(glyph);
    total=baseline.timeline.totalMs;
    const stage=baseline.timeline.strokes[current.stroke];
    elapsed=stage.startMs+stage.durationMs*.62;
    $('glyphs').querySelectorAll('button').forEach(button=>
      button.setAttribute('aria-pressed',String(button.dataset.char===current.char)));
    $('explain').textContent='「'+current.label+'」：源中心线仅作粗略轨迹参考，'+
      'B为'+width+'个SVG单位的固定圆头硬笔接触（非校准毫米宽度），'+
      '几何细化段 '+plans[current.stroke].geometry.smoothedSegments+
      '，原线段回退 '+plans[current.stroke].geometry.rejectedSegments+
      '。折钩只作短促减速，不模拟毛笔的夸张蓄势。';
    return render();
  }
  function setWidth(value){
    const n=+value;
    if(n!==21&&n!==26)throw Error('Unsupported normalized hardpen width');
    if(!current)return;
    const keep=elapsed,wasPlaying=playing;
    width=n;
    attach(glyph);
    elapsed=keep;
    playing=wasPlaying;
    $('penWidths').querySelectorAll('button').forEach(button=>
      button.setAttribute('aria-pressed',String(+button.dataset.width===n)));
    return render();
  }
  function setSpeed(value){
    const n=+value;
    if(![.5,1,1.5,2].includes(n))throw Error('Invalid hardpen time multiplier');
    speed=n;
    $('speedButtons').querySelectorAll('button').forEach(button=>
      button.setAttribute('aria-pressed',String(+button.dataset.speed===n)));
  }
  function tick(now){
    if(!playing)return;
    if(lastTick!==null)
      elapsed=Math.min(total,elapsed+Math.max(0,now-lastTick)*speed);
    lastTick=now;
    if(elapsed>=total){playing=false;lastTick=null;render();return;}
    render();requestAnimationFrame(tick);
  }
  function play(){
    if(playing)return;
    if(elapsed>=total)elapsed=baseline.timeline.strokes[current.stroke].startMs;
    playing=true;lastTick=null;render();
    requestAnimationFrame(tick);
  }
  for(const e of examples){
    const b=document.createElement('button');
    b.type='button';b.textContent=e.label;
    b.dataset.char=e.char;
    b.setAttribute('aria-pressed','false');
    b.addEventListener('click',()=>select(e));
    $('glyphs').append(b);
  }
  $('play').addEventListener('click',()=>playing?pause():play());
  $('restart').addEventListener('click',()=>{
    seek(baseline.timeline.strokes[current.stroke].startMs);play();
  });
  $('showAll').addEventListener('click',()=>seek(total));
  $('showGuide').addEventListener('click',()=>{
    showGuide=!showGuide;
    $('showGuide').setAttribute('aria-pressed',String(showGuide));
    $('showGuide').textContent=showGuide?'隐藏骨架轨迹':'显示骨架轨迹';
    render();
  });
  $('penWidths').addEventListener('click',e=>{
    const b=e.target.closest('[data-width]');if(b)setWidth(b.dataset.width);
  });
  $('speedButtons').addEventListener('click',e=>{
    const b=e.target.closest('[data-speed]');if(b)setSpeed(b.dataset.speed);
  });
  $('seek').addEventListener('input',e=>seek(total*+e.target.value/1000));
  window.ZITIE_A22_HARDPEN={
    baseline,examples,select,seek,render,play,pause,setWidth,setSpeed,
    get glyph(){return glyph;},get selected(){return current;},
    get rows(){return rows;},get plans(){return plans;},
    get svg(){return svg;},get tip(){return tip;},
    get state(){return lastState;},get width(){return width;},
    get elapsed(){return elapsed;},get total(){return total;},
    get speed(){return speed;},get playing(){return playing;}
  };
  select(examples[4]); // 水, hook approach visible at first open.
});
