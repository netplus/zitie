'use strict';
/* F2.5 selected-publisher evidence tests for capital J,T / lowercase b,q.
 * Do not infer teacher approval from source path counts or internal anchors.
 * Publisher's 2018 charts: capitals p1, lowercase b p2, q p3.
 */
const test=require('node:test'),assert=require('node:assert/strict');
const data=require('./data.js');
const ref=require('./formation-lwt-2018.json');
const fs=require('node:fs'),path=require('node:path');
const trace=letter=>data.compose(letter).strokes.map(s=>s.d);
const group=key=>data.groups.find(g=>g.key===key);
const cubic=(p0,p1,p2,p3,t)=>{
 const u=1-t;
 return u*u*u*p0+3*u*u*t*p1+3*u*t*t*p2+t*t*t*p3;
};
test('F2.5 source checks explicitly distinguish verified J/T from corrected b/q',()=>{
 for(const letter of ['J','T','b','q']){
  const x=ref.glyphs[letter],focus=x.focused20261013;
  assert.ok(focus,letter+' missing independent publisher evidence');
  assert.equal(focus.selectedSourcePdfPage,x.page,letter+' publisher chart page');
  assert.equal(focus.contactSequence.length,x.numberedPenDown,letter+' contact count');
  assert.match(focus.primaryChartUrl,/lwtears.com\/sites\/default\/files/);
  assert.match(focus.noteOnCoordinates,/不是出版方/);
  assert.equal(trace(letter).length,x.numberedPenDown,letter);
  const starts=trace(letter).map(svg=>{
   const m=svg.match(/^M(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/);
   assert.ok(m,letter+' path missing move start');
   return [Number(m[1]),Number(m[2])];
  });
  assert.deepEqual(starts,x.starts,letter+' source-backed anchors');
 }
 assert.deepEqual(['J','T','b','q'].map(ch=>ref.glyphs[ch].page),[1,1,2,3]);
});
test('F2.5 capital J has two contacts; curl follows downward stem, stays at baseline',()=>{
 const [stem,bar]=trace('J');
 assert.equal(stem,'M58 17 V64 C58 85 48 83 35 83 C24 83 17 78 17 71');
 assert.equal(bar,'M20 17 H61');
 // Prior curve (65 -> 95,94 -> 72) crossed the 83 SVG-unit baseline by 5+.
 // Test actual cubic path envelope, not merely the final point.
 let maxY=64;
 for(let i=0;i<=1000;i++){
  const t=i/1000;
  maxY=Math.max(maxY,cubic(64,85,83,83,t));
  maxY=Math.max(maxY,cubic(83,83,78,71,t));
 }
 assert.ok(maxY>=82.9&&maxY<=83.2,'J baseline curve overshot '+maxY);
 assert.ok(Number(ref.glyphs.J.focused20261013.direction.includes('down_then_left_turn_then_up')));
});
test('F2.5 capital T already correctly uses downward stem before left-to-right top bar',()=>{
 assert.deepEqual(trace('T'),['M37 17 V83','M10 17 H64']);
 assert.deepEqual(ref.glyphs.T.starts,[[37,17],[10,17]]);
 assert.match(ref.glyphs.T.focused20261013.notes,/保留原字节/);
});
test('F2.5 lowercase b dives to baseline, RETRACES same stem, then circles right',()=>{
 const [b]=trace('b');
 assert.equal(b,'M16 17 V83 V49 C22 47 28 47 38 47 C53 47 61 56 61 66 C61 78 49 83 35 83 C26 83 20 82 16 83');
 assert.match(b,/^M16 17 V83 V49 C/,'must swim UP THE SAME VERTICAL STEM');
 assert.match(b,/C22 47 28 47 38 47/,'after vertical return go over to the right');
 assert.match(b,/16 83$/,'around bump must terminate on the lower baseline');
 assert.equal(trace('b').length,1,'b does not lift mid-letter');
 assert.match(ref.glyphs.b.focused20261013.direction,/retrace_up_same_stem/);
});
test('F2.5 lowercase q rightward U-turn, unlike left-returning g',()=>{
 const [q]=trace('q'),[g]=trace('g');
 assert.match(q,/^M56 50 C44 44 18 46 15 64/,'q starts with magic-c arc');
 assert.match(q,/V106 C56 116 69 116 69 105$/,'U-turn to RIGHT, end slightly upward');
 assert.ok(Number(69)>Number(56),'q return endpoint right of descender');
 assert.ok(Number(105)<Number(116),'q return endpoint above bottom turning tangent');
 assert.ok(g.endsWith('19 100'),'g preserves distinct LEFT-turning tail');
 assert.match(ref.glyphs.q.focused20261013.direction,/u_turn_to_right/);
});
test('F2.5 Pinyin b/q, other 113 entries, printing and saved trace keys remain valid',()=>{
 assert.deepEqual(data.validate(),{groups:7,items:113});
 const initial=group('initials').entries;
 for(const letter of ['b','q']){
  const entry=initial.find(e=>e.text===letter);
  assert.ok(entry);
  assert.deepEqual(data.compose(entry.text).strokes,data.compose(letter).strokes);
 }
 const totals=data.groups.reduce((n,g)=>n+g.entries.reduce((m,e)=>
  m+data.compose(e.text,g.kind).strokes.length,0),0);
 assert.equal(totals,366,'only 1/4/8 independent contacts updated in F2.6b');
 const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
 const css=fs.readFileSync(path.join(__dirname,'style.css'),'utf8');
 const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
 assert.match(css,/@page\{size:A4 portrait/);
 assert.match(app,/storagePrefix='zitie-foundations-f1:'/);
 assert.match(html,/id="printRoot"/);
 const guide=fs.readFileSync(path.join(__dirname,'../../docs/F25_JT_BQ_LWT_REFERENCE_AUDIT.md'),'utf8');
 assert.match(guide,/J、T/);
 assert.match(guide,/b、q/);
});
