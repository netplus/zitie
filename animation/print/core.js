/* P3 printable A4 worksheet planner. Millimetres are physical CSS units.
 * No storage, network, font downloading, inferred stroke order or PDF mutation.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePrintCore=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const PAPER={width:210,height:297};
  const DEFAULTS=Object.freeze({
    kind:'hanzi',content:'水 火 木 日 月 田',grid:'tian',
    sizeMm:15,marginMm:15,gapMm:1.5,rowGapMm:3,columns:10,
    rows:4,layout:'classic',traceCount:4,scale:0.8,
    gridColor:'#ccabb0',traceColor:'#c95160',opacity:0.55,
    showPinyin:true,showTitle:true,showStrokeOrder:true,title:'循序渐进 · 我的练字帖'
  });
  const OPTIONS=Object.freeze({
    kind:['hanzi','latin','pinyin','numbers'],
    grid:['tian','mi','square','four'],
    layout:['classic','sample','trace','blank']
  });
  function clamp(n,min,max,step=1){
    n=Number(n);
    if(!Number.isFinite(n))return min;
    const snapped=Math.round((n-min)/step)*step+min;
    return Math.max(min,Math.min(max,Math.round(snapped*10000)/10000));
  }
  function color(s,fallback){
    return typeof s==='string'&&/^#[0-9a-fA-F]{6}$/.test(s)?s:fallback;
  }
  function normalize(raw={}){
    const d=DEFAULTS;
    const kind=OPTIONS.kind.includes(raw.kind)?raw.kind:d.kind;
    // Do not silently omit a learner's last characters or clip a printed title.
    if(typeof raw.content==='string'&&raw.content.length>500)
      throw Error('练习内容最多500个字符，请分批排版。');
    if(typeof raw.title==='string'&&raw.title.trim().length>26)
      throw Error('打印标题最多26个字符，请缩短后重试。');
    return {
      kind,
      content:typeof raw.content==='string'?raw.content:d.content,
      grid:OPTIONS.grid.includes(raw.grid)?raw.grid:(kind==='latin'||kind==='pinyin'?'four':d.grid),
      sizeMm:clamp(raw.sizeMm??d.sizeMm,10,25),
      marginMm:clamp(raw.marginMm??d.marginMm,10,25),
      gapMm:d.gapMm,
      rowGapMm:clamp(raw.rowGapMm??d.rowGapMm,0,12),
      columns:clamp(raw.columns??d.columns,0,16),
      rows:clamp(raw.rows??d.rows,1,6),
      layout:OPTIONS.layout.includes(raw.layout)?raw.layout:d.layout,
      traceCount:clamp(raw.traceCount??d.traceCount,0,16),
      scale:clamp(raw.scale??d.scale,0.5,0.95,0.01),
      gridColor:color(raw.gridColor,d.gridColor),
      traceColor:color(raw.traceColor,d.traceColor),
      opacity:clamp(raw.opacity??d.opacity,0.15,0.95,0.01),
      showPinyin:raw.showPinyin!==false,
      showTitle:raw.showTitle!==false,
      showStrokeOrder:kind==='hanzi'&&(raw.showStrokeOrder??d.showStrokeOrder)===true,
      title:(typeof raw.title==='string'?raw.title:d.title).trim()
    };
  }
  function parseItems(input,kind){
    if(!OPTIONS.kind.includes(kind))throw Error('Unsupported writing category');
    let parts=[];
    if(kind==='hanzi'){
      parts=Array.from(input).filter(c=>/\p{Script=Han}/u.test(c));
    }else if(kind==='latin'){
      parts=(input.match(/[A-Za-z]/g)||[]);
    }else if(kind==='numbers'){
      parts=(input.match(/[0-9]/g)||[]);
    }else{
      parts=input.normalize('NFC').split(/[\s,，、;；]+/u)
        .filter(Boolean);
      if(parts.some(p=>!(/^[a-züāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]{1,9}$/iu.test(p))))
        throw Error('拼音只支持字母、ü及常见带调拼音；请用空格隔开各音节。');
    }
    if(parts.length===0)throw Error('请输入至少一个可练习的字或字符。');
    if(parts.length>60)throw Error('单次最多排版60项；请分批打印。');
    return parts;
  }
  function columns(c){
    const available=PAPER.width-2*c.marginMm;
    const fit=Math.floor((available+c.gapMm+1e-8)/(c.sizeMm+c.gapMm));
    if(fit<1)throw Error('页边距和格子尺寸不允许放入一个完整方格');
    return Math.min(fit,c.columns||fit);
  }
  function rowInk(layout,row,col,traceCount,cols){
    if(layout==='blank')return 'blank';
    if(layout==='trace')return 'red';
    if(layout==='sample')return col===0?'sample':
      row===0&&col<=Math.min(traceCount,cols-1)?'red':'blank';
    // Classic PDF teaching: one full red row, one full pale row, then
    // specimen on the first square with independent writing in remaining cells.
    if(row===0)return 'red';
    if(row===1)return 'pale';
    return col===0?'sample':'blank';
  }
  // Printed teaching cards re-use the ordered, released-book vector strokes.
  // Never calculate a stroke order from a font or an unrelated character.
  function strokeOrderLayout(glyph,c,gridWidth){
    if(!c.showStrokeOrder||c.kind!=='hanzi')return null;
    if(!glyph)return {kind:'unavailable',heightMm:13};
    const n=glyph.expected_stroke_count;
    if(!Number.isInteger(n)||n<1||n>64||
       !Array.isArray(glyph.strokes)||glyph.strokes.length!==n||
       glyph.strokes.some(stroke=>!stroke||typeof stroke.outline!=='string'||
         !/^ *M +/i.test(stroke.outline)))
      throw Error('笔顺数据不完整，无法打印：'+(glyph.character||'未知汉字'));
    const cellMm=Math.min(22,Math.max(16,c.sizeMm+4));
    const gapMm=2,headingMm=6,labelMm=7,rowGapMm=2;
    const perRow=Math.max(1,Math.floor((gridWidth+gapMm+1e-8)/(cellMm+gapMm)));
    const countRows=Math.ceil(n/perRow);
    const heightMm=headingMm+countRows*(cellMm+labelMm)+
      (countRows-1)*rowGapMm+3;
    return {kind:'steps',count:n,cellMm,gapMm,headingMm,labelMm,
      rowGapMm,perRow,countRows,heightMm};
  }
  function paginate(settings,sourceMap){
    const c=normalize(settings);
    const items=parseItems(c.content,c.kind);
    const cols=columns(c);
    const gridWidth=cols*c.sizeMm+(cols-1)*c.gapMm;
    const gridX=(PAPER.width-gridWidth)/2;
    const headerMm=c.showTitle?21:11;
    const footerMm=8;
    const blockMm=7+c.rows*c.sizeMm+(c.rows-1)*c.rowGapMm+5;
    const top=c.marginMm+headerMm;
    // Keep a printer-safe footer area without reserving two full bottom margins.
    const bottom=PAPER.height-Math.max(8,c.marginMm/2)-footerMm;
    if(top+blockMm>bottom+0.001)
      throw Error('纸张空间不足：请减小格子、行数或页边距。');
    const pages=[];
    let page={index:1,blocks:[],nextY:top};
    let fallback=0;
    const sources=sourceMap instanceof Map?sourceMap:new Map();
    for(const token of items){
      const glyph=c.kind==='hanzi'?(sources.get(token)||null):null;
      if(c.kind==='hanzi'&&!glyph)fallback++;
      const order=strokeOrderLayout(glyph,c,gridWidth);
      const heightMm=blockMm+(order?order.heightMm:0);
      if(top+heightMm>bottom+1e-7)
        throw Error('该字的笔顺示范和练习格无法完整放在一页，请减少练习行数、格子尺寸或行间距：'+token);
      if(page.blocks.length&&page.nextY+heightMm>bottom+1e-7){
        pages.push(page);
        page={index:pages.length+1,blocks:[],nextY:top};
      }
      const block={token,glyph,kind:c.kind,x:gridX,y:page.nextY,
        strokeOrder:order,heightMm,practiceTopMm:7+(order?order.heightMm:0),
        rows:Array.from({length:c.rows},(_,r)=>
          Array.from({length:cols},(_,i)=>
            rowInk(c.layout,r,i,c.traceCount,cols)))};
      page.blocks.push(block);
      page.nextY+=heightMm;
    }
    if(page.blocks.length)pages.push(page);
    if(pages.length>60)throw Error('生成页面过多，请分批打印。');
    return {pages,settings:c,columns:cols,gridX,gridWidth,headerMm,
      footerMm,printableBottom:bottom,blockMm,sourceFallback:fallback,items:items.length,
      paper:PAPER};
  }
  return Object.freeze({PAPER,DEFAULTS,normalize,parseItems,columns,rowInk,strokeOrderLayout,paginate});
});
