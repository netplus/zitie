/* P2.2a — whole-character free-flow handwriting model.
 * Each natural pointerup is recorded automatically; there is no per-stroke
 * confirmation. An ordinal here is a learner-input sequence only and must
 * NOT be confused with a verified match to a canonical reference stroke.
 * Supports fail-closed read-only import of P2.1c local user-confirmed ink.
 */
(function(root,factory){
 const Legacy=typeof module==='object'&&module.exports?
   require('./progress-controller.js'):root.ZitiePracticeProgress;
 const api=factory(Legacy);
 if(typeof module==='object'&&module.exports)module.exports=api;
 if(root)root.ZitieWholeWriting=api;
})(typeof window!=='undefined'?window:null,function(Legacy){
 'use strict';
 function freezeRecord(draft,index){
   const converted=Legacy.copyConfirmed(draft,index);
   if(!converted)return null;
   return Object.freeze({index,status:'raw-captured',
     pointerType:converted.pointerType,durationMs:converted.durationMs,
     samples:converted.samples});
 }
 function validateRecord(stroke,index){
   if(!stroke||stroke.index!==index||stroke.status!=='raw-captured')
     return null;
   const valid=Legacy.validateConfirmed({...stroke,status:'userConfirmed'},index);
   if(!valid)return null;
   return Object.freeze({index,status:'raw-captured',pointerType:valid.pointerType,
     durationMs:valid.durationMs,samples:valid.samples});
 }
 class WholeWriting{
   constructor(identity={}){
     const checked=new Legacy.PracticeProgress(identity);
     this.glyphId=checked.glyphId;
     this.strokeCount=checked.strokeCount;
     this.sourceHash=checked.sourceHash;
     this.pdfHash=checked.pdfHash;
     this.written=[];this.revision=0;this.legacyImported=false;
   }
   get currentIndex(){return this.written.length;}
   get complete(){return this.currentIndex>=this.strokeCount;}
   getWritten(){return this.written.slice();}
   getState(){return {glyphId:this.glyphId,strokeCount:this.strokeCount,
     currentIndex:this.currentIndex,writtenStrokes:this.currentIndex,
     completed:this.complete,revision:this.revision,
     legacyImported:this.legacyImported};}
   append(draft){
     if(this.complete)return {ok:false,reason:'whole-character-full'};
     const value=freezeRecord(draft,this.currentIndex);
     if(!value)return {ok:false,reason:'invalid-or-incomplete-trace'};
     this.written.push(value);this.revision++;
     return {ok:true,written:this.currentIndex,completed:this.complete};
   }
   undo(){
     if(!this.written.length)return false;
     this.written.pop();this.revision++;
     if(this.written.length===0)this.legacyImported=false;
     return true;
   }
   restart(){
     const had=this.written.length>0||this.legacyImported;
     this.written=[];this.revision++;this.legacyImported=false;
     return had;
   }
   snapshot(){
     return {schemaVersion:2,glyphId:this.glyphId,strokeCount:this.strokeCount,
       sourceHash:this.sourceHash,pdfHash:this.pdfHash,revision:this.revision,
       legacyImported:this.legacyImported,
       written:this.written.map(s=>({
         index:s.index,status:'raw-captured',pointerType:s.pointerType,
         durationMs:s.durationMs,samples:s.samples.map(p=>({...p}))
       }))};
   }
   restore(data){
     if(data?.schemaVersion===1){
       const old=new Legacy.PracticeProgress({
         glyphId:this.glyphId,strokeCount:this.strokeCount,
         sourceHash:this.sourceHash,pdfHash:this.pdfHash
       });
       if(!old.restore(data))return false;
       const verified=old.getAccepted().map((s,index)=>Object.freeze({
         index,status:'raw-captured',pointerType:s.pointerType,
         durationMs:s.durationMs,samples:s.samples}));
       // P2.1c users pressed 'confirm', but that confirmation is NOT evidence
       // a machine verified the order; keep the legacy flag until restart.
       this.written=verified;this.revision=old.revision;
       this.legacyImported=verified.length>0;
       return true;
     }
     if(!data||data.schemaVersion!==2||
        data.glyphId!==this.glyphId||data.strokeCount!==this.strokeCount||
        data.sourceHash!==this.sourceHash||data.pdfHash!==this.pdfHash||
        !Number.isSafeInteger(data.revision)||data.revision<0||
        !Array.isArray(data.written)||data.written.length>this.strokeCount||
        data.revision<data.written.length||
        typeof data.legacyImported!=='boolean')return false;
     const values=[];
     for(let i=0;i<data.written.length;i++){
       const valid=validateRecord(data.written[i],i);
       if(!valid)return false;
       values.push(valid);
     }
     // Transactional restore; do not mutate the live state on any failure.
     this.written=values;this.revision=data.revision;
     this.legacyImported=data.legacyImported&&values.length>0;
     return true;
   }
 }
 return {WholeWriting,freezeRecord,validateRecord};
});