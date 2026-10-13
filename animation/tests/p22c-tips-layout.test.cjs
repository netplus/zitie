'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(root,'animation/book.html'),'utf8');
const ui=fs.readFileSync(path.join(root,'animation/book-ui.js'),'utf8');
const css=fs.readFileSync(path.join(root,'animation/practice/practice.css'),'utf8');
const bridge=fs.readFileSync(path.join(root,'animation/practice/practice-bridge.js'),'utf8');

test('P2.2c shows exact source writing tips beside live stroke progress and retains the full PDF hints',()=>{
  for(const id of ['writingTipLead','writingTipJump','writingTipsDetail','tipText',
                   'practiceBookTip','practiceStrokeTitle','practiceStrokeHint',
                   'practiceOrderResult']){
    assert.equal([...html.matchAll(new RegExp('id="'+id+'"','g'))].length,1,
      'Exactly one source-hint/result ID: '+id);
  }
  const progress=html.indexOf('class="progressHead"');
  const tip=html.indexOf('class="writingTipHighlight"');
  const controls=html.indexOf('class="controls"');
  assert.ok(progress<tip&&tip<controls,
    'Published tip must be visible by playback controls without scrolling past them');
  assert.match(html,/href="#writingTipsDetail"/);
  assert.match(html,/<h2>02 字帖原有书写提示<\/h2>/);
  assert.match(ui,/\$\('writingTipLead'\)\.textContent=g\.tips\[0\]/);
  assert.match(ui,/const notes=\[\.\.\.g\.tips,'写完检查：'\+g\.check\]/);
  assert.match(ui,/\$\('tipText'\)\.append\(p\)/);
});

test('P2.2c moves the current practice hint and completed verdict ABOVE actual blue touch canvas',()=>{
  const card=html.indexOf('class="practicePaperCard"');
  const guide=html.indexOf('class="practiceActiveGuide"',card);
  const title=html.indexOf('id="practiceStrokeTitle"',card);
  const source=html.indexOf('id="practiceBookTip"',card);
  const hint=html.indexOf('id="practiceStrokeHint"',card);
  const result=html.indexOf('id="practiceOrderResult"',card);
  const board=html.indexOf('id="practiceBoard"',card);
  const canvas=html.indexOf('id="practiceInk"',card);
  assert.ok([guide,title,source,hint,result,board,canvas].every(x=>x>card));
  assert.ok(guide<title&&title<source&&source<hint&&hint<result&&result<board&&board<canvas);
  assert.match(bridge,/\$\('practiceBookTip'\)\.textContent=bookTips\[0\]/);
  assert.match(css,/\.practiceActiveGuide/);
  assert.match(css,/\.practiceBoard,\.practiceActiveGuide/);
  assert.doesNotMatch(bridge,/\$\('practiceClearPrompt'\)/,
    'One-tap restart must never regain a confirmation modal');
});
