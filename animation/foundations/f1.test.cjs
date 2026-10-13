'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=__dirname;
const lib=require('./data.js');
const names=['letters','numbers','initials','finals','syllables','tones','words'];
test('F1 catalogue is exhaustive, stable and independent of the Chinese book',()=>{
  assert.deepEqual(lib.groups.map(x=>x.key),names);
  assert.deepEqual(lib.groups.map(x=>x.entries.length),[26,10,23,24,16,6,8]);
  assert.deepEqual(lib.validate(),{groups:7,items:113});
  assert.deepEqual(lib.groups[2].entries.map(x=>x.text),
    'b p m f d t n l g k h j q x zh ch sh r z c s y w'.split(' '));
  assert.deepEqual(lib.groups[3].entries.map(x=>x.text),
    'a o e i u ü ai ei ui ao ou iu ie üe er an en in un ün ang eng ing ong'.split(' '));
  assert.deepEqual(lib.groups[4].entries.map(x=>x.text),
    'zhi chi shi ri zi ci si yi wu yu ye yue yuan yin yun ying'.split(' '));
  assert.deepEqual([...new Set(lib.groups.flatMap(g=>g.entries.map(e=>e.id)))].length,113);
});
test('F1 original monoline vectors support every upper/lower letter and digit',()=>{
  for(const str of [...'ABCDEFGHIJKLMNOPQRSTUVWXYZ',...'abcdefghijklmnopqrstuvwxyz',...'0123456789']){
    const part=lib.compose(str,/[0-9]/.test(str)?'squares':'lines');
    assert.ok(part.strokes.length>0,str);
    assert.ok(part.strokes.every(s=>s.d[0]==='M'),str);
    assert.equal(part.width,76);
  }
  for(const group of lib.groups)for(const entry of group.entries){
    const m=lib.compose(entry.text,group.kind);
    assert.ok(m.width>0&&m.height===132);
    assert.ok(m.strokes.every(s=>s.d&&Number.isFinite(s.x)),entry.text);
  }
});
test('F1 Unicode tone decomposition preserves ü dots and removes dotted i when accented',()=>{
  assert.equal(lib.compose('i').strokes.length,2);
  assert.equal(lib.compose('ī').strokes.length,2);
  assert.ok(lib.compose('ā').strokes.some(x=>x.part==='tone'));
  assert.equal(lib.compose('ü').strokes.filter(x=>x.part==='diaeresis').length,2);
  for(const s of ['ǖ','ǘ','ǚ','ǜ']){
    const strokes=lib.compose(s).strokes;
    assert.equal(strokes.filter(x=>x.part==='diaeresis').length,2,s);
    assert.equal(strokes.filter(x=>x.part==='tone').length,1,s);
  }
  assert.throws(()=>lib.compose('字'),/Unknown practice vector/);
  assert.throws(()=>lib.parts('\u0301'),/Unattached diacritic/);
});
test('F1 is opt-in, has independent pointer practice, A4 print and explicit disclaimers',()=>{
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const css=fs.readFileSync(path.join(root,'style.css'),'utf8');
  const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
  for(const id of ['guide','ink','clear','undo','print','printRoot','items','tabs','demo'])
    assert.match(html,new RegExp('id="'+id+'"'));
  assert.match(html,/书法教师逐项复核/);
  assert.match(html,/不自动评分/);
  assert.match(css,/@page\{size:A4 portrait/);
  assert.match(css,/#ink\{touch-action:none/);
  assert.match(app,/width:64,height:66/);
  assert.match(app,/const W=1600/);
  assert.match(app,/cellWidth=W\/copies/);
  assert.match(app,/touchstart/);
  assert.match(app,/pointerdown/);
  assert.match(app,/preferNativeTouch/);
  assert.match(app,/state\.active\.kind='touch'/);
  assert.match(app,/window\.addEventListener\('orientationchange',cancel\)/);
  const smoke=fs.readFileSync(path.join(root,'browser-smoke.html'),'utf8');
  for(const scenario of ['pointer-only stroke','pointer-to-touch handoff',
    'touch-first has no duplicate','multitouch aborts','unchanged-size resize preserves'])
    assert.ok(smoke.includes(scenario),scenario);
  assert.match(app,/localStorage\.setItem/);
  assert.match(app,/window\.print\(\)/);
  assert.match(app,/state\.strokes=\[\]/);
  assert.doesNotMatch(app,/fetch\(|XMLHttpRequest|sendBeacon/);
});
