/* A1.4 opt-in experimental renderer. Standalone from the production player.
 * O(t) = exact SVG source outline ∩ union of precomputed arrival-time nib
 * footprints. Each stamp stays immutable once painted: reverse seek simply
 * hides later stamps, while forward motion never erases earlier deposited ink.
 * This renderer is research-only, NOT an approved writing-direction source.
 */
(function(root,factory){
  const api=factory(
    typeof module==='object'&&module.exports?require('../timeline.js'):root.ZitieTimeline,
    typeof module==='object'&&module.exports?require('../brush-union.js'):root.ZitieInkBrushUnion,
    typeof module==='object'&&module.exports?require('./pen-contact.js'):root.ZitiePenContact,
    typeof module==='object'&&module.exports?require('./gesture-data.js'):root.ZitieGestureCandidates
  );
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePenLab=api;
})(typeof window!=='undefined'?window:null,function(T,Brush,Pen,Gestures){
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  let instance=0;
  function element(tag,attributes={}){
    const x=document.createElementNS(NS,tag);
    for(const [key,value] of Object.entries(attributes))
      x.setAttribute(key,String(value));
    return x;
  }
  class FootprintRenderer {
    constructor({svg}={}){
      if(!svg||svg.namespaceURI!==NS)throw Error('Experimental SVG stage required');
      this.svg=svg;
      this.prefix='zitie-a14-nib-'+(++instance)+'-';
      this.rows=[];
      this.timeline=null;
      this.tip=null;
      this.stats={segments:0,stamps:0,buildMs:0};
    }
    setGlyph(glyph){
      T.validateGlyph(glyph);
      const start=performance.now();
      const tl=T.buildTimeline(glyph);
      this.svg.replaceChildren();
      this.svg.setAttribute('viewBox','0 0 1024 1024');
      this.svg.setAttribute('aria-label',glyph.character+'：椭圆形仿真笔尖实验');
      this.svg.appendChild(element('rect',{
        x:0,y:0,width:1024,height:1024,fill:'#FFFFFF'}));
      this.svg.appendChild(element('rect',{
        x:56,y:48,width:912,height:928,fill:'none',
        stroke:'#C9979B','stroke-width':2}));
      for(const [x1,y1,x2,y2] of [[512,48,512,976],[56,512,968,512]])
        this.svg.appendChild(element('line',{x1,y1,x2,y2,
          stroke:'#E2C9CD','stroke-width':2,'stroke-dasharray':'12 12'}));
      const defs=element('defs');
      const group=element('g',{transform:'translate(0 900) scale(1 -1)'});
      this.svg.append(defs,group);
      this.rows=glyph.strokes.map((stroke,index)=>{
        const id=this.prefix+index;
        const reference=element('path',{d:stroke.outline,fill:'#000',
          opacity:0,'pointer-events':'none'});
        // SVGGeometryElement.isPointInFill requires a CONNECTED path.
        group.append(reference);
        const contains=typeof reference.isPointInFill==='function'&&
          typeof DOMPoint!=='undefined'?
          (x,y)=>reference.isPointInFill(new DOMPoint(x,y)):null;
        const profile=Brush.makeProfile(stroke.median,contains);
        reference.remove();
        const gesture=Gestures.lookup(glyph,index);
        const plan=Pen.makePlan(stroke,profile,tl.strokes[index].motion,gesture);
        const mask=element('mask',{id,maskUnits:'userSpaceOnUse',
          maskContentUnits:'userSpaceOnUse',x:-240,y:-240,width:1504,height:1504,
          'mask-type':'alpha'});
        const stamps=plan.samples.map(s=>{
          const e=element('ellipse',{cx:s.x,cy:s.y,rx:s.rx,ry:s.ry,
            fill:'#FFFFFF',transform:'rotate('+(180/Math.PI*s.angle)+' '+s.x+' '+s.y+')',
            'pointer-events':'none'});
          e.style.display='none';
          mask.appendChild(e);
          return e;
        });
        defs.append(mask);
        const hint=element('path',{d:stroke.outline,fill:'#E1E4E7'});
        const solid=element('path',{d:stroke.outline,fill:'#5C6269'});
        const reveal=element('path',{d:stroke.outline,
          fill:'#BD3945',mask:'url(#'+id+')'});
        return {hint,solid,reveal,stamps,plan,profile,id,count:0};
      });
      for(const row of this.rows)group.append(row.hint);
      for(const row of this.rows)group.append(row.solid);
      for(const row of this.rows)group.append(row.reveal);
      this.tip=element('ellipse',{cx:0,cy:0,rx:1,ry:1,
        fill:'#BD3945',stroke:'#FFFFFF','stroke-width':2.4,
        'pointer-events':'none'});
      group.append(this.tip);
      this.timeline=tl;
      this.stats={
        glyph:glyph.character,
        segments:this.rows.reduce((n,r)=>n+r.profile.segments.length,0),
        stamps:this.rows.reduce((n,r)=>n+r.stamps.length,0),
        measuredContourSamples:this.rows.reduce((n,r)=>n+r.profile.sampledWithFill,0),
        fallbackContourSamples:this.rows.reduce((n,r)=>n+r.profile.fallbackSamples,0),
        buildMs:+(performance.now()-start).toFixed(1)
      };
      return this.renderAt(0);
    }
    renderAt(elapsed){
      if(!this.timeline)return null;
      const frame=T.frameAt(this.timeline,elapsed);
      this.rows.forEach((row,i)=>{
        const finished=frame.phase==='finished';
        const done=finished||i<frame.index;
        const active=!finished&&i===frame.index;
        row.solid.style.display=done?'':'none';
        row.reveal.style.display=active?'':'none';
        if(!active)return;
        if(frame.progress>=1){
          row.reveal.removeAttribute('mask');
          return;
        }
        row.reveal.setAttribute('mask','url(#'+row.id+')');
        const snapshot=Pen.snapshot(row.plan,frame.progress);
        if(snapshot.count>row.count){
          for(let j=row.count;j<snapshot.count;j++)
            row.stamps[j].style.display='';
        }else if(snapshot.count<row.count){
          for(let j=snapshot.count;j<row.count;j++)
            row.stamps[j].style.display='none';
        }
        row.count=snapshot.count;
      });
      const visible=frame.phase==='writing'&&frame.progress>0&&frame.progress<1;
      if(visible){
        const penState=Pen.snapshot(this.rows[frame.index].plan,frame.progress);
        const head=penState.head;
        this.tip.setAttribute('cx',frame.tip[0]);
        this.tip.setAttribute('cy',frame.tip[1]);
        this.tip.setAttribute('rx',Math.min(25,head.rx*.27));
        this.tip.setAttribute('ry',Math.min(20,head.ry*.27));
        this.tip.setAttribute('transform','rotate('+(180/Math.PI*head.angle)+
          ' '+frame.tip[0]+' '+frame.tip[1]+')');
        this.tip.style.display='';
      }else{
        this.tip.style.display='none';
      }
      const current=this.rows[frame.index];
      const contact=frame.phase==='writing'?
        Pen.snapshot(current.plan,frame.progress):
        {state:frame.phase==='finished'?'finished':'pause',pressure:0,count:0};
      return {...frame,contact,gesture:current.plan.gesture,
        glyph:this.timeline.glyph.character,stats:this.stats};
    }
  }
  return {FootprintRenderer};
});