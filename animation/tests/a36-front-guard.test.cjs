'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const B=require('../brush-union.js');
const Front=require('../ink-front-guard.js');
const root=path.resolve(__dirname,'../..');
const raw=fs.readFileSync(path.join(root,'animation/book-pack.js'),'utf8');
assert.ok(raw.startsWith('window.ZITIE_BOOK_PACK = '));
const pack=JSON.parse(raw.split(' = ',2)[1].replace(/;\s*$/,''));
const nearest=(stations,pt)=>{
  let best=Infinity,owner=-1;
  for(let i=0;i<stations.length;i++){
    const s=stations[i],dist=(s.x-pt[0])**2+(s.y-pt[1])**2;
    if(dist<best-1e-8){best=dist;owner=i;}
  }
  return owner;
};
const pointInside=(poly,pt)=>{
  let sign=0;
  for(let i=0;i<poly.length;i++){
    const a=poly[i],b=poly[(i+1)%poly.length];
    const cross=(b[0]-a[0])*(pt[1]-a[1])-(b[1]-a[1])*(pt[0]-a[0]);
    if(Math.abs(cross)<.0001)continue;
    const x=Math.sign(cross);
    if(sign&&x!==sign)return false;
    sign=x;
  }
  return true;
};
test('201 PDF glyphs, all 1045 strokes have monotone source-front Voronoi partitions',()=>{
  assert.equal(pack.glyphs.length,201);
  assert.equal(pack.publication.version,'0.5.1');
  assert.equal(pack.publication.pages,299);
  const before=JSON.stringify(pack.glyphs);
  let strokes=0,stationsCount=0,empty=0,maxGap=0,leads=0;
  for(const glyph of pack.glyphs){
    for(const stroke of glyph.strokes){
      strokes++;
      const stations=B.sampleMedian(stroke.median,4);
      const guard=Front.buildCells({stations});
      assert.equal(guard.kind,'source_arc_voronoi_progress_gate');
      assert.equal(guard.sourceMedianModified,false);
      assert.equal(guard.sourceOutlineModified,false);
      assert.equal(guard.nibClockModified,false);
      assert.equal(guard.cells.length,stations.length);
      assert.ok(guard.maxStationGap<=4.00001);
      assert.equal(Front.visibleCount(guard,0),0);
      assert.equal(Front.visibleCount(guard,stations.at(-1).distance),stations.length);
      const L=stations.at(-1).distance;
      for(let k=0;k<stations.length;k++){
        const cell=guard.cells[k];
        if(!cell.outline){empty++;continue;}
        assert.ok(cell.outline.startsWith('M ')&&cell.outline.endsWith(' Z'));
        assert.equal(cell.distance,stations[k].distance);
        if(k%9===0){
          const polygon=cell.outline.slice(2,-2).split(' L ').map(s=>s.split(' ').map(Number));
          assert.ok(pointInside(polygon,[stations[k].x,stations[k].y]),
            'Front guard lost station '+glyph.character+' '+stroke.index+' '+k);
        }
      }
      for(const p of [.012,.04,.08,.15,.28,.42,.58,.73,.87,.96]){
        const d=L*p,visible=Front.visibleCount(guard,d);
        assert.ok(visible>0&&visible<stations.length);
        for(const ahead of [12,20,32,50,96,144,210]){
          if(d+ahead>=L)continue;
          const point=B.pointAtDistance({stations,length:L},d+ahead);
          const owner=nearest(stations,point);
          assert.ok(owner>=visible,
            'Premature source-front pigment '+glyph.character+' stroke '+
              stroke.index+' at '+p+' lead '+ahead+
              ' owner '+owner+' visible '+visible);
          leads++;
        }
      }
      maxGap=Math.max(maxGap,guard.maxStationGap);
      stationsCount+=stations.length;
    }
  }
  assert.equal(strokes,1045);
  assert.ok(stationsCount>100000);
  assert.equal(empty,0);
  assert.ok(leads>25000);
  assert.ok(maxGap<=4.00001);
  assert.equal(JSON.stringify(pack.glyphs),before);
});
test('frontier guard fail-closed invalid station geometry and safe backwards seek',()=>{
  assert.throws(()=>Front.buildCells(null),/input/);
  assert.throws(()=>Front.buildCells({stations:[]}),/input/);
  assert.throws(()=>Front.buildCells({stations:[
    {x:1,y:2,distance:0},{x:5,y:2,distance:0}]}),/station/);
  const stations=B.sampleMedian([[0,0],[350,0],[350,-350]],4);
  const guard=Front.buildCells({stations});
  assert.equal(Front.visibleCount(guard,guard.cells.at(-1).distance),guard.cells.length);
  assert.ok(Front.visibleCount(guard,guard.cells[32].distance)>32);
  assert.equal(Front.visibleCount(guard,0),0);
  assert.throws(()=>Front.visibleCount(guard,NaN),/visibility/);
  assert.throws(()=>Front.buildCells({stations},{bounds:[0,0,-1,3]}),/input/);
});
