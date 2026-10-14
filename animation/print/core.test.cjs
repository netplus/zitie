'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const C=require('./core.js');
const sample={main_id:4,character:'水',expected_stroke_count:4,pinyin:'shuǐ',
  strokes:[{outline:'M 100 100 L 200 200 Z'}]};
const lookup=new Map([['水',sample]]);
test('15mm printable A4 always fits requested columns within the paper',()=>{
  const c=C.normalize({content:'水'});
  assert.equal(c.sizeMm,15);
  const p=C.paginate(c,lookup);
  assert.equal(p.columns,10);
  assert.equal(p.gridWidth,10*15+9*1.5);
  assert.ok(p.gridX>=c.marginMm);
  assert.ok(p.gridX+p.gridWidth<=210-c.marginMm);
  assert.equal(p.pages[0].blocks[0].rows.length,4);
  assert.equal(p.pages[0].blocks[0].rows[0].length,10);
  assert.equal(p.pages[0].blocks[0].rows[0][0],'red');
  assert.equal(p.pages[0].blocks[0].rows[1][0],'pale');
  assert.equal(p.pages[0].blocks[0].rows[2][0],'sample');
  assert.equal(p.pages[0].blocks[0].rows[2][1],'blank');
  assert.equal(p.sourceFallback,0);
});
test('large cells and page margins reduce the number of columns safely',()=>{
  for(let size of [10,12,15,18,20,25]){
    for(let margin of [10,15,20,25]){
      const c=C.normalize({sizeMm:size,marginMm:margin,columns:16,rows:2,content:'水'});
      const p=C.paginate(c,lookup);
      assert.ok(p.gridX>=margin-1e-7);
      assert.ok(p.gridX+p.gridWidth<=210-margin+1e-7);
      for(const page of p.pages)for(const block of page.blocks)
        assert.ok(block.y+p.blockMm<=297-margin-p.footerMm+1e-6);
    }
  }
});
test('multi-page pagination uses whole row groups and stays on paper',()=>{
  const p=C.paginate({content:'水'.repeat(50),rows:4,sizeMm:18,marginMm:20},lookup);
  assert.equal(p.items,50);
  assert.ok(p.pages.length>10);
  assert.equal(p.pages.reduce((n,v)=>n+v.blocks.length,0),50);
  assert.ok(p.pages.every(page=>page.blocks.every(b=>
    b.y+p.blockMm<=p.printableBottom+1e-7)));
});
test('custom Hanzi not in frozen 201 use native system-font fallback only',()=>{
  const p=C.paginate({content:'水龍',rows:1},lookup);
  assert.equal(p.sourceFallback,1);
  assert.equal(p.pages[0].blocks[0].glyph,sample);
  assert.equal(p.pages[0].blocks[1].glyph,null);
});
test('four-line Pinyin treats syllables, not individual letter fallback paths',()=>{
  const p=C.paginate({kind:'pinyin',content:'zh ch sh ǖ',grid:'four',rows:2});
  assert.equal(p.items,4);
  assert.deepEqual(p.pages.flatMap(x=>x.blocks.map(y=>y.token)),['zh','ch','sh','ǖ']);
  assert.equal(p.settings.grid,'four');
  assert.throws(()=>C.parseItems('zh@','pinyin'),/拼音/);
});
test('numeric and English inputs are separated and high-risk input discarded',()=>{
  assert.deepEqual(C.parseItems('AB c d','latin'),['A','B','c','d']);
  assert.deepEqual(C.parseItems('001,2','numbers'),['0','0','1','2']);
  assert.deepEqual(C.parseItems('水 <script>火</script>','hanzi'),['水','火']);
  assert.throws(()=>C.parseItems('123','hanzi'),/至少一个/);
  assert.throws(()=>C.parseItems('水'.repeat(61),'hanzi'),/60/);
});
test('layout patterns support all blank, full trace and partially guided forms',()=>{
  assert.equal(C.rowInk('trace',3,5,2,10),'red');
  assert.equal(C.rowInk('blank',0,0,4,10),'blank');
  assert.equal(C.rowInk('sample',0,0,4,10),'sample');
  assert.equal(C.rowInk('sample',0,4,4,10),'red');
  assert.equal(C.rowInk('sample',0,5,4,10),'blank');
  assert.equal(C.rowInk('sample',1,1,4,10),'blank');
});
test('malformed options never inject CSS tokens; sizes always stay in print-safe range',()=>{
  const p=C.normalize({sizeMm:999,marginMm:-2,gridColor:'red;transform:none',
    traceColor:'#12345X',content:'水',rows:999});
  assert.equal(p.sizeMm,25);
  assert.equal(p.marginMm,10);
  assert.equal(p.rows,6);
  assert.match(p.gridColor,/^#[\da-f]{6}$/i);
  assert.match(p.traceColor,/^#[\da-f]{6}$/i);
});

test('long content or page title is rejected rather than silently truncated',()=>{
  assert.throws(()=>C.normalize({content:'字'.repeat(501)}),/最多500/);
  assert.throws(()=>C.normalize({title:'练'.repeat(27)}),/最多26/);
  assert.equal(C.normalize({title:'练'.repeat(26)}).title.length,26);
});

function reviewedGlyph(character,strokeCount){
  return {character,expected_stroke_count:strokeCount,
    strokes:Array.from({length:strokeCount},(_,i)=>({
      outline:'M '+(i+1)+' 0 L 3 3 Z',
      name:i%2?'竖钩':'横',name_status:i%2?'ordinal_only':'reviewed'
    }))};
}
test('stroke-order option defaults off and does not change the legacy A4 layout',()=>{
  assert.equal(C.DEFAULTS.showStrokeOrder,false);
  const source=new Map([['水',reviewedGlyph('水',4)]]);
  const p=C.paginate({content:'水水',showStrokeOrder:false},source);
  assert.equal(p.pages[0].blocks[0].strokeOrder,null);
  assert.equal(p.pages[0].blocks[0].heightMm,p.blockMm);
  assert.equal(p.pages[0].blocks[1].y-p.pages[0].blocks[0].y,p.blockMm);
});
test('opt-in steps use the exact ordered source and reserve physical millimetres',()=>{
  const source=new Map([['水',reviewedGlyph('水',4)]]);
  const p=C.paginate({content:'水水水水水水',showStrokeOrder:true},source);
  assert.equal(p.settings.showStrokeOrder,true);
  assert.equal(p.pages.length,3);
  for(const page of p.pages){
    assert.equal(page.blocks.length,2);
    for(const block of page.blocks){
      assert.equal(block.strokeOrder.kind,'steps');
      assert.equal(block.strokeOrder.count,4);
      assert.equal(block.strokeOrder.countRows,1);
      assert.ok(block.strokeOrder.cellMm>p.settings.sizeMm);
      assert.equal(block.practiceTopMm,7+block.strokeOrder.heightMm);
      assert.ok(block.y+block.heightMm<=p.printableBottom+1e-7);
    }
  }
});
test('complex Hanzi stroke order wraps without dropping any cumulative step',()=>{
  const n=22,source=new Map([['龠',reviewedGlyph('龠',n)]]);
  const p=C.paginate({content:'龠',showStrokeOrder:true},source);
  const b=p.pages[0].blocks[0],seq=b.strokeOrder;
  assert.equal(seq.count,n);
  assert.ok(seq.countRows>=3);
  assert.ok(seq.perRow*seq.countRows>=n);
  assert.ok((seq.countRows-1)*seq.perRow<n);
  assert.ok(b.y+b.heightMm<=p.printableBottom);
});
test('unknown Hanzi has an explicit missing-order warning but no invented strokes',()=>{
  const p=C.paginate({content:'龘',showStrokeOrder:true},new Map());
  assert.equal(p.sourceFallback,1);
  const step=p.pages[0].blocks[0].strokeOrder;
  assert.equal(step.kind,'unavailable');
  assert.equal(step.count,undefined);
  assert.equal(p.pages[0].blocks[0].practiceTopMm,7+step.heightMm);
});
test('only Hanzi can include the optional stroke sequence',()=>{
  const p=C.paginate({kind:'pinyin',content:'zh ch',showStrokeOrder:true});
  assert.equal(p.settings.showStrokeOrder,false);
  assert.ok(p.pages.every(page=>page.blocks.every(b=>b.strokeOrder===null)));
});
test('impossible A4 combination fails instead of clipping complex order or practice',()=>{
  const source=new Map([['龠',reviewedGlyph('龠',22)]]);
  assert.throws(()=>C.paginate({content:'龠',sizeMm:25,rows:6,
      rowGapMm:12,marginMm:25,showStrokeOrder:true},source),
    /无法完整放在一页/);
  const valid=C.paginate({content:'龠',sizeMm:15,showStrokeOrder:true},source);
  assert.equal(valid.items,1);
});
test('invalid or incomplete stroke vectors fail closed only when printing orders',()=>{
  const broken={character:'水',expected_stroke_count:2,
    strokes:[{outline:'M 0 0 L 1 1 Z'}]};
  const source=new Map([['水',broken]]);
  assert.doesNotThrow(()=>C.paginate({content:'水',showStrokeOrder:false},source));
  assert.throws(()=>C.paginate({content:'水',showStrokeOrder:true},source),
    /笔顺数据不完整/);
});
