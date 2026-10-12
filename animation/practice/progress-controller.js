/* P2.1c — ordered user-confirmed handwritten strokes, independent of A3.
 * PDF source strokes and motion medians remain read-only teaching references;
 * the only recorded geometry is the learner's actual P2.1b pointer samples.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePracticeProgress=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const hash=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const types=['pen','touch','mouse'];
  const MAX_SAMPLES=8192;
  const MODEL_BOUNDS={minX:0,maxX:1024,minY:-124,maxY:900};
  function validSamples(samples,pointerType){
    if(!Array.isArray(samples)||samples.length<2||samples.length>MAX_SAMPLES||
       !types.includes(pointerType))return false;
    let previous=-1,distance=0,old=null;
    for(const s of samples){
      if(!s||!finite(s.x)||!finite(s.y)||!finite(s.tMs)||
         s.x<MODEL_BOUNDS.minX||s.x>MODEL_BOUNDS.maxX||
         s.y<MODEL_BOUNDS.minY||s.y>MODEL_BOUNDS.maxY||
         s.tMs<previous||s.tMs<0||s.tMs>120000||s.pointerType!==pointerType||
         !(s.pressure===null||(pointerType==='pen'&&finite(s.pressure)&&
           s.pressure>=0&&s.pressure<=1))||
         !(s.tiltX===null||(pointerType==='pen'&&finite(s.tiltX)&&
           Math.abs(s.tiltX)<=90))||
         !(s.tiltY===null||(pointerType==='pen'&&finite(s.tiltY)&&
           Math.abs(s.tiltY)<=90))||
         (s.pressureSource!==null&&s.pressureSource!=='device-reported-unverified'))
        return false;
      if(old)distance+=Math.hypot(s.x-old.x,s.y-old.y);
      previous=s.tMs;old=s;
    }
    // A one-point tap (or same-coordinate noise) is not a drawn stroke.
    return distance>=3;
  }
  function copyConfirmed(draft,index){
    if(!draft||draft.schemaVersion!==1||
       draft.status!=='draft-not-accepted'||draft.droppedSamples!==0||
       !validSamples(draft.samples,draft.pointerType))return null;
    const samples=Object.freeze(draft.samples.map(s=>Object.freeze({
      x:s.x,y:s.y,tMs:s.tMs,pressure:s.pressure,
      tiltX:s.tiltX,tiltY:s.tiltY,pointerType:s.pointerType,
      pressureSource:s.pressureSource
    })));
    return Object.freeze({index,status:'userConfirmed',
      pointerType:draft.pointerType,durationMs:samples.at(-1).tMs,
      samples});
  }
  function validateConfirmed(s,index){
    if(!s||s.index!==index||s.status!=='userConfirmed'||
       !types.includes(s.pointerType)||!validSamples(s.samples,s.pointerType)||
       !finite(s.durationMs)||s.durationMs!==s.samples.at(-1).tMs)
      return null;
    return Object.freeze({index,status:'userConfirmed',pointerType:s.pointerType,
      durationMs:s.durationMs,
      samples:Object.freeze(s.samples.map(p=>Object.freeze({
        x:p.x,y:p.y,tMs:p.tMs,pressure:p.pressure,
        tiltX:p.tiltX,tiltY:p.tiltY,pointerType:p.pointerType,
        pressureSource:p.pressureSource
      })))});
  }
  class PracticeProgress{
    constructor({glyphId,strokeCount,sourceHash,pdfHash}={}){
      if(!Number.isInteger(glyphId)||glyphId<1||glyphId>201||
         !Number.isInteger(strokeCount)||strokeCount<1||strokeCount>35||
         !hash(sourceHash)||!hash(pdfHash))
        throw Error('Invalid canonical PDF practice identity');
      this.glyphId=glyphId;this.strokeCount=strokeCount;
      this.sourceHash=sourceHash;this.pdfHash=pdfHash;
      this.accepted=[];this.revision=0;
    }
    get currentIndex(){return this.accepted.length;}
    get complete(){return this.currentIndex===this.strokeCount;}
    getAccepted(){return this.accepted.slice();}
    getState(){return {glyphId:this.glyphId,strokeCount:this.strokeCount,
      currentIndex:this.currentIndex,acceptedStrokes:this.currentIndex,
      completed:this.complete,revision:this.revision};}
    accept(draft){
      if(this.complete)return {ok:false,reason:'already-completed'};
      const value=copyConfirmed(draft,this.currentIndex);
      if(!value)return {ok:false,reason:'invalid-or-incomplete-stroke'};
      this.accepted.push(value);this.revision++;
      return {ok:true,index:value.index,completed:this.complete};
    }
    undo(){
      if(!this.accepted.length)return false;
      this.accepted.pop();this.revision++;return true;
    }
    restart(){
      if(!this.accepted.length)return false;
      this.accepted=[];this.revision++;return true;
    }
    snapshot(){
      return {schemaVersion:1,glyphId:this.glyphId,
        strokeCount:this.strokeCount,sourceHash:this.sourceHash,
        pdfHash:this.pdfHash,revision:this.revision,
        accepted:this.accepted.map(s=>({
          index:s.index,status:s.status,pointerType:s.pointerType,
          durationMs:s.durationMs,samples:s.samples.map(p=>({...p}))
        }))};
    }
    restore(value){
      if(!value||value.schemaVersion!==1||
         value.glyphId!==this.glyphId||value.strokeCount!==this.strokeCount||
         value.sourceHash!==this.sourceHash||value.pdfHash!==this.pdfHash||
         !Number.isSafeInteger(value.revision)||value.revision<0||
         !Array.isArray(value.accepted)||
         value.accepted.length>this.strokeCount||
         value.revision<value.accepted.length)
        return false;
      const accepted=[];
      for(let i=0;i<value.accepted.length;i++){
        const valid=validateConfirmed(value.accepted[i],i);
        if(!valid)return false;accepted.push(valid);
      }
      // Transactional, all-or-nothing restore. Never adopt untrusted geometry
      // until every field and every consecutive ordinal is valid.
      this.accepted=accepted;
      this.revision=value.revision;
      return true;
    }
  }
  return {PracticeProgress,validSamples,copyConfirmed,validateConfirmed};
});
