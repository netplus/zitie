/* A1.5 opt-in pressure visualization using TWO unchanged stable A1.3
 * StrokePlayer ink engines. Pressure is a synthetic visual cue only.
 * No original source medians, masks, or timeline data are modified.
 */
window.addEventListener('DOMContentLoaded',function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const NS='http://www.w3.org/2000/svg';
  const T=window.ZitieTimeline,P=window.ZitiePressureModel;
  const candidates=window.ZitieGestureCandidates;
  const Player=window.ZitiePlayer.StrokePlayer;
  const glyphs=['一','口','水','月','火','龠'].map(ch=>
    window.ZITIE_SAMPLES.glyphs.find(g=>g.character===ch));
  if(glyphs.some(g=>!g))throw Error('Source-backed pressure sample missing');
  const a=new Player({svg:$('baselineStage')});
  const b=new Player({svg:$('pressureStage')});
  let glyph=null,plans=[],elapsed=0,total=0,playing=false,lastTick=null,
    speed=1,showPressure=true,mostRecent=null;
  const ring=document.createElementNS(NS,'circle');
  ring.setAttribute('fill','none');
  ring.setAttribute('stroke','#883542');
  ring.setAttribute('stroke-width','2.5');
  ring.setAttribute('opacity','.68');
  ring.setAttribute('pointer-events','none');
  const phaseNames={hover:'悬笔',touch:'轻触起笔',travel:'稳定行笔',
    pivot:'转锋按顿',flick:'顺势出钩',lift:'收锋提笔',released:'已离纸'};
  function ensureRing(){
    if(b.tip&&ring.parentNode!==b.tip.parentNode){
      b.tip.parentNode.insertBefore(ring,b.tip);
    }
  }
  function fmt(ms){
    const secs=Math.floor(ms/1000);
    return String(Math.floor(secs/60)).padStart(2,'0')+':'+
      String(secs%60).padStart(2,'0');
  }
  function chart(plan,spatial){
    const c=$('pressureCurve'),ctx=c.getContext('2d');
    const W=c.width,H=c.height,left=53,right=W-22,top=20,bottom=H-38;
    ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='#e2e7ea';ctx.lineWidth=1;
    for(const p of [0,.25,.5,.75,1]){
      const y=bottom-(bottom-top)*p;
      ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();
      ctx.fillStyle='#6b7681';ctx.font='16px system-ui';ctx.textAlign='right';
      ctx.fillText(Math.round(p*100)+'%',left-9,y+5);
    }
    ctx.textAlign='center';ctx.fillStyle='#66747d';
    for(const p of [0,.25,.5,.75,1]){
      const x=left+(right-left)*p;
      ctx.fillText(Math.round(p*100)+'%',x,H-12);
    }
    ctx.strokeStyle='#b63b4c';ctx.lineWidth=4;ctx.lineJoin='round';
    ctx.beginPath();
    P.curve(plan,192).forEach((d,i)=>{
      const x=left+d.progress*(right-left);
      const y=bottom-d.pressure*(bottom-top);
      if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);
    });
    ctx.stroke();
    const x=left+spatial*(right-left);
    const y=bottom-P.pressureAt(plan,spatial)*(bottom-top);
    ctx.strokeStyle='#347e91';ctx.lineWidth=2;ctx.beginPath();
    ctx.moveTo(x,top);ctx.lineTo(x,bottom);ctx.stroke();
    ctx.fillStyle='#347e91';ctx.beginPath();ctx.arc(x,y,7,0,2*Math.PI);ctx.fill();
    ctx.fillStyle='#657581';ctx.font='16px system-ui';ctx.textAlign='left';
    ctx.fillText('归一化接触力度（非实测）',left+10,top+15);
  }
  function render(){
    a.elapsed=elapsed;b.elapsed=elapsed;
    a.render();b.render();ensureRing();
    const frame=T.frameAt(a.timeline,elapsed),plan=plans[frame.index];
    const working=frame.phase==='writing'&&frame.progress>0&&frame.progress<1;
    const pressureState=working?P.snapshot(plan,frame.progress):{
      progress:frame.progress,pressure:0,phase:frame.phase==='finished'?
        'released':'hover',measured:false};
    const value=pressureState.pressure;
    if(working&&showPressure){
      const cx=b.tip.getAttribute('cx'),cy=b.tip.getAttribute('cy');
      const radius=7.2+8.8*value;
      b.tip.setAttribute('r',radius.toFixed(3));
      b.tip.setAttribute('fill','#9f3342');
      b.tip.setAttribute('stroke','#712b37');
      b.tip.setAttribute('stroke-width','1');
      ring.setAttribute('cx',cx);ring.setAttribute('cy',cy);
      ring.setAttribute('r',(radius+4+5*value).toFixed(3));
      ring.style.display='';
    }else{
      b.tip.setAttribute('r','8');
      b.tip.setAttribute('fill','#BD3945');
      b.tip.setAttribute('stroke','#FFFFFF');
      b.tip.setAttribute('stroke-width','2.5');
      ring.style.display='none';
    }
    $('pressureValue').textContent=Math.round(value*100)+'%';
    $('pressureFill').style.width=(100*value).toFixed(2)+'%';
    $('pressurePhase').textContent=phaseNames[pressureState.phase]||
      pressureState.phase;
    $('strokeNumber').textContent=(frame.index+1)+' / '+glyph.strokes.length;
    $('pressureSource').textContent='合成参数';
    $('seek').value=total===0?0:Math.round(elapsed/total*1000);
    $('clock').textContent=fmt(elapsed)+' / '+fmt(total);
    $('play').textContent=playing?'Ⅱ 暂停':'▶ 同步播放';
    chart(plan,frame.progress);
    mostRecent={elapsed,frame,pressure:pressureState,visualCircle:{
      cx:Number(b.tip.getAttribute('cx')),cy:Number(b.tip.getAttribute('cy')),
      radius:Number(b.tip.getAttribute('r'))}};
    return mostRecent;
  }
  function pause(){playing=false;lastTick=null;render();}
  function seek(ms){if(!Number.isFinite(ms))throw Error('Nonfinite lab seek');
    playing=false;lastTick=null;elapsed=Math.max(0,Math.min(total,ms));return render();}
  function select(value){
    const selected=typeof value==='string'?
      glyphs.find(g=>g.character===value):value;
    if(!glyphs.includes(selected))throw Error('Unknown experimental glyph');
    playing=false;lastTick=null;glyph=selected;
    const original=JSON.stringify(glyph.strokes);
    a.setGlyph(glyph);b.setGlyph(glyph);
    plans=glyph.strokes.map((stroke,i)=>
      P.makePlan(stroke,candidates.lookup(glyph,i)));
    if(JSON.stringify(glyph.strokes)!==original)
      throw Error('Pressure lab changed canonical stroke evidence');
    elapsed=0;total=a.timeline.totalMs;
    $('glyphs').querySelectorAll('button').forEach(btn=>
      btn.setAttribute('aria-pressed',String(btn.dataset.glyph===glyph.character)));
    return render();
  }
  function setSpeed(value){
    if(!Number.isFinite(value)||value<.5||value>3)
      throw Error('Unsupported shared speed');
    speed=value;
    $('speeds').querySelectorAll('[data-speed]').forEach(btn=>
      btn.setAttribute('aria-pressed',String(Number(btn.dataset.speed)===value)));
    return speed;
  }
  function setIndicator(value){
    showPressure=Boolean(value);
    $('togglePressure').setAttribute('aria-pressed',String(showPressure));
    $('togglePressure').textContent=showPressure?'隐藏力度指示':'显示力度指示';
    render();return showPressure;
  }
  function tick(time){
    if(!playing)return;
    if(lastTick!==null)elapsed=Math.min(total,elapsed+
      Math.max(0,time-lastTick)*speed);
    lastTick=time;
    if(elapsed>=total){playing=false;lastTick=null;render();return;}
    render();requestAnimationFrame(tick);
  }
  function play(){
    if(playing)return;
    if(elapsed>=total)elapsed=0;
    playing=true;lastTick=null;render();requestAnimationFrame(tick);
  }
  for(const item of glyphs){
    const btn=document.createElement('button');
    btn.type='button';btn.dataset.glyph=item.character;
    btn.textContent=item.character;btn.setAttribute('aria-pressed','false');
    btn.addEventListener('click',()=>select(item));
    $('glyphs').appendChild(btn);
  }
  $('play').addEventListener('click',()=>playing?pause():play());
  $('restart').addEventListener('click',()=>{seek(0);play();});
  $('nextStroke').addEventListener('click',()=>{
    const i=a.getState().index;
    seek(T.strokeStart(a.timeline,(i+1)%glyph.strokes.length));
  });
  $('togglePressure').addEventListener('click',()=>setIndicator(!showPressure));
  $('seek').addEventListener('input',e=>seek(total*Number(e.target.value)/1000));
  $('speeds').querySelectorAll('[data-speed]').forEach(btn=>
    btn.addEventListener('click',()=>setSpeed(Number(btn.dataset.speed))));
  window.ZITIE_PRESSURE_LAB={
    glyphs,baseline:a,experimental:b,ring,select,seek,play,pause,setSpeed,
    setIndicator,render,
    get glyph(){return glyph;},get plans(){return plans;},
    get speed(){return speed;},get elapsed(){return elapsed;},
    get total(){return total;},get playing(){return playing;},
    get showPressure(){return showPressure;},get state(){return mostRecent;}
  };
  select(glyphs[0]);
});
