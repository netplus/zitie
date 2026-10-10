/* A1.2.2 offline gallery + motion-aware playback controls; one timeline. */
window.addEventListener('DOMContentLoaded', function () {
  'use strict';
  const pack=window.ZITIE_SAMPLES;
  if(!pack||pack.schema_version!==1||!Array.isArray(pack.glyphs))
    throw new Error('Offline canonical sample data unavailable');
  const $=id=>document.getElementById(id);
  const glyphs=pack.glyphs;
  const gallery=window.ZitieGallery;
  const selector=$('glyphGallery'),filterRow=$('batchFilters');
  const play=$('play'),speedButtons=$('speedButtons'),seek=$('timelineSeek');
  const penStyleButtons=$('penStyleOptions');
  const penToolButtons=$('penToolOptions');
  const penStyle=new window.ZitiePressureStyle.StyleController();
  // One canonical clock: original legacy StrokePlayer owns time/actions;
  // rigid hardpen renders passively from those same source stroke timestamps.
  const hardpen=new window.ZitieHardpenStage.HardpenStage({
    svg:$('hardpenStage'),width:26});
  let penTool='hardpen'; // User-chosen default is ordinary rigid hardpen.
  let speed=1;
  let query='',batch='all',selectedId=null,visibleGlyphs=[];
  const player=new window.ZitiePlayer.StrokePlayer({
    svg:$('glyphStage'),status:$('state'),
    onUpdate(state){
      if(!state)return;
      let activePlayer=player,visualState=state;
      let hardState=null;
      if(hardpen.glyph===player.timeline?.glyph){
        hardState=hardpen.render(state);
        if(penTool==='hardpen'){
          // Keep hidden legacy renderer unmodified and remove any old halo.
          penStyle.resetTip(player.tip);
          activePlayer=hardpen.getAdapter();
          visualState={...state,progress:hardState.progress};
        }else{
          // A1.3 brush remains selectable, byte-for-byte original ink/pen.
          penStyle.resetTip(hardpen.tip);
        }
      }
      const force=penStyle.apply(activePlayer,visualState);
      updatePressureView(force);
      play.textContent=state.playing?'Ⅱ 暂停':'▶ 播放笔顺';
      play.setAttribute('aria-label',state.playing?'暂停书写动画':'播放书写动画');
      seek.value=String(Math.round(state.elapsedMs/state.totalMs*1000));
      $('timelineReadout').textContent=formatTime(state.elapsedMs)+' / '+formatTime(state.totalMs);
      $('strokeIndex').textContent='第 '+(state.index+1)+' / '+state.count+' 笔';
      const stroke=player.timeline.glyph.strokes[state.index];
      $('strokeName').textContent=stroke.name_status==='reviewed'?stroke.name:'第'+(state.index+1)+'笔';
      const motionLabel=penTool==='hardpen'&&hardState?
        hardState.label:state.motion&&state.motion.label;
      $('strokePhase').textContent=state.phase==='finished'?'已完成':
        state.phase==='pause'?'观察笔形':
        (motionLabel ? motionLabel+' · '+(state.playing?'运笔中':'预览位置') :
         (state.playing?'正在书写':'待播放'));
    }
  });
  const phaseLabels={
    hover:'未落笔',touch:'轻触起笔',travel:'匀力行笔',
    pivot:'转锋顿笔',flick:'出钩提笔',lift:'收锋提笔',released:'已离纸'
  };
  function drawPressureTrace(force){
    const canvas=$('pressureCurve'),ctx=canvas.getContext('2d');
    if(!ctx)return;
    const w=canvas.width,h=canvas.height;
    const left=22,right=w-13,top=10,bottom=h-22;
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle='#fafbfb';ctx.fillRect(0,0,w,h);
    ctx.strokeStyle='#e4e8ea';ctx.lineWidth=1;
    for(const p of [0,.5,1]){
      const y=bottom-p*(bottom-top);
      ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();
    }
    ctx.strokeStyle='#b63b48';ctx.lineWidth=3;ctx.lineJoin='round';
    ctx.beginPath();
    force.curve.forEach((sample,i)=>{
      const x=left+(right-left)*sample.progress;
      const y=bottom-(bottom-top)*sample.pressure;
      if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);
    });
    ctx.stroke();
    const at=left+(right-left)*force.progress;
    ctx.strokeStyle='#287c8d';ctx.lineWidth=1.6;ctx.beginPath();
    ctx.moveTo(at,top);ctx.lineTo(at,bottom);ctx.stroke();
    ctx.fillStyle='#287c8d';ctx.beginPath();
    ctx.arc(at,bottom-force.pressure*(bottom-top),5,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#6a7780';ctx.font='12px system-ui';
    ctx.fillText('起',left,bottom+16);ctx.textAlign='right';
    ctx.fillText('收',right,bottom+16);ctx.textAlign='start';
  }
  function updatePressureView(force){
    const simulated=force.mode==='simulated';
    $('pressureDetails').hidden=!simulated;
    $('penStyleHint').textContent=simulated?
      '模拟笔压版 · 力度随起笔、转锋和收笔渐变；不改变原始墨迹与笔速':
      '稳定版 · 原有圆头笔尖与书写节奏';
    if(!simulated)return;
    $('pressureValue').textContent=Math.round(force.pressure*100)+'%';
    $('pressureFill').style.width=(force.pressure*100).toFixed(2)+'%';
    $('pressurePhase').textContent=phaseLabels[force.phase]||force.phase;
    drawPressureTrace(force);
  }
  const formatTime=ms=>{
    const seconds=Math.floor(ms/1000);
    return String(Math.floor(seconds/60)).padStart(2,'0')+':'+
      String(seconds%60).padStart(2,'0');
  };
  glyphs.forEach(g=>window.ZitieTimeline.validateGlyph(g));
  const selectGlyph=g=>{
    if(!g)return;
    selectedId=g.main_id;
    player.setGlyph(g);
    hardpen.setGlyph(g,player.timeline);
    player.setSpeed(speed);
    $('selectedGlyph').textContent=g.character;
    $('selectedMeta').textContent=g.expected_stroke_count+' 画 · '+g.batch_id+
      ' · 主部首 #'+g.main_id;
    document.title=g.character+' · 动态笔顺 — zitie';
    renderTiles();
  };
  function renderFilters(){
    filterRow.replaceChildren();
    for(const id of ['all',...gallery.batches(glyphs)]){
      const count=id==='all'?glyphs.length:glyphs.filter(g=>g.batch_id===id).length;
      const b=document.createElement('button');
      b.type='button';
      b.className='filter'+(batch===id?' active':'');
      b.setAttribute('aria-pressed',String(batch===id));
      b.textContent=(id==='all'?'全部':id)+' · '+count;
      b.addEventListener('click',()=>{
        batch=id;renderFilters();refresh();
      });
      filterRow.append(b);
    }
  }
  function renderTiles(){
    const fragment=document.createDocumentFragment();
    visibleGlyphs.forEach(g=>{
      const button=document.createElement('button');
      button.className='glyphTile'+(g.main_id===selectedId?' selected':'');
      button.type='button';
      button.dataset.glyphId=String(g.main_id);
      button.setAttribute('aria-pressed',String(g.main_id===selectedId));
      button.setAttribute('aria-label',g.character+'，'+g.expected_stroke_count+
        '画，'+g.batch_id+(g.main_id===selectedId?'，当前选择':''));
      const glyph=document.createElement('span');
      glyph.className='glyphSymbol';glyph.textContent=g.character;
      const count=document.createElement('span');
      count.className='glyphCount';count.textContent=g.expected_stroke_count+'画';
      button.append(glyph,count);
      button.addEventListener('click',()=>selectGlyph(g));
      fragment.append(button);
    });
    selector.replaceChildren(fragment);
    $('libraryCount').textContent='显示 '+visibleGlyphs.length+' / '+glyphs.length+' 个工程样例';
    $('emptyState').hidden=visibleGlyphs.length>0;
  }
  function refresh(){
    visibleGlyphs=gallery.filteredGlyphs(glyphs,query,batch);
    if(visibleGlyphs.length>0&&!visibleGlyphs.some(g=>g.main_id===selectedId))
      selectGlyph(visibleGlyphs[0]);
    else renderTiles();
  }
  const navigate=offset=>{
    const g=gallery.neighbor(visibleGlyphs,selectedId,offset);
    if(g)selectGlyph(g);
  };
  $('glyphSearch').addEventListener('input',e=>{
    query=e.target.value;refresh();
  });
  $('clearSearch').addEventListener('click',()=>{
    $('glyphSearch').value='';query='';batch='all';renderFilters();refresh();
    $('glyphSearch').focus();
  });
  $('previousGlyph').addEventListener('click',()=>navigate(-1));
  $('nextGlyph').addEventListener('click',()=>navigate(1));
  play.addEventListener('click',()=>player.playing?player.pause():player.play());
  $('restart').addEventListener('click',()=>player.restart());
  $('previous').addEventListener('click',()=>player.previous());
  $('next').addEventListener('click',()=>player.next());
  $('replayOne').addEventListener('click',()=>player.replayStroke());
  $('showAll').addEventListener('click',()=>player.showAll());
  function setSpeed(value){
    const num=Number(value);
    if(!Number.isFinite(num)||![0.5,1,1.5,2,3].includes(num))
      throw new Error('Invalid playback speed button');
    speed=num;
    player.setSpeed(num);
    speedButtons.querySelectorAll('button[data-speed]').forEach(button=>{
      const selected=Number(button.dataset.speed)===num;
      button.classList.toggle('active',selected);
      button.setAttribute('aria-pressed',String(selected));
    });
  }
  function setPenTool(value){
    if(value!=='hardpen'&&value!=='brush')
      throw Error('Unsupported writing pen tool');
    penTool=value;
    penToolButtons.querySelectorAll('button[data-pen-tool]').forEach(btn=>{
      btn.setAttribute('aria-pressed',String(btn.dataset.penTool===penTool));
    });
    for(const [kind,stage] of [
      ['hardpen',$('hardpenStage')],['brush',$('glyphStage')]]){
      const visible=kind===penTool;
      stage.classList.toggle('active',visible);
      stage.setAttribute('aria-hidden',String(!visible));
    }
    $('penToolHint').textContent=penTool==='hardpen'?
      '普通硬笔 · 近乎恒定线宽、短促转折、自然提笔；轨迹仍属工程预览':
      '毛笔（原版）· 保留既有SVG书法轮廓和稳定圆头墨迹';
    // A visual-only tool choice: elapsed, playing, speed, selected glyph,
    // and same old timeline must remain identical.
    if(player.timeline)player.render();
    return penTool;
  }
  penToolButtons.addEventListener('click',event=>{
    const button=event.target.closest('button[data-pen-tool]');
    if(button&&penToolButtons.contains(button))
      setPenTool(button.dataset.penTool);
  });
  function setPenStyle(value){
    const selected=penStyle.setMode(value);
    penStyleButtons.querySelectorAll('button[data-pen-style]').forEach(button=>{
      const active=button.dataset.penStyle===selected;
      button.setAttribute('aria-pressed',String(active));
    });
    // Changing the *visual* mode must not call pause(), seek() or
    // change the selected glyph, elapsed time, speed or active stroke.
    player.render();
    return selected;
  }
  penStyleButtons.addEventListener('click',event=>{
    const button=event.target.closest('button[data-pen-style]');
    if(button&&penStyleButtons.contains(button))
      setPenStyle(button.dataset.penStyle);
  });
  speedButtons.addEventListener('click',event=>{
    const button=event.target.closest('button[data-speed]');
    if(button) setSpeed(button.dataset.speed);
  });
  seek.addEventListener('input',e=>{
    if(player.timeline)player.seekElapsed(Number(e.target.value)/1000*player.timeline.totalMs);
  });
  document.addEventListener('keydown',e=>{
    const target=e.target;
    if(e.altKey||e.ctrlKey||e.metaKey||
       (target&&typeof target.closest==='function'&&
        target.closest('input,textarea,select,button,[contenteditable]')))return;
    const lower=e.key.toLowerCase();
    if(e.code==='Space'){e.preventDefault();player.playing?player.pause():player.play();}
    else if(lower==='a'){e.preventDefault();navigate(-1);}
    else if(lower==='d'){e.preventDefault();navigate(1);}
    else if(lower==='r'){e.preventDefault();player.restart();}
  });
  renderFilters();
  visibleGlyphs=glyphs.slice();
  selectGlyph(glyphs[0]);
  window.ZITIE_A1_APP=player; // Legacy A1.3 source SVG remains accessible for QA.
  window.ZITIE_A1_SPEED={get:()=>speed,set:setSpeed};
  window.ZITIE_A1_HARDPEN=hardpen;
  window.ZITIE_A1_PEN_TOOL={get:()=>penTool,set:setPenTool,
    getState:()=>hardpen.state,getDefault:()=> 'hardpen'};
  window.ZITIE_A1_PEN_STYLE={get:()=>penStyle.mode,set:setPenStyle,
    getState:()=>penStyle.state,getRing:()=>penStyle.ring};
  window.ZITIE_A1_GALLERY={getVisible:()=>visibleGlyphs.slice(),
    getSelectedId:()=>selectedId, selectGlyph, navigate};
});