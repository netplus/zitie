/* A1.2.1 accessible gallery filtering, with no network or DOM dependencies. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieGallery=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  function filteredGlyphs(glyphs,query='',batch='all'){
    const q=String(query).trim().toLocaleLowerCase();
    if(!Array.isArray(glyphs))throw new Error('Invalid glyph library');
    return glyphs.filter(g=>{
      if(batch!=='all' && g.batch_id!==batch)return false;
      if(!q)return true;
      const tokens=[g.character,g.batch_id,String(g.main_id),
        String(g.expected_stroke_count),
        ...g.strokes.map(s=>s.name_status==='reviewed'?s.name:'')];
      return tokens.some(s=>String(s).toLocaleLowerCase().includes(q));
    });
  }
  function batches(glyphs){
    return Array.from(new Set(glyphs.map(g=>g.batch_id))).sort();
  }
  function neighbor(glyphs,id,offset){
    if(!Array.isArray(glyphs)||glyphs.length===0)return null;
    const current=glyphs.findIndex(g=>g.main_id===id);
    if(current<0)return glyphs[0];
    return glyphs[(current+offset+glyphs.length)%glyphs.length];
  }
  return {filteredGlyphs,batches,neighbor};
});