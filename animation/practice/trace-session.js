/* P2.1b — a temporary, source-coordinate, lossless user pointer trace.
 * This is a learner's ACTUAL input, never a synthetic brush/teacher score.
 * No browser DOM, networking, localStorage, IndexedDB or SVG source edits.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePracticeTraceSession=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const TYPES=Object.freeze(['pen','touch','mouse']);
  const finite=n=>typeof n==='number'&&Number.isFinite(n);
  const inRange=(x,a,b)=>finite(x)&&x>=a&&x<=b;
  const SOURCE_BOUNDS=Object.freeze({minX:0,maxX:1024,minY:-124,maxY:900});
  const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
  const reasonablePointerId=id=>Number.isInteger(id)&&id>=0;
  function normalizePoint(point,startedAt,previousT,pointerType){
    if(!point||!finite(point.x)||!finite(point.y)||!finite(point.timeStamp))
      throw Error('Nonfinite source pointer sample');
    if(!finite(startedAt)||!finite(previousT))throw Error('Bad pointer clock');
    const x=clamp(point.x,SOURCE_BOUNDS.minX,SOURCE_BOUNDS.maxX);
    const y=clamp(point.y,SOURCE_BOUNDS.minY,SOURCE_BOUNDS.maxY);
    const pressure=pointerType==='pen'&&inRange(point.pressure,0,1)?
      point.pressure:null;
    const tiltX=pointerType==='pen'&&inRange(point.tiltX,-90,90)?
      point.tiltX:null;
    const tiltY=pointerType==='pen'&&inRange(point.tiltY,-90,90)?
      point.tiltY:null;
    return Object.freeze({
      x,y,tMs:Math.max(previousT,point.timeStamp-startedAt,0),
      pressure,tiltX,tiltY,pointerType,
      // Pen pressure from a browser may still be a 0.5 device default.
      pressureSource:pressure===null?null:'device-reported-unverified'
    });
  }
  class TraceSession {
    constructor({maxPoints=8192}={}){
      if(!Number.isInteger(maxPoints)||maxPoints<2||maxPoints>65536)
        throw Error('Bad trace size limit');
      this.maxPoints=maxPoints;
      this.active=null;
      this.draft=null;
      this.cancellations=0;
      this.dropped=0;
    }
    begin(pointerId,pointerType,point){
      if(!reasonablePointerId(pointerId)||!TYPES.includes(pointerType)||
         !point||!finite(point.timeStamp)||point.timeStamp<0)
        return false;
      if(this.active||this.draft)return false; // one stroke per draft
      const start=point.timeStamp;
      const first=normalizePoint(point,start,0,pointerType);
      this.active={pointerId,pointerType,startedAt:start,points:[first]};
      this.dropped=0;
      return true;
    }
    append(pointerId,point){
      const a=this.active;
      if(!a||a.pointerId!==pointerId||!point||
        !finite(point.timeStamp)||point.timeStamp<a.startedAt)return false;
      const prev=a.points[a.points.length-1];
      if(a.points.length>=this.maxPoints){this.dropped++;return false;}
      const value=normalizePoint(point,a.startedAt,prev.tMs,a.pointerType);
      if(value.x===prev.x&&value.y===prev.y&&value.tMs===prev.tMs)
        return false;
      a.points.push(value);
      return true;
    }
    end(pointerId,point){
      const a=this.active;
      if(!a||a.pointerId!==pointerId)return false;
      if(point)this.append(pointerId,point);
      this.draft=Object.freeze({
        schemaVersion:1,
        pointerType:a.pointerType,
        // Stored relative to the pointerdown monotonic event clock.
        durationMs:a.points[a.points.length-1].tMs,
        samples:Object.freeze(a.points.slice()),
        droppedSamples:this.dropped,
        status:'draft-not-accepted'
      });
      this.active=null;
      return true;
    }
    cancel(pointerId,reason='cancelled'){
      if(!this.active||this.active.pointerId!==pointerId)return false;
      this.active=null;
      this.dropped=0;
      this.cancellations++;
      this.lastCancellation=String(reason);
      return true;
    }
    reset(){
      if(this.active)this.cancel(this.active.pointerId,'reset');
      const had=!!this.draft;
      this.draft=null;
      this.dropped=0;
      return had;
    }
    getSamples(){
      return this.active?this.active.points.slice():
        this.draft?this.draft.samples.slice():[];
    }
    getState(){
      return Object.freeze({
        phase:this.active?'drawing':this.draft?'review':'ready',
        pointCount:this.getSamples().length,
        pointerType:this.active?.pointerType||this.draft?.pointerType||null,
        activePointerId:this.active?.pointerId??null,
        durationMs:this.active?
          this.active.points.at(-1).tMs:this.draft?.durationMs??0,
        cancellations:this.cancellations,
        droppedSamples:this.dropped,
        // P2.1c alone may change the accepted-stroke count.
        acceptedStrokes:0,
        hasDraft:!!this.draft
      });
    }
  }
  return {TraceSession,normalizePoint,SOURCE_BOUNDS};
});
