'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(ROOT,'animation/book.html'),'utf8');
const ui=fs.readFileSync(path.join(ROOT,'animation/book-ui.js'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'animation/main-layout.css'),'utf8');
test('P2.2e preserves original sticky pressure and adds one read-only companion',()=>{
 const stage=html.indexOf('class="writingStage"');
 const paper=html.indexOf('class="paper" role="button"',stage);
 const panel=html.indexOf('class="pressureBox"',paper);
 const guide=html.indexOf('class="pressureStudy"',panel);
 const end=html.indexOf('<!-- A3.8 handwriting stage end -->',guide);
 assert.ok(stage>=0&&paper>stage&&panel>paper&&guide>panel&&end>guide);
 for(const id of ['pressureStyleOptions','pressureDetails','pressureCurve',
    'pressureValue','pressureStudyHeading','pressureStudyTip','pressureStudyCheck',
    'paperSvg','writingTipLead','tipText','practiceOverlay'])
  assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1,id);
 assert.doesNotMatch(html,/class="pressureStudyLink"/,'Remove redundant full-tip link');
 assert.match(css,/\.writingStage>\.pressureBox\{grid-column:2;grid-row:1\}/);
 assert.match(css,/\.writingStage>\.pressureStudy\{grid-column:2;grid-row:2/);
 assert.match(css,/\.writingStage\{grid-template-rows:max-content minmax\(0,1fr\);height:var\(--board-size\)\}/);
 assert.match(css,/@media\(max-width:720px\), \(max-height:699px\)\{/);
});
test('P2.2e displays ONLY immutable second source tip and original completion check',()=>{
 assert.match(ui,/\$\('pressureStudyTip'\)\.textContent=g\.tips\.slice\(1\)\.join\('；'\)/);
 assert.match(ui,/\$\('pressureStudyCheck'\)\.textContent=g\.check/);
 assert.match(ui,/\$\('writingTipLead'\)\.textContent=g\.tips\[0\]/);
 assert.match(ui,/const notes=\[\.\.\.g\.tips\.slice\(1\),'写完检查：'\+g\.check\]/);
 assert.match(ui,/new window\.ZitiePressureStyle\.StyleController\(\)/);
 assert.match(ui,/frontGuard:true/);
 assert.doesNotMatch(css,/@font-face|fonts\.googleapis|unpkg\.com|cdn\./);
});
