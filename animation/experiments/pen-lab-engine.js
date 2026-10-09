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
    typeof module==='object'&&module.exports?require('./gesture-data.js'):root.ZitieGestureCandidates,
    typeof module==='object'&&module.exports?require('./pen-kinematics.js'):root.ZitiePenKinematics,
    typeof module==='object'&&module.exports?require('./source-onset.js'):root.ZitieSourceOnset
  );
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePenLab=api;
})(typeof window!=='undefined'?window:null,function(T,Brush,Pen,Gestures,Kinematics,Onset){
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
      this.showTip=true; // Show a dark nib silhouette without white ink-occluding edges.
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
        const gesture=Gestures.lookup(glyph,index);
        // The visible start of the source silhouette need not be the
        // first INSIDE medial vertex (一 starts at [121,393]).
        // Probe the connected source shape before detaching its path.
        const startCap=gesture.kind==='horizontal'&&contains?
          Onset.makeStartCap(stroke,profile,contains):null;
        reference.remove();
        const plan=Pen.makePlan(stroke,profile,tl.strokes[index].motion,gesture);
        const motionWarp=Kinematics.makeTimeWarp(plan,tl.strokes[index].motion);
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
        // Delayed reference-width coverage: each source-probed segment is
        // added only once the pen has travelled BEYOND it. This fixes
        // permanent edge gaps caused by pressure-scaled elliptical impressions,
        // without exposing any ink ahead of the current pen or editing path d.
        const repairFragments=profile.segments.map(part=>{
          const ink=element('path',{d:part.d,fill:'none',
            stroke:'#FFFFFF','stroke-width':part.width,
            'stroke-linecap':'round','stroke-linejoin':'round',
            'pointer-events':'none'});
          ink.style.display='none';
          mask.appendChild(ink);
          return ink;
        });
        const repairFront=element('path',{d:'',fill:'none',
          stroke:'#FFFFFF','stroke-linecap':'round',
          'stroke-linejoin':'round','pointer-events':'none'});
        repairFront.style.display='none';
        mask.appendChild(repairFront);
        // Fill the source-supported start cap from its actual first
        // projected support point, sweeping across the initial tangent.
        // This is unioned and clipped with the exact original outline.
        const sourceSweep=startCap?element('path',{
          d:'',fill:'#FFFFFF','pointer-events':'none'}):null;
        if(sourceSweep)mask.appendChild(sourceSweep);
        defs.append(mask);
        const hint=element('path',{d:stroke.outline,fill:'#E1E4E7'});
        const solid=element('path',{d:stroke.outline,fill:'#5C6269'});
        const reveal=element('path',{d:stroke.outline,
          fill:'#BD3945',mask:'url(#'+id+')'});
        return {hint,solid,reveal,stamps,plan,profile,motionWarp,id,
          repairFragments,repairFront,repairCount:0,count:0,
          startCap,sourceSweep};
      });
      for(const row of this.rows)group.append(row.hint);
      for(const row of this.rows)group.append(row.solid);
      for(const row of this.rows)group.append(row.reveal);
      // A visible pen-shaped silhouette, not an opaque white-ringed
      // ellipse painted over the red stroke. The nib POINT is local 0,0.
      // No white fill/stroke is present anywhere in this guide.
      this.tip=element('g',{'pointer-events':'none'});
      this.tip.append(
        element('path',{d:'M 0 0 L -8 10 L -39 43 L -49 34 L -17 0 Z',
          fill:'#40505B',stroke:'#253742','stroke-width':1.7,
          'pointer-events':'none'}),
        element('path',{d:'M -15 3 L -38 35 L -44 30 L -20 0 Z',
          fill:'#84949B','pointer-events':'none'}),
        element('path',{d:'M -5 3 L 0 0 L -2 7 Z',
          fill:'#9F3442','pointer-events':'none'})
      );
      group.append(this.tip);
      this.timeline=tl;
      this.stats={
        glyph:glyph.character,
        segments:this.rows.reduce((n,r)=>n+r.profile.segments.length,0),
        stamps:this.rows.reduce((n,r)=>n+r.stamps.length,0),
        measuredContourSamples:this.rows.reduce((n,r)=>n+r.profile.sampledWithFill,0),
        fallbackContourSamples:this.rows.reduce((n,r)=>n+r.profile.fallbackSamples,0),
        sourceCoverageRepairFragments:this.rows.reduce((n,r)=>n+r.repairFragments.length,0),
        sourceCoverageModel:'source_outline_delayed_reference_width_not_pressure',
        sourceDerivedStartCaps:this.rows.filter(r=>r.startCap!==null).length,
        buildMs:+(performance.now()-start).toFixed(1)
      };
      return this.renderAt(0);
    }
    setTipIndicator(enabled){
      this.showTip=Boolean(enabled);
      return this.showTip;
    }
    renderAt(elapsed){
      if(!this.timeline)return null;
      const baseline=T.frameAt(this.timeline,elapsed);
      const activeRow=this.rows[baseline.index];
      const experimentProgress=baseline.phase==='writing'?
        activeRow.motionWarp.progressAt(baseline.timeProgress):baseline.progress;
      const frame=baseline.phase==='writing'?
        {...baseline,progress:experimentProgress,
          tip:T.pointAt(this.timeline.glyph.strokes[baseline.index].median,
            experimentProgress)}:baseline;
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
        const repairDistance=Pen.repairDistanceAt(row.plan,frame.progress);
        const repair=Brush.stateAt(row.profile,repairDistance.spatialProgress);
        if(repair.visibleCount>row.repairCount){
          for(let j=row.repairCount;j<repair.visibleCount;j++)
            row.repairFragments[j].style.display='';
        }else if(repair.visibleCount<row.repairCount){
          for(let j=repair.visibleCount;j<row.repairCount;j++)
            row.repairFragments[j].style.display='none';
        }
        row.repairCount=repair.visibleCount;
        if(row.startCap){
          const contact=Onset.sweepAt(row.startCap,
            row.plan.length*frame.progress,frame.timeProgress);
          row.sourceSweep.setAttribute('d',contact.d);
        }
        // Synchronize the start cap with early pen contact. Repair widths
        // grow smoothly for the first 12-22 source units; already painted
        // fragments only gain coverage and can never shrink during playback.
        for(let j=0;j<row.profile.segments.length;j++){
          const segment=row.profile.segments[j];
          if(segment.start>=repairDistance.contactRampDistance)break;
          row.repairFragments[j].setAttribute('stroke-width',String(
            segment.width*repairDistance.contactScale));
        }
        if(repair.active>=0&&repair.partial>0){
          const segment=row.profile.segments[repair.active];
          row.repairFront.setAttribute('d',
            'M '+segment.x0+' '+segment.y0+
            ' L '+repair.tip[0]+' '+repair.tip[1]);
          row.repairFront.setAttribute('stroke-width',String(
            segment.width*repairDistance.contactScale));
          row.repairFront.style.display='';
        }else{
          row.repairFront.style.display='none';
        }
      });
      const visible=frame.phase==='writing'&&frame.progress>0&&frame.progress<1;
      if(visible&&this.showTip){
        const row=this.rows[frame.index];
        const penState=Pen.snapshot(row.plan,frame.progress);
        let tipPosition=frame.tip;
        if(row.startCap&&frame.timeProgress<row.startCap.landingTime){
          // The cursor travels from the actual filled-outline contact
          // edge to the first medial vertex before ordinary line motion.
          tipPosition=Onset.sweepAt(row.startCap,
            row.plan.length*frame.progress,frame.timeProgress).tip;
        }
        const degrees=(penState.head.angle-Math.PI/2)*180/Math.PI;
        this.tip.setAttribute('transform','translate('+
          tipPosition[0]+' '+tipPosition[1]+') rotate('+degrees+')');
        this.tip.style.display='';
      }else{
        this.tip.style.display='none';
      }
      const current=this.rows[frame.index];
      const contact=frame.phase==='writing'?
        Pen.snapshot(current.plan,frame.progress):
        {state:frame.phase==='finished'?'finished':'pause',pressure:0,count:0};
      return {...frame,contact,gesture:current.plan.gesture,
        motionWarp:current.motionWarp.kind,
        experimentPace:baseline.phase==='writing'?
          current.motionWarp.normalizedPace(baseline.timeProgress):0,
        glyph:this.timeline.glyph.character,stats:this.stats};
    }
  }
  return {FootprintRenderer};
});