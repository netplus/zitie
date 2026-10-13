'use strict';
/* F2 geometry baseline: shapes are engineering references, NOT reviewed
 * educational stroke-order models. Validate only measurable SVG geometry.
 */
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const source=require('./data.js');
const GRID={top:14,middle:47,baseline:83,bottom:117,height:132,advance:76};
const CELL_STROKE_TOLERANCE=1.4;
// Sample each cubic much more closely than the 113-entry visual smoke;
// overshoots should be detected but tiny curve/sampling deviations tolerated.
function bounds(d){
  const parts=d.match(/[MLHVCZ]|-?\d+(?:\.\d+)?/g)||[];
  const strip=d.replace(/\s+/g,'').replace(/(?:[MLHVCZ]|-?\d+(?:\.\d+)?)/g,'');
  if(!parts.length||strip)throw Error('Invalid or unsupported SVG path: '+d);
  let i=0,command='',x=0,y=0,startX=0,startY=0;
  let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;
  const point=(a,b)=>{
    if(!Number.isFinite(a)||!Number.isFinite(b))throw Error('Non-finite point');
    minX=Math.min(minX,a);minY=Math.min(minY,b);
    maxX=Math.max(maxX,a);maxY=Math.max(maxY,b);
  };
  const number=()=>{
    if(i>=parts.length||/^[MLHVCZ]$/.test(parts[i]))
      throw Error('Missing SVG coordinate: '+d);
    return Number(parts[i++]);
  };
  while(i<parts.length){
    if(/^[MLHVCZ]$/.test(parts[i]))command=parts[i++];
    if(command==='M'||command==='L'){
      x=number();y=number();point(x,y);
      if(command==='M'){startX=x;startY=y;command='L';}
    }else if(command==='H'){x=number();point(x,y);}
    else if(command==='V'){y=number();point(x,y);}
    else if(command==='C'){
      const x1=number(),y1=number(),x2=number(),y2=number(),
        x3=number(),y3=number(),oldX=x,oldY=y;
      for(let sample=0;sample<=100;sample++){
        const t=sample/100,u=1-t;
        point(u*u*u*oldX+3*u*u*t*x1+3*u*t*t*x2+t*t*t*x3,
              u*u*u*oldY+3*u*u*t*y1+3*u*t*t*y2+t*t*t*y3);
      }
      x=x3;y=y3;
    }else if(command==='Z'){
      x=startX;y=startY;point(x,y);command='';
    }else throw Error('Unsupported SVG command in '+d);
  }
  if(!Number.isFinite(minX)||!Number.isFinite(maxY))
    throw Error('Empty SVG shape');
  return {minX,minY,maxX,maxY};
}
function category(name){return source.groups.find(g=>g.key===name);}
test('F2 preserves every F1 bookmark and all 113 published storage identities',()=>{
  assert.equal(source.validate().items,113);
  assert.deepEqual(source.groups.map(g=>g.entries.length),[26,10,23,24,16,6,8]);
  const expected=[...Array(26)].map((_,i)=>'letters-'+i);
  assert.deepEqual(category('letters').entries.map(e=>e.id),expected);
  for(const group of source.groups){
    group.entries.forEach((entry,index)=>{
      assert.equal(entry.id,group.key+'-'+index);
      assert.ok(!entry.text.includes('<')&&!entry.text.includes('>'));
    });
  }
});
test('F2 samples ALL glyphs and keeps their vectors inside printable/canvas cells',()=>{
  let strokes=0;
  for(const group of source.groups){
    for(const entry of group.entries){
      const composition=source.compose(entry.text,group.kind);
      assert.equal(composition.height,GRID.height,entry.id);
      assert.ok(composition.width>=GRID.advance&&composition.width<1000,entry.id);
      for(const [index,stroke] of composition.strokes.entries()){
        const b=bounds(stroke.d);strokes++;
        const context=entry.id+' stroke#'+(index+1)+' '+stroke.part;
        assert.ok(b.minX>=-CELL_STROKE_TOLERANCE,context+' x starts off cell');
        assert.ok(b.maxX<=GRID.advance+CELL_STROKE_TOLERANCE,
          context+' x exceeds character advance');
        assert.ok(b.minY>=GRID.top-2.5,context+' exceeds top printable guide');
        assert.ok(b.maxY<=GRID.bottom+2.5,context+' exceeds bottom printable guide');
        assert.ok(stroke.x+b.minX>=-CELL_STROKE_TOLERANCE,context+' off left');
        assert.ok(stroke.x+b.maxX<=composition.width+CELL_STROKE_TOLERANCE,
          context+' off right');
      }
      const chars=source.parts(entry.text);
      const expectedWidth=Math.max(GRID.advance,chars.reduce(
        (sum,c)=>sum+(c.base===' '?33:76),0));
      assert.equal(composition.width,expectedWidth,entry.id+' width changed');
    }
  }
  assert.ok(strokes>400,'audit should cover many hundreds of real paths');
});
test('F2 distinguish 4 pinyin tones, mark-less i, and ü two dots in source geometry',()=>{
  const tones=category('tones');
  assert.equal(tones.entries.length,6);
  for(const entry of tones.entries){
    assert.equal(source.parts(entry.text).filter(x=>x.base!==' ').length,4);
    const m=source.compose(entry.text);
    assert.equal(m.strokes.filter(s=>s.part==='tone').length,4,entry.id);
  }
  const bareI=source.compose('i');
  for(const accented of ['ī','í','ǐ','ì'])
    assert.equal(source.compose(accented).strokes.length,bareI.strokes.length,
      accented+' should replace rather than stack over the i dot');
  for(const accented of ['ǖ','ǘ','ǚ','ǜ']){
    const strokes=source.compose(accented).strokes;
    assert.equal(strokes.filter(x=>x.part==='diaeresis').length,2,accented);
    assert.equal(strokes.filter(x=>x.part==='tone').length,1,accented);
  }
});
test('F2 printed worksheet keeps four parallel lines, square digit grids and A4 width',()=>{
  const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
  const css=fs.readFileSync(path.join(__dirname,'style.css'),'utf8');
  for(const n of GRID.top===14?[14,47,83,117]:[])assert.ok(app.includes(String(n)),
    'missing grid line '+n);
  assert.match(app,/const W=1600/);
  assert.match(app,/cellWidth=W\/copies/);
  assert.match(app,/width:64,height:66/);
  assert.match(css,/@page\{size:A4 portrait/);
  assert.match(css,/\.printLine\{width:100%;height:15mm/);
  assert.doesNotMatch(app,/(?:XMLHttpRequest|sendBeacon|fetch\s*\()/);
});
