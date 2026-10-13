'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const model=require('./data.js');
const qa=require('./legibility-audit.cjs');
test('F2.6a every child-facing Latin/number glyph gets a measurable report',()=>{
 const report=qa.summary();
 assert.match(report.scope,/not teacher-certified/);
 assert.deepEqual(report.catalogItems,113);
 assert.deepEqual(report.guides,{top:14,middle:47,baseline:83,bottom:117,advance:76});
 assert.equal(report.letters.length,52);
 assert.equal(report.digits.length,10);
 assert.deepEqual(report.letters.map(x=>x.letter),
   [...'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz']);
 assert.deepEqual(report.digits.map(x=>x.letter),[...'0123456789']);
 for(const row of report.letters.concat(report.digits)){
   assert.ok(row.bounds.left>=0&&row.bounds.right<=77,row.letter+' horizontal glyph bound');
   assert.ok(row.bounds.top>=11&&row.bounds.bottom<=119,row.letter+' vertical glyph bound');
   assert.ok(row.contacts>=1&&row.inkWidth>=0);
   assert.ok(Number.isFinite(row.bodyBaselineOvershoot));
 }
 assert.deepEqual(model.validate(),{groups:7,items:113});
});
test('F2.6a known irregular ordinary-lowercase s must be visibly flagged, not certified',()=>{
 const s=qa.metrics('s'),e=qa.metrics('e'),u=qa.metrics('u');
 assert.ok(s.bounds.bottom>87&&s.bodyBaselineOvershoot>4,'s is presently below baseline');
 assert.ok(s.warnings.includes('body-exceeds-baseline-review'));
 assert.ok(e.bodyBaselineOvershoot<3&&u.bodyBaselineOvershoot<3);
 assert.ok(!e.warnings.includes('body-exceeds-baseline-review'));
});
test('F2.6a fixed 76-unit spacing is not justified for narrow i/l versus m/w',()=>{
 const i=qa.metrics('i'),l=qa.metrics('l'),m=qa.metrics('m'),w=qa.metrics('w');
 assert.equal(i.advance,76);
 assert.equal(l.advance,76);
 assert.equal(m.advance,76);
 assert.equal(w.advance,76);
 assert.equal(i.inkWidth,0);
 assert.equal(l.inkWidth,0);
 assert.ok(m.inkWidth>=50&&w.inkWidth>=50);
 assert.ok(i.warnings.includes('narrow-glyph-fixed-advance-spacing-review'));
 assert.ok(l.warnings.includes('narrow-glyph-fixed-advance-spacing-review'));
 // Entire spacing model still maps two glyphs to 2×76; a future optical
 // spacing experiment must include saved-trace versioned coordinates.
 assert.equal(model.compose('ii').width,152);
});
test('F2.6a detects 1/4/8 mismatch with selected official LWT 2018 Number Stories p4',()=>{
 const one=qa.metrics('1'),four=qa.metrics('4'),eight=qa.metrics('8');
 assert.ok(one.warnings.includes('digit-1-extra-foot-conflicts-with-LWT-p4'));
 assert.ok(four.warnings.includes('digit-4-first-pen-travels-up-conflicts-with-LWT-p4'));
 assert.ok(eight.warnings.includes('digit-8-two-rings-conflicts-with-LWT-p4-one-loop'));
 assert.equal(eight.contacts,2);
 const evidence=fs.readFileSync(
   path.join(__dirname,'../../docs/F26_CHILD_HANDWRITING_LEGIBILITY.md'),'utf8');
 assert.match(evidence,/LWT 官方 PDF p4/);
 assert.match(evidence,/不是国家标准/);
});
test('F2.6a report must expose known problems and not rewrite student writing source',()=>{
 const report=qa.summary();
 const flags=Object.fromEntries(report.flagged.map(f=>[f.letter,f.notes]));
 assert.deepEqual(Object.keys(flags),['i','l','s','1','4','8']);
 const data=fs.readFileSync(path.join(__dirname,'data.js'),'utf8');
 assert.match(data,/const initialValues=/);
 const application=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
 assert.match(application,/storagePrefix='zitie-foundations-f1:'/);
 assert.match(application,/localStorage\.setItem/);
 assert.doesNotMatch(
   fs.readFileSync(path.join(__dirname,'legibility-audit.cjs'),'utf8'),
   /localStorage|indexedDB|navigator\.sendBeacon|fetch\s*\(/);
});
