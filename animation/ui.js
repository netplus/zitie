/* A1.2.1 offline gallery + playback controls; no alternative animation timeline. */
window.addEventListener('DOMContentLoaded', function () {
  'use strict';
  const pack=window.ZITIE_SAMPLES;
  if(!pack||pack.schema_version!==1||!Array.isArray(pack.glyphs))
    throw new Error('Offline canonical sample data unavailable');
  const $=id=>document.getElementById(id);
  const glyphs=pack.glyphs;
  const gallery=window.ZitieGallery;
  const selector=$('glyphGallery'),filterRow=$('batchFilters');
  const play=$('play'),speed=$('speed'),seek=$('timelineSeek');
  let query='',batch='all',selectedId=null,visibleGlyphs=[];
  const player=new window.ZitiePlayer.StrokePlayer({
    svg:$('glyphStage'),status:$('state'),
    onUpdate(state){
      if(!state)return;
      play.textContent=state.playing?'Ⅱ 暂停':'▶ 播放笔顺';
      play.setAttribute('aria-label',state.playing?'暂停书写动画':'播放书写动画');
      seek.value=String(Math.round(state.elapsedMs/state.totalMs*1000));
      $('timelineReadout').textContent=formatTime(state.elapsedMs)+' / '+formatTime(state.totalMs);
      $('strokeIndex').textContent='第 '+(state.index+1)+' / '+state.count+' 笔';
      const stroke=player.timeline.glyph.strokes[state.index];
      $('strokeName').textContent=stroke.name_status==='reviewed'?stroke.name:'第'+(state.index+1)+'笔';
      $('strokePhase').textContent=state.phase==='finished'?'已完成':
        state.phase==='pause'?'观察笔形':state.playing?'正在书写':'待播放';
    }
  });
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
    player.setSpeed(Number(speed.value));
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
  speed.addEventListener('change',e=>player.setSpeed(Number(e.target.value)));
  seek.addEventListener('input',e=>{
    if(player.timeline)player.seekElapsed(Number(e.target.value)/1000*player.timeline.totalMs);
  });
  document.addEventListener('keydown',e=>{
    if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest('input,textarea,select,[contenteditable]'))return;
    const lower=e.key.toLowerCase();
    if(e.code==='Space'){e.preventDefault();player.playing?player.pause():player.play();}
    else if(lower==='a'){e.preventDefault();navigate(-1);}
    else if(lower==='d'){e.preventDefault();navigate(1);}
    else if(lower==='r'){e.preventDefault();player.restart();}
  });
  renderFilters();
  visibleGlyphs=glyphs.slice();
  selectGlyph(glyphs[0]);
  window.ZITIE_A1_APP=player; // Stable embedding/browser-QA interface.
  window.ZITIE_A1_GALLERY={getVisible:()=>visibleGlyphs.slice(),
    getSelectedId:()=>selectedId, selectGlyph, navigate};
});