'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const Onset=require('../experiments/source-onset.js');
const Brush=require('../brush-union.js');
global.window=global;
require('../samples.js');
const glyphs=global.ZITIE_SAMPLES.glyphs;
delete global.window;

function rectangle(){
  const median=[[100,100],[210,100]];
  const source={median};
  const contains=(x,y)=>x>=75&&x<=230&&y>=67&&y<=139;
  const profile=Brush.makeProfile(median,contains,{spacing:5});
  return {source,profile,contains};
}

test('source onset probes the original contour support, not the interior median vertex',()=>{
  const {source,profile,contains}=rectangle();
  const cap=Onset.makeStartCap(source,profile,contains);
  assert.equal(cap.kind,'source_contour_probed_directional_contact');
  assert.deepEqual(cap.sourceMedianStart,[100,100]);
  assert.deepEqual(cap.tangent,[1,0]);
  assert.ok(cap.sourceStart<-22,'a true beginning lies 25 units before the centerline first point');
  assert.ok(cap.sourceStart>-35);
  assert.ok(cap.hitSamples>0);
  assert.ok(contains(...cap.sourceStartPoint));
  assert.equal(cap.sourceDirectionModified,false);
});

test('directional sweep leaves empty mask at zero and grows from actual support toward the source tangent',()=>{
  const {source,profile,contains}=rectangle();
  const cap=Onset.makeStartCap(source,profile,contains);
  const atZero=Onset.sweepAt(cap,0,0);
  assert.equal(atZero.d,'');
  assert.equal(atZero.contact,0);
  let last=-Infinity;
  for(let i=0;i<=1000;i++){
    const t=i/1000;
    const d=Math.min(cap.capLength,110*t);
    const state=Onset.sweepAt(cap,d,t);
    assert.ok(state.front>=last-1e-6,'source projected contact front moved backwards');
    assert.ok(state.front<=d+1e-6,'source contact revealed beyond current median travel');
    assert.ok(state.contact>=0&&state.contact<=1);
    assert.ok(state.tip.every(Number.isFinite));
    if(t>0.002)assert.ok(state.d.startsWith('M '));
    last=state.front;
  }
  const end=Onset.sweepAt(cap,cap.capLength,1);
  assert.ok(Math.abs(end.front-cap.capLength)<1e-6);
  assert.deepEqual(end.tip,source.median[0],
    'pen guide arrives at the source median after initial contact settles');
});

test('source onset fails closed if fill geometry APIs are absent',()=>{
  const {source,profile}=rectangle();
  assert.equal(Onset.makeStartCap(source,profile,null),null);
  assert.throws(()=>Onset.makeStartCap({median:[[1,1]]},profile,()=>true),
    /Invalid source start-cap geometry/);
  assert.throws(()=>Onset.makeStartCap(source,profile,()=>true,
    {landingTime:.4}),/Invalid source start contact settings/);
  assert.throws(()=>Onset.sweepAt(null,.5,.2),/Invalid directional/);
});

test('source samples and canonical medians remain byte-identical, no extra strokes',()=>{
  const glyph=glyphs.find(g=>g.character==='一');
  const original=JSON.stringify(glyph);
  const stroke=glyph.strokes[0];
  const contains=(x,y)=>x>=105&&x<=220&&y>=320&&y<=450;
  const profile=Brush.makeProfile(stroke.median,contains);
  const cap=Onset.makeStartCap(stroke,profile,contains);
  assert.ok(cap&&cap.hitSamples>10);
  assert.deepEqual(cap.sourceMedianStart,stroke.median[0]);
  assert.equal(JSON.stringify(glyph),original);
  assert.equal(glyph.strokes.length,1);
});