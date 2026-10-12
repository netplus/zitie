/* P2.1a — immutable, PDF-backed stroke reference for immersive practice.
 * This is deliberately NOT the A3 StrokePlayer or an ink/capture engine.
 * Source data remains in the exact licensed PDF-derived outline coordinates.
 */
(function(root,factory){
  const Timeline=typeof module==='object'&&module.exports?
    require('../timeline.js'):root.ZitieTimeline;
  const api=factory(Timeline);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePracticeReference=api;
})(typeof window!=='undefined'?window:null,function(Timeline){
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  const SOURCE_TRANSFORM='translate(0 900) scale(1 -1)';
  const el=(name,attrs={})=>{
    const node=document.createElementNS(NS,name);
    for(const [key,value] of Object.entries(attrs))
      node.setAttribute(key,String(value));
    return node;
  };
  function prepareReference(glyph){
    if(!Timeline||!Timeline.validateGlyph(glyph))
      throw Error('Valid PDF-linked source glyph is required');
    if(!/^[a-f0-9]{64}$/.test(glyph.source_sha256||''))
      throw Error('PDF source hash is missing');
    if(glyph.trajectory_review_status!=='engineering_preview_unreviewed')
      throw Error('Unrecognized source motion review status');
    const strokes=glyph.strokes.map((s,i)=>Object.freeze({
      index:i,
      outline:s.outline,
      median:Object.freeze(s.median.map(p=>Object.freeze(p.slice()))),
      name:s.name_status==='reviewed'?s.name:null,
      nameStatus:s.name_status
    }));
    return Object.freeze({
      mainId:glyph.main_id,
      character:glyph.character,
      strokeCount:strokes.length,
      sourceHash:glyph.source_sha256,
      trajectoryStatus:glyph.trajectory_review_status,
      strokes:Object.freeze(strokes)
    });
  }
  function label(reference,index){
    const s=reference.strokes[index];
    return s.nameStatus==='reviewed'?s.name:'第'+(index+1)+'笔';
  }
  class ReferenceStage{
    constructor(svg){
      if(!svg||svg.namespaceURI!==NS)
        throw Error('P2.1a requires its own SVG reference stage');
      this.svg=svg;
      this.reference=null;
      this.currentIndex=0;
      this.paths=[];
      this.group=null;
      this.guides=null;
    }
    setGlyph(glyph){
      const reference=prepareReference(glyph);
      this.svg.replaceChildren();
      this.svg.setAttribute('viewBox','0 0 1024 1024');
      this.svg.setAttribute('aria-label',reference.character+
        '的PDF同源笔画轮廓参考，非真人运笔轨迹');
      this.svg.appendChild(el('rect',{x:0,y:0,width:1024,height:1024,fill:'#ffffff'}));
      this.svg.appendChild(el('rect',{x:56,y:48,width:912,height:928,
        fill:'none',stroke:'#cfadb2','stroke-width':2}));
      for(const [x1,y1,x2,y2] of [[512,48,512,976],[56,512,968,512]])
        this.svg.appendChild(el('line',{x1,y1,x2,y2,stroke:'#dfc6ca',
          'stroke-width':2,'stroke-dasharray':'12 12'}));
      this.group=el('g',{transform:SOURCE_TRANSFORM,
        'data-practice-source-transform':'true'});
      this.paths=reference.strokes.map((stroke,index)=>
        el('path',{d:stroke.outline,fill:'#e1e4e7','pointer-events':'none',
          'data-practice-stroke-index':index}));
      this.paths.forEach(path=>this.group.appendChild(path));
      this.guides=el('g',{'pointer-events':'none','aria-hidden':'true',
        'data-practice-reference-guide':'true'});
      this.guideLine=el('path',{fill:'none',stroke:'#984d5c',
        'stroke-width':6,'stroke-dasharray':'14 13',opacity:'.66'});
      this.startDot=el('circle',{r:16,fill:'#fff',stroke:'#ae4457',
        'stroke-width':7,'data-guide-point':'start'});
      this.endDot=el('circle',{r:9,fill:'#ae4457',
        'data-guide-point':'end'});
      this.guides.append(this.guideLine,this.startDot,this.endDot);
      this.group.appendChild(this.guides);
      this.svg.appendChild(this.group);
      this.reference=reference;
      this.showStroke(0);
      return reference;
    }
    showStroke(index){
      if(!this.reference||!Number.isInteger(index)||
         index<0||index>=this.reference.strokeCount)
        throw Error('Stroke reference index outside the current PDF glyph');
      this.currentIndex=index;
      this.paths.forEach((path,i)=>{
        path.setAttribute('fill',i===index?'#bb6778':
          i<index?'#91959d':'#dfe2e6');
        path.setAttribute('data-reference-current',String(i===index));
      });
      // Paint the active outline after all other outlines at intersections.
      this.group.appendChild(this.paths[index]);
      this.group.appendChild(this.guides);
      const median=this.reference.strokes[index].median;
      const d=median.map((p,i)=>(i?'L ':'M ')+p[0]+' '+p[1]).join(' ');
      this.guideLine.setAttribute('d',d);
      const first=median[0],last=median[median.length-1];
      this.startDot.setAttribute('cx',first[0]);
      this.startDot.setAttribute('cy',first[1]);
      this.endDot.setAttribute('cx',last[0]);
      this.endDot.setAttribute('cy',last[1]);
      return {index,label:label(this.reference,index),
        count:this.reference.strokeCount};
    }
    getState(){
      if(!this.reference)return null;
      return {glyphId:this.reference.mainId,character:this.reference.character,
        sourceHash:this.reference.sourceHash,
        referenceIndex:this.currentIndex,strokeCount:this.reference.strokeCount,
        referenceOnly:true,label:label(this.reference,this.currentIndex)};
    }
  }
  return {SOURCE_TRANSFORM,prepareReference,ReferenceStage};
});
