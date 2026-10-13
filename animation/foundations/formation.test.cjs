'use strict';
/* F2.3: independent regression fixture against an explicitly selected
 * publisher instructional model. Path counts and start anchors are NOT
 * the same as national Pinyin pen-stroke standards; none exist.
 */
const test=require('node:test');
const assert=require('node:assert/strict');
const source=require('./data.js');
const fs=require('node:fs'),path=require('node:path');
const CAPS='ABCDEFGHIJKLMNOPQRSTUVWXYZ',LOW='abcdefghijklmnopqrstuvwxyz';
const expectedCaps=[3,3,1,2,4,3,3,3,3,2,3,2,4,3,1,2,2,3,1,2,1,2,4,2,2,3];
const expectedLower=[1,1,1,1,1,2,1,1,2,2,2,1,1,1,1,1,1,1,1,2,1,1,1,2,2,1];
// Freeze the starting positions independently of data.js so an accidental
// reversion to lower-left upstrokes or wrong order cannot silently pass.
const anchors={
  A:[[37,17],[37,17],[21,58]],
  B:[[14,17],[14,17],[14,49]],
  C:[[63,25]],
  D:[[14,17],[14,17]],
  E:[[14,17],[14,17],[14,50],[14,83]],
  F:[[14,17],[14,17],[14,50]],
  G:[[63,25],[42,54],[63,54]],
  H:[[14,17],[62,17],[14,50]],
  I:[[38,17],[20,17],[20,83]],
  J:[[58,17],[20,17]],
  K:[[14,17],[63,17],[34,41]],
  L:[[14,17],[14,83]],
  M:[[11,17],[11,17],[63,17],[63,17]],
  N:[[13,17],[13,17],[62,17]],
  O:[[37,17]],
  P:[[14,17],[14,17]],
  Q:[[37,17],[45,68]],
  R:[[14,17],[14,17],[40,52]],
  S:[[62,25]],
  T:[[37,17],[10,17]],
  U:[[14,17]],
  V:[[11,17],[64,17]],
  W:[[8,17],[21,83],[37,40],[51,83]],
  X:[[12,17],[64,17]],
  Y:[[10,17],[64,17]],
  Z:[[12,17],[63,17],[12,83]],
  a:[[56,50]],
  b:[[16,17]],
  c:[[57,51]],
  d:[[56,50]],
  e:[[17,65]],
  f:[[61,21],[22,49]],
  g:[[56,50]],
  h:[[17,17]],
  i:[[35,49],[35,30]],
  j:[[50,49],[50,30]],
  k:[[17,17],[58,49]],
  l:[[35,17]],
  m:[[10,49]],
  n:[[17,49]],
  o:[[56,53]],
  p:[[16,49]],
  q:[[56,50]],
  r:[[18,49]],
  s:[[57,52]],
  t:[[37,20],[22,49]],
  u:[[17,49]],
  v:[[15,49]],
  w:[[9,49]],
  x:[[15,49],[61,49]],
  y:[[13,49],[61,49]],
  z:[[16,49]],
};
function strokes(letter){
  return source.compose(letter).strokes.map(s=>s.d);
}
function start(path){
  const m=path.match(/^M(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/);
  if(!m)throw Error('Invalid first move: '+path);
  return [Number(m[1]),Number(m[2])];
}
test('F2.3 checks all 52 independent Latin print letter formations and pen-down counts',()=>{
  assert.equal(Object.keys(anchors).length,52);
  for(const [alphabet,counts] of [[CAPS,expectedCaps],[LOW,expectedLower]])
    for(let i=0;i<alphabet.length;i++){
      const letter=alphabet[i],paths=strokes(letter);
      assert.equal(paths.length,counts[i],letter+' independent pen-down count');
      assert.deepEqual(paths.map(start),anchors[letter],
        letter+' must start each independent pen-down at reviewed anchor');
      for(const [i,d] of paths.entries()){
        assert.equal((d.match(/\bM-?\d/g)||[]).length,1,
          letter+' path '+i+' must be one connected downstroke, no disjoint M teleport');
        assert.match(d,/^[MLHVCZ0-9 ,.-]+$/,'Simple drawn vector only: '+letter);
      }
    }
});
test('F2.3 directions of A E L M N T and lowercase a b d g m n p q',()=>{
  assert.deepEqual(strokes('A'),[
    'M37 17 L9 83','M37 17 L65 83','M21 58 H53']);
  assert.deepEqual(strokes('E'),[
    'M14 17 V83','M14 17 H64','M14 50 H54','M14 83 H64']);
  assert.deepEqual(strokes('L'),['M14 17 V83','M14 83 H63']);
  assert.deepEqual(strokes('T'),['M37 17 V83','M10 17 H64']);
  assert.deepEqual(strokes('M').map(d=>d.startsWith('M')),Array(4).fill(true));
  assert.equal(strokes('N').length,3);
  assert.equal(strokes('a').length,1);
  assert.ok(strokes('a')[0].startsWith('M56 50 C'));
  assert.ok(strokes('d')[0].startsWith('M56 50 C'));
  assert.ok(strokes('d')[0].endsWith('V17 V83'));
  for(const letter of 'bghmnpqr')
    assert.equal(strokes(letter).length,1,
      letter+' is continuously drawn in this manuscript scheme');
  assert.equal(strokes('i').length,2);
  assert.match(strokes('i')[0],/^M35 49 V83$/);
  assert.match(strokes('i')[1],/^M35 30 L35 31$/);
});
test('F2.3 preserves original 113 IDs and applies the SAME letters to Pinyin',()=>{
  assert.deepEqual(source.validate(),{groups:7,items:113});
  const groups=source.groups;
  assert.deepEqual(groups.map(g=>g.entries.length),[26,10,23,24,16,6,8]);
  for(const c of 'bcdfghjkmnpqrstyuw')
    assert.equal(source.compose(c).strokes.length,strokes(c).length);
  for(const s of ['zhi','ch','sh','ai','ang','üe','ǜ','nǐ hǎo']){
    const comp=source.compose(s);
    assert.ok(comp.strokes.length>0);
    assert.ok(comp.width>0);
  }
  assert.equal(source.compose('i').strokes.length,2);
  assert.equal(source.compose('ī').strokes.length,2);
  for(const x of ['ǖ','ǘ','ǚ','ǜ'])
    assert.equal(source.compose(x).strokes.filter(s=>s.part==='diaeresis').length,2);
  const reference=fs.readFileSync(path.join(__dirname,'../../docs/F23_LATIN_LETTER_FORMATION_AUDIT.md'),'utf8');
  assert.match(reference,/Learning Without Tears/);
  assert.match(reference,/国家统一的笔顺标准/);
  assert.match(reference,/Zaner-Bloser/);
});
