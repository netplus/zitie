'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(root,'animation/book.html'),'utf8');
const code=fs.readFileSync(path.join(root,'animation/book-ui.js'),'utf8');
const css=fs.readFileSync(path.join(root,'animation/main-layout.css'),'utf8');
test('P2.2f keeps first book tip visible and one supplementary semantic block',()=>{
 for(const id of ['writingTipJump','writingTipLead','writingTipsDetail','tipText',
                  'pressureStudyHeading','pressureStudyTip','pressureStudyCheck'])
  assert.equal([...html.matchAll(new RegExp('id="'+id+'"','g'))].length,1,id);
 assert.doesNotMatch(html,/02 字帖原有书写提示/);
 assert.match(html,/<h2>补充要点 · 写完检查<\/h2>/);
 assert.match(html,/<h2>逐笔示范 · 点按笔画跳转<\/h2>/);
 assert.doesNotMatch(html,/class="pressureStudyLink"/);
 assert.match(code,/const notes=\[\.\.\.g\.tips\.slice\(1\),'写完检查：'\+g\.check\]/);
 assert.match(code,/\$\('writingTipLead'\)\.textContent=g\.tips\[0\]/);
 assert.match(code,/\$\('pressureStudyTip'\)\.textContent=g\.tips\.slice\(1\)\.join\('；'\)/);
 assert.match(code,/\$\('pressureStudyCheck'\)\.textContent=g\.check/);
});
test('P2.2f links to only the visible source complement and does not clip stable hints',()=>{
 assert.match(code,/window\.matchMedia\('\(max-width:720px\), \(max-height:699px\)'\)/);
 assert.match(code,/narrow\|\|penStyle\.mode==='simulated'\?'#writingTipsDetail':'#pressureStudyHeading'/);
 assert.match(code,/window\.addEventListener\('resize',updateTipTarget\)/);
 assert.match(code,/if\(player\.timeline\)player\.render\(\);\s*updateTipTarget\(\)/);
 assert.match(css,/#writingTipsDetail\{display:none/);
 assert.match(css,/\.writingStage:has\(\.pressureDetails:not\(\[hidden\]\)\)>\.pressureStudy\{display:none\}/);
 assert.match(css,/\.main:has\(\.pressureDetails:not\(\[hidden\]\)\) #writingTipsDetail\{display:block\}/);
 assert.match(css,/@media\(max-width:720px\), \(max-height:699px\)\{/);
 assert.match(css,/\.pressureStudy\{display:none\}\s*#writingTipsDetail\{display:block\}/);
 assert.doesNotMatch(css,/\.pressureStudyCheck\{display:none\}/);
 assert.doesNotMatch(css,/-webkit-line-clamp:3/);
});
