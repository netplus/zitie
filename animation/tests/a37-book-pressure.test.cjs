'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const style=require('../pressure-style.js');
const force=require('../experiments/pressure-model.js');
const gesture=require('../experiments/gesture-data.js');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const js=read('animation/book-ui.js'),html=read('animation/book.html');
const packPath=fs.existsSync(path.join(root,'build/a3/book-pack.js'))?
  'build/a3/book-pack.js':'animation/book-pack.js';
const raw=read(packPath);
assert.ok(raw.startsWith('window.ZITIE_BOOK_PACK = '),
  'Pack must come from formal PDF source generation');
const pack=JSON.parse(raw.slice('window.ZITIE_BOOK_PACK = '.length).trim().replace(/;$/,''));
test('production 201-glyph book loads the original A1.6 force model with correct dependency order',()=>{
  const ordered=['./experiments/gesture-data.js',
    './experiments/pressure-model.js','./pressure-style.js','./book-ui.js'];
  let pos=-1;
  for(const src of ordered){
    const i=html.indexOf('src="'+src+'"');
    assert.ok(i>pos,'Missing/misordered pressure dependency '+src);
    pos=i;
  }
  assert.match(html,/笔压风格/);
  assert.match(html,/data-pen-style="stable"\s+aria-pressed="false"/);
  assert.match(html,/data-pen-style="simulated"\s+aria-pressed="true"/);
  assert.match(html,/data-speed="0\.8"\s+aria-pressed="true"/);
  assert.match(html,/data-speed="1"\s+aria-pressed="false"/);
  assert.match(js,/const DEFAULT_RATE=0\.8/);
  assert.match(js,/const DEFAULT_PEN_STYLE='simulated'/);
  assert.match(js,/setPressureStyle\(DEFAULT_PEN_STYLE\)/);
  for(const id of ['pressureStyleOptions','pressureDetails','pressureCurve',
                    'pressureValue','pressureFill','pressurePhase']){
    assert.match(html,new RegExp('id="'+id+'"'));
  }
  assert.match(js,/new window\.ZitiePressureStyle\.StyleController\(\)/);
  assert.match(js,/const force=penStyle\.apply\(player,s\);/);
  assert.match(js,/player\.render\(\)/);
  assert.match(js,/getPressureStyle:\(\)=>penStyle\.mode/);
  assert.equal(style.styles.join('|'),'stable|simulated');
});

test('original A1.6 synthetic pressure plan supports all 201 / 1045 released PDF source strokes without source mutation',()=>{
  assert.equal(pack.glyphs.length,201);
  assert.equal(pack.publication.pages,299);
  const original=JSON.stringify(pack.glyphs);
  const controller=new style.StyleController();
  assert.equal(controller.mode,'stable');
  assert.equal(controller.setMode('simulated'),'simulated');
  let strokes=0,unreviewed=0,planned=0,nonzero=0;
  for(const glyph of pack.glyphs){
    controller.prepare(glyph);
    assert.equal(controller.plans.length,glyph.strokes.length);
    assert.equal(controller.curves.length,glyph.strokes.length);
    for(let i=0;i<glyph.strokes.length;i++){
      const s=glyph.strokes[i],p=controller.plans[i];
      assert.equal(p.kind,'synthetic_pressure_independent_of_velocity_unfitted');
      assert.equal(p.measured,false);
      assert.equal(p.calibratedToDataset,false);
      assert.equal(p.sourceMedianModified,false);
      assert.equal(p.sourceInkModified,false);
      assert.equal(p.sourceStrokeCountModified,false);
      assert.ok(p.length>.01);
      const points=controller.curves[i];
      assert.equal(points.length,97);
      assert.equal(points[0].pressure,0);
      assert.equal(points.at(-1).pressure,0);
      assert.ok(points.every(v=>v.pressure>=0&&v.pressure<=1&&
        Number.isFinite(v.pressure)&&v.measured===false));
      if(points.some(v=>v.pressure>.06))nonzero++;
      if(s.name_status!=='reviewed'){
        const g=gesture.lookup(glyph,i);
        assert.equal(g.kind,'generic',
          'Do not invent semantic gestures for fine-name-restricted sources');
        unreviewed++;
      }
      planned++;strokes++;
    }
  }
  assert.equal(strokes,1045);
  assert.equal(planned,1045);
  assert.ok(nonzero>1000);
  assert.ok(unreviewed>30);
  assert.equal(JSON.stringify(pack.glyphs),original);
  assert.equal(controller.setMode('stable'),'stable');
  assert.throws(()=>controller.setMode('measured'),/Unsupported/);
});

test('pressure geometry is independent from hardpen or PDF source ink',()=>{
  for(const x of [0,.1,.2,.5,.85,1]){
    const a=style.markerGeometry(x,'brush');
    assert.ok(a.radius>=7&&a.ringRadius>a.radius);
    assert.equal(a.ringFill,'none');
  }
  assert.throws(()=>style.markerGeometry(-.1),/Invalid/);
  assert.throws(()=>style.markerGeometry(1.1),/Invalid/);
  assert.equal(force.pressureAt(
    force.makePlan(pack.glyphs[0].strokes[0]),0),0);
});
