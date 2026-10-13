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
    if(!event||!group||typeof group.getScreenCTM!=='function')
      throw Error('SVG source coordinates unavailable');
    const m=group.getScreenCTM();
    if(!m)throw Error('Reference SVG is not connected');
    // getScreenCTM() returns an affine client-CSS-pixel transform.
    // This exact inverse works on SVGMatrix and DOMMatrix alike; some iOS
    // WebViews do not expose global DOMPoint or its matrixTransform().
    const values=[m.a,m.b,m.c,m.d,m.e,m.f,event.clientX,event.clientY];
    if(!values.every(Number.isFinite))
      throw Error('Invalid SVG screen transform or client coordinates');
    const det=m.a*m.d-m.b*m.c;
    if(!Number.isFinite(det)||Math.abs(det)<1e-12)
      throw Error('Singular SVG screen transform');
    const dx=event.clientX-m.e,dy=event.clientY-m.f;
    const x=(m.d*dx-m.c*dy)/det,y=(m.a*dy-m.b*dx)/det;
    if(!Number.isFinite(x)||!Number.isFinite(y))
      throw Error('Invalid transformed pointer coordinate');
    return {x,y,timeStamp:event.timeStamp,
      pressure:event.pressure,tiltX:event.tiltX,tiltY:event.tiltY};
  }
  function edgeIOSPreferredTouch(ua,touchSupported){
    return !!touchSupported&&/EdgiOS\//i.test(ua||'')&&
      /iPhone|iPad|iPod/i.test(ua||'');
  }
  function changedTouch(event,id){
    const touches=event?.changedTouches;
    if(!touches)return null;
    for(let i=0;i<touches.length;i++){
      const t=touches[i];
      if(t.identifier===id)return t;
    }
    return null;
  }
  function sourceTouch(touch,event,group){
    // Touch force must NEVER masquerade as pen pressure. We record finger
    // coordinates and real event timestamps, not a generated pen stroke.
    return sourcePoint({clientX:touch.clientX,clientY:touch.clientY,
      timeStamp:event.timeStamp,pressure:undefined,tiltX:undefined,
      tiltY:undefined},group);
  }
  function geometry(surface){
    const rect=surface.getBoundingClientRect();
    return {width:rect.width,height:rect.height};
  }
  function geometryChanged(before,after){
    return !before||!after||
      Math.abs(before.width-after.width)>1.5||
      Math.abs(before.height-after.height)>1.5;
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
    constructor({surface,group,session,onChange=()=>{},onLayout=()=>{},
      preferTouchInput=null}={}){
      if(!surface||!group||!session)throw Error('P2.1b input stage missing');
      this.surface=surface;
      this.group=group;
      this.session=session;
      this.onChange=onChange;
      this.onLayout=onLayout;
      this.enabled=true;
      this.lastCancel=null;
      this.captureFailures=0;
      // Prefer actual Touch Events only for Edge's iOS WKWebView finger
      // channel. Native pointer pen and mouse are left intact. Elsewhere
      // Touch Events are a fallback only when pointerdown did not arrive.
      const ua=typeof navigator!=='undefined'?navigator.userAgent:'';
      const touchAvailable=typeof window!=='undefined'&&
        ('ontouchstart' in window||typeof window.TouchEvent==='function');
      this.preferTouchInput=preferTouchInput===null?
        edgeIOSPreferredTouch(ua,touchAvailable):!!preferTouchInput;
      this.activeSource=null;
      this.touchIdentifier=null;
      this.activeGeometry=null;
      this.touchFallbackStarts=0;
      this.handlers={
        down:e=>this.down(e),
        move:e=>this.move(e),
        up:e=>this.up(e),
        cancel:e=>this.cancelEvent(e,'pointercancel'),
        lost:e=>this.cancelEvent(e,'lostpointercapture'),
        touchStart:e=>this.touchStart(e),
        touchMove:e=>this.touchMove(e),
        touchEnd:e=>this.touchEnd(e),
        touchCancel:e=>this.touchCancel(e),
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
      surface.addEventListener('touchstart',this.handlers.touchStart,{passive:false});
      window.addEventListener('touchmove',this.handlers.touchMove,
        {capture:true,passive:false});
      window.addEventListener('touchend',this.handlers.touchEnd,true);
      window.addEventListener('touchcancel',this.handlers.touchCancel,true);
      document.addEventListener('visibilitychange',this.handlers.hidden);
      window.addEventListener('orientationchange',this.handlers.rotate);
      window.addEventListener('resize',this.handlers.resize);
    }
    point(e){return sourcePoint(e,this.group);}
    down(e){
      if(this.preferTouchInput&&e.pointerType==='touch')return;
      if(!this.enabled||this.session.active||this.session.draft||
         e.isPrimary===false||e.pointerType==='mouse'&&e.button!==0)return;
      const b=this.surface.getBoundingClientRect();
      if(e.clientX<b.left||e.clientX>b.right||
         e.clientY<b.top||e.clientY>b.bottom)return;
      let point;
      try{point=this.point(e);}catch(_){return;}
      if(!this.session.begin(e.pointerId,e.pointerType,point))return;
      this.activeSource='pointer';
      this.activeGeometry=geometry(this.surface);
      try{this.surface.setPointerCapture(e.pointerId);}
      catch(_){this.captureFailures++;} // Fallback: window move/up.
      if(e.cancelable)e.preventDefault();
      this.onChange('down');
    }
    move(e){
      const active=this.session.active;
      if(!this.enabled||this.activeSource!=='pointer'||!active||
         e.pointerId!==active.pointerId)return;
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
      if(this.activeSource!=='pointer'||!active||
         e.pointerId!==active.pointerId)return;
      let point;
      try{point=this.point(e);}
      catch(_){this.abort('invalid-coordinate');return;}
      this.session.end(e.pointerId,point);
      this.release(e.pointerId);
      this.activeSource=null;
      this.activeGeometry=null;
      if(e.cancelable)e.preventDefault();
      this.onChange('up');
    }
    cancelEvent(e,reason){
      if(this.activeSource!=='pointer'||!this.session.active||
         e.pointerId!==this.session.active.pointerId)return;
      this.abort(reason);
    }
    touchStart(e){
      if(!this.enabled||this.session.draft)return;
      if(this.activeSource==='touch'&&e.touches?.length>1){
        this.abort('multitouch');return;
      }
      if(this.session.active||e.touches?.length!==1||
         e.changedTouches?.length!==1)return;
      const touch=e.changedTouches[0];
      if(!Number.isInteger(touch.identifier)||touch.identifier<0)return;
      let point;
      try{point=sourceTouch(touch,e,this.group);}catch(_){return;}
      if(!this.session.begin(touch.identifier,'touch',point))return;
      this.activeSource='touch';
      this.touchIdentifier=touch.identifier;
      this.activeGeometry=geometry(this.surface);
      this.touchFallbackStarts++;
      if(e.cancelable)e.preventDefault();
      this.onChange('down');
    }
    touchMove(e){
      if(this.activeSource!=='touch'||!this.session.active)return;
      if(e.touches?.length>1){this.abort('multitouch');return;}
      const touch=changedTouch(e,this.touchIdentifier);
      if(!touch)return;
      try{this.session.append(this.touchIdentifier,
        sourceTouch(touch,e,this.group));}
      catch(_){this.abort('invalid-coordinate');return;}
      if(e.cancelable)e.preventDefault();
      this.onChange('move');
    }
    touchEnd(e){
      if(this.activeSource!=='touch'||!this.session.active)return;
      const touch=changedTouch(e,this.touchIdentifier);
      if(!touch)return;
      try{this.session.end(this.touchIdentifier,
        sourceTouch(touch,e,this.group));}
      catch(_){this.abort('invalid-coordinate');return;}
      this.activeSource=null;this.touchIdentifier=null;
      this.activeGeometry=null;
      if(e.cancelable)e.preventDefault();
      this.onChange('up');
    }
    touchCancel(e){
      if(this.activeSource!=='touch'||!this.session.active)return;
      if(changedTouch(e,this.touchIdentifier))this.abort('touchcancel');
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
      if(this.activeSource==='pointer')this.release(id);
      this.activeSource=null;
      this.touchIdentifier=null;
      this.activeGeometry=null;
      this.lastCancel=reason;
      this.onChange('cancel');
      return true;
    }
    reset(){
      this.abort('reset');
      this.session.reset();
      this.activeSource=null;
      this.touchIdentifier=null;
      this.activeGeometry=null;
      this.lastCancel=null;
      this.onChange('reset');
    }
    onResize(){
      // iOS browser chrome may emit resize when its toolbar changes even
      // though the drawing surface is unchanged. Do not discard that ink.
      // Source coordinates always use the current screen CTM.
      // Edge iOS native touch can survive a dynamic-toolbar size adjustment;
      // real orientation changes still cancel via orientationchange.
      if(this.session.active&&
         geometryChanged(this.activeGeometry,geometry(this.surface))&&
         !(this.preferTouchInput&&this.activeSource==='touch'))
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
      this.surface.removeEventListener('touchstart',this.handlers.touchStart);
      window.removeEventListener('touchmove',this.handlers.touchMove,true);
      window.removeEventListener('touchend',this.handlers.touchEnd,true);
      window.removeEventListener('touchcancel',this.handlers.touchCancel,true);
      document.removeEventListener('visibilitychange',this.handlers.hidden);
      window.removeEventListener('orientationchange',this.handlers.rotate);
      window.removeEventListener('resize',this.handlers.resize);
    }
    getState(){
      return {lastCancel:this.lastCancel,captureFailures:this.captureFailures,
        inputSource:this.activeSource,
        touchFallbackStarts:this.touchFallbackStarts,
        edgeIOSNativeTouch:this.preferTouchInput,
        ...this.session.getState()};
    }
  }
  return {sourcePoint,sourceTouch,edgeIOSPreferredTouch,
    geometryChanged,sampleEvents,PointerInput};
});
