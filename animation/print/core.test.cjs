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
