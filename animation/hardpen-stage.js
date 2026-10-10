/* A2.2 main-page hardpen renderer.
 * The existing A1.3 source-outline player remains the canonical timeline
 * and the *entire* selectable legacy brush view. This strictly passive
 * hardpen stage renders a different visual ink geometry, not a new source.
 *
 * The pen is a firm round nib (near-uniform hardpen stroke), not a flex nib,
 * traditional brush, or calibrated physical millimeter measurement.
 */
(function(root,factory){
  const api=factory(
    typeof module==='object'&&module.exports?
      require('./experiments/hardpen-model.js'):root.ZitieHardpenModel,
    typeof module==='object'&&module.exports?
      require('./experiments/stroke-primitives.js'):root.ZitieStrokePrimitives,
    typeof module==='object'&&module.exports?
      require('./hardpen-ink-union.js'):root.ZitieHardpenInkUnion
  );
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieHardpenStage=api;
})(typeof window!=='undefined'?window:null,function(Hardpen,Primitives,Ink){
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  const make=(tag,attrs={})=>{
    const el=document.createElementNS(NS,tag);
    for(const [key,value] of Object.entries(attrs))
      el.setAttribute(key,String(value));
    return el;
  };
  class HardpenStage{
    constructor({svg,width=26}={}){
      if(!svg||svg.namespaceURI!==NS)throw Error('Invalid hardpen SVG stage');
      if(width!==21&&width!==26)throw Error('Unsupported hardpen width');
      this.svg=svg;this.width=width;this.glyph=null;this.timeline=null;
      this.rows=[];this.tip=null;this.state=null;
      this.sourceInkOutlineUsed=false;
    }
    setGlyph(glyph,timeline){
      if(!glyph||!timeline||timeline.glyph!==glyph||
         !Array.isArray(glyph.strokes)||glyph.strokes.length!==timeline.strokes.length)
        throw Error('Hardpen source timeline and glyph must be identical');
      const original=JSON.stringify(glyph.strokes);
      const plans=glyph.strokes.map((s,i)=>
        Hardpen.makePlan(s,Primitives.semantics(glyph,i),
          {width:this.width}));
      if(original!==JSON.stringify(glyph.strokes))
        throw Error('Hardpen geometry modified source medians');
      this.glyph=glyph;this.timeline=timeline;
      this.svg.replaceChildren();
      this.svg.setAttribute('viewBox','0 0 1024 1024');
      this.svg.setAttribute('aria-label',glyph.character+
        '硬笔中心线工程预览，笔画动作未经教学核验');
      this.svg.append(make('rect',{x:0,y:0,width:1024,height:1024,
        fill:'#FFFFFF'}));
      this.svg.append(make('rect',{x:56,y:48,width:912,height:928,
        fill:'none',stroke:'#C9979B','stroke-width':2}));
      for(const [x1,y1,x2,y2] of [[512,48,512,976],[56,512,968,512]])
        this.svg.append(make('line',{x1,y1,x2,y2,stroke:'#E2C9CD',
          'stroke-width':2,'stroke-dasharray':'12 12'}));
      const group=make('g',{transform:'translate(0 900) scale(1 -1)'});
      this.svg.append(group);
      this.rows=plans.map(plan=>Ink.createRow(plan,this.width));
      for(const row of this.rows)group.append(row.hint);
      for(const row of this.rows)group.append(row.finished);
      for(const row of this.rows)group.append(row.redGroup);
      this.tip=make('circle',{
        cx:0,cy:0,r:5,fill:'#BD3945',stroke:'#BD3945',
        'stroke-width':.7,'pointer-events':'none',
        'data-pen-tool':'hardpen'
      });
      this.tip.style.display='none';
      group.append(this.tip);
      this.state=null;
      return this;
    }
    render(frame){
      if(!this.timeline||!this.glyph||!frame)
        throw Error('Cannot render uninitialized hardpen stage');
      if(frame.index<0||frame.index>=this.rows.length)
        throw Error('Hardpen frame stroke outside source');
      const completed=frame.phase==='finished';
      for(let i=0;i<this.rows.length;i++){
        const row=this.rows[i];
        const earlier=i<frame.index,chosen=i===frame.index;
        const settled=completed||earlier||
          (chosen&&frame.phase==='pause');
        const writing=chosen&&!settled&&frame.phase==='writing';
        row.finished.style.display=settled?'':'none';
        row.redGroup.style.display=writing?'':'none';
        if(writing){
          const stage=this.timeline.strokes[i];
          const time=Math.max(0,Math.min(1,
            (frame.elapsedMs-stage.startMs)/stage.durationMs));
          const spatial=row.plan.progressAt(time);
          Ink.progressAt(row,spatial);
        }
      }
      const stage=this.timeline.strokes[frame.index];
      const normalTime=Math.max(0,Math.min(1,
        (frame.elapsedMs-stage.startMs)/stage.durationMs));
      const selected=this.rows[frame.index];
      const motion=selected.plan.stateAt(normalTime);
      const active=frame.phase==='writing'&&motion.progress>0&&
        motion.progress<1;
      if(active){
        this.tip.setAttribute('cx',motion.point.x.toFixed(5));
        this.tip.setAttribute('cy',motion.point.y.toFixed(5));
        this.tip.style.display='';
      }else this.tip.style.display='none';
      this.state={
        mode:'hardpen',
        frame,progress:motion.progress,phase:motion.phase,
        label:motion.label,point:motion.point,
        active,penWidth:this.width,
        brushSilhouetteUsed:false,
        physicalPressureMeasured:false,
        strokeIndex:frame.index
      };
      return this.state;
    }
    setWidth(width){
      if(width!==21&&width!==26)throw Error('Invalid hardpen width');
      if(this.width===width)return;
      this.width=width;
      // No geometric nor timeline rebuild: the same rigid skeleton and
      // normalized motion remain identical when only width changes.
      for(const row of this.rows)Ink.setWidth(row,width);
      if(this.state)this.state.penWidth=width;
    }
    getAdapter(){
      return this; // exposes .timeline and .tip for existing pressure style
    }
  }
  return {HardpenStage};
});
