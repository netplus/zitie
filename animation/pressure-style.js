/* A1.6: two styles for the SAME stable round-brush player.
 * Stable mode preserves the existing circle exactly. Synthetic pressure
 * reuses A1.5's independent position/gesture model and changes ONLY the
 * visible cursor and a non-white, unfilled force ring. No source ink edits.
 */
(function(root,factory){
  const CommonJS=typeof module==='object'&&module.exports;
  const api=factory(
    CommonJS?require('./experiments/pressure-model.js'):root.ZitiePressureModel,
    CommonJS?require('./experiments/gesture-data.js'):root.ZitieGestureCandidates
  );
  if(CommonJS)module.exports=api;
  if(root)root.ZitiePressureStyle=api;
})(typeof window!=='undefined'?window:null,function(Pressure,Gestures){
  'use strict';
  if(!Pressure||!Gestures)throw Error('A1.5 pressure/gesture modules are required');
  const NS='http://www.w3.org/2000/svg';
  const styles=Object.freeze(['stable','simulated']);
  const finite=n=>typeof n==='number'&&Number.isFinite(n);
  function markerGeometry(pressure,penTool='brush'){
    if(!finite(pressure)||pressure<0||pressure>1)
      throw Error('Invalid normalized contact pressure');
    if(penTool!=='brush'&&penTool!=='hardpen')
      throw Error('Unknown writing pen tool');
    // A firm nib cannot flex into a wide paintbrush. The independent
    // pressure curve changes only the visual contact cue, never ink width.
    const rigid=penTool==='hardpen';
    const radius=rigid?4.5+3.5*pressure:7.2+8.8*pressure;
    return {radius,ringRadius:rigid?radius+3+2*pressure:
      radius+4+5*pressure,
      markerFill:rigid?'#BD3945':'#9F3342',
      markerStroke:rigid?'#A32F3D':'#712B37',
      ringStroke:'#883542',ringFill:'none'};
  }
  class StyleController{
    constructor(){
      this.mode='stable';this.glyph=null;this.plans=[];
      this.curves=[];this.ring=null;this.state=null;
    }
    setMode(mode){
      if(!styles.includes(mode))throw Error('Unsupported pen pressure style');
      this.mode=mode;
      return this.mode;
    }
    prepare(glyph){
      if(!glyph||!Array.isArray(glyph.strokes))throw Error('Missing source glyph');
      if(this.glyph!==glyph){
        // Build pressure profiles from immutable canonical source medians.
        // A1.5's candidate gestures do not provide teacher approval.
        this.plans=glyph.strokes.map((stroke,i)=>
          Pressure.makePlan(stroke,Gestures.lookup(glyph,i)));
        this.curves=this.plans.map(plan=>Pressure.curve(plan,96));
        this.glyph=glyph;
      }
    }
    ensureRing(tip){
      if(!this.ring){
        this.ring=document.createElementNS(NS,'circle');
        this.ring.setAttribute('fill','none');
        this.ring.setAttribute('stroke','#883542');
        this.ring.setAttribute('stroke-width','2.5');
        this.ring.setAttribute('opacity','.68');
        this.ring.setAttribute('pointer-events','none');
        this.ring.setAttribute('aria-hidden','true');
      }
      if(this.ring.parentNode!==tip.parentNode)
        tip.parentNode.insertBefore(this.ring,tip);
      return this.ring;
    }
    resetTip(tip){
      const hardpen=tip.getAttribute('data-pen-tool')==='hardpen';
      tip.setAttribute('r',hardpen?'5':'8');
      tip.setAttribute('fill','#BD3945');
      tip.setAttribute('stroke',hardpen?'#BD3945':'#FFFFFF');
      tip.setAttribute('stroke-width',hardpen?'.7':'2.5');
      if(this.ring)this.ring.remove(); // Stable style has no overlay.
    }
    apply(player,frame){
      if(!player?.timeline||!player.tip||!frame)
        throw Error('Cannot render pressure style without a stable player');
      const tip=player.tip;
      if(this.mode==='stable'){
        this.resetTip(tip);
        this.state={mode:'stable',pressure:0,phase:'none',measured:false,
          plan:null,curve:null,active:false,progress:frame.progress};
        return this.state;
      }
      this.prepare(player.timeline.glyph);
      const plan=this.plans[frame.index];
      if(!plan)throw Error('Missing source stroke pressure plan');
      const active=frame.phase==='writing'&&frame.progress>0&&
        frame.progress<1&&tip.style.display!=='none';
      const sample=active?Pressure.snapshot(plan,frame.progress):
        {pressure:0,phase:frame.phase==='finished'?'released':'hover',
          progress:frame.progress,measured:false};
      if(active){
        const geo=markerGeometry(sample.pressure,
          tip.getAttribute('data-pen-tool')==='hardpen'?'hardpen':'brush');
        tip.setAttribute('r',geo.radius.toFixed(3));
        tip.setAttribute('fill',geo.markerFill);
        tip.setAttribute('stroke',geo.markerStroke);
        tip.setAttribute('stroke-width','1');
        const ring=this.ensureRing(tip);
        ring.setAttribute('cx',tip.getAttribute('cx'));
        ring.setAttribute('cy',tip.getAttribute('cy'));
        ring.setAttribute('r',geo.ringRadius.toFixed(3));
        ring.style.display='';
      }else{
        this.resetTip(tip);
      }
      this.state={mode:'simulated',pressure:sample.pressure,
        phase:sample.phase,measured:false,active,progress:frame.progress,
        plan,curve:this.curves[frame.index]};
      return this.state;
    }
  }
  return {styles,markerGeometry,StyleController};
});
