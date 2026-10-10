/* A2.3 Kaishu research UI. One source timeline controls two complete
 * genuine SVG stroke renderers: published basic hardpen vs Kaishu candidate.
 * Never uses or changes original artistic source outlines or teacher data.
 */
window.addEventListener('DOMContentLoaded',function(){
  'use strict';
  const $=id=>document.getElementById(id),T=window.ZitieTimeline;
  const K=window.ZitieKaishuModel;
  const Basic=window.ZitieHardpenStage.HardpenStage;
  const Kaishu=window.ZitieKaishuStage.KaishuStage;
  const samples=window.ZITIE_SAMPLES.glyphs;
  const entries=[
    {char:'一',index:0},
    {char:'十',index:0},
    {char:'人',index:0},
    {char:'火',index:2},
    {char:'口',index:1},
    {char:'巾',index:1},
    {char:'水',index:0},
    {char:'月',index:1},
    {char:'龠',index:13}
  ];
  const old=new Basic({svg:$('oldStage')});
  const candidate=new Kaishu({svg:$('newStage')});
  let current=null,glyph=null,timeline=null,elapsed=0,total=0,
    speed=1,playing=false,lastTick=null,state=null;
  function chart(){
    const el=$('comparisonChart'),ctx=el.getContext('2d');
    const w=el.width,h=el.height,left=28,right=w-20,top=19,bottom=h-25;
    ctx.clearRect(0,0,w,h);ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);
    ctx.strokeStyle='#e6eaec';ctx.lineWidth=1;
    for(let i=0;i<=4;i++){
      const y=top+i*(bottom-top)/4;
      ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();
    }
    ctx.lineWidth=3.0;ctx.strokeStyle='#318391';ctx.beginPath();
    const a=old.rows[current.index].plan,
      b=candidate.rows[current.index].plan;
    let max=0,displacements=[];
    for(let i=0;i<=120;i++){
      const p=i/120;
      const A=a.stateAt(p).point,B=b.stateAt(p).point;
      const d=Math.hypot(A.x-B.x,A.y-B.y);
      max=Math.max(max,d);displacements.push(d);
    }
    const bound=Math.max(25,Math.ceil(max/10)*10);
    displacements.forEach((d,i)=>{
      const x=left+(right-left)*i/(displacements.length-1),
        y=bottom-(bottom-top)*d/bound;
      if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);
    });
    ctx.stroke();ctx.textAlign='left';ctx.font='13px system-ui';
    ctx.fillStyle='#65737b';ctx.fillText('0',left,bottom+17);
    ctx.textAlign='right';ctx.fillText('笔画终点',right,bottom+17);
  }
  function describe(){
    const row=candidate.rows[current.index],plan=row.plan;
    let text='形态：'+plan.semantics.label+
      '；候选控制节点 '+plan.revisedControlPoints.length+
      ' 个；生成方法：'+plan.revisedSource+
      '。源中心线与SVG轮廓均未修改。';
    if(plan.semantics.kind==='heng'){
      const measure=K.horizontalMetrics(plan);
      $('shapeQuality').textContent='横角度 '+measure.angleDeg.toFixed(1)+'°';
      text+=' 横画向右上角度 '+measure.angleDeg.toFixed(2)+
        '°，偏离直线的最大摆幅 '+measure.maxNormalDeviation.toFixed(2)+' 单位。';
    }else if(plan.semantics.kind==='shu'){
      const measure=K.verticalMetrics(plan);
      $('shapeQuality').textContent='竖摆幅 '+measure.maxNormalDeviation.toFixed(1);
      text+=' 竖画最大偏移 '+measure.maxNormalDeviation.toFixed(2)+' 单位。';
    }else if(plan.revisedHookVertex!==null){
      $('shapeQuality').textContent='短钩＋精细收笔';
    }else if(plan.revisedFoldVertex!==null){
      $('shapeQuality').textContent='折前稳行笔';
    }else{
      $('shapeQuality').textContent='起行收独立';
    }
    text+=' 字体结构的方整性仍须人工验收，不能由少数曲率指标认证。';
    $('diagnosticText').textContent=text;
    chart();
  }
  function render(){
    if(!timeline)throw Error('No Kaishu source timeline');
    const frame=T.frameAt(timeline,elapsed);
    const a=old.render(frame),b=candidate.render(frame);
    $('clock').textContent=(elapsed/1000).toFixed(2)+' / '+
      (total/1000).toFixed(2)+'s';
    $('seek').value=total?Math.round(1000*elapsed/total):0;
    $('play').textContent=playing?'Ⅱ 暂停':'▶ 同步播放';
    $('phase').textContent=frame.phase==='finished'?'完整字形':
      frame.phase==='pause'?'笔间停顿':b.label;
    state={frame,elapsed,old:a,new:b,selection:current,
      oldStroke:old.rows[current.index].plan,
      newStroke:candidate.rows[current.index].plan};
    return state;
  }
  function pause(){playing=false;lastTick=null;return render();}
  function seek(ms){
    if(!Number.isFinite(ms))throw Error('Invalid Kaishu timeline seek');
    playing=false;lastTick=null;
    elapsed=Math.max(0,Math.min(total,ms));
    return render();
  }
  function select(value){
    const target=typeof value==='string'?
      entries.find(e=>e.char===value):value;
    if(!entries.includes(target))throw Error('Unknown Kaishu study glyph');
    current=target;glyph=samples.find(g=>g.character===target.char);
    if(!glyph)throw Error('Original glyph source is unavailable');
    const before=JSON.stringify(glyph.strokes);
    timeline=T.buildTimeline(glyph);
    old.setGlyph(glyph,timeline);candidate.setGlyph(glyph,timeline);
    if(JSON.stringify(glyph.strokes)!==before)
      throw Error('Experiment wrote into original source medians');
    total=timeline.totalMs;elapsed=total;
    playing=false;lastTick=null;
    $('glyphName').textContent=glyph.character+' · '+glyph.strokes.length+'画';
    $('glyphs').querySelectorAll('button').forEach(b=>
      b.setAttribute('aria-pressed',
        String(b.dataset.char===glyph.character)));
    describe();return render();
  }
  function play(){
    if(playing)return;
    if(elapsed>=total)elapsed=0;
    playing=true;lastTick=null;render();
    requestAnimationFrame(tick);
  }
  function tick(now){
    if(!playing)return;
    if(lastTick!==null)elapsed=Math.min(total,elapsed+
      Math.max(0,now-lastTick)*speed);
    lastTick=now;
    if(elapsed>=total){playing=false;lastTick=null;render();return;}
    render();requestAnimationFrame(tick);
  }
  function setSpeed(v){
    const n=+v;
    if(![.5,1,1.5,2].includes(n))throw Error('Invalid Kaishu animation rate');
    speed=n;$('speeds').querySelectorAll('button').forEach(b=>
      b.setAttribute('aria-pressed',String(+b.dataset.speed===n)));
  }
  entries.forEach(item=>{
    const btn=document.createElement('button');
    btn.type='button';btn.dataset.char=item.char;btn.textContent=item.char;
    btn.setAttribute('aria-pressed','false');
    btn.addEventListener('click',()=>select(item));
    $('glyphs').append(btn);
  });
  $('play').addEventListener('click',()=>playing?pause():play());
  $('replay').addEventListener('click',()=>{seek(0);play();});
  $('showAll').addEventListener('click',()=>seek(total));
  $('seek').addEventListener('input',e=>seek(total*+e.target.value/1000));
  $('speeds').addEventListener('click',e=>{
    const btn=e.target.closest('button[data-speed]');
    if(btn)setSpeed(btn.dataset.speed);
  });
  window.ZITIE_A23_KAISHU={entries,old,candidate,select,seek,render,
    pause,play,setSpeed,
    get glyph(){return glyph;},get selection(){return current;},
    get timeline(){return timeline;},get elapsed(){return elapsed;},
    get total(){return total;},get speed(){return speed;},
    get playing(){return playing;},get state(){return state;}};
  select('一'); // The original waving 一 exposes the hardpen root cause.
});
