/* A3: PDF-v0.5.1-backed 201-glyph BRUSH player.
 * Keeps the verified page/step/provenance data read-only; no hardpen,
 * font outlines or remote runtime dependencies. Existing A1 renderer is reused.
 */
window.addEventListener('DOMContentLoaded', function(){
  'use strict';
  const pack=window.ZITIE_BOOK_PACK,T=window.ZitieTimeline;
  const $=id=>document.getElementById(id);
  const required=['paperSvg','status','search','tiles','steps','pdfLink',
    'pressureStyleOptions','pressureDetails','pressureCurve','pressureValue',
    'pressureFill','pressurePhase','pressureStyleHint',
    'writingTipLead','writingTipJump','tipText',
    'pressureStudyTip','pressureStudyCheck'];
  if(!pack||pack.schema_version!==1||
     pack.publication?.version!=='0.5.1'||
     pack.publication?.pages!==299||
     !Array.isArray(pack.glyphs)||pack.glyphs.length!==201||
     !window.ZitiePressureStyle||!window.ZitiePressureModel||
     !window.ZitieGestureCandidates||required.some(id=>!$(id))){
    $('status').textContent='字帖资源不可用：必须通过 PDF 同源数据验证后生成。';
    document.documentElement.setAttribute('data-a3-error','pack');
    return;
  }
  const glyphs=pack.glyphs;
  glyphs.forEach((g,i)=>{
    T.validateGlyph(g);
    if(g.main_id!==i+1||!Number.isInteger(g.pdf_page_start)||
       g.pdf_page_start<1||g.pdf_page_end>299)
      throw Error('A3 indexed PDF glyph integrity error');
  });
  const byId=new Map(glyphs.map(g=>[g.main_id,g]));
  const state={current:null,query:'',batch:'all',visible:glyphs.slice(),
    speed:1,lastFrame:null};
  const $steps=$('steps'),$tiles=$('tiles'),$filters=$('filters');
  // Reuse A1.6's original, proven brush-contact visualization controller.
  // It changes ONLY the nib marker / force ring, never A3.6 source ink.
  const penStyle=new window.ZitiePressureStyle.StyleController();
  const player=new window.ZitiePlayer.StrokePlayer({
    svg:$('paperSvg'),status:$('status'),frontGuard:true,
    onUpdate(s){
      if(!s||!state.current)return;
      state.lastFrame=s;
      // StrokePlayer.setGlyph() calls pause() on the OLD timeline before
      // installing its next glyph. Always use the clock-owned glyph, never
      // a selection that may already refer to the next character.
      const g=player.timeline.glyph;
      const force=penStyle.apply(player,s);
      updatePressureView(force);
      $('stepLabel').textContent='第 '+(s.index+1)+' / '+
        s.count+' 笔 · '+(g.strokes[s.index].name_status==='reviewed'?
          g.strokes[s.index].name:'第'+(s.index+1)+'笔');
      $('phase').textContent=s.phase==='finished'?'全字完成':
        s.phase==='pause'?'当前笔已完成':
        s.motion?.label||'按笔顺逐笔书写';
      $('play').textContent=s.playing?'Ⅱ 暂停':'▶ 播放';
      $('seek').value=String(Math.round(s.elapsedMs/s.totalMs*1000));
      $('clock').textContent=formatTime(s.elapsedMs)+' / '+formatTime(s.totalMs);
      $steps.querySelectorAll('button[data-stroke]').forEach(button=>{
        const current=+button.dataset.stroke===s.index;
        if(current)button.setAttribute('aria-current','step');
        else button.removeAttribute('aria-current');
      });
      setPdfPage(g,s.index);
    }
  });
  const pressurePhaseLabels={
    hover:'未落笔',touch:'轻触起笔',travel:'匀力行笔',
    pivot:'转锋顿笔',flick:'出钩提笔',lift:'收锋提笔',released:'已离纸'
  };
  function drawPressureTrace(force){
    const canvas=$('pressureCurve'),ctx=canvas.getContext('2d');
    if(!ctx||!force.curve)return;
    const w=canvas.width,h=canvas.height;
    const left=22,right=w-13,top=10,bottom=h-22;
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle='#fbf9fc';ctx.fillRect(0,0,w,h);
    ctx.strokeStyle='#e4e8ea';ctx.lineWidth=1;
    for(const p of [0,.5,1]){
      const y=bottom-p*(bottom-top);
      ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();
    }
    ctx.strokeStyle='#b43c48';ctx.lineWidth=3;ctx.lineJoin='round';
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
    ctx.fillStyle='#697680';ctx.font='12px system-ui';
    ctx.fillText('起',left,bottom+16);ctx.textAlign='right';
    ctx.fillText('收',right,bottom+16);ctx.textAlign='start';
  }
  function updatePressureView(force){
    const simulated=force.mode==='simulated';
    $('pressureDetails').hidden=!simulated;
    $('pressureStyleHint').textContent=simulated?
      '模拟版 · 笔尖及曲线提示力度，墨迹不变':
      '稳定版 · 原有笔尖，墨迹不变';
    if(!simulated)return;
    $('pressureValue').textContent=Math.round(force.pressure*100)+'%';
    $('pressureFill').style.width=(force.pressure*100).toFixed(2)+'%';
    $('pressurePhase').textContent=pressurePhaseLabels[force.phase]||force.phase;
    drawPressureTrace(force);
  }
  function setPressureStyle(mode){
    const next=penStyle.setMode(mode);
    $('pressureStyleOptions').querySelectorAll('button[data-pen-style]')
      .forEach(button=>button.setAttribute('aria-pressed',
        String(button.dataset.penStyle===next)));
    // Render the same millisecond frame; never pause/seek/change the mask.
    if(player.timeline)player.render();
    return next;
  }
  function formatTime(ms){
    const n=Math.floor(ms/1000);
    return String(Math.floor(n/60)).padStart(2,'0')+':'+
      String(n%60).padStart(2,'0');
  }
  function setPdfPage(g,strokeIndex){
    const page=g.pdf_page_start+Math.floor(strokeIndex/6);
    if(page<g.pdf_page_start||page>g.pdf_page_end)
      throw Error('A3 PDF step mapping escaped glyph pages');
    $('pdfLink').href=pack.publication.site_url+'#page='+page;
    $('pdfPage').textContent='PDF 第 '+page+' / '+
      pack.publication.pages+' 页'+
      (g.pdf_page_start!==g.pdf_page_end?
        ' · 本字第 '+(page-g.pdf_page_start+1)+'/'+g.pdf_step_pages+' 页':'');
  }
  function renderSteps(g){
    const fragment=document.createDocumentFragment();
    g.strokes.forEach((stroke,i)=>{
      const button=document.createElement('button');
      button.type='button';button.className='step';
      button.dataset.stroke=String(i);
      button.textContent=(i+1)+' '+(stroke.name_status==='reviewed'?
        stroke.name:'第'+(i+1)+'笔');
      button.setAttribute('aria-label','跳至第'+(i+1)+'笔'+
        (stroke.name_status==='reviewed'?'：'+stroke.name:''));
      button.addEventListener('click',()=>player.seekStroke(i));
      fragment.append(button);
    });
    $steps.replaceChildren(fragment);
  }
  function selectGlyph(g){
    if(!g)return;
    state.current=g;
    $('selectedChar').textContent=g.character;
    $('meta').textContent=g.expected_stroke_count+' 画 · '+g.batch_id+
      ' · 主部首 #'+g.main_id;
    $('reading').textContent=g.pinyin||g.reading_note||'本页不单列读音';
    // Surface the exact book-authored hint alongside live stroke progress.
    // The unabridged tips/check remain in #tipText below; no advice is inferred.
    $('writingTipLead').textContent=g.tips[0];
    // Place only already-authored PDF advice in the otherwise unused
    // pressure-side column; no new coaching or inferred correctness.
    $('pressureStudyTip').textContent=g.tips.slice(1).join('；');
    $('pressureStudyCheck').textContent=g.check;
    $('writingTipJump').title='本字书写提示：'+g.tips.join('；')+'；写完检查：'+g.check;
    $('tipText').replaceChildren();
    const notes=[...g.tips,'写完检查：'+g.check];
    for(const tip of notes){
      const p=document.createElement('p');
      p.textContent=tip;$('tipText').append(p);
    }
    renderSteps(g);
    document.title=g.character+' · v0.5.1 字帖笔顺动画';
    player.setGlyph(g);
    player.setSpeed(state.speed);
    renderTiles();
    // The query string is a bookmarkable canonical main ID, not a PDF guess.
    if(window.history&&typeof window.history.replaceState==='function'){
      const url=new URL(window.location.href);
      url.searchParams.set('id',String(g.main_id));
      window.history.replaceState(null,'',url.pathname+url.search+url.hash);
    }
    return g;
  }
  function applyFilter(){
    const q=state.query.trim().toLocaleLowerCase();
    state.visible=glyphs.filter(g=>
      (state.batch==='all'||g.batch_id===state.batch)&&
      (!q||[
        g.character,g.batch_id,String(g.main_id),
        g.pinyin||'',String(g.expected_stroke_count),
        ...g.strokes.map(s=>s.name_status==='reviewed'?s.name:'')
      ].some(v=>String(v).toLocaleLowerCase().includes(q)))
    );
    $('count').textContent='显示 '+state.visible.length+' / 201 个字帖主部首';
    $('empty').hidden=state.visible.length!==0;
    renderTiles();
  }
  function renderTiles(){
    const fragment=document.createDocumentFragment();
    for(const g of state.visible){
      const btn=document.createElement('button');
      btn.type='button';btn.className='tile';btn.dataset.glyphId=String(g.main_id);
      btn.setAttribute('aria-pressed',
        String(g.main_id===state.current?.main_id));
      btn.setAttribute('aria-label',g.character+'，'+g.expected_stroke_count+
        '画，PDF第'+g.pdf_page_start+'页');
      const sym=document.createElement('strong');sym.textContent=g.character;
      const count=document.createElement('small');
      count.textContent=g.expected_stroke_count+'画';
      btn.append(sym,count);
      btn.addEventListener('click',()=>{
        selectGlyph(g);
        // On narrow viewports the catalog is below the lesson. Return to
        // the newly selected source-backed glyph without extra navigation.
        if(window.matchMedia('(max-width: 860px)').matches){
          // Keep the bookmarkable ?id but drop the jump-to-directory hash.
          // Otherwise reloading the newly selected glyph jumps to the tiles.
          if(window.location.hash==='#characterLibrary'){
            const url=new URL(window.location.href);
            url.hash='';
            window.history.replaceState(null,'',url.pathname+url.search);
          }
          $('lessonHero').scrollIntoView({block:'start',behavior:'auto'});
        }
      });
      fragment.append(btn);
    }
    $tiles.replaceChildren(fragment);
  }
  function renderFilters(){
    const frag=document.createDocumentFragment();
    for(const batch of ['all',...Array.from(
      new Set(glyphs.map(g=>g.batch_id))).sort()]){
      const btn=document.createElement('button');
      btn.type='button';btn.dataset.batch=batch;
      btn.textContent=batch==='all'?'全部':' '+batch;
      btn.setAttribute('aria-pressed',String(batch===state.batch));
      btn.addEventListener('click',()=>{
        state.batch=batch;
        $filters.querySelectorAll('button[data-batch]').forEach(b=>
          b.setAttribute('aria-pressed',String(b.dataset.batch===batch)));
        applyFilter();
      });
      frag.append(btn);
    }
    $filters.replaceChildren(frag);
  }
  function neighbor(delta){
    const i=glyphs.findIndex(g=>g.main_id===state.current?.main_id);
    if(i>=0)selectGlyph(glyphs[(i+delta+glyphs.length)%glyphs.length]);
  }
  $('prevChar').addEventListener('click',()=>neighbor(-1));
  $('nextChar').addEventListener('click',()=>neighbor(1));
  $('play').addEventListener('click',()=>player.playing?player.pause():player.play());
  $('restart').addEventListener('click',()=>player.restart());
  $('prevStroke').addEventListener('click',()=>player.previous());
  $('nextStroke').addEventListener('click',()=>player.next());
  $('replayStroke').addEventListener('click',()=>player.replayStroke());
  $('complete').addEventListener('click',()=>player.showAll());
  $('seek').addEventListener('input',e=>player.seekElapsed(
    +e.target.value/1000*player.timeline.totalMs));
  $('pressureStyleOptions').addEventListener('click',e=>{
    const button=e.target.closest('button[data-pen-style]');
    if(button&&$('pressureStyleOptions').contains(button))
      setPressureStyle(button.dataset.penStyle);
  });
  $('speedButtons').addEventListener('click',e=>{
    const b=e.target.closest('button[data-speed]');
    if(!b)return;
    const value=+b.dataset.speed;
    if(![.5,1,1.5,2].includes(value))throw Error('Invalid A3 rate');
    state.speed=value;player.setSpeed(value);
    $('speedButtons').querySelectorAll('button[data-speed]').forEach(x=>
      x.setAttribute('aria-pressed',String(+x.dataset.speed===value)));
  });
  $('search').addEventListener('input',e=>{
    state.query=e.target.value;applyFilter();
  });
  document.addEventListener('keydown',e=>{
    // P2.1a is an independent, modal *reference* stage. Never let
    // the background player consume its keyboard shortcuts.
    if(document.getElementById('practiceOverlay')?.hidden===false)return;
    if(e.altKey||e.metaKey||e.ctrlKey||e.target.closest?.(
      'input,button,select,textarea,[contenteditable]'))return;
    if(e.code==='Space'){e.preventDefault();player.playing?player.pause():player.play();}
    else if(e.key.toLowerCase()==='r'){e.preventDefault();player.restart();}
  });
  renderFilters();
  applyFilter();
  const id=+(new URLSearchParams(window.location.search).get('id')||1);
  selectGlyph(byId.get(id)||glyphs[0]);
  window.ZITIE_A3_BOOK={
    pack,player,selectGlyph:(id)=>selectGlyph(byId.get(+id)),
    getGlyph:()=>state.current,getVisible:()=>state.visible.slice(),
    getPressureStyle:()=>penStyle.mode,setPressureStyle,
    getPressureState:()=>penStyle.state,getPressureRing:()=>penStyle.ring,
    getPdfPage:()=>Number($('pdfLink').href.match(/#page=(\d+)$/)?.[1]),
    setSpeed(value){
      const b=$('speedButtons').querySelector('button[data-speed="'+value+'"]');
      if(!b)throw Error('Unknown rate');b.click();
    }
  };
  document.documentElement.setAttribute('data-a3-ready','201');
});
