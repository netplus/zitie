/* P2.1b — Pointer Events bridge for actual contact samples only.
 * No browser-generated prediction, synthetic A3 pressure, score or storage.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePracticePointerInput=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  function sourcePoint(event,group){
    if(!event||!group||typeof group.getScreenCTM!=='function'||
       typeof DOMPoint==='undefined')throw Error('SVG source coordinates unavailable');
    const screen=group.getScreenCTM();
    if(!screen)throw Error('Reference SVG is not connected');
    const point=new DOMPoint(event.clientX,event.clientY)
      .matrixTransform(screen.inverse());
    if(!Number.isFinite(point.x)||!Number.isFinite(point.y))
      throw Error('Invalid transformed pointer coordinate');
    return {x:point.x,y:point.y,timeStamp:event.timeStamp,
      pressure:event.pressure,tiltX:event.tiltX,tiltY:event.tiltY};
  }
  function sampleEvents(event,withCoalesced){
    let values=[];
    if(withCoalesced&&typeof event.getCoalescedEvents==='function'){
      try{const items=event.getCoalescedEvents();if(Array.isArray(items))values=items;}
      catch(_){values=[];} // Safari/WebView implementations may differ.
    }
    return [...values,event].filter(x=>x&&x.pointerId===event.pointerId)
      .sort((a,b)=>a.timeStamp-b.timeStamp);
  }
  class PointerInput{
    constructor({surface,group,session,onChange=()=>{},onLayout=()=>{}}={}){
      if(!surface||!group||!session)throw Error('P2.1b input stage missing');
      this.surface=surface;
      this.group=group;
      this.session=session;
      this.onChange=onChange;
      this.onLayout=onLayout;
      this.enabled=true;
      this.lastCancel=null;
      this.captureFailures=0;
      this.handlers={
        down:e=>this.down(e),
        move:e=>this.move(e),
        up:e=>this.up(e),
        cancel:e=>this.cancelEvent(e,'pointercancel'),
        lost:e=>this.cancelEvent(e,'lostpointercapture'),
        hidden:()=>{if(document.visibilityState==='hidden')this.abort('visibilitychange');},
        rotate:()=>this.abort('orientationchange'),
        resize:()=>this.onResize()
      };
      surface.addEventListener('pointerdown',this.handlers.down);
      // Window listeners catch events even when capture is unavailable.
      window.addEventListener('pointermove',this.handlers.move,true);
      window.addEventListener('pointerup',this.handlers.up,true);
      window.addEventListener('pointercancel',this.handlers.cancel,true);
      surface.addEventListener('lostpointercapture',this.handlers.lost);
      document.addEventListener('visibilitychange',this.handlers.hidden);
      window.addEventListener('orientationchange',this.handlers.rotate);
      window.addEventListener('resize',this.handlers.resize);
    }
    point(e){return sourcePoint(e,this.group);}
    down(e){
      if(!this.enabled||this.session.active||this.session.draft||
         e.isPrimary===false||e.pointerType==='mouse'&&e.button!==0)return;
      const b=this.surface.getBoundingClientRect();
      if(e.clientX<b.left||e.clientX>b.right||
         e.clientY<b.top||e.clientY>b.bottom)return;
      let point;
      try{point=this.point(e);}catch(_){return;}
      if(!this.session.begin(e.pointerId,e.pointerType,point))return;
      try{this.surface.setPointerCapture(e.pointerId);}
      catch(_){this.captureFailures++;} // Fallback: window move/up.
      if(e.cancelable)e.preventDefault();
      this.onChange('down');
    }
    move(e){
      const active=this.session.active;
      if(!this.enabled||!active||e.pointerId!==active.pointerId)return;
      let changed=false;
      for(const item of sampleEvents(e,true)){
        try{changed=this.session.append(e.pointerId,this.point(item))||changed;}
        catch(_){this.abort('invalid-coordinate');return;}
      }
      if(changed)this.onChange('move');
      if(e.cancelable)e.preventDefault();
    }
    up(e){
      const active=this.session.active;
      if(!active||e.pointerId!==active.pointerId)return;
      let point;
      try{point=this.point(e);}
      catch(_){this.abort('invalid-coordinate');return;}
      this.session.end(e.pointerId,point);
      this.release(e.pointerId);
      if(e.cancelable)e.preventDefault();
      this.onChange('up');
    }
    cancelEvent(e,reason){
      if(!this.session.active||e.pointerId!==this.session.active.pointerId)return;
      this.abort(reason);
    }
    release(pointerId){
      try{
        if(this.surface.hasPointerCapture(pointerId))
          this.surface.releasePointerCapture(pointerId);
      }catch(_){/* pointer capture may have been revoked by the browser */}
    }
    abort(reason){
      if(!this.session.active)return false;
      const id=this.session.active.pointerId;
      this.session.cancel(id,reason);
      this.release(id);
      this.lastCancel=reason;
      this.onChange('cancel');
      return true;
    }
    reset(){
      this.abort('reset');
      this.session.reset();
      this.lastCancel=null;
      this.onChange('reset');
    }
    onResize(){
      // Resizing during an active stroke changes geometry and hence its
      // path; never splice different coordinate transforms into one line.
      this.abort('resize');
      this.onLayout();
    }
    destroy(){
      this.enabled=false;
      this.abort('destroy');
      this.surface.removeEventListener('pointerdown',this.handlers.down);
      window.removeEventListener('pointermove',this.handlers.move,true);
      window.removeEventListener('pointerup',this.handlers.up,true);
      window.removeEventListener('pointercancel',this.handlers.cancel,true);
      this.surface.removeEventListener('lostpointercapture',this.handlers.lost);
      document.removeEventListener('visibilitychange',this.handlers.hidden);
      window.removeEventListener('orientationchange',this.handlers.rotate);
      window.removeEventListener('resize',this.handlers.resize);
    }
    getState(){
      return {lastCancel:this.lastCancel,captureFailures:this.captureFailures,
        ...this.session.getState()};
    }
  }
  return {sourcePoint,sampleEvents,PointerInput};
});
