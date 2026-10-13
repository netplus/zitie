'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..');
const ui=fs.readFileSync(path.join(root,'animation/book-ui.js'),'utf8');
const html=fs.readFileSync(path.join(root,'animation/book.html'),'utf8');
test('P2.2g sets 0.8x simulated pressure ONLY on the production book',()=>{
 assert.match(ui,/const DEFAULT_RATE=0\.8/);
 assert.match(ui,/const DEFAULT_PEN_STYLE='simulated'/);
 assert.match(ui,/speed:DEFAULT_RATE,lastFrame:null/);
 assert.match(ui,/setPressureStyle\(DEFAULT_PEN_STYLE\);\s*renderFilters\(\)/);
 assert.match(ui,/player\.setSpeed\(state\.speed\)/);
 assert.match(ui,/if\(!\[\.5,\.8,1,1\.5,2\]\.includes\(value\)\)/);
 assert.match(html,/data-pen-style="stable"\s+aria-pressed="false"/);
 assert.match(html,/data-pen-style="simulated"\s+aria-pressed="true"/);
 assert.match(html,/data-speed="0\.8" aria-pressed="true">0\.8×/);
 assert.match(html,/data-speed="1" aria-pressed="false">1×/);
 assert.match(html,/class="pressureDetails" id="pressureDetails">/);
 assert.doesNotMatch(html,/id="pressureDetails" hidden/);
 assert.match(html,/合成演示，非实测笔压/);
});
test('P2.2g keeps all previous alternative rates and both pressure styles',()=>{
 const speeds=[...html.matchAll(/data-speed="([0-9.]+)" aria-pressed="(true|false)"/g)]
   .map(m=>[Number(m[1]),m[2]]);
 assert.deepEqual(speeds,[[.5,'false'],[.8,'true'],[1,'false'],
   [1.5,'false'],[2,'false']]);
 assert.equal((html.match(/data-pen-style=/g)||[]).length,2);
 const player=fs.readFileSync(path.join(root,'animation/player.js'),'utf8');
 const pressure=fs.readFileSync(path.join(root,'animation/pressure-style.js'),'utf8');
 assert.match(player,/this\.speed = 1;/);
 assert.match(pressure,/this\.mode='stable';/);
});
