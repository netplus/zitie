'use strict';
/* F2.4 source figure QA; NOT a count of publisher's Big Line words.
 * The JSON mapping is independently transcribed from numbered diagrams.
 */
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const model=require('./data.js');
const ref=require('./formation-lwt-2018.json');
const UPPER='ABCDEFGHIJKLMNOPQRSTUVWXYZ',LOWER='abcdefghijklmnopqrstuvwxyz';
function trace(char){return model.compose(char).strokes.map(s=>s.d);}
function start(svg){
 const match=svg.match(/^M(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/);
 if(!match)throw Error('Stroke has no start '+svg);
 return [Number(match[1]),Number(match[2])];
}
test('F2.4 independently source-checks all 52 numbered formation diagrams',()=>{
 assert.equal(Object.keys(ref.glyphs).length,52);
 assert.equal(ref.source.year,2018);
 assert.match(ref.source.url,/www\.lwtears\.com/);
 assert.match(ref.independentPenDownDefinition,/NOT individual pen lifts/);
 let upper=0,lower=0;
 for(const letter of UPPER+LOWER){
   const expected=ref.glyphs[letter],actual=trace(letter);
   assert.ok(expected,'Missing publisher source page '+letter);
   assert.ok([1,2,3].includes(expected.page),'Missing source picture page '+letter);
   assert.equal(expected.movementSummary.length,expected.numberedPenDown,letter+' source movements');
   assert.equal(actual.length,expected.numberedPenDown,letter+' false pen lift');
   assert.deepEqual(actual.map(start),expected.starts,letter+' incorrect source-aligned start');
   for(const d of actual){
     // No mid-path M: one contact cannot secretly teleport to another point.
     assert.equal((d.match(/M-?\d/g)||[]).length,1,letter+' discontinuous pen contact');
     assert.match(d,/^[MLHVCZ0-9 .,-]+$/);
   }
   if(/[A-Z]/.test(letter))upper+=actual.length;else lower+=actual.length;
 }
 assert.equal(upper,50);
 assert.equal(lower,33);
});
test('F2.4 rejects phantom lifts previously added from Big Line action labels',()=>{
 for(const c of 'LUVWZ')assert.equal(trace(c).length,1,c+' must turn without lifting');
 for(const c of 'BGKMNR')assert.equal(trace(c).length,2,c+' must not split motions into strokes');
 assert.equal(trace('A').length,3,'A has three explicitly numbered contacts');
 assert.equal(trace('E').length,4,'E has four explicitly numbered contacts');
 assert.equal(trace('T').length,2);
 assert.equal(trace('f').length,2);
 assert.equal(trace('k').length,2);
});
test('F2.4 tests turn direction, travel continuity and actual starting anchors',()=>{
 assert.equal(trace('L')[0],'M14 17 V83 H63');
 assert.equal(trace('M')[1],'M11 17 L37 56 L63 17 V83');
 assert.equal(trace('N')[1],'M13 17 L62 83 V17','N must ascend right');
 assert.equal(trace('V')[0],'M11 17 L37 83 L64 17','V must ascend after valley');
 assert.equal(trace('W')[0],'M8 17 L21 83 L37 40 L51 83 L66 17');
 assert.equal(trace('Z')[0],'M12 17 H63 L12 83 H64');
 assert.equal(trace('K')[1],'M63 17 L14 55 L65 83');
 assert.equal(trace('G')[1],'M42 54 H63 V73');
 assert.match(trace('B')[1],/H14 H42 C73/,'B curves are continuous in pen-down two');
 assert.match(trace('R')[1],/H14 H40 L66 83$/,'R leg stays within pen-down two');
 assert.match(trace('f')[0],/^M42 47 C40 34/,'f begins by curving up');
 assert.equal(trace('k')[1],'M19 68 L58 49 L19 68 L61 83');
 assert.match(trace('O')[0],/^M53 20 C33 12/);
 assert.match(trace('Q')[0],/^M53 20 C33 12/);
});
test('F2.4 remains source- and storage-compatible with 113 Pinyin entries',()=>{
 assert.deepEqual(model.validate(),{groups:7,items:113});
 const total=model.groups.reduce((a,g)=>a+g.entries.reduce((b,e)=>
   b+model.compose(e.text,g.kind,g.script).strokes.length,0),0);
 assert.equal(total,447);
 for(const ch of LOWER)
   assert.equal(trace(ch).length,ref.glyphs[ch].numberedPenDown);
 for(const word of ['zhi','ch','sh','üe','nǐ hǎo']){
   assert.ok(model.compose(word).strokes.length>0,word);
 }
 assert.equal(trace('ī').length,trace('i').length);
 for(const v of ['ǖ','ǘ','ǚ','ǜ'])
   assert.equal(model.compose(v).strokes.filter(s=>s.part==='diaeresis').length,2);
 const d=fs.readFileSync(path.join(__dirname,'../../docs/F24_PUBLISHER_CHART_AUDIT.md'),'utf8');
 assert.match(d,/动作段数不等于/);
 assert.match(d,/不等于国家统一/);
});
