/* A2.1 isolated A/B experiment. NEVER swap the published main renderer.
 * Both panels use the original A1.3 source-clipped round brush and SVG
 * silhouette. Only the B-side spatial timing and visual tip follow the
 * explicitly unreviewed basic-stroke grammar.
 */
window.addEventListener('DOMContentLoaded',function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const NS='http://www.w3.org/2000/svg';
  const T=window.ZitieTimeline,M=window.ZitieMotion;
  const P=window.ZitieStrokePrimitives;
  const Player=window.ZitiePlayer.StrokePlayer;
  const examples=[
    {character:'一',index:0,label:'横 · 一'},
    {character:'十',index:1,label:'竖 · 十'},
    {character:'人',index:0,label:'撇 · 人'},
    {character:'口',index:1,label:'折 · 口'},
    {character:'水',index:0,label:'钩 · 水'},
    {character:'月',index:1,label:'折钩 · 月'},
    {character:'龠',index:13,label:'复杂折 · 龠'}
  ];
  const glyphs=window.ZITIE_SAMPLES.glyphs;
  const baseline=new Player({svg:$('baselineStage')});
  const experimental=new Player({svg:$('gestureStage')});
  let selection=null,glyph=null,plan=null,elapsed=0,total=0,
    playing=false,lastTick=null,speed=1,showPath=true,lastState=null,
    pathGuide=null;
  function sourceContains(svg,stroke){
    const group=svg.querySelector('g[transform]');
    if(!group)throw Error('Unable to access source SVG drawing group');
    const temp=document.createElementNS(NS,'path');
    temp.setAttribute('d',stroke.outline);
    temp.setAttribute('opacity','0');
    temp.setAttribute('fill','#000');
    temp.setAttribute('pointer-events','none');
    group.appendChild(temp);
    const contains=typeof temp.isPointInFill==='function'&&
      typeof DOMPoint!=='undefined'?
      (x,y)=>temp.isPointInFill(new DOMPoint(x,y)):null;
    return {contains,clear:()=>temp.remove()};
  }
  function profileForSelected(target,g){
    const stroke=g.strokes[target.index],probe=sourceContains(experimental.svg,stroke);
    try{
      return P.makePlan(stroke,P.semantics(g,target.index),probe.contains);
    }finally{probe.clear();}
  }
  function makeGuide(g){
    if(pathGuide)pathGuide.remove();
    const group=experimental.svg.querySelector('g[transform]');
    if(!group)throw Error('A2 cannot find source-space visual group');
    pathGuide=document.createElementNS(NS,'path');
    const coords=plan.geometry.samples;
    const d=coords.map((p,i)=>(i?'L ':'M ')+
      p.x.toFixed(3)+' '+p.y.toFixed(3)).join(' ');
    pathGuide.setAttribute('d',d);
    pathGuide.setAttribute('stroke','#157B89');
    pathGuide.setAttribute('stroke-width','3');
    pathGuide.setAttribute('stroke-linecap','round');
    pathGuide.setAttribute('stroke-linejoin','round');
    pathGuide.setAttribute('stroke-dasharray','9 11');
    pathGuide.setAttribute('opacity','.48');
    pathGuide.setAttribute('fill','none');
    pathGuide.setAttribute('pointer-events','none');
    group.insertBefore(pathGuide,experimental.tip);
    pathGuide.style.display=showPath?'':'none';
  }
  function invertOriginal(stage,target){
    const p=Math.max(0,Math.min(1,target));
    if(p===0||p===1)return p;
    let lo=0,hi=1;
    for(let i=0;i<36;i++){
      const mid=(lo+hi)*.5;
      if(stage.motion.progressAt(mid)<p)lo=mid;
      else hi=mid;
    }
    return (lo+hi)*.5;
  }
  function velocityGraph(now){
    const canvas=$('velocityChart'),ctx=canvas.getContext('2d');
    const w=canvas.width,h=canvas.height;
    const left=46,right=w-20,top=17,bottom=h-28;
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle='white';ctx.fillRect(0,0,w,h);
    ctx.strokeStyle='#e4e8e9';ctx.lineWidth=1;
    for(let i=0;i<=4;i++){
      const y=top+(bottom-top)*i/4;
      ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();
    }
    const stage=baseline.timeline.strokes[selection.index];
    const vOld=t=>{
      const d=.002,a=Math.max(0,t-d),b=Math.min(1,t+d);
      return (stage.motion.progressAt(b)-stage.motion.progressAt(a))/(b-a||1);
    };
    const vNew=t=>plan.timing.speedAt(t);
    const traces=[[vOld,'#9aa5ad'],[vNew,'#167e8a']];
    for(const [curve,color] of traces){
      ctx.strokeStyle=color;ctx.lineWidth=3.3;
      ctx.beginPath();
      for(let i=0;i<=220;i++){
        const t=i/220;
        const x=left+(right-left)*t;
        const y=bottom-(bottom-top)*Math.min(3.8,curve(t))/3.8;
        if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);
      }
      ctx.stroke();
    }
    ctx.strokeStyle='#a23a46';ctx.lineWidth=2;
    const cursor=left+(right-left)*Math.max(0,Math.min(1,now));
    ctx.beginPath();ctx.moveTo(cursor,top);ctx.lineTo(cursor,bottom);ctx.stroke();
    ctx.fillStyle='#6b7a84';ctx.font='14px system-ui';
    ctx.textAlign='left';ctx.fillText('起笔',left,bottom+19);
    ctx.textAlign='right';ctx.fillText('收笔',right,bottom+19);
  }
  function render(){
    if(!selection||!plan)return null;
    const stage=baseline.timeline.strokes[selection.index];
    baseline.elapsed=elapsed;
    baseline.render();
    const frame=T.frameAt(baseline.timeline,elapsed);
    const selected=frame.phase==='writing'&&frame.index===selection.index;
    const t=selected?frame.timeProgress:frame.index<selection.index?0:1;
    const expProgress=plan.timing.progressAt(t);
    if(selected){
      experimental.elapsed=stage.startMs+
        invertOriginal(stage,expProgress)*stage.durationMs;
    }else experimental.elapsed=elapsed;
    experimental.render();
    const state=plan.stateAt(t);
    if(selected&&experimental.tip.style.display!=='none'){
      // Appearance-only candidate trajectory. The ORIGINAL median still
      // drives the true source-color brush fill; this must not mutate it.
      experimental.tip.setAttribute('cx',state.point.x.toFixed(4));
      experimental.tip.setAttribute('cy',state.point.y.toFixed(4));
      experimental.tip.setAttribute('fill','#177987');
      experimental.tip.setAttribute('stroke','#0E5863');
      experimental.tip.setAttribute('stroke-width','2');
    }
    if(pathGuide)pathGuide.style.display=showPath?'':'none';
    $('phase').textContent=selected?state.label:frame.phase==='finished'?'已收笔':'待落笔';
    $('baselineProgress').textContent=Math.round(
      selected?frame.progress*100:t*100)+'%';
    $('gestureProgress').textContent=Math.round(expProgress*100)+'%';
    $('geometryStatus').textContent=plan.geometry.outsideSourceSamples===0?
      (plan.geometry.verification==='source_svg_fill_probe'?'轮廓内':'未核源轮廓'):
      '来源轨迹有越界';
    $('seek').value=total?Math.round(elapsed/total*1000):0;
    const totalSeconds=baseline.timeline.totalMs/1000;
    $('clock').textContent=(elapsed/1000).toFixed(2)+' / '+
      totalSeconds.toFixed(2)+'s';
    $('play').textContent=playing?'Ⅱ 暂停':'▶ 同步播放';
    velocityGraph(t);
    lastState={frame,stage,t,experimentalProgress:expProgress,
      sourceProgress:selected?frame.progress:t,
      state,tip:{x:+experimental.tip.getAttribute('cx'),
        y:+experimental.tip.getAttribute('cy')},
      glyph:glyph.character,sourceStroke:selection.index,elapsed,
      gesture:plan.sem.kind};
    return lastState;
  }
  function seek(time){
    if(!Number.isFinite(time))throw Error('Invalid A2 seek');
    playing=false;lastTick=null;elapsed=Math.max(0,Math.min(total,time));
    return render();
  }
  function select(entry){
    const target=typeof entry==='string'?
      examples.find(x=>x.character===entry):entry;
    if(!examples.includes(target))throw Error('Unknown A2 stroke example');
    playing=false;lastTick=null;selection=target;
    glyph=glyphs.find(x=>x.character===target.character);
    if(!glyph)throw Error('Missing pinned source glyph');
    const original=JSON.stringify(glyph.strokes);
    baseline.setGlyph(glyph);experimental.setGlyph(glyph);
    plan=profileForSelected(target,glyph);
    makeGuide(glyph);
    if(original!==JSON.stringify(glyph.strokes))
      throw Error('A2 prototype changed source vectors');
    total=baseline.timeline.totalMs;
    elapsed=baseline.timeline.strokes[target.index].startMs;
    $('glyphButtons').querySelectorAll('button').forEach(btn=>
      btn.setAttribute('aria-pressed',
        String(btn.dataset.character===target.character)));
    $('geometryNote').textContent=
      glyph.character+' · '+glyph.strokes[target.index].name+
      '：'+plan.geometry.smoothedSegments+'段候选曲线；'+
      plan.geometry.rejectedSegments+'段回退原中心线；'+
      plan.geometry.outsideSourceSamples+'个采样点不在源SVG内部；'+
      '与源折点的最大局部偏移 '+plan.geometry.maxDeviation.toFixed(2)+
      ' 坐标单位。模型仍为工程假设，非教材规范证据。';
    return render();
  }
  function tick(time){
    if(!playing)return;
    if(lastTick!==null)elapsed=Math.min(total,
      elapsed+Math.max(0,time-lastTick)*speed);
    lastTick=time;
    if(elapsed>=total){playing=false;lastTick=null;render();return;}
    render();requestAnimationFrame(tick);
  }
  function play(){
    if(playing)return;
    if(elapsed>=total)elapsed=baseline.timeline.strokes[selection.index].startMs;
    playing=true;lastTick=null;render();requestAnimationFrame(tick);
  }
  function pause(){playing=false;lastTick=null;render();}
  function setSpeed(value){
    const v=Number(value);
    if(![.5,1,1.5,2,3].includes(v))throw Error('Invalid A2 speed');
    speed=v;
    $('speedButtons').querySelectorAll('button').forEach(btn=>
      btn.setAttribute('aria-pressed',String(+btn.dataset.speed===v)));
  }
  for(const target of examples){
    const btn=document.createElement('button');
    btn.type='button';btn.dataset.character=target.character;
    btn.textContent=target.label;
    btn.setAttribute('aria-pressed','false');
    btn.addEventListener('click',()=>select(target));
    $('glyphButtons').appendChild(btn);
  }
  $('play').addEventListener('click',()=>playing?pause():play());
  $('replay').addEventListener('click',()=>{
    seek(baseline.timeline.strokes[selection.index].startMs);play();
  });
  $('showAll').addEventListener('click',()=>seek(total));
  $('showPath').addEventListener('click',()=>{
    showPath=!showPath;
    $('showPath').setAttribute('aria-pressed',String(showPath));
    $('showPath').textContent=showPath?'隐藏候选轨迹':'显示候选轨迹';
    render();
  });
  $('speedButtons').addEventListener('click',e=>{
    const btn=e.target.closest('button[data-speed]');
    if(btn)setSpeed(btn.dataset.speed);
  });
  $('seek').addEventListener('input',e=>seek(total*(+e.target.value)/1000));
  window.ZITIE_A2_LAB={
    examples,baseline,experimental,select,seek,render,play,pause,
    setSpeed,invertOriginal,
    get glyph(){return glyph;},get selection(){return selection;},
    get plan(){return plan;},get state(){return lastState;},
    get pathGuide(){return pathGuide;},
    get elapsed(){return elapsed;},get total(){return total;},
    get speed(){return speed;},get playing(){return playing;}
  };
  select(examples[4]); // 水竖钩 is the most useful fold/flick demonstration.
});
