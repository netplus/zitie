/* P2.1c — genuine handwritten strokes, explicitly confirmed in source order.
 * SVG source and A3 player are read-only. Confirmed ink persists ONLY in
 * browser IndexedDB; unconfirmed pointer drafts are never persisted.
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
    const Progress=root.ZitiePracticeProgress;
    const Storage=root.ZitiePracticeLocalStore;
    const overlay=$('practiceOverlay'),source=$('paperSvg');
    const board=$('practiceSvg'),surface=$('practiceInk'),launch=$('practiceLaunch');
    const paper=source?.closest('.paper');
    const main=document.querySelector('main.page');
    const exit=$('practiceExit'),prev=$('practicePrev'),next=$('practiceNext'),
      reset=$('practiceReset'),accept=$('practiceAccept'),undo=$('practiceUndo'),
      restart=$('practiceRestart'),returnCurrent=$('practiceReturnCurrent');
    if(!book||!reference||!Trace||!Ink||!Input||!Progress||!Storage||
       !overlay||!source||!board||!surface||!launch||!paper||!main||
       !accept||!undo||!restart||!returnCurrent){
      document.documentElement.dataset.p21cError='missing-dependency';
      return;
    }
    const stage=new reference.ReferenceStage(board);
    const store=new Storage.LocalPracticeStore();
    let active=false,saved=null,priorFocus=null,priorOverflow='',priorInert=false;
    let session=null,renderer=null,input=null,progress=null,ready=false;
    let saveStatus='loading',storageUsable=true,storageMessage='';
    let generation=0,loadingPromise=Promise.resolve(false),savingPromise=Promise.resolve();
    let lastFeedback='',closeQueued=false;
    const identity=()=>({glyphId:progress.glyphId,
      sourceHash:progress.sourceHash,pdfHash:progress.pdfHash});
    const drawingAllowed=()=>active&&ready&&!progress.complete&&
      stage.currentIndex===progress.currentIndex;
    const hasDraft=()=>!!session&&(!!session.draft||!!session.active);
    const closeWarning=()=>hasDraft()||(!storageUsable&&
      progress&&progress.currentIndex>0);

    function update(){
      if(!active||!progress)return;
      const frame=stage.getState(),state=progress.getState(),ink=session?.getState();
      const preview=stage.currentIndex!==state.currentIndex&&!state.completed;
      $('practiceTitle').textContent='逐笔临摹 · '+frame.character;
      $('practiceProgress').textContent=state.completed?
        '已完成 '+state.strokeCount+' / '+state.strokeCount+' 笔':
        '已确认 '+state.acceptedStrokes+' / '+state.strokeCount+' 笔';
      $('practiceStrokeTitle').textContent=state.completed?
        '整字书写完成 · '+state.strokeCount+' 笔':
        '第 '+(state.currentIndex+1)+' 笔 · '+frame.label;
      $('practiceStrokeHint').textContent=state.completed?
        '蓝墨为你实际写过且逐笔确认的轨迹，灰红轮廓与 PDF 同源。':
        preview?'正在浏览笔画参考；请返回当前待写笔后再落笔。':
        '当前淡红笔画为参考；请沿参考写出自己的真实蓝墨笔迹，抬笔后人工确认。';
      board.setAttribute('aria-label',frame.character+'第'+(stage.currentIndex+1)+
        '笔源参考与本人真实笔迹，不是自动书法评分');
      prev.disabled=!ready||stage.currentIndex===0;
      next.disabled=!ready||stage.currentIndex>=frame.strokeCount-1;
      returnCurrent.hidden=!ready||(!state.completed&&!preview);
      returnCurrent.disabled=!ready;
      reset.disabled=!drawingAllowed()||(!ink?.hasDraft&&ink?.phase!=='drawing');
      accept.disabled=!drawingAllowed()||ink?.phase!=='review';
      undo.disabled=!ready||!state.acceptedStrokes||ink?.phase==='drawing';
      restart.disabled=!ready;
      if(input)input.enabled=drawingAllowed();
      const status=$('practicePreviewStatus');
      if(!ready)status.textContent='正在校验并读取本地练习记录…';
      else if(state.completed)status.textContent='全部笔画已由你逐笔确认（非自动评分）；可撤销最后一笔或重新练习。';
      else if(preview)status.textContent='仅预览字帖参考：预览不推进笔顺，也不记录完成；可返回当前待写笔。';
      else if(lastFeedback)status.textContent=lastFeedback;
      else if(ink?.phase==='drawing')status.textContent=
        '正在真实书写：'+ink.pointCount+' 个采样点，尚未确认。';
      else if(ink?.phase==='review')status.textContent=
        '蓝色真实笔迹已保留（'+ink.pointCount+' 点）。请确认这一笔，或重写。';
      else status.textContent=input?.lastCancel?
        '触控中断，未确认的笔迹已丢弃；可重新落笔。':
        '请落笔：每写完一笔，需点「确认这一笔」才能进入下一笔。';
      $('practiceCompletion').hidden=!state.completed;
      $('practiceCompletion').textContent=state.completed?
        '完成 '+state.strokeCount+' 笔！这些蓝色笔迹均来自你的实际书写，未经书法教师评分。':'';
      const save=$('practiceSaved');
      save.dataset.status=saveStatus==='error'?'error':'normal';
      const names={
        loading:'正在读取本机保存的已确认笔迹…',
        new:'本机尚无已确认笔迹；确认后会自动尝试保存。',
        restored:'已从本机恢复 '+state.acceptedStrokes+' 笔。',
        saving:'正在把已确认笔迹保存到本机…',
        saved:'已在本机保存 '+state.acceptedStrokes+' 笔（不会上传）。',
        cleared:'本机该字练习记录已清空。',
        error:'本机保存不可用：当前已确认笔迹只保留在页面内，退出可能丢失。'
      };
      save.textContent=(names[saveStatus]||names.new)+
        (storageMessage?' · '+storageMessage:'');
    }

    function hidePrompts(){
      $('practiceClearPrompt').hidden=true;
      $('practiceLeavePrompt').hidden=true;
    }
    function syncInk(){
      if(renderer)renderer.paint(true);
    }
    function renderCurrent(){
      if(!progress)return;
      const target=Math.min(progress.currentIndex,progress.strokeCount-1);
      stage.showStroke(target);
      if(input)input.enabled=drawingAllowed();
      syncInk();
      update();
    }
    function note(message){lastFeedback=message;update();}

    function persist(){
      if(!storageUsable)return Promise.resolve(false);
      const captured=progress.snapshot(),g=generation;
      saveStatus='saving';storageMessage='';update();
      const job=store.save(captured).then(()=>{
        if(active&&g===generation&&progress.revision===captured.revision){
          saveStatus='saved';update();
        }
        return true;
      }).catch(error=>{
        if(g===generation){
          storageUsable=false;saveStatus='error';
          storageMessage='已确认笔迹仍在内存，请勿直接关闭网页';
          update();
        }
        return false;
      });
      savingPromise=job;
      return job;
    }

    function open(){
      if(active)return true;
      const glyph=book.getGlyph(),state=book.player.getState();
      if(!glyph||!state)return false;
      stage.setGlyph(glyph);
      const pdfHash=book.pack.publication.sha256;
      progress=new Progress.PracticeProgress({
        glyphId:glyph.main_id,strokeCount:glyph.strokes.length,
        sourceHash:glyph.source_sha256,pdfHash
      });
      saved={glyphId:glyph.main_id,elapsedMs:state.elapsedMs,
        speed:state.speed,pressureStyle:book.getPressureStyle()};
      priorFocus=document.activeElement;
      priorOverflow=document.body.style.overflow;
      priorInert=main.inert;
      book.player.pause();
      $('practiceGlyphMeta').textContent=glyph.character+' · '+
        glyph.expected_stroke_count+'画 · '+glyph.batch_id+
        ' · '+(glyph.pinyin||glyph.reading_note||'读音不单列');
      stage.showStroke(0);
      overlay.hidden=false;active=true;ready=false;
      generation++;const g=generation;
      document.documentElement.dataset.p21aActive='true';
      document.documentElement.dataset.p21bActive='true';
      document.documentElement.dataset.p21cActive='true';
      document.body.style.overflow='hidden';main.inert=true;
      saveStatus='loading';storageUsable=true;storageMessage='';
      lastFeedback='';closeQueued=false;hidePrompts();
      session=new Trace.TraceSession();
      renderer=new Ink.TraceCanvas(surface,stage.group,
        ()=>session.getSamples(),()=>progress.getAccepted());
      input=new Input.PointerInput({
        surface,group:stage.group,session,
        onChange:()=>{lastFeedback='';renderer.schedule();update();},
        onLayout:()=>renderer.resize()
      });
      input.enabled=false;
      update();exit.focus({preventScroll:true});
      loadingPromise=(async()=>{
        try{
          const savedRecord=await store.load(identity());
          if(!active||g!==generation)return false;
          if(savedRecord&&!progress.restore(savedRecord)){
            storageUsable=false;saveStatus='error';
            storageMessage='检测到不兼容的历史记录；请先选择「重新练习整字」清空';
            input.enabled=false;
          }else{
            saveStatus=savedRecord?'restored':'new';
          }
        }catch(_){
          if(!active||g!==generation)return false;
          storageUsable=false;saveStatus='error';
          storageMessage='浏览器可能禁用 IndexedDB';
        }
        if(!active||g!==generation)return false;
        ready=true;renderCurrent();
        return true;
      })();
      return true;
    }

    function disposeInk(){
      if(input){input.destroy();input=null;}
      if(renderer){renderer.destroy();renderer=null;}
      if(session){session.reset();session=null;}
    }
    function reallyClose(){
      if(!active)return false;
      generation++;
      disposeInk();overlay.hidden=true;active=false;ready=false;
      delete document.documentElement.dataset.p21aActive;
      delete document.documentElement.dataset.p21bActive;
      delete document.documentElement.dataset.p21cActive;
      main.inert=priorInert;
      document.body.style.overflow=priorOverflow;
      hidePrompts();
      if(saved){
        if(book.getGlyph()?.main_id!==saved.glyphId)
          book.selectGlyph(saved.glyphId);
        if(book.getPressureStyle()!==saved.pressureStyle)
          book.setPressureStyle(saved.pressureStyle);
        if(book.player.speed!==saved.speed)
          book.setSpeed(saved.speed);
        book.player.seekElapsed(saved.elapsedMs);
      }
      saved=null;progress=null;
      if(priorFocus?.isConnected&&typeof priorFocus.focus==='function')
        priorFocus.focus({preventScroll:true});
      else launch.focus({preventScroll:true});
      return true;
    }
    function close({discardDraft=false}={}){
      if(!active)return false;
      if(!discardDraft&&closeWarning()){
        $('practiceLeavePrompt').hidden=false;
        $('practiceClearPrompt').hidden=true;
        $('practiceLeaveYes').focus();
        return false;
      }
      // Explicitly wait for the write queue before destroying UI. A user
      // must never see "saved" before the IndexedDB transaction completes.
      if(saveStatus==='saving'){
        if(!closeQueued){
          closeQueued=true;
          savingPromise.finally(()=>{
            if(active){closeQueued=false;reallyClose();}
          });
        }
        return false;
      }
      return reallyClose();
    }

    function referenceTo(index){
      if(!active||!ready||!Number.isInteger(index)||
         index<0||index>=stage.reference.strokeCount)return false;
      // Preview is always read-only; it does not modify accepted ordinals.
      if(input)input.reset();
      stage.showStroke(index);
      lastFeedback='';
      syncInk();update();
      return true;
    }
    function returnToCurrent(){
      if(!active||!ready)return false;
      if(input)input.reset();
      lastFeedback='';
      renderCurrent();
      return true;
    }
    function rewrite(){
      if(!active||!ready||!input||!drawingAllowed())return false;
      input.reset();lastFeedback='';syncInk();update();return true;
    }
    function confirmStroke(){
      if(!drawingAllowed()||session?.active)return false;
      const result=progress.accept(session?.draft);
      if(!result.ok){
        note('这一笔的有效行程不足，或触控数据不完整。请重写当前笔。');
        return false;
      }
      input.reset();lastFeedback='';
      renderCurrent();
      persist();
      return true;
    }
    function undoStroke(){
      if(!active||!ready||!progress.accepted.length||session?.active)
        return false;
      input.reset();
      if(!progress.undo())return false;
      lastFeedback='已撤销上一笔，重新书写后请手动确认。';
      renderCurrent();
      persist();
      return true;
    }
    function requestRestart(){
      if(!active||!ready)return false;
      $('practiceClearPrompt').hidden=false;
      $('practiceLeavePrompt').hidden=true;
      $('practiceClearNo').focus();
      return true;
    }
    function restartAll(){
      if(!active||!ready)return false;
      hidePrompts();
      input.reset();progress.restart();
      lastFeedback='已清空这一个字的已确认笔迹；请从第一笔重新开始。';
      renderCurrent();
      // Clear only this precise PDF/glyph ID/source-hash record.
      const gen=generation;
      saveStatus='saving';update();
      savingPromise=store.remove(identity()).then(()=>{
        if(active&&gen===generation){saveStatus='cleared';storageUsable=true;
          storageMessage='';update();}
        return true;
      }).catch(()=>{
        if(active&&gen===generation){saveStatus='error';storageUsable=false;
          storageMessage='清除本地记录失败，请检查浏览器存储权限';update();}
        return false;
      });
      return true;
    }
    const closeFromUser=()=>close();
    launch.addEventListener('click',open);
    paper.addEventListener('click',open);
    paper.addEventListener('keydown',e=>{
      if(e.key==='Enter'||e.key===' '){
        e.preventDefault();e.stopPropagation();open();
      }
    });
    exit.addEventListener('click',closeFromUser);
    prev.addEventListener('click',()=>referenceTo(stage.currentIndex-1));
    next.addEventListener('click',()=>referenceTo(stage.currentIndex+1));
    reset.addEventListener('click',rewrite);
    accept.addEventListener('click',confirmStroke);
    undo.addEventListener('click',undoStroke);
    restart.addEventListener('click',requestRestart);
    returnCurrent.addEventListener('click',returnToCurrent);
    $('practiceClearYes').addEventListener('click',restartAll);
    $('practiceClearNo').addEventListener('click',()=>{
      $('practiceClearPrompt').hidden=true;restart.focus();
    });
    $('practiceLeaveYes').addEventListener('click',()=>{
      $('practiceLeavePrompt').hidden=true;close({discardDraft:true});
    });
    $('practiceLeaveNo').addEventListener('click',()=>{
      $('practiceLeavePrompt').hidden=true;exit.focus();
    });
    document.addEventListener('keydown',e=>{
      if(!active)return;
      if(e.key==='Escape'){
        e.preventDefault();e.stopPropagation();
        if(!$('practiceLeavePrompt').hidden){
          $('practiceLeavePrompt').hidden=true;exit.focus();
        }else if(!$('practiceClearPrompt').hidden){
          $('practiceClearPrompt').hidden=true;restart.focus();
        }else close();
        return;
      }
      if(e.key==='Tab'){
        const available=[...overlay.querySelectorAll('button')].filter(
          b=>!b.disabled&&b.getClientRects().length>0);
        const first=available[0],last=available.at(-1);
        if(e.shiftKey&&document.activeElement===first){
          e.preventDefault();last.focus();
        }else if(!e.shiftKey&&document.activeElement===last){
          e.preventDefault();first.focus();
        }else if(!overlay.contains(document.activeElement)){
          e.preventDefault();first.focus();
        }
      }
    },true);
    root.addEventListener('beforeunload',e=>{
      if(!active)return;
      if(hasDraft()||saveStatus==='saving'||
         !storageUsable&&progress?.accepted.length){
        e.preventDefault();e.returnValue='';
      }
    });
    const api={
      open,close,reference:referenceTo,rewrite,returnToCurrent,
      accept:confirmStroke,undo:undoStroke,restart:restartAll,
      whenReady:()=>loadingPromise,whenSaved:()=>savingPromise,
      getTrace:()=>session?session.getSamples().map(p=>({...p})):[],
      getAccepted:()=>progress?progress.getAccepted().map(s=>({
        ...s,samples:s.samples.map(p=>({...p}))
      })):[],
      getInkMetrics:()=>renderer?.getMetrics()||null,
      getState(){
        const s=input?.getState()||{phase:'inactive',acceptedStrokes:0};
        return {active,...(active?stage.getState():{}),
          originalGlyphId:saved?.glyphId??null,
          originalElapsedMs:saved?.elapsedMs??null,
          input:{...s,acceptedStrokes:progress?.currentIndex??0},
          progress:progress?.getState()||null,
          ready,saveStatus,storageUsable,
          liveInkEnabled:true,noHandwritingInput:false,
          noAutomaticScore:true,noPersistentWritingStorage:false,
          localOnlyPersistence:true};
      }
    };
    root.ZITIE_P21A=api;
    root.ZITIE_P21B=api;
    root.ZITIE_P21C=api;
    document.documentElement.dataset.p21aReady='reference-only';
    document.documentElement.dataset.p21bReady='raw-pointer-canvas';
    document.documentElement.dataset.p21cReady='guided-local-v1';
  });
})(typeof window!=='undefined'?window:null);
