'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(ROOT,'animation/book.html'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'animation/main-layout.css'),'utf8');
const logic=fs.readFileSync(path.join(ROOT,'animation/book-ui.js'),'utf8');
const pages=fs.readFileSync(path.join(ROOT,'.github/workflows/animation-pages.yml'),'utf8');
test('P2.2d: main lesson and library are visible, accessible, and source-preserving',()=>{
 for(const id of ['lessonHero','practiceLaunch','prevChar','nextChar','characterLibrary',
  'paperSvg','pressureStyleOptions','pressureCurve','writingTipLead','writingTipJump',
  'writingTipsDetail','tipText','steps','pdfLink','search','filters','tiles']){
   assert.equal([...html.matchAll(new RegExp('id="'+id+'"','g'))].length,1,
     'unique main classroom element '+id);
 }
 assert.match(html,/<details class="resourceNav"><summary>更多资源<\/summary>/);
 for(const link of ['./experiments/brush-motion-lab.html','./index.html'])
  assert.ok(html.includes('href="'+link+'"'),link);
 assert.match(html,/href="#characterLibrary"/);
 assert.match(html,/href="\.\/main-layout\.css"/);
 assert.match(html,/开始临摹/);
 assert.match(html,/id="practiceOverlay"/);
 assert.match(css,/\.writingTipHighlight\{grid-column:1\/-1;grid-row:2/);
 assert.match(css,/#writingTipLead\{[^}]*-webkit-line-clamp:2/);
 assert.match(css,/\.controls\{display:grid/);
 assert.match(css,/\.filter\{display:flex;flex-wrap:nowrap/);
 assert.match(css,/@media\(max-width:510px\)/);
 assert.match(css,/\.pager \.practiceLaunchText\{display:inline\}/);
 assert.match(pages,/cp animation\/index\.html animation\/book\.html animation\/book-ui\.js animation\/main-layout\.css/);
 assert.match(pages,/test -s _site\/animation\/main-layout\.css/);
});
test('P2.2d: book glyph source/tip/scroll navigation is the original data model',()=>{
 assert.match(logic,/\$\('writingTipLead'\)\.textContent=g\.tips\[0\]/);
 assert.match(logic,/const notes=\[\.\.\.g\.tips\.slice\(1\),'写完检查：'\+g\.check\]/);
 assert.match(logic,/btn\.addEventListener\('click',\(\)=>\{\s*selectGlyph\(g\);/);
 assert.match(logic,/\$\('lessonHero'\)\.scrollIntoView\(\{block:'start',behavior:'auto'\}\)/);
 assert.match(logic,/window\.history\.replaceState\(null/);
 assert.ok(!html.includes('id="practiceClearPrompt"'),
   'Practice restart confirmation is intentionally retired');
 for(const forbidden of ['font-face','googleapis.com','unpkg.com','cdn.'])
  assert.ok(!css.includes(forbidden),'No external stylesheet dependencies');
});
