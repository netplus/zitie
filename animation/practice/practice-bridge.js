/* P2.1b: immersive PDF-backed reference plus real transient user ink.
 * P2.1c alone will add confirmed stroke progression and local persistence.
 * Original A3 StrokePlayer, glyph objects and PDF release stay immutable.
 */
(function(root){
  'use strict';
  const $=id=>document.getElementById(id);
  root.addEventListener('DOMContentLoaded',()=>{
    const book=root.ZITIE_A3_BOOK;
    const reference=root.ZitiePracticeReference;
    const Trace=root.ZitiePracticeTraceSession;
    const Ink=root.ZitiePracticeInkCanvas;
    const Input=root.ZitiePracticePointerInput;
    const overlay=$('practiceOverlay'),source=$('paperSvg');
    const board=$('practiceSvg'),surface=$('practiceInk'),launch=$('practiceLaunch');
    const paper=source?.closest('.paper');
    const main=document.querySelector('main.page');
    if(!book||!reference||!Trace||!Ink||!Input||!overlay||
       !source||!board||!surface||!launch||!paper||!main){
      document.documentElement.dataset.p21bError='missing-dependency';
      return;
    }
    const stage=new reference.ReferenceStage(board);
    const exit=$('practiceExit'),prev=$('practicePrev'),next=$('practiceNext'),
      reset=$('practiceReset');
    const controls=[exit,prev,next,reset];
    let active=false,saved=null,priorFocus=null,priorOverflow='',priorInert=false;
    let session=null,renderer=null,input=null;

    function update(){
      const frame=stage.getState();
      if(!frame)return;
      const index=frame.referenceIndex,count=frame.strokeCount;
      $('practiceTitle').textContent='逐笔临摹 · '+frame.character;
      $('practiceProgress').textContent='参考笔画 '+(index+1)+' / '+count;
      $('practiceStrokeTitle').textContent='第 '+(index+1)+' 笔 · '+frame.label;
      $('practiceStrokeHint').textContent=
        '淡红色为参考轮廓，圆点标识工程参考起收笔位置；请用手指、手写笔或鼠标写出蓝色轨迹。';
      prev.disabled=index===0;
      next.disabled=index>=count-1;
      board.setAttribute('aria-label',frame.character+'第'+(index+1)+
        '笔源轮廓参考，真实蓝墨由独立Canvas记录');
      const status=session?.getState();
      reset.disabled=!status||status.phase==='ready';
      const statusText=$('practicePreviewStatus');
      if(!status||status.phase==='ready'){
        statusText.textContent=input?.lastCancel?
          '触控已中断，本次未完成轨迹已丢弃，可重新落笔；未记录练习成绩':
          '沿当前笔画书写：等待落笔 · 蓝墨仅在本次页面内暂存，未记录练习成绩';
      }else if(status.phase==='drawing'){
        statusText.textContent='正在真实书写：'+status.pointCount+
          ' 个触点 · 未记录练习成绩';
      }else{
        statusText.textContent='已绘制本笔真实轨迹（'+status.pointCount+
          ' 个采样点），尚未确认或保存；可重写本笔 · 未记录练习成绩';
      }
    }

    function open(){
      if(active)return true;
      const glyph=book.getGlyph(),state=book.player.getState();
      if(!glyph||!state)return false;
      // Build a separate PDF-source SVG; never replace the A3 SVG/player.
      stage.setGlyph(glyph);
      saved={glyphId:glyph.main_id,elapsedMs:state.elapsedMs,
        speed:state.speed,pressureStyle:book.getPressureStyle(),
        playing:state.playing};
      priorFocus=document.activeElement;
      priorOverflow=document.body.style.overflow;
      priorInert=main.inert;
      book.player.pause();
      $('practiceGlyphMeta').textContent=glyph.character+' · '+
        glyph.expected_stroke_count+'画 · '+glyph.batch_id+
        ' · '+(glyph.pinyin||glyph.reading_note||'读音不单列');
      stage.showStroke(0);
      overlay.hidden=false;
      active=true;
      document.documentElement.dataset.p21aActive='true';
      document.documentElement.dataset.p21bActive='true';
      document.body.style.overflow='hidden';
      main.inert=true;
      session=new Trace.TraceSession();
      renderer=new Ink.TraceCanvas(surface,stage.group,()=>session.getSamples());
      input=new Input.PointerInput({
        surface,group:stage.group,session,
        onChange:()=>{renderer.schedule();update();},
        onLayout:()=>renderer.resize()
      });
      update();
      exit.focus({preventScroll:true});
      return true;
    }

    function disposeInk(){
      if(input){input.destroy();input=null;}
      if(renderer){renderer.destroy();renderer=null;}
      if(session){session.reset();session=null;}
    }

    function close(){
      if(!active)return false;
      disposeInk(); // temporary P2.1b draft never survives exiting
      overlay.hidden=true;
      active=false;
      delete document.documentElement.dataset.p21aActive;
      delete document.documentElement.dataset.p21bActive;
      main.inert=priorInert;
      document.body.style.overflow=priorOverflow;
      if(saved){
        if(book.getGlyph()?.main_id!==saved.glyphId)
          book.selectGlyph(saved.glyphId);
        if(book.getPressureStyle()!==saved.pressureStyle)
          book.setPressureStyle(saved.pressureStyle);
        if(book.player.speed!==saved.speed)
          book.setSpeed(saved.speed);
        // Do not suddenly resume A3 playback on leaving practice.
        book.player.seekElapsed(saved.elapsedMs);
      }
      saved=null;
      if(priorFocus?.isConnected&&typeof priorFocus.focus==='function')
        priorFocus.focus({preventScroll:true});
      else launch.focus({preventScroll:true});
      return true;
    }

    function showReference(index){
      if(!active)return false;
      const count=stage.reference.strokeCount;
      if(!Number.isInteger(index)||index<0||index>=count)return false;
      // Reference preview is not learned/accepted progression in P2.1b.
      // Existing unconfirmed temporary ink belongs only to its prior stroke.
      if(input)input.reset();
      stage.showStroke(index);
      if(renderer)renderer.resize();
      update();
      return true;
    }

    function rewrite(){
      if(!active||!input)return false;
      input.reset();
      renderer.clear();
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
    prev.addEventListener('click',()=>showReference(stage.currentIndex-1));
    next.addEventListener('click',()=>showReference(stage.currentIndex+1));
    reset.addEventListener('click',rewrite);
    document.addEventListener('keydown',e=>{
      if(!active)return;
      if(e.key==='Escape'){
        e.preventDefault();e.stopPropagation();close();return;
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
    const exported={
      open,close,reference:showReference,rewrite,
      getTrace(){return session?session.getSamples().map(p=>({...p})):[];},
      getInkMetrics(){return renderer?.getMetrics()||null;},
      getState(){
        return {active,...(active?stage.getState():{}),
          originalGlyphId:saved?.glyphId??null,
          originalElapsedMs:saved?.elapsedMs??null,
          ... (input?{input:input.getState()}:
            {input:{phase:'inactive',acceptedStrokes:0}}),
          liveInkEnabled:true,noHandwritingInput:false,
          noAutomaticScore:true,noPersistentWritingStorage:true};
      }
    };
    root.ZITIE_P21A=exported; // keep existing P2.1a public test hook
    root.ZITIE_P21B=exported;
    document.documentElement.dataset.p21aReady='reference-only';
    document.documentElement.dataset.p21bReady='raw-pointer-canvas';
  });
})(typeof window!=='undefined'?window:null);
