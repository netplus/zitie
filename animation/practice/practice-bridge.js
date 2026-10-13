/* P2.2a — one uninterrupted whole-character practice workflow.
 * Natural pointerup automatically records each actual learner stroke.
 * After the expected count, conservatively match traced strokes by geometry
 * and sequence. No per-stroke confirmation and no authoritative teacher score.
 * A3 brush player, published PDF outlines and canonical order stay read-only.
 */
(function(root){
 'use strict';
 const $=id=>document.getElementById(id);
 root.addEventListener('DOMContentLoaded',()=>{
   const book=root.ZITIE_A3_BOOK,Ref=root.ZitiePracticeReference;
   const Trace=root.ZitiePracticeTraceSession,Ink=root.ZitiePracticeInkCanvas;
   const Input=root.ZitiePracticePointerInput,Whole=root.ZitieWholeWriting;
   const Matcher=root.ZitieStrokeOrderCheck,Storage=root.ZitiePracticeLocalStore;
   const overlay=$('practiceOverlay'),source=$('paperSvg');
   const board=$('practiceSvg'),surface=$('practiceInk'),launch=$('practiceLaunch');
   const paper=source?.closest('.paper'),main=document.querySelector('main.page');
   const exit=$('practiceExit'),prev=$('practicePrev'),next=$('practiceNext'),
     undo=$('practiceUndo'),restart=$('practiceRestart'),
     returnCurrent=$('practiceReturnCurrent');
   if(!book||!Ref||!Trace||!Ink||!Input||!Whole||!Matcher||!Storage||
      !overlay||!source||!board||!surface||!launch||!paper||!main||
      !exit||!prev||!next||!undo||!restart||!returnCurrent||
      !$('practiceOrderResult')){
     document.documentElement.dataset.p22aError='missing-dependency';return;
   }
   const stage=new Ref.ReferenceStage(board);
   const store=new Storage.LocalPracticeStore();
   let active=false,saved=null,priorFocus=null,priorOverflow='',priorInert=false;
   let session=null,renderer=null,input=null,progress=null,ready=false;
   let saveStatus='loading',storageUsable=true,storageMessage='',restoreBlocked=false;
   let generation=0,loadingPromise=Promise.resolve(false),savingPromise=Promise.resolve();
   let lastFeedback='',closeQueued=false,cachedVerdict=null,cachedRevision=-1;
   const identity=()=>({glyphId:progress.glyphId,
     sourceHash:progress.sourceHash,pdfHash:progress.pdfHash});
   const drawingAllowed=()=>active&&ready&&!restoreBlocked&&!progress.complete&&
     stage.currentIndex===progress.currentIndex;
   const hasIncompleteStroke=()=>!!session?.active||!!session?.draft;
   const closeWarning=()=>hasIncompleteStroke()||
     (!storageUsable&&progress?.currentIndex>0);
   function verdict(){
     if(!progress?.complete)return null;
     if(progress.legacyImported)return {status:'uncertain',
       matcherVersion:Matcher.VERSION,
       message:'旧版逐笔确认记录已保留，但未经轨迹自动识别，不判定正确。建议重新写完整个字。'};
     if(cachedRevision!==progress.revision){
       cachedVerdict=Matcher.evaluate(
         {strokes:stage.reference.strokes},progress.getWritten());
       cachedRevision=progress.revision;
     }
     return cachedVerdict;
   }
   function update(){
     if(!active||!progress)return;
     const s=progress.getState(),frame=stage.getState(),ink=session?.getState();
     const preview=stage.currentIndex!==s.currentIndex&&!s.completed;
     $('practiceTitle').textContent='整字临摹 · '+frame.character;
     $('practiceProgress').textContent='已写 '+s.writtenStrokes+' / '+s.strokeCount+' 笔';
     $('practiceStrokeTitle').textContent=s.completed?
       '整字书写完成 · '+s.strokeCount+' 笔':
       '第 '+(s.currentIndex+1)+' / '+s.strokeCount+
       ' 次落笔 · 参考：'+frame.label;
     $('practiceStrokeHint').textContent=s.completed?
       '蓝墨是你实际写出的每一笔；下方显示参考笔顺工程检查结果。':
       preview?'正在查看参考笔画；点「返回当前待写笔」即可继续写。':
       '沿参考自然书写并抬笔即可记录，不用点击确认；请继续写完整个字。';
     board.setAttribute('aria-label',frame.character+
       '真实手写蓝墨，完整写字后给出参考笔顺的保守工程判断');
     prev.disabled=!ready||stage.currentIndex===0;
     next.disabled=!ready||stage.currentIndex>=frame.strokeCount-1;
     returnCurrent.hidden=!ready||(!s.completed&&!preview);
     returnCurrent.disabled=!ready;
     undo.disabled=!ready||!s.writtenStrokes||ink?.phase==='drawing';
     restart.disabled=!ready;
     if(input)input.enabled=drawingAllowed();
     const status=$('practicePreviewStatus');
     if(!ready)status.textContent='正在读取这个字已写的本地笔迹…';
     else if(restoreBlocked)status.textContent=
       '历史记录与字形来源不匹配；需要先明确清空此字练习记录。';
     else if(s.completed)status.textContent=
       '已自动记录 '+s.writtenStrokes+' 笔并完成整字比对。可撤销或重写整字。';
     else if(preview)status.textContent=
       '只读参考预览；不会改变已写笔画，也不能在预览状态落笔。';
     else if(lastFeedback)status.textContent=lastFeedback;
     else if(ink?.phase==='drawing')status.textContent=
       '正在书写：已采集 '+ink.pointCount+' 个真实触点。';
     else status.textContent=input?.lastCancel?
       '触控中断，当前未完成笔画已舍弃，之前已写的笔迹保留。':
       '请直接落笔；每次自然抬笔即自动记一笔。';
     const complete=$('practiceCompletion');
     complete.hidden=!s.completed;
     complete.textContent=s.completed?
       '整字已写完：'+s.writtenStrokes+' / '+s.strokeCount+
       ' 笔。保留全部实际蓝色轨迹，不代替书法教师评分。':'';
     const result=$('practiceOrderResult'),assessment=verdict();
     result.hidden=!assessment;
     if(assessment){
       result.dataset.outcome=assessment.status;
       result.textContent=assessment.message;
     }else{
       result.dataset.outcome='none';result.textContent='';
     }
     const save=$('practiceSaved');
     save.dataset.status=saveStatus==='error'?'error':'normal';
     const names={
       loading:'正在读取浏览器本地已写笔迹…',
       new:'还没有本地笔迹；每次抬笔后自动保存。',
       restored:'已从本机恢复 '+s.writtenStrokes+' 笔。',
       saving:'正在将实际笔迹保存在本机…',
       saved:'已在本机保存 '+s.writtenStrokes+' 笔（不会上传）。',
       cleared:'本机该字的已写笔迹已清空。',
       error:'本机保存不可用：笔迹暂时只在页面内，退出可能丢失。'
     };
     save.textContent=(names[saveStatus]||names.new)+
       (storageMessage?' · '+storageMessage:'');
   }
   function hidePrompts(){
     // Exiting while a pen stroke is unfinished may still warn; restarting
     // the whole character is an immediate action without a dialog.
     $('practiceLeavePrompt').hidden=true;
   }
   function invalidateVerdict(){cachedVerdict=null;cachedRevision=-1;}
   function syncInk(){if(renderer)renderer.paint(true);}
   function renderCurrent(){
     if(!progress)return;
     stage.showStroke(Math.min(progress.currentIndex,progress.strokeCount-1));
     if(input)input.enabled=drawingAllowed();
     syncInk();update();
   }
   function persist(){
     if(!storageUsable)return Promise.resolve(false);
     const captured=progress.snapshot(),g=generation;
     saveStatus='saving';storageMessage='';update();
     const job=store.save(captured).then(()=>{
       if(active&&g===generation&&progress.revision===captured.revision){
         saveStatus='saved';update();
       }
       return true;
     }).catch(()=>{
       if(g===generation){
         storageUsable=false;saveStatus='error';
         storageMessage='当前已写笔迹保留在内存，请勿直接关闭浏览器';
         update();
       }
       return false;
     });
     savingPromise=job;
     return job;
   }
   function onInputChanged(reason){
     if(!active||!progress)return;
     if(reason==='up'&&drawingAllowed()&&session?.draft){
       // Natural lift records ONE user stroke without a confirmation button.
       const result=progress.append(session.draft);
       // Raw points have been frozen into the progress record before reset.
       input.reset();
       if(result.ok){
         invalidateVerdict();
         lastFeedback=progress.complete?'已写完整个字，正在展示笔顺比对结果。':
           '第 '+progress.currentIndex+' 笔已自动记录，继续写下一笔。';
         renderCurrent();persist();
       }else{
         lastFeedback='本次落笔行程过短或采样无效，未计入笔画；请重新写。';
         renderer.schedule();update();
       }
       return;
     }
     renderer?.schedule();
     update();
   }
   function open(){
     if(active)return true;
     const glyph=book.getGlyph(),state=book.player.getState();
     if(!glyph||!state)return false;
     stage.setGlyph(glyph);
     progress=new Whole.WholeWriting({glyphId:glyph.main_id,
       strokeCount:glyph.strokes.length,sourceHash:glyph.source_sha256,
       pdfHash:book.pack.publication.sha256});
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
     overlay.hidden=false;active=true;ready=false;generation++;
     const g=generation;
     document.documentElement.dataset.p21aActive='true';
     document.documentElement.dataset.p21bActive='true';
     document.documentElement.dataset.p21cActive='true';
     document.documentElement.dataset.p22aActive='true';
     document.body.style.overflow='hidden';main.inert=true;
     saveStatus='loading';storageUsable=true;storageMessage='';
     restoreBlocked=false;lastFeedback='';closeQueued=false;
     invalidateVerdict();hidePrompts();
     session=new Trace.TraceSession();
     renderer=new Ink.TraceCanvas(surface,stage.group,
       ()=>session.getSamples(),()=>progress.getWritten());
     input=new Input.PointerInput({surface,group:stage.group,session,
       onChange:onInputChanged,onLayout:()=>renderer.resize()});
     input.enabled=false;
     update();exit.focus({preventScroll:true});
     loadingPromise=(async()=>{
       try{
         const value=await store.load(identity());
         if(!active||g!==generation)return false;
         if(value&&!progress.restore(value)){
           storageUsable=false;saveStatus='error';restoreBlocked=true;
           storageMessage='历史记录与笔画来源不匹配；请先选择重新写整字清空';
         }else saveStatus=value?'restored':'new';
       }catch(_){
         if(!active||g!==generation)return false;
         storageUsable=false;saveStatus='error';
         storageMessage='浏览器可能禁用 IndexedDB';
       }
       if(!active||g!==generation)return false;
       ready=true;invalidateVerdict();renderCurrent();
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
     generation++;disposeInk();overlay.hidden=true;active=false;ready=false;
     for(const name of ['p21aActive','p21bActive','p21cActive','p22aActive'])
       delete document.documentElement.dataset[name];
     main.inert=priorInert;document.body.style.overflow=priorOverflow;
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
     saved=null;progress=null;invalidateVerdict();
     if(priorFocus?.isConnected&&typeof priorFocus.focus==='function')
       priorFocus.focus({preventScroll:true});
     else launch.focus({preventScroll:true});
     return true;
   }
   function close({discardDraft=false}={}){
     if(!active)return false;
     if(!discardDraft&&closeWarning()){
       $('practiceLeavePrompt').hidden=false;
       $('practiceLeavePrompt').querySelector('p').textContent=
         !storageUsable&&progress?.currentIndex?
         '本机保存失败，退出将丢失已经写过的笔迹，确定离开吗？':
         '当前一笔尚未抬笔完成，退出将舍弃这笔；已经存储的笔迹仍保留在本机。';
       $('practiceLeaveYes').focus();return false;
     }
     if(saveStatus==='saving'){
       if(!closeQueued){
         closeQueued=true;
         savingPromise.finally(()=>{
           closeQueued=false;
           if(active)close({discardDraft});
         });
       }
       return false;
     }
     return reallyClose();
   }
   function referenceTo(index){
     if(!active||!ready||!Number.isInteger(index)||
        index<0||index>=stage.reference.strokeCount)return false;
     if(input)input.reset();
     stage.showStroke(index);
     lastFeedback='';syncInk();update();return true;
   }
   function returnToCurrent(){
     if(!active||!ready)return false;
     if(input)input.reset();
     lastFeedback='';renderCurrent();return true;
   }
   function undoStroke(){
     if(!active||!ready||!progress.written.length||session?.active)return false;
     input.reset();if(!progress.undo())return false;
     invalidateVerdict();
     lastFeedback='已撤销上一笔，可以直接重新写；无需确认按钮。';
     renderCurrent();persist();return true;
   }
   function restartAll(){
     if(!active||!ready)return false;
     hidePrompts();input.reset();progress.restart();invalidateVerdict();
     lastFeedback='已清空整字，请从第一笔重新连续书写。';
     renderCurrent();
     const g=generation;
     saveStatus='saving';update();
     savingPromise=store.remove(identity()).then(()=>{
       if(active&&g===generation){
         saveStatus='cleared';storageUsable=true;
         storageMessage='';restoreBlocked=false;update();
       }
       return true;
     }).catch(()=>{
       if(active&&g===generation){
         saveStatus='error';storageUsable=false;
         storageMessage='浏览器清除该字记录失败，请检查存储权限';
         update();
       }
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
   undo.addEventListener('click',undoStroke);
   restart.addEventListener('click',restartAll);
   returnCurrent.addEventListener('click',returnToCurrent);
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
     if(active&&(hasIncompleteStroke()||saveStatus==='saving'||
       (!storageUsable&&progress?.currentIndex))){
       e.preventDefault();e.returnValue='';
     }
   });
   const api={
     open,close,reference:referenceTo,returnToCurrent,
     undo:undoStroke,restart:restartAll,
     whenReady:()=>loadingPromise,whenSaved:()=>savingPromise,
     getTrace:()=>session?session.getSamples().map(p=>({...p})):[],
     getWritten:()=>progress?progress.getWritten().map(s=>({
       ...s,samples:s.samples.map(p=>({...p}))
     })):[],
     // Retain a read-only test hook for old integration code; these are
     // *captured*, not human-confirmed, strokes.
     getAccepted:()=>progress?progress.getWritten().map(s=>({
       ...s,samples:s.samples.map(p=>({...p}))
     })):[],
     getInkMetrics:()=>renderer?.getMetrics()||null,
     getOrderCheck:()=>verdict(),
     getState(){
       const s=input?.getState()||{phase:'inactive',acceptedStrokes:0};
       return {active,...(active?stage.getState():{}),
         originalGlyphId:saved?.glyphId??null,
         originalElapsedMs:saved?.elapsedMs??null,
         input:{...s,writtenStrokes:progress?.currentIndex??0,
           acceptedStrokes:0},
         progress:progress?.getState()||null,
         orderCheck:verdict(),ready,saveStatus,storageUsable,restoreBlocked,
         liveInkEnabled:true,noHandwritingInput:false,
         noAutomaticScore:true,noPersistentWritingStorage:false,
         localOnlyPersistence:true,continuousWriting:true,
         manualStrokeConfirm:false};
     }
   };
   root.ZITIE_P21A=api;
   root.ZITIE_P21B=api;
   root.ZITIE_P21C=api;
   root.ZITIE_P22A=api;
   document.documentElement.dataset.p21aReady='reference-only';
   document.documentElement.dataset.p21bReady='raw-pointer-canvas';
   document.documentElement.dataset.p21cReady='guided-local-v1';
   document.documentElement.dataset.p22aReady='whole-word-v1';
 });
})(typeof window!=='undefined'?window:null);