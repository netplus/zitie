/* P2.1b — actual learner ink in a Canvas separate from PDF source SVG.
 * The original samples are model-space coordinates and are never smoothed
 * or replaced with a standard/animated glyph outline.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePracticeInkCanvas=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const finite=n=>typeof n==='number'&&Number.isFinite(n);
  class TraceCanvas{
    constructor(canvas,referenceGroup,getSamples,getConfirmed=()=>[]){
      if(!canvas||typeof canvas.getContext!=='function'||
         !referenceGroup||typeof referenceGroup.getScreenCTM!=='function'||
         typeof getSamples!=='function'||typeof getConfirmed!=='function')
        throw Error('Canvas, SVG source group and actual trace samples required');
      this.canvas=canvas;
      this.group=referenceGroup;
      this.getSamples=getSamples;
      this.getConfirmed=getConfirmed;
      this.confirmedSignature='';
      this.confirmedPainted=0;
      this.ctx=canvas.getContext('2d',{alpha:true});
      if(!this.ctx)throw Error('2D ink context unavailable');
      this.lastPainted=0;
      this.frame=null;
      this.redrawCount=0;
      this.scale=1;
      this.resizeObserver=typeof ResizeObserver==='function'?
        new ResizeObserver(()=>this.resize()):null;
      if(this.resizeObserver)this.resizeObserver.observe(canvas);
      this.resize();
    }
    // Full recomposition is used only for resize, reset and orientation.
    resize(){
      const rect=this.canvas.getBoundingClientRect();
      if(rect.width<=0||rect.height<=0)return false;
      const dpr=Math.max(1,Math.min(3,window.devicePixelRatio||1));
      const width=Math.max(1,Math.round(rect.width*dpr));
      const height=Math.max(1,Math.round(rect.height*dpr));
      const changed=this.canvas.width!==width||this.canvas.height!==height;
      if(changed){
        this.canvas.width=width;this.canvas.height=height;
        this.lastPainted=0;
      }
      this.paint(true);
      return changed;
    }
    schedule(){
      if(this.frame!==null)return;
      this.frame=requestAnimationFrame(()=>{
        this.frame=null;
        this.paint(false);
      });
    }
    clear(){
      if(this.frame!==null){cancelAnimationFrame(this.frame);this.frame=null;}
      this.ctx.setTransform(1,0,0,1,0,0);
      this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
      this.lastPainted=0;
      this.confirmedSignature='';
      this.confirmedPainted=0;
    }
    paint(force=false){
      const rect=this.canvas.getBoundingClientRect();
      const m=this.group.getScreenCTM();
      if(!m||rect.width<=0||rect.height<=0)return false;
      const sx=this.canvas.width/rect.width,sy=this.canvas.height/rect.height;
      const ctx=this.ctx;
      const points=this.getSamples();
      const confirmed=this.getConfirmed();
      const signature=confirmed.map(s=>s.index+':'+s.samples.length+
        ':'+s.samples.at(-1).x+','+s.samples.at(-1).y).join('|');
      if(force||points.length<this.lastPainted||
         signature!==this.confirmedSignature){
        ctx.setTransform(1,0,0,1,0,0);
        ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
        this.lastPainted=0;
      }
      if(points.length===this.lastPainted&&
         signature===this.confirmedSignature)return true;
      // The screen CTM includes SVG viewBox, source transform, CSS layout,
      // page translation and rotation. Compose device px relative to canvas.
      ctx.setTransform(m.a*sx,m.b*sy,m.c*sx,m.d*sy,
        (m.e-rect.left)*sx,(m.f-rect.top)*sy);
      const logicalScale=Math.hypot(m.a,m.b);
      if(!finite(logicalScale)||logicalScale<=0)throw Error('Invalid source CTM');
      this.scale=logicalScale;
      ctx.lineWidth=7.5/logicalScale; // fixed visual 7.5 CSS pixels
      ctx.lineCap='round';ctx.lineJoin='round';
      ctx.strokeStyle='#1964ae';ctx.fillStyle='#1964ae';
      if(force||signature!==this.confirmedSignature){
        this.confirmedPainted=0;
        for(const stroke of confirmed){
          const sequence=stroke.samples;
          if(!sequence?.length)continue;
          // Independent paths: never connect pen lifts or replace a
          // learner's true points with the canonical source outline.
          ctx.beginPath();
          ctx.moveTo(sequence[0].x,sequence[0].y);
          for(let i=1;i<sequence.length;i++)
            ctx.lineTo(sequence[i].x,sequence[i].y);
          ctx.stroke();
          ctx.beginPath();
          ctx.arc(sequence[0].x,sequence[0].y,ctx.lineWidth/2,
            0,Math.PI*2);
          ctx.fill();
          this.confirmedPainted+=sequence.length;
        }
        this.confirmedSignature=signature;
      }
      if(this.lastPainted===0&&points.length){
        const p=points[0];
        ctx.beginPath();ctx.arc(p.x,p.y,ctx.lineWidth/2,0,Math.PI*2);ctx.fill();
      }
      if(points.length>1){
        const start=Math.max(1,this.lastPainted);
        ctx.beginPath();
        ctx.moveTo(points[start-1].x,points[start-1].y);
        for(let i=start;i<points.length;i++){
          const p=points[i];
          ctx.lineTo(p.x,p.y);
        }
        ctx.stroke();
      }
      this.lastPainted=points.length;
      this.redrawCount++;
      return true;
    }
    getMetrics(){
      return {paintedSamples:this.lastPainted,
        confirmedSamples:this.confirmedPainted,
        confirmedStrokes:this.getConfirmed().length,
        backingWidth:this.canvas.width,backingHeight:this.canvas.height,
        redraws:this.redrawCount,logicalCssUnit:this.scale};
    }
    destroy(){
      if(this.resizeObserver)this.resizeObserver.disconnect();
      this.clear();
    }
  }
  return {TraceCanvas};
});
