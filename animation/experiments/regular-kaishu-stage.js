/* A2.3 standalone candidate hardpen-Kaishu SVG stage.
 * Do not replace main A2.2 hardpen or A1.3 source brush yet.
 * All current glyphs/order and clock arrive from the unchanged timeline.
 */
(function(root,factory){
  const K=typeof module==='object'&&module.exports?
    require('./regular-kaishu-model.js'):root.ZitieKaishuModel;
  const Ink=typeof module==='object'&&module.exports?
    require('./regular-kaishu-ink.js'):root.ZitieKaishuInk;
  const api=factory(K,Ink);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieKaishuStage=api;
})(typeof window!=='undefined'?window:null,function(Kaishu,Ink){
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  const tag=(name,attrs={})=>{
    const el=document.createElementNS(NS,name);
    for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));
    return el;
  };
  class KaishuStage{
    constructor({svg,width=26}={}){
      if(!svg||svg.namespaceURI!==NS)throw Error('Missing Kaishu SVG stage');
      if(width!==21&&width!==26)throw Error('Unsupported trial Kaishu line size');
      this.svg=svg;this.width=width;this.glyph=null;this.timeline=null;
      this.rows=[];this.tip=null;this.state=null;
      this.sourceInkOutlineUsed=false;
    }
    setGlyph(glyph,timeline){
      if(!glyph||!timeline||timeline.glyph!==glyph||
         glyph.strokes.length!==timeline.strokes.length)
        throw Error('Kaishu source/timeline mismatch');
      const original=JSON.stringify(glyph.strokes);
      const plans=glyph.strokes.map((stroke,index)=>
        Kaishu.makePlan(stroke,glyph,index,{width:this.width}));
      if(original!==JSON.stringify(glyph.strokes))
        throw Error('Kaishu candidate rewrote source glyph');
      this.glyph=glyph;this.timeline=timeline;
      this.svg.replaceChildren();
      this.svg.setAttribute('viewBox','0 0 1024 1024');
      this.svg.setAttribute('aria-label',glyph.character+
        '硬笔楷书几何工程候选，未经过教学认证');
      this.svg.append(tag('rect',{x:0,y:0,width:1024,height:1024,
        fill:'#FFFFFF'}));
      this.svg.append(tag('rect',{x:56,y:48,width:912,height:928,
        fill:'none',stroke:'#C9979B','stroke-width':2}));
      for(const [x1,y1,x2,y2] of [[512,48,512,976],[56,512,968,512]])
        this.svg.append(tag('line',{x1,y1,x2,y2,stroke:'#E2C9CD',
          'stroke-width':2,'stroke-dasharray':'12 12'}));
      const group=tag('g',{transform:'translate(0 900) scale(1 -1)'});
      this.svg.append(group);
      this.rows=plans.map(plan=>Ink.createRow(plan));
      for(const row of this.rows)group.append(row.hint);
      for(const row of this.rows)group.append(row.finished);
      for(const row of this.rows)group.append(row.redGroup);
      this.tip=tag('circle',{cx:0,cy:0,r:5,fill:'#BD3945',
        stroke:'#BD3945','stroke-width':.7,'pointer-events':'none',
        'data-pen-tool':'hardpen'});
      this.tip.style.display='none';
      group.append(this.tip);
      this.state=null;
      return this;
    }
    render(frame){
      if(!this.timeline||!frame||!this.glyph)
        throw Error('Kaishu stage not initialized');
      if(frame.index<0||frame.index>=this.rows.length)
        throw Error('Kaishu stroke index outside source glyph');
      const completed=frame.phase==='finished';
      for(let i=0;i<this.rows.length;i++){
        const row=this.rows[i];
        const settled=completed||i<frame.index||
          (i===frame.index&&frame.phase==='pause');
        const writing=!settled&&i===frame.index&&frame.phase==='writing';
        row.finished.style.display=settled?'':'none';
        row.redGroup.style.display=writing?'':'none';
        if(writing){
          const segment=this.timeline.strokes[i];
          const t=Math.max(0,Math.min(1,
            (frame.elapsedMs-segment.startMs)/segment.durationMs));
          Ink.progressAt(row,row.plan.progressAt(t));
        }
      }
      const current=this.rows[frame.index],stage=this.timeline.strokes[frame.index];
      const clock=Math.max(0,Math.min(1,
        (frame.elapsedMs-stage.startMs)/stage.durationMs));
      const motion=current.plan.stateAt(clock);
      const active=frame.phase==='writing'&&motion.progress>0&&
        motion.progress<1;
      if(active){
        this.tip.setAttribute('cx',motion.point.x.toFixed(5));
        this.tip.setAttribute('cy',motion.point.y.toFixed(5));
        this.tip.style.display='';
      }else this.tip.style.display='none';
      this.state={mode:'regular-kaishu-candidate',
        frame,progress:motion.progress,phase:motion.phase,
        label:motion.label,point:motion.point,active,
        penWidth:this.width,
        writingSchemaApproved:false,
        brushSilhouetteUsed:false,
        physicalPressureMeasured:false,
        strokeIndex:frame.index};
      return this.state;
    }
    getAdapter(){return this;}
  }
  return {KaishuStage};
});
