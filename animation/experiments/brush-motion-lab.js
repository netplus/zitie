/* A3.5 laboratory UI. A and B use TWO original, identical StrokePlayers.
 * The B timeline receives an opt-in timing-only reparameterization. The A
 * source clock alone controls playback; both SVGS render from the same tick.
 */
window.addEventListener('DOMContentLoaded',function(){
  'use strict';
  const pack=window.ZITIE_BOOK_PACK;
  const Model=window.ZitieA35BrushMotion;
  const $=id=>document.getElementById(id);
  if(!pack||pack.publication?.version!=='0.5.1'||
     !Array.isArray(pack.glyphs)||pack.glyphs.length!==201||!Model){
    $('baselineStatus').textContent='字帖原始素材未通过加载校验。';
    document.documentElement.setAttribute('data-a35-ready','FAIL');
    return;
  }
  const T=window.ZitieTimeline,glyphs=pack.glyphs,
    byId=new Map(glyphs.map(g=>[g.main_id,g]));
  glyphs.forEach(g=>T.validateGlyph(g));
  const state={glyph:null,plans:[],query:'',batch:'all',visible:glyphs.slice(),
    speed:1,last:null};
  const baseline=new window.ZitiePlayer.StrokePlayer({
    svg:$('baseline'),onUpdate(s){
      if(!s||!state.glyph||baseline.timeline?.glyph!==state.glyph||
         candidate.timeline?.glyph!==state.glyph)return;
      // Candidate never starts a requestAnimationFrame loop of its own.
      // It follows the original elapsed millisecond clock exactly.
      candidate.seekElapsed(s.elapsedMs);
      state.last=s;
      $('seek').value=String(Math.round(s.elapsedMs/s.totalMs*1000));
      $('time').textContent=format(s.elapsedMs)+' / '+format(s.totalMs);
      $('play').textContent=s.playing?'Ⅱ 暂停':'▶ 同步播放';
      const stroke=state.glyph.strokes[s.index];
      const name=stroke.name_status==='reviewed'?stroke.name:
        '第'+(s.index+1)+'笔';
      const plan=state.plans[s.index];
      $('baselineStatus').textContent='第'+(s.index+1)+' / '+s.count+
        ' 笔 · '+name+' · '+(s.motion?.label||'原版节奏');
      const timeProgress=baseline.timeline.strokes[s.index].durationMs===0?0:
        (s.elapsedMs-baseline.timeline.strokes[s.index].startMs)/
          baseline.timeline.strokes[s.index].durationMs;
      const phase=plan?.phaseAt(Math.max(0,Math.min(1,timeProgress)))||'通用';
      $('candidateStatus').textContent=plan?.enabled?
        '第'+(s.index+1)+' / '+s.count+' 笔 · '+name+' · '+phase:
        '第'+(s.index+1)+' / '+s.count+' 笔 · 使用与A相同的原版动作';
      $('stepButtons').querySelectorAll('button[data-stroke]').forEach(btn=>{
        if(+btn.dataset.stroke===s.index)btn.setAttribute('aria-current','step');
        else btn.removeAttribute('aria-current');
      });
      renderNotes(state.glyph,s.index,s);
    }
  });
  const candidate=new window.ZitiePlayer.StrokePlayer({svg:$('candidate')});
  function format(ms){
    const sec=Math.floor(ms/1000);
    return String(Math.floor(sec/60)).padStart(2,'0')+':'+
      String(sec%60).padStart(2,'0');
  }
  function renderNotes(g,i,s){
    const st=g.strokes[i],plan=state.plans[i];
    const name=st.name_status==='reviewed'?st.name:'第'+(i+1)+'笔';
    const pdfPage=g.pdf_page_start+Math.floor(i/6);
    const original=baseline.timeline.strokes[i],now=candidate.timeline.strokes[i];
    const pdf=$('bookLink');
    pdf.textContent='原 PDF 第 '+pdfPage+' 页 · '+g.character+
      ' · 第'+(i+1)+'笔 ↗';
    pdf.href=pack.publication.site_url.replace('../book','../../book')+'#page='+pdfPage;
    $('notes').replaceChildren();
    const info=[
      '字帖：'+g.character+' · 第'+(i+1)+' / '+g.strokes.length+'笔 · '+name+
        ' · '+g.batch_id,
      plan.enabled?
        '候选动作：'+({hook:'钩笔减速后短促出锋',
          fold:'折前制动并连续转锋',dot:'点画轻触及提笔',
          sweep:'撇捺渐进收锋',straight:'横竖提起收笔分段'}[plan.kind]||plan.kind):
        '保守回退：'+(plan.reason==='ordinal_only_no_semantic_inference'?
          '来源不允许引用细笔画名称，不猜动作':
          plan.reason==='ambiguous_turn_no_forced_semantic_pivot'?
          '原始中线转折不明确，不强制施加动作':
          '此笔未形成安全候选'),
      '总时长：A '+Math.round(original.durationMs)+'ms / B '+
        Math.round(now.durationMs)+'ms（始终相同）',
      '当前进度 A '+Math.round(s.progress*100)+'% / B '+
        Math.round(window.ZitieTimeline.frameAt(candidate.timeline,
          candidate.elapsed).progress*100)+'%'+
        '；候选相对基线最大偏移 ≤'+
        (plan.maxDrift*100).toFixed(1)+'%（行程归一化）',
      '推导事件：'+(plan.events.length?
        plan.events.map(e=>e.type+' @'+(100*e.position).toFixed(1)+
          '% 源点#'+e.sourceVertex).join('；'):'无可信折钩节点'),
      '轨迹审核：未教学确认，保持与PDF完全相同的轮廓/中心线/笔顺。'
    ];
    for(const line of info){
      const p=document.createElement('p');p.textContent=line;$('notes').append(p);
    }
  }
  function renderSteps(g){
    const frag=document.createDocumentFragment();
    g.strokes.forEach((stroke,i)=>{
      const button=document.createElement('button');
      button.type='button';button.dataset.stroke=String(i);
      button.textContent=(i+1)+' '+(stroke.name_status==='reviewed'?
        stroke.name:'第'+(i+1)+'笔');
      button.addEventListener('click',()=>baseline.seekStroke(i));
      frag.append(button);
    });
    $('stepButtons').replaceChildren(frag);
  }
  function renderTiles(){
    const frag=document.createDocumentFragment();
    state.visible.forEach(g=>{
      const b=document.createElement('button');
      b.type='button';b.className='tile';b.dataset.glyphId=String(g.main_id);
      b.setAttribute('aria-pressed',String(g.main_id===state.glyph?.main_id));
      const label=document.createElement('strong');label.textContent=g.character;
      const count=document.createElement('small');count.textContent=g.strokes.length+'笔';
      b.append(label,count);b.addEventListener('click',()=>select(g.main_id));
      frag.append(b);
    });
    $('tiles').replaceChildren(frag);
  }
  function renderFilters(){
    const root=$('batchFilters'),frag=document.createDocumentFragment();
    for(const batch of ['all',...new Set(glyphs.map(g=>g.batch_id))]){
      const b=document.createElement('button');
      b.type='button';b.dataset.batch=batch;
      b.setAttribute('aria-pressed',String(batch===state.batch));
      b.textContent=batch==='all'?'全部':batch;
      b.addEventListener('click',()=>{
        state.batch=batch;
        root.querySelectorAll('[data-batch]').forEach(other=>
          other.setAttribute('aria-pressed',String(other.dataset.batch===batch)));
        filter();
      });
      frag.append(b);
    }
    root.replaceChildren(frag);
  }
  function filter(){
    const q=state.query.trim().toLocaleLowerCase();
    state.visible=glyphs.filter(g=>(state.batch==='all'||
      g.batch_id===state.batch)&&(!q||[
      g.character,g.pinyin||'',g.batch_id,String(g.main_id),
      ...g.strokes.map(st=>st.name_status==='reviewed'?st.name:'')
    ].some(s=>String(s).toLocaleLowerCase().includes(q))));
    $('count').textContent='显示 '+state.visible.length+' / '+glyphs.length+
      ' 个字帖主部首';
    renderTiles();
  }
  function select(id){
    const g=byId.get(Number(id));if(!g)return null;
    state.glyph=g;
    $('glyphName').textContent=g.character;
    $('glyphMeta').textContent=g.batch_id+' · #'+g.main_id+
      ' · '+g.strokes.length+'笔 · PDF第'+g.pdf_page_start+'页起';
    // Each page gets a new candidate timeline; main A3 data and engine
    // are immutable. The candidate overrides ONLY its own motion maps.
    candidate.setGlyph(g);
    state.plans=Model.applyToTimeline(candidate.timeline);
    renderSteps(g);
    baseline.setGlyph(g);
    baseline.setSpeed(state.speed);
    renderTiles();
    const url=new URL(window.location.href);
    url.searchParams.set('id',String(g.main_id));
    window.history?.replaceState?.(null,'',url.pathname+url.search+url.hash);
    return g;
  }
  function step(delta){
    if(!state.glyph)return;
    const i=glyphs.indexOf(state.glyph);
    select(glyphs[(i+delta+glyphs.length)%glyphs.length].main_id);
  }
  $('search').addEventListener('input',e=>{state.query=e.target.value;filter();});
  $('play').addEventListener('click',()=>baseline.playing?
    baseline.pause():baseline.play());
  $('restart').addEventListener('click',()=>baseline.restart());
  $('prevStroke').addEventListener('click',()=>baseline.previous());
  $('nextStroke').addEventListener('click',()=>baseline.next());
  $('replayStroke').addEventListener('click',()=>baseline.replayStroke());
  $('complete').addEventListener('click',()=>baseline.showAll());
  $('seek').addEventListener('input',e=>baseline.seekElapsed(
    +e.target.value/1000*baseline.timeline.totalMs));
  $('rates').addEventListener('click',e=>{
    const b=e.target.closest('button[data-speed]');
    if(!b)return;
    const speed=+b.dataset.speed;
    if(![.5,1,1.5,2].includes(speed))throw Error('Unsupported A3.5 rate');
    state.speed=speed;
    baseline.setSpeed(speed);
    $('rates').querySelectorAll('button[data-speed]').forEach(button=>
      button.setAttribute('aria-pressed',String(+button.dataset.speed===speed)));
  });
  document.addEventListener('keydown',e=>{
    if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest?.(
      'input,button,select,textarea,[contenteditable]'))return;
    if(e.code==='Space'){e.preventDefault();baseline.playing?baseline.pause():baseline.play();}
  });
  renderFilters();
  filter();
  const id=+(new URLSearchParams(window.location.search).get('id')||77);
  select(byId.has(id)?id:77);
  // Optional deep link for reproducible A/B screenshots, never autoplay.
  const params=new URLSearchParams(window.location.search);
  const stroke=Number(params.get('stroke'));
  const fraction=Number(params.get('fraction'));
  if(params.has('stroke')&&params.has('fraction')&&
     Number.isInteger(stroke)&&stroke>=1&&
     stroke<=state.glyph.strokes.length&&Number.isFinite(fraction)&&
     fraction>=0&&fraction<=1){
    const s=baseline.timeline.strokes[stroke-1];
    baseline.seekElapsed(s.startMs+s.durationMs*fraction);
  }
  window.ZITIE_A35={
    pack,baseline,candidate,select,step,getGlyph:()=>state.glyph,
    getPlans:()=>state.plans.slice(),
    getSelectedStroke:()=>state.last?.index,
    seekFraction:(fraction)=>baseline.seekElapsed(
      baseline.timeline.totalMs*fraction),
    getTime:()=>baseline.elapsed,
    setSpeed:(speed)=>{
      const b=$('rates').querySelector('button[data-speed="'+speed+'"]');
      if(!b)throw Error('Unsupported speed');b.click();
    },
    getVisible:()=>state.visible.slice()
  };
  document.documentElement.setAttribute('data-a35-ready','201');
});
