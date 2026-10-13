'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const data=require('./data.js'),teaching=require('./teaching.js');
const group=key=>data.groups.find(x=>x.key===key);
const cue=(key,value)=>teaching.tipFor(key,value);
test('F2.2 every one of 113 stable entries has a source-classified nonempty cue',()=>{
  let count=0;
  for(const category of data.groups)for(const entry of category.entries){
    const note=teaching.tipFor(category,entry);
    assert.equal(typeof note.headline,'string',entry.id);
    assert.ok(note.headline.length>=5&&note.headline.length<70,entry.id);
    assert.ok(note.detail.length>=12&&note.detail.length<150,entry.id);
    assert.ok(['spelling','recognition','geometry'].includes(note.source),entry.id);
    assert.ok(teaching.sources[note.source]?.length,entry.id);
    assert.ok(note.label.length>4,entry.id);
    assert.doesNotMatch(note.headline+note.detail,/官方笔顺|国家规定笔顺|已获得教师审定/);
    assert.equal(note.headline,teaching.tipFor(category.key,entry.text).headline);
    count++;
  }
  assert.equal(count,113);
});
test('F2.2 b/d/p/q explain different sides and descending tails without prescribing a stroke order',()=>{
  const g=group('initials');
  const tips=Object.fromEntries(['b','d','p','q'].map(x=>[x,teaching.tipFor(g,g.entries.find(e=>e.text===x))]));
  assert.match(tips.b.headline,/左竖右圆/);
  assert.match(tips.d.headline,/左圆右竖/);
  assert.match(tips.p.headline,/下伸到下格/);
  assert.match(tips.q.headline,/下伸到下格/);
  for(const x of ['b','d','p','q'])
    assert.equal(tips[x].source,'recognition');
  assert.match(cue('initials','n').headline,/一门/);
  assert.match(cue('initials','m').headline,/两门/);
  for(const name of ['zh','ch','sh'])
    assert.match(cue('initials',name).headline,/两个字母/);
});
test('F2.2 tone rules: i loses its dot, ü keeps both, iu and ui stress the second vowel',()=>{
  assert.match(cue('finals','i').detail,/省去/);
  for(const x of ['ü','üe','ün'])
    assert.match(cue('finals',x).headline,/两点/);
  assert.match(cue('finals','iu').headline,/后面的 u/);
  assert.match(cue('finals','ui').headline,/后面的 i/);
  assert.match(cue('finals','iu').detail,/liú/);
  assert.match(cue('finals','ui').detail,/shuǐ/);
  const tones=group('tones');
  assert.equal(tones.entries.length,6);
  for(const entry of tones.entries)
    assert.equal(teaching.tipFor(tones,entry).source,'spelling',entry.id);
  assert.match(cue('tones','ī í ǐ ì').headline,/i 去点/);
  assert.match(cue('tones','ǖ ǘ ǚ ǜ').headline,/ü 两点不消失/);
  assert.equal(data.compose('ǜ').strokes.filter(x=>x.part==='diaeresis').length,2);
});
test('F2.2 y-related whole-syllable spellings retain the explicit ü omission',()=>{
  for(const x of ['yu','yue','yuan','yun']){
    const a=cue('syllables',x);
    assert.equal(a.source,'spelling');
    assert.match(a.detail,/省点|省去两点/);
    assert.ok(a.headline.includes('整体认读'));
  }
  assert.match(cue('syllables','ying').headline,/整体认读/);
});
test('F2.2 UI and printing source cues stay read-only, avoid duplicate guidance',()=>{
  const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
  const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
  const css=fs.readFileSync(path.join(__dirname,'style.css'),'utf8');
  assert.match(html,/defer src="\.\/teaching\.js"/);
  assert.match(html,/id="tipBasis"/);
  assert.equal((html.match(/id="tipText"/g)||[]).length,1);
  assert.match(app,/const cue=teaching\.tipFor\(state\.group,item\)/);
  assert.match(app,/printCue\.textContent=cue\.headline/);
  assert.match(css,/\.tipCopy\{/);
  assert.doesNotMatch(app,/fetch\s*\(|sendBeacon|XMLHttpRequest/);
  assert.throws(()=>teaching.tipFor('unknown','x'),/Invalid foundation teaching entry/);
});
