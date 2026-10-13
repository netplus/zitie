'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const model=require('./data.js');
const source=require('./number-formation-lwt2018.json');
function vectors(n){return model.compose(n,'squares').strokes.map(s=>s.d);}
function end(str){
 const toks=str.match(/[MLHVCZ]|-?\d+(?:\.\d+)?/g)||[];
 let i=0,mode='',x=0,y=0,sx=0,sy=0;
 const n=()=>Number(toks[i++]);
 while(i<toks.length){
  if(/^[MLHVCZ]$/.test(toks[i]))mode=toks[i++];
  if(mode==='M'||mode==='L'){x=n();y=n();if(mode==='M'){sx=x;sy=y;mode='L';}}
  else if(mode==='H')x=n();
  else if(mode==='V')y=n();
  else if(mode==='C'){for(let z=0;z<4;z++)n();x=n();y=n();}
  else if(mode==='Z'){x=sx;y=sy;mode='';}
  else throw Error('unexpected SVG command '+mode);
 }
 return [x,y];
}
test('F2.6b 2018 publisher number stories provide independent 1/4/8 directions',()=>{
 assert.equal(source.source.publisher,'Learning Without Tears');
 assert.equal(source.source.pdfPage,4);
 assert.match(source.source.url,/lwtears.com/);
 assert.deepEqual(Object.keys(source.numerals),['1','4','8']);
 for(const n of ['1','4','8']){
  const e=source.numerals[n],actual=vectors(n);
  assert.equal(actual.length,e.contacts,n+' count of pen-downs');
  assert.equal(actual.length,e.steps.length,n+' source step groups');
  const m=actual[0].match(/^M(-?\d+) (-?\d+)/);
  assert.deepEqual(m&&[+m[1],+m[2]],e.start,n+' starting coordinate');
  assert.deepEqual(end(actual.at(-1)),e.end,n+' ending coordinate');
  assert.ok(actual.every(x=>(x.match(/M-?\d/g)||[]).length===1),n+' disjoint path');
 }
});
test('F2.6b numeral 1 is a single top-to-bottom teaching downstroke',()=>{
 assert.deepEqual(vectors('1'),['M37 17 V83']);
 assert.doesNotMatch(vectors('1').join(''),/H58|M22 36/);
});
test('F2.6b numeral 4 has down-right uninterrupted turn, lift, then down',()=>{
 assert.deepEqual(vectors('4'),['M17 17 V59 H61','M52 17 V83']);
 assert.equal(end(vectors('4')[0])[0],61);
 assert.equal(end(vectors('4')[0])[1],59);
 assert.equal(source.numerals['4'].firstDirection,'down');
});
test('F2.6b numeral 8 is one closed, uninterrupted S-shaped crossover',()=>{
 const d=vectors('8');
 assert.equal(d.length,1);
 assert.equal(d[0],'M37 17 C15 12 14 42 37 50 C64 56 67 80 40 83 C10 85 17 59 37 50 C61 39 59 18 37 17');
 assert.deepEqual(end(d[0]),[37,17]);
 assert.equal((d[0].match(/C/g)||[]).length,4);
 assert.equal((d[0].match(/M/g)||[]).length,1);
 assert.doesNotMatch(d[0],/Z;| Z /,'not two independent rings');
});
test('F2.6b A4 number category and saved practice records stay stable',()=>{
 assert.deepEqual(model.validate(),{groups:7,items:113});
 assert.deepEqual(model.groups.find(g=>g.key==='numbers').entries.map(x=>x.text),[...'0123456789']);
 const all=model.groups.reduce((n,g)=>n+g.entries.reduce((v,e)=>v+model.compose(e.text,g.kind).strokes.length,0),0);
 assert.equal(all,366);
 const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
 assert.match(app,/storagePrefix='zitie-foundations-f1:'/);
 assert.match(app,/localStorage\.setItem/);
 assert.match(app,/const W=1600/);
 assert.match(app,/cellWidth=W\/copies/);
 const doc=fs.readFileSync(path.join(__dirname,'../../docs/F26B_NUMBER_FORMATION.md'),'utf8');
 assert.match(doc,/2018/);
 assert.match(doc,/不.*国家.*标准/);
});
