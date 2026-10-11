'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const T=require('../timeline.js');
const ROOT=path.resolve(__dirname,'../..');
const relative='build/a3/book-pack.js';
const raw=fs.readFileSync(path.join(ROOT,relative),'utf8');
assert.ok(raw.startsWith('window.ZITIE_BOOK_PACK = ')&&raw.endsWith(';\n'),
  'No frozen generated A3 book asset');
const pack=JSON.parse(raw.slice('window.ZITIE_BOOK_PACK = '.length,-2));
const reference=JSON.parse(fs.readFileSync(path.join(ROOT,
  'deliverables/manifest.json'),'utf8'));
const pdfPath='deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf';
const published=reference.artifacts.find(x=>x.path===pdfPath);
const idx=new Map(pack.glyphs.map(g=>[g.main_id,g]));
const load=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));

test('201 source identities, 21 batches, immutable released 299-page PDF',()=>{
  assert.equal(pack.schema_version,1);
  assert.equal(pack.publication.version,'0.5.1');
  assert.equal(pack.publication.pages,299);
  assert.equal(pack.publication.path,pdfPath);
  assert.equal(pack.publication.sha256,published.sha256);
  assert.equal(pack.review_state,'stroke_order_source_reviewed_motion_unreviewed');
  assert.equal(pack.glyphs.length,201);
  assert.deepEqual([...idx.keys()],Array.from({length:201},(_,i)=>i+1));
  assert.equal(new Set(pack.glyphs.map(g=>g.character)).size,201);
  assert.equal(new Set(pack.glyphs.map(g=>g.batch_id)).size,21);
  assert.equal(pack.source_revision,'68d10a4b21150cae5e1ebbd223eed289cf32d90c');
});

test('all rendered book strokes use approved PDF input metadata, not guessed code',()=>{
  const expected=new Map();
  for(let i=1;i<=21;i++){
    const batch='B'+String(i).padStart(2,'0');
    const data=load('data/'+batch+'.json');
    for(const entry of data.entries)expected.set(entry.main_id,{entry,batch});
  }
  assert.equal(expected.size,201);
  let strokes=0;
  const seenPages=new Set();
  for(const glyph of pack.glyphs){
    T.validateGlyph(glyph);
    const source=expected.get(glyph.main_id);
    assert.ok(source);
    assert.equal(glyph.character,source.entry.character);
    assert.equal(glyph.batch_id,source.batch);
    assert.equal(glyph.expected_stroke_count,glyph.strokes.length);
    assert.equal(glyph.order_code.length,glyph.strokes.length);
    assert.ok(glyph.pdf_page_start>=1&&glyph.pdf_page_end<=299);
    assert.equal(glyph.pdf_page_end-glyph.pdf_page_start+1,
      Math.ceil(glyph.strokes.length/6));
    assert.equal(glyph.pdf_step_pages,Math.ceil(glyph.strokes.length/6));
    assert.equal(glyph.trajectory_review_status,'engineering_preview_unreviewed');
    assert.ok(glyph.source_sha256.match(/^[0-9a-f]{64}$/));
    assert.equal(glyph.tips.length,2);
    assert.ok(glyph.check.length>2);
    for(let n=glyph.pdf_page_start;n<=glyph.pdf_page_end;n++){
      assert.ok(!seenPages.has(n),'Overlapping PDF practice page '+n);
      seenPages.add(n);
    }
    strokes+=glyph.strokes.length;
    const timeline=T.buildTimeline(glyph);
    assert.equal(timeline.strokes.length,glyph.strokes.length);
    assert.ok(timeline.totalMs>0);
    const final=T.frameAt(timeline,timeline.totalMs);
    assert.equal(final.phase,'finished');
  }
  assert.equal(strokes,pack.summary.strokes);
  assert.ok(strokes>600);
  assert.equal(seenPages.size,pack.glyphs.reduce((n,g)=>n+g.pdf_step_pages,0));
});

test('the exact nine old samples retain stroke order and SVG source silhouettes',()=>{
  const source=fs.readFileSync(path.join(ROOT,'animation/samples.js'),'utf8');
  const old=JSON.parse(source.split('window.ZITIE_SAMPLES = ')[1].trim().replace(/;$/,''));
  assert.equal(old.glyphs.length,9);
  for(const glyph of old.glyphs){
    const book=idx.get(glyph.main_id);
    assert.equal(glyph.character,book.character);
    assert.equal(glyph.order_code,book.order_code);
    assert.equal(glyph.strokes.length,book.strokes.length);
    for(let i=0;i<glyph.strokes.length;i++){
      assert.equal(glyph.strokes[i].outline,book.strokes[i].outline);
      assert.deepEqual(glyph.strokes[i].median,book.strokes[i].median);
    }
  }
});

test('restricted fine stroke names and pronunciations stay unpublished',()=>{
  const policy=load('data/teaching-source-policy.json');
  const rule=field=>policy.rules.find(r=>r.field===field).main_ids;
  for(const id of rule('fine_stroke_names')){
    const glyph=idx.get(id);
    assert.equal(glyph.fine_name_policy,'ordinal_only');
    assert.ok(glyph.strokes.every(s=>s.name===null&&
      s.name_status==='ordinal_only'));
  }
  for(const id of rule('pronunciation')){
    const glyph=idx.get(id);
    assert.equal(glyph.pinyin,null);
    assert.ok(glyph.reading_note,'Missing blocked-reading explanation for '+id);
  }
  assert.equal(idx.get(201).expected_stroke_count,17);
  assert.equal(idx.get(201).pdf_step_pages,3);
  assert.equal(idx.get(201).pinyin,null);
});

test('the generated A3 pack is deterministic and safe to load offline',()=>{
  assert.equal(pack.glyphs[0].character,'一');
  assert.equal(pack.glyphs[0].pdf_step_pages,1);
  assert.equal(pack.glyphs.at(-1).character,'龠');
  assert.equal(pack.publication.step_limit_per_pdf_page,6);
  assert.equal(pack.publication.site_url,'../book/zitie-v0.5.1-A4.pdf');
  assert.ok(!raw.includes('fetch('));
  assert.ok(!raw.includes('<script'));
});
