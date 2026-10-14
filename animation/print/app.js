/* Online print studio: vector-only, client-side worksheet rendering.
 * Original published book/PDF, learner ink and teaching-motion assets remain read-only.
 */
(function(){
'use strict';
window.addEventListener('DOMContentLoaded',()=>{
  const C=window.ZitiePrintCore,book=window.ZITIE_BOOK_PACK,F=window.ZitieFoundations;
  const $=id=>document.getElementById(id);
  const NS='http://www.w3.org/2000/svg',MM_PX=96/25.4;
  const INPUTS=['kind','content','title','sizeMm','grid','columns','marginMm',
    'rowGapMm','rows','layout','traceCount','scale','opacity',
    'gridColor','traceColor','showPinyin','showTitle'];
  const state={plan:null,handle:null};
  function sayError(message){
    $('error').hidden=!message;
    $('error').textContent=message||'';
  }
  if(!C||!F||!book||book.schema_version!==1||
     book.publication?.version!=='0.5.1'||
     book.publication?.sha256!=='7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90'||
     book.summary?.characters!==201||book.glyphs?.length!==201){
    sayError('缺少与正式 v0.5.1 PDF 对应的201字数据，无法安全排版；请刷新页面。');
    return;
  }
  const lookup=new Map(book.glyphs.map(g=>[g.character,g]));
  if(lookup.size!==201){sayError('字帖来源中有重复字符，打印已停止。');return;}
  const el=(name,attrs={},text)=>{
    const node=document.createElement(name);
    for(const [key,value] of Object.entries(attrs))node.setAttribute(key,String(value));
    if(text!==undefined)node.textContent=String(text);
    return node;
  };
  const svg=(name,attrs={},text)=>{
    const node=document.createElementNS(NS,name);
    for(const [key,value] of Object.entries(attrs))node.setAttribute(key,String(value));
    if(text!==undefined)node.textContent=String(text);
    return node;
  };
  function controls(){
    const fields={};
    for(const id of INPUTS){
      const control=$(id);
      fields[id]=control.type==='checkbox'?control.checked:control.value;
    }
    // Source enum/content key names match the core model.
    return C.normalize({...fields});
  }
  function fillControls(c){
    const fields=C.normalize(c);
    for(const id of INPUTS){
      const control=$(id);
      if(id==='content'&&!(id in c))continue;
      if(control.type==='checkbox')control.checked=Boolean(fields[id]);
      else control.value=String(fields[id]);
    }
    $('traceCountValue').textContent=fields.traceCount+' 格';
    $('scaleValue').textContent=Math.round(fields.scale*100)+'%';
    $('opacityValue').textContent=Math.round(fields.opacity*100)+'%';
    $('traceCountWrap').hidden=fields.layout!=='sample';
    $('showPinyin').disabled=fields.kind!=='hanzi';
    $('contentHint').textContent=fields.kind==='pinyin'?
      '用空格隔开每个音节，如 zh ch sh ai ü':'逐字排版，每字或字母一组练习行';
  }
  function gridCell(out,settings){
    const c=settings,g=settings.grid;
    const col=c.gridColor;
    const border={fill:'none',stroke:col,'stroke-width':'0.65'};
    if(g==='four'){
      for(const [i,y] of [12,38,64,90].entries()){
        out.append(svg('line',{x1:0,y1:y,x2:100,y2:y,stroke:col,
          'stroke-width':i===2?0.8:0.55}));
      }
    }else{
      out.append(svg('rect',{x:0.6,y:0.6,width:98.8,height:98.8,...border}));
      if(g==='tian'||g==='mi'){
        out.append(svg('line',{x1:50,y1:0,x2:50,y2:100,stroke:col,
          'stroke-width':'0.45','stroke-dasharray':'3 3'}));
        out.append(svg('line',{x1:0,y1:50,x2:100,y2:50,stroke:col,
          'stroke-width':'0.45','stroke-dasharray':'3 3'}));
      }
      if(g==='mi')for(const d of ['M0 0 L100 100','M100 0 L0 100'])
        out.append(svg('path',{d,fill:'none',stroke:col,
          'stroke-width':'0.4','stroke-dasharray':'3 3'}));
    }
  }
  function hanziInk(parent,block,settings,color,alpha){
    const size=Number(settings.scale)/0.8;
    const outer=svg('g',{transform:'translate(50 50) scale('+size+') translate(-50 -50)',
      opacity:alpha,'data-glyph-source':block.glyph?'v0.5.1-pdf':'system-fallback'});
    if(block.glyph){
      // Exact released-PDF-source outlines; coordinate transform identical in
      // orientation to the A3 player, uniformly scaled (no glyph mutation).
      const g=svg('g',{transform:'translate(4 95) scale(0.102 -0.102)'});
      for(const stroke of block.glyph.strokes){
        g.append(svg('path',{d:stroke.outline,fill:color}));
      }
      outer.append(g);
    }else{
      // A font fallback is intentionally not advertised as reviewed handwriting.
      outer.append(svg('text',{x:50,y:77,'text-anchor':'middle','font-size':83,
        'font-family':'KaiTi,STKaiti,SimKai,serif',fill:color},block.token));
    }
    parent.append(outer);
  }
  function foundationInk(parent,block,settings,color,alpha){
    const type=block.kind;
    const src=type==='numbers'?'numbers':type==='pinyin'?'pinyin':'latin';
    const kind=type==='numbers'?'squares':'lines';
    const data=F.compose(block.token,kind,src);
    const maxW=Math.max(76,data.width);
    const base=Math.min(82/data.height,88/maxW)*(settings.scale/0.8);
    if(!(base>0&&Number.isFinite(base)))throw Error('书写字形宽度不合法');
    const left=(100-maxW*base)/2,top=(100-data.height*base)/2;
    const outer=svg('g',{transform:'translate('+left+' '+top+') scale('+base+')',
      opacity:alpha,'data-glyph-source':'foundations-'+src});
    for(const s of data.strokes)outer.append(svg('path',{
      d:s.d,transform:'translate('+s.x+' 0)',fill:'none',stroke:color,
      'stroke-width':'4.5','stroke-linejoin':'round','stroke-linecap':'round'
    }));
    parent.append(outer);
  }
  function makeCell(block,settings,ink,ix){
    const cell=svg('svg',{xmlns:NS,viewBox:'0 0 100 100',
      'aria-label':block.token+'：'+(ink==='blank'?'空白':
        ink==='sample'?'范字':ink==='red'?'描红':'描淡'),
      'data-ink':ink,'data-item':block.token,class:'printCell'});
    cell.style.width=settings.sizeMm+'mm';
    cell.style.height=settings.sizeMm+'mm';
    gridCell(cell,settings);
    if(ink!=='blank'){
      const sample=ink==='sample',pale=ink==='pale';
      const color=sample?'#2e3236':pale?'#8e9398':settings.traceColor;
      const alpha=sample?1:pale?0.29:settings.opacity;
      if(block.kind==='hanzi')hanziInk(cell,block,settings,color,alpha);
      else foundationInk(cell,block,settings,color,alpha);
    }
    cell.dataset.col=String(ix);
    return cell;
  }
  function labelFor(block,settings){
    if(settings.layout==='blank')return '自由练习';
    if(block.kind==='hanzi'){
      const g=block.glyph;
      return g?block.token+' · '+g.expected_stroke_count+' 画':
        block.token+' · 系统字体（未审核笔顺）';
    }
    const categories={pinyin:'拼音',latin:'英文',numbers:'数字'};
    return block.token+' · '+categories[block.kind]+'工程示范';
  }
  function makeSheet(page,plan){
    const c=plan.settings;
    const wrapper=el('div',{class:'paperFrame','data-paper-frame':page.index});
    const paper=el('section',{class:'paperPage','data-paper-page':page.index,
      'aria-label':'A4 第'+page.index+'页'});
    if(c.showTitle){
      const heading=el('header',{class:'sheetHeading'});
      heading.style.left=c.marginMm+'mm';
      heading.style.right=c.marginMm+'mm';
      heading.style.top=c.marginMm+'mm';
      heading.append(el('h3',{},c.title||'我的练字帖'));
      heading.append(el('p',{},'姓名：______________________      日期：______年______月______日'));
      paper.append(heading);
      const rule=el('div',{class:'sheetTopRule'});
      rule.style.left=c.marginMm+'mm';rule.style.right=c.marginMm+'mm';
      rule.style.top=(c.marginMm+18.5)+'mm';paper.append(rule);
    }
    for(const block of page.blocks){
      const blockRoot=el('section',{class:'sheetBlock','data-worksheet-item':block.token});
      blockRoot.style.top=block.y+'mm';
      const caption=el('div',{class:'sheetBlockCaption'},labelFor(block,c));
      caption.style.left=plan.gridX+'mm';
      if(block.glyph&&c.kind==='hanzi'&&c.showPinyin&&block.glyph.pinyin)
        caption.append(el('span',{class:'reading'},block.glyph.pinyin));
      blockRoot.append(caption);
      for(let ri=0;ri<block.rows.length;ri++){
        const line=el('div',{class:'sheetRow','data-row':ri});
        line.style.left=plan.gridX+'mm';
        line.style.top=(7+ri*(c.sizeMm+c.rowGapMm))+'mm';
        line.style.gap=c.gapMm+'mm';
        for(let ci=0;ci<block.rows[ri].length;ci++)
          line.append(makeCell(block,c,block.rows[ri][ci],ci));
        blockRoot.append(line);
      }
      paper.append(blockRoot);
    }
    const footer=el('footer',{class:'sheetFooter'});
    footer.style.left=c.marginMm+'mm';footer.style.right=c.marginMm+'mm';
    footer.style.bottom='6mm';
    footer.append(el('span',{},'A4 · '+c.sizeMm+' mm · '+
      plan.columns+' 格/行 · 请按100%比例打印'));
    footer.append(el('span',{},page.index+' / '+plan.pages.length));
    paper.append(footer);
    wrapper.append(paper);
    return wrapper;
  }
  function previewScale(){
    const available=Math.max(180,$('printPages').clientWidth-16);
    const naturalWidth=C.PAPER.width*MM_PX,naturalHeight=C.PAPER.height*MM_PX;
    const factor=Math.min(1,available/naturalWidth);
    for(const frame of $('printPages').querySelectorAll('.paperFrame')){
      frame.style.width=(naturalWidth*factor)+'px';
      frame.style.height=(naturalHeight*factor)+'px';
      frame.firstElementChild.style.transform='scale('+factor+')';
    }
  }
  function paint(){
    try{
      const c=controls();
      const plan=C.paginate(c,lookup);
      // Ensure every non-Chinese sample actually has a vector construction.
      if(c.kind!=='hanzi')for(const page of plan.pages)for(const block of page.blocks){
        F.compose(block.token,c.kind==='numbers'?'squares':'lines',
          c.kind==='numbers'?'numbers':c.kind==='pinyin'?'pinyin':'latin');
      }
      const nodes=plan.pages.map(page=>makeSheet(page,plan));
      $('printPages').replaceChildren(...nodes);
      state.plan=plan;
      sayError('');
      $('stats').textContent=plan.pages.length+' 页 A4 · '+plan.items+' 项练习 · '+
        plan.columns+' 格/行 · '+c.sizeMm+' mm'+
        (plan.sourceFallback?' · '+plan.sourceFallback+' 字使用系统字体':'');
      $('traceCountValue').textContent=c.traceCount+' 格';
      $('scaleValue').textContent=Math.round(c.scale*100)+'%';
      $('opacityValue').textContent=Math.round(c.opacity*100)+'%';
      $('traceCountWrap').hidden=c.layout!=='sample';
      $('showPinyin').disabled=c.kind!=='hanzi';
      previewScale();
      document.documentElement.dataset.printReady='true';
    }catch(error){
      state.plan=null;
      $('printPages').replaceChildren();
      $('stats').textContent='请调整参数后再预览';
      document.documentElement.dataset.printReady='error';
      sayError('无法排版：'+(error.message||String(error)));
    }
  }
  function refresh(){if(state.handle)clearTimeout(state.handle);
    state.handle=setTimeout(paint,85);
  }
  for(const id of INPUTS){
    $(id).addEventListener('input',refresh);
    $(id).addEventListener('change',refresh);
  }
  $('kind').addEventListener('change',()=>{
    const kind=$('kind').value;
    const presets={hanzi:'水 火 木 日 月 田',latin:'A B C D E F G',
      numbers:'0 1 2 3 4 5 6 7 8 9',pinyin:'a o e i u ü zh ch sh'};
    $('content').value=presets[kind];
    $('grid').value=kind==='latin'||kind==='pinyin'?'four':'tian';
    refresh();
  });
  for(const button of document.querySelectorAll('[data-preset]')){
    button.addEventListener('click',()=>{
      const preset=button.dataset.preset;
      $('kind').value='hanzi';$('grid').value='tian';
      const words={basic:'一 十 人 八 大 工 土 口 山 巾',
        nature:'水 火 木 日 月 山 石 田',blank:'田'};
      $('content').value=words[preset]||words.basic;
      $('layout').value=preset==='blank'?'blank':'classic';
      refresh();
    });
  }
  function doPrint(){
    if(state.handle){clearTimeout(state.handle);state.handle=null;paint();}
    if(!state.plan){sayError('目前尚未生成可打印的页面，请检查输入。');return;}
    window.print();
  }
  $('print').addEventListener('click',doPrint);
  $('printTop').addEventListener('click',doPrint);
  $('reset').addEventListener('click',()=>{
    fillControls(C.DEFAULTS);
    paint();
  });
  window.addEventListener('resize',previewScale);
  window.addEventListener('beforeprint',()=>{
    if(state.handle){clearTimeout(state.handle);state.handle=null;paint();}
  });
  // Browser QA only: no user content or learner ink is written to storage.
  window.ZITIE_PRINT=Object.freeze({
    getPlan:()=>state.plan,
    render:paint,
    getPages:()=>$('printPages').querySelectorAll('.paperPage').length
  });
  fillControls(C.DEFAULTS);
  paint();
});
})();
