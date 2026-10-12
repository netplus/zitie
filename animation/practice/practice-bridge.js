/* P2.1a — enter/exit and read-only per-stroke reference for the formal book.
 * No Pointer Events drawing, handwriting storage or automatic matching here.
 */
(function(root){
  'use strict';
  const $=id=>document.getElementById(id);
  root.addEventListener('DOMContentLoaded',()=>{
    const book=root.ZITIE_A3_BOOK;
    const api=root.ZitiePracticeReference;
    const overlay=$('practiceOverlay'),source=$('paperSvg');
    const board=$('practiceSvg'),launch=$('practiceLaunch');
    const paper=source?.closest('.paper');
    const main=document.querySelector('main.page');
    if(!book||!api||!overlay||!source||!board||!launch||!paper||!main){
      document.documentElement.dataset.p21aError='missing-dependency';
      return;
    }
    const stage=new api.ReferenceStage(board);
    const exit=$('practiceExit'),prev=$('practicePrev'),next=$('practiceNext');
    const controls=[exit,prev,next];
    let active=false,saved=null,priorFocus=null,priorOverflow='',priorInert=false;
    const update=()=>{
      const frame=stage.getState();
      if(!frame)return;
      const index=frame.referenceIndex,count=frame.strokeCount;
      $('practiceTitle').textContent='逐笔临摹 · '+frame.character;
      $('practiceProgress').textContent='笔顺参考 '+(index+1)+' / '+count;
      $('practiceStrokeTitle').textContent='第 '+(index+1)+' 笔 · '+frame.label;
      $('practiceStrokeHint').textContent=
        '淡红色是当前笔画；空心圆为参考起笔位置，实心圆为参考收笔位置。';
      $('practicePreviewStatus').textContent='仅预览笔顺参考，未记录练习成绩';
      prev.disabled=index===0;
      next.disabled=index>=count-1;
      board.setAttribute('aria-label',frame.character+'第'+(index+1)+
        '笔源轮廓参考，起收笔中心线未经教学动作审定');
    };
    function open(){
      if(active)return true;
      const glyph=book.getGlyph();
      if(!glyph)return false;
      // Build a separate reference SVG before touching the original player.
      stage.setGlyph(glyph);
      const state=book.player.getState();
      if(!state)return false;
      saved={glyphId:glyph.main_id,elapsedMs:state.elapsedMs,
        speed:state.speed,pressureStyle:book.getPressureStyle(),
        playing:state.playing};
      priorFocus=document.activeElement;
      priorOverflow=document.body.style.overflow;
      priorInert=main.inert;
      book.player.pause();
      $('practiceGlyphMeta').textContent=glyph.character+' · '+glyph.expected_stroke_count+
        '画 · '+glyph.batch_id+' · '+(glyph.pinyin||glyph.reading_note||'读音不单列');
      stage.showStroke(0);
      update();
      overlay.hidden=false;
      active=true;
      document.documentElement.dataset.p21aActive='true';
      document.body.style.overflow='hidden';
      main.inert=true;
      exit.focus({preventScroll:true});
      return true;
    }
    function close(){
      if(!active)return false;
      overlay.hidden=true;
      active=false;
      delete document.documentElement.dataset.p21aActive;
      main.inert=priorInert;
      document.body.style.overflow=priorOverflow;
      if(saved){
        if(book.getGlyph()?.main_id!==saved.glyphId)
          book.selectGlyph(saved.glyphId);
        if(book.getPressureStyle()!==saved.pressureStyle)
          book.setPressureStyle(saved.pressureStyle);
        if(book.player.speed!==saved.speed)
          book.setSpeed(saved.speed);
        // Never resume playback automatically: the learner returned to study.
        book.player.seekElapsed(saved.elapsedMs);
      }
      saved=null;
      if(priorFocus?.isConnected&&typeof priorFocus.focus==='function')
        priorFocus.focus({preventScroll:true});
      else launch.focus({preventScroll:true});
      return true;
    }
    function reference(index){
      if(!active)return false;
      const count=stage.reference.strokeCount;
      if(!Number.isInteger(index)||index<0||index>=count)return false;
      stage.showStroke(index);
      update();
      return true;
    }
    launch.addEventListener('click',open);
    paper.addEventListener('click',open);
    paper.addEventListener('keydown',e=>{
      if(e.key==='Enter'||e.key===' '){
        e.preventDefault();e.stopPropagation();open();
      }
    });
    exit.addEventListener('click',close);
    prev.addEventListener('click',()=>reference(stage.currentIndex-1));
    next.addEventListener('click',()=>reference(stage.currentIndex+1));
    document.addEventListener('keydown',e=>{
      if(!active)return;
      if(e.key==='Escape'){
        e.preventDefault();e.stopPropagation();close();
        return;
      }
      if(e.key==='Tab'){
        const available=controls.filter(button=>!button.disabled);
        const first=available[0],last=available[available.length-1];
        if(e.shiftKey&&document.activeElement===first){
          e.preventDefault();last.focus();
        }else if(!e.shiftKey&&document.activeElement===last){
          e.preventDefault();first.focus();
        }else if(!overlay.contains(document.activeElement)){
          e.preventDefault();first.focus();
        }
      }
    },true);
    root.ZITIE_P21A={
      open,close,reference,
      getState(){
        return {active,...(active?stage.getState():{}),
          originalGlyphId:saved?.glyphId??null,
          originalElapsedMs:saved?.elapsedMs??null,
          noHandwritingInput:true,noAutomaticScore:true};
      }
    };
    document.documentElement.dataset.p21aReady='reference-only';
  });
})(typeof window!=='undefined'?window:null);
