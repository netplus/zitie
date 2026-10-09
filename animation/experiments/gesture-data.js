/* A1.4 experimental *candidate* writing gestures, NOT normative teaching evidence.
 * These labels only guide an A/B lab. They never modify source medians/order.
 * Each pivotVertex is a zero-based ORIGINAL source median index (not resampled).
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieGestureCandidates=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const fixtures=Object.freeze({
    '1:1':{kind:'horizontal',label:'横 · 起承收'},
    '37:2':{kind:'fold',pivotVertex:6,label:'横折 · 折前制动、转锋'},
    '77:1':{kind:'hook',pivotVertex:5,label:'竖钩 · 钩前制动、短促出锋'},
    '88:2':{kind:'hook',pivotVertex:8,label:'横折钩 · 连续折转及出钩'},
    '95:1':{kind:'dot',label:'点 · 点按与提笔'},
    '95:3':{kind:'sweep',label:'撇 · 渐进提笔'},
    '95:4':{kind:'sweep',label:'捺 · 收锋'},
    '201:14':{kind:'fold',pivotVertex:9,label:'复杂折画 · 连续转锋'}
  });
  const allowed=new Set(['generic','horizontal','fold','hook','dot','sweep']);
  function lookup(glyph,strokeIndex){
    const key=String(glyph.main_id)+':'+String(strokeIndex+1);
    const rule=fixtures[key];
    if(!rule)return {kind:'generic',label:'未标注笔形 · 通用接触模型',
      reviewed:false,source:'engineering_heuristic_only',strokeKey:key};
    if(!allowed.has(rule.kind))throw Error('Unsupported gesture');
    const stroke=glyph.strokes[strokeIndex];
    if(!stroke||stroke.name_status!=='reviewed')
      throw Error('Cannot attach semantic gesture to unreviewed stroke name');
    if(rule.pivotVertex!==undefined&&
       (!Number.isInteger(rule.pivotVertex)||rule.pivotVertex<1||
       rule.pivotVertex>=stroke.median.length-1))
      throw Error('Invalid candidate pivot source index: '+key);
    return {...rule,reviewed:false,source:'engineering_heuristic_only',strokeKey:key};
  }
  return {lookup,fixtures};
});