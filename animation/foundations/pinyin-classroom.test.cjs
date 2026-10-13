'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const lib=require('./data.js');
const source=require('./pinyin-classroom-sources.json');
const by=key=>lib.groups.find(g=>g.key===key);
const P=c=>lib.compose(c,'lines','pinyin').strokes;
const E=c=>lib.compose(c,'lines','latin').strokes;
test('F2.6c separates all seven catalogue groups into independently named writing models',()=>{
 assert.deepEqual(lib.groups.map(g=>g.script),['latin','numbers','pinyin','pinyin','pinyin','pinyin','pinyin']);
 assert.deepEqual(lib.validate(),{groups:7,items:113});
 assert.deepEqual(lib.verifiedPinyinLetters,['a','b','d','g','m','n','p','q','u']);
 assert.equal(source.independentFromEnglish,true);
 assert.match(source.status,/not constitute teacher certification/);
 assert.throws(()=>lib.compose('a','lines','invalid'),/Unknown writing model/);
 for(const g of lib.groups)for(let i=0;i<g.entries.length;i++)
   assert.equal(g.entries[i].id,g.key+'-'+i,'stable local saved entry ID');
});
test('F2.6c grade-1 classroom source independently maps 9 letters to pen-down counts',()=>{
 for(const [letter,evidence] of Object.entries(source.overrides)){
   const pinyin=P(letter),english=E(letter);
   assert.equal(pinyin.length,evidence.contacts,letter+' classroom source count');
   assert.equal(evidence.steps.length,evidence.contacts,letter+' cited contact descriptions');
   assert.equal(lib.modelInfo(letter,'pinyin'),'pinyin-classroom-source-mapped');
   assert.notDeepEqual(pinyin.map(s=>s.d),english.map(s=>s.d),
     letter+' cannot alias English manuscript trajectory');
   assert.ok(pinyin.every(x=>(x.d.match(/M-?\d/g)||[]).length===1),
     letter+' no hidden pointer teleport inside contact');
 }
 assert.equal(Object.keys(source.overrides).length,9);
 assert.equal(lib.modelInfo('h','pinyin'),'pinyin-pending-review');
});
test('F2.6c Pinyin a/b/p/d/q use correct first semicurve vs stem direction',()=>{
 assert.equal(P('a').length,2);
 assert.ok(P('a')[0].d.startsWith('M55 49 C'));
 assert.ok(P('a')[1].d.startsWith('M56 49 V77'));
 for(const c of ['b','p']){
   assert.equal(P(c).length,2);
   assert.match(P(c)[0].d,/^M16 (17 V83|49 V109)$/);
   assert.match(P(c)[1].d,/^M16 49 C/);
 }
 for(const c of ['d','q']){
   assert.ok(P(c)[0].d.startsWith('M56 49 C'));
   assert.ok(P(c)[1].d.startsWith('M56 '));
 }
 assert.match(P('q')[1].d,/V109$/);
 assert.match(P('g')[1].d,/V98 C56 111/);
});
test('F2.6c Pinyin u has two contacts, ü four including separate two dots',()=>{
 assert.equal(E('u').length,1);
 assert.equal(P('u').length,2);
 assert.equal(lib.compose('ü','lines','pinyin').strokes.length,4);
 assert.equal(lib.compose('ǖ','lines','pinyin').strokes.length,5);
 for(const c of ['ǖ','ǘ','ǚ','ǜ']){
  const v=lib.compose(c,'lines','pinyin').strokes;
  assert.equal(v.filter(x=>x.part==='diaeresis').length,2,c+' two dots retained');
  assert.equal(v.filter(x=>x.part==='tone').length,1,c+' tone additional');
 }
 assert.equal(lib.compose('ā','lines','pinyin').strokes.length,3);
 assert.equal(lib.compose('ā','lines','latin').strokes.length,2);
});
test('F2.6c Pinyin source must also power every category including whole syllables and A4 words',()=>{
 for(const g of lib.groups){
  for(const item of g.entries){
   const comp=lib.compose(item.text,g.kind,g.script);
   assert.ok(comp.strokes.length>0,item.id);
   if(g.script==='pinyin'&&item.text.includes('a')){
      const legacy=lib.compose(item.text,g.kind,'latin');
      assert.ok(comp.strokes.length>=legacy.strokes.length,item.id);
   }
  }
 }
 const total=lib.groups.reduce((s,g)=>s+g.entries.reduce((v,i)=>
   v+lib.compose(i.text,g.kind,g.script).strokes.length,0),0);
 assert.equal(total,447);
 const b=by('initials').entries.find(x=>x.text==='b');
 const q=by('initials').entries.find(x=>x.text==='q');
 assert.equal(lib.compose(b.text,'lines',by('initials').script).strokes.length,2);
 assert.equal(lib.compose(q.text,'lines',by('initials').script).strokes.length,2);
});
test('F2.6c previous blue learner marks remain under original keys and labelled',()=>{
 const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
 const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
 assert.match(app,/storagePrefix='zitie-foundations-f1:'/);
 assert.match(app,/version:1,strokes:state\.strokes,model:sourceVersion\(\),legacyInk:state\.legacyInk/);
 assert.match(app,/sourceVersion\(\)/);
 assert.match(app,/hasLegacyLessonInk\(item\)/);
 assert.match(app,/已保留旧版练习笔迹/);
 assert.match(app,/state\.legacyInk=false/);
 assert.match(app,/model\.compose\(item\.text,state\.group\.kind,state\.group\.script\)/);
 assert.match(app,/model\.compose\(entry\.text,state\.group\.kind,state\.group\.script\)/);
 assert.match(html,/id="printRoot"/);
 assert.doesNotMatch(app,/\bfetch\s*\(|sendBeacon|XMLHttpRequest/);
});
