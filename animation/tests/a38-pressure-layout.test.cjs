'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(root,'animation/book.html'),'utf8');
const js=fs.readFileSync(path.join(root,'animation/book-ui.js'),'utf8');
test('one pressure controller stays physically attached to handwriting stage',()=>{
 const stage=html.indexOf('<div class="writingStage"');
 const paper=html.indexOf('<div class="paper">',stage);
 const svg=html.indexOf('id="paperSvg"',paper);
 const panel=html.indexOf('<section class="pressureBox"',svg);
 const closing=html.indexOf('<!-- A3.8 handwriting stage end -->',panel);
 const controls=html.indexOf('id="speedButtons"',closing);
 assert.ok(stage>0&&stage<paper&&paper<svg&&svg<panel&&panel<closing&&closing<controls,
  'Pressure panel must be inside handwriting stage, not after playback controls');
 for(const id of ['writingStage','paperSvg','pressureStyleOptions',
                  'pressureDetails','pressureCurve','pressureValue']){
  assert.equal([...html.matchAll(new RegExp('id="'+id+'"','g'))].length,1,
   'No duplicate pressure control '+id);
 }
});
test('desktop side-by-side and narrow-screen above/sticky layout are explicit',()=>{
 assert.match(html,/\.writingStage\{display:grid;grid-template-columns:minmax\(0,1fr\) 220px/);
 assert.match(html,/\.pressureBox\{position:sticky;top:10px/);
 assert.match(html,/@media\(max-width:1150px\)\{/);
 assert.match(html,/\.pressureBox\{order:-1;width:100%;top:7px/);
 assert.match(html,/@media\(max-width:510px\)/);
 assert.match(html,/\.main\{overflow:visible\}/);
 assert.match(html,/role="group" aria-labelledby="pressureStyleLabel"/);
});
test('layout did not replace source-immutable A1.6 pressure or A3.6 renderer',()=>{
 assert.match(js,/new window\.ZitiePressureStyle\.StyleController\(\)/);
 assert.match(js,/frontGuard:true/);
 assert.match(js,/const force=penStyle\.apply\(player,s\)/);
 assert.match(js,/getPressureStyle:\(\)=>penStyle\.mode/);
 assert.match(html,/src="\.\/pressure-style\.js"/);
 assert.match(html,/src="\.\/ink-front-guard\.js"/);
 for(const mode of ['stable','simulated'])
  assert.match(html,new RegExp('data-pen-style="'+mode+'"'));
});
