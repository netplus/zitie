'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');
const {prepareReference,SOURCE_TRANSFORM}=require('../practice/reference-stage.js');
const html=fs.readFileSync(path.join(ROOT,'animation/book.html'),'utf8');
const bridge=fs.readFileSync(path.join(ROOT,'animation/practice/practice-bridge.js'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'animation/practice/practice.css'),'utf8');
const script=fs.readFileSync(path.join(ROOT,'build/a3/book-pack.js'),'utf8');
assert.ok(script.startsWith('window.ZITIE_BOOK_PACK = '));
const pack=JSON.parse(script.slice('window.ZITIE_BOOK_PACK = '.length,-2));

test('P2.1a snapshot preserves exactly 201 PDF-backed source glyphs and 1045 source strokes',()=>{
 assert.equal(pack.publication.version,'0.5.1');
 assert.equal(pack.publication.pages,299);
 assert.equal(pack.glyphs.length,201);
 assert.equal(SOURCE_TRANSFORM,'translate(0 900) scale(1 -1)');
 let count=0;
 for(const glyph of pack.glyphs){
   const before=JSON.stringify(glyph);
   const reference=prepareReference(glyph);
   assert.equal(reference.mainId,glyph.main_id);
   assert.equal(reference.character,glyph.character);
   assert.equal(reference.strokeCount,glyph.expected_stroke_count);
   assert.equal(reference.sourceHash,glyph.source_sha256);
   assert.equal(reference.trajectoryStatus,'engineering_preview_unreviewed');
   assert.equal(Object.isFrozen(reference),true);
   for(let i=0;i<reference.strokeCount;i++){
     const current=reference.strokes[i],source=glyph.strokes[i];
     assert.notStrictEqual(current,source);
     assert.equal(current.outline,source.outline);
     assert.deepEqual(current.median,source.median);
     assert.notStrictEqual(current.median,source.median);
     assert.equal(Object.isFrozen(current.median),true);
     assert.equal(current.index,i);
     assert.equal(current.name,source.name_status==='reviewed'?source.name:null);
     if(source.name_status==='ordinal_only')assert.equal(current.name,null);
   }
   count+=reference.strokeCount;
   assert.equal(JSON.stringify(glyph),before,'Source mutated on snapshot '+glyph.character);
 }
 assert.equal(count,1045);
 assert.equal(pack.glyphs[76].character,'水');
 assert.equal(prepareReference(pack.glyphs[76]).strokeCount,4);
 assert.equal(prepareReference(pack.glyphs[200]).strokeCount,17);
});
test('P2.1a source rejects invalid/unapproved data without modifying original',()=>{
 const src=pack.glyphs[76];
 assert.throws(()=>prepareReference({...src,source_sha256:'bad'}),/hash/);
 assert.throws(()=>prepareReference({...src,strokes:src.strokes.slice(1)}),/source|metadata|Invalid|Missing/i);
 assert.throws(()=>prepareReference({...src,trajectory_review_status:'teacher_verified'}),/Trajectory audit status required|Unrecognized source motion review status/);
 const snapshot=prepareReference(src);
 assert.throws(()=>{snapshot.strokes[0].median[0][0]=NaN;},TypeError);
 assert.notEqual(src.strokes[0].median[0][0],NaN);
});
test('P2.1a modal has exactly one accessible trigger and independent source stage',()=>{
 for(const id of ['practiceLaunch','practiceOverlay','practiceExit',
   'practiceBoard','practiceSvg','practicePrev','practiceNext']){
   assert.equal([...html.matchAll(new RegExp('id="'+id+'"','g'))].length,1,id);
 }
 assert.match(html,/<div class="paper" role="button" tabindex="0"/);
 assert.match(html,/aria-label="开始逐笔临摹"/);
 assert.match(html,/\.pager \.practiceLaunchText\{display:none\}/);
 assert.match(html,/id="practiceOverlay" class="practiceOverlay" role="dialog"/);
 assert.match(html,/aria-modal="true"/);
 assert.match(html,/id="practiceOverlay"[\s\S]{0,150}hidden>/);
 assert.match(html,/src="\.\/practice\/reference-stage\.js"/);
 assert.match(html,/src="\.\/practice\/practice-bridge\.js"/);
 assert.match(html,/href="\.\/practice\/practice\.css"/);
 assert.match(bridge,/book\.player\.pause\(\)/);
 assert.match(bridge,/book\.player\.seekElapsed\(saved\.elapsedMs\)/);
 assert.match(bridge,/main\.inert=true/);
 assert.match(css,/\.practiceOverlay\[hidden\]\{display:none!important\}/);
 assert.match(css,/height:100vh;height:100dvh/);
 assert.doesNotMatch(bridge,/pointerdown|pointermove|getCoalescedEvents|fetch\(/i);
 assert.match(html,/<canvas id="practiceInk"/);
 assert.match(html,/src="\.\/practice\/trace-session\.js"/);
 assert.match(html,/src="\.\/practice\/trace-canvas\.js"/);
 assert.match(html,/src="\.\/practice\/pointer-input\.js"/);
 assert.match(bridge,/noAutomaticScore:true,noPersistentWritingStorage:false/);
 assert.match(html,/src="\.\/practice\/progress-controller\.js"/);
 assert.match(html,/src="\.\/practice\/storage\.js"/);
 assert.doesNotMatch(bridge,/XMLHttpRequest|fetch\(/i);
 assert.match(bridge,/Storage\.LocalPracticeStore\(\)/);
});
