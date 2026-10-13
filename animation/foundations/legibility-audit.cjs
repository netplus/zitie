'use strict';
/* F2.6a – MEASURE, do not auto-certify, childish handwriting form.
 * Source material: docs/F26_CHILD_HANDWRITING_LEGIBILITY.md.
 * These project-specific tolerances are not official/teacher standards.
 */
const model=require('./data.js');
const GRID=Object.freeze({top:14,middle:47,baseline:83,bottom:117,advance:76});
function pathBounds(d){
  const tokens=d.match(/[MLHVCZ]|-?\d+(?:\.\d+)?/g)||[];
  const leftovers=d.replace(/\s+/g,'').replace(/(?:[MLHVCZ]|-?\d+(?:\.\d+)?)/g,'');
  if(leftovers||!tokens.length)throw Error('Unsupported SVG path');
  let index=0,cmd='',x=0,y=0,firstX=0,firstY=0;
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  const plot=(a,b)=>{
    if(!Number.isFinite(a)||!Number.isFinite(b))throw Error('Non-finite path point');
    minX=Math.min(minX,a);maxX=Math.max(maxX,a);
    minY=Math.min(minY,b);maxY=Math.max(maxY,b);
  };
  const number=()=>{
    if(index>=tokens.length||/^[MLHVCZ]$/.test(tokens[index]))
      throw Error('Missing SVG coordinate');
    return Number(tokens[index++]);
  };
  while(index<tokens.length){
    if(/^[MLHVCZ]$/.test(tokens[index]))cmd=tokens[index++];
    if(cmd==='M'||cmd==='L'){
      x=number();y=number();plot(x,y);
      if(cmd==='M'){firstX=x;firstY=y;cmd='L';}
    }else if(cmd==='H'){x=number();plot(x,y);}
    else if(cmd==='V'){y=number();plot(x,y);}
    else if(cmd==='C'){
      const x1=number(),y1=number(),x2=number(),y2=number(),
        x3=number(),y3=number(),oldX=x,oldY=y;
      for(let step=0;step<=200;step++){
        const t=step/200,u=1-t;
        plot(u*u*u*oldX+3*u*u*t*x1+3*u*t*t*x2+t*t*t*x3,
             u*u*u*oldY+3*u*u*t*y1+3*u*t*t*y2+t*t*t*y3);
      }
      x=x3;y=y3;
    }else if(cmd==='Z'){x=firstX;y=firstY;plot(x,y);cmd='';}
    else throw Error('Unsupported path command: '+cmd);
  }
  return {minX,maxX,minY,maxY};
}
const round=n=>Math.round(n*100)/100;
function metrics(ch,kind='lines'){
  if(!/^[a-zA-Z0-9]$/.test(ch))throw Error('Exactly one Latin letter or digit required');
  if(/[0-9]/.test(ch))kind='squares';
  const p=model.compose(ch,kind);
  const vectors=p.strokes.map(s=>pathBounds(s.d));
  const left=Math.min(...vectors.map(v=>v.minX));
  const right=Math.max(...vectors.map(v=>v.maxX));
  const top=Math.min(...vectors.map(v=>v.minY));
  const bottom=Math.max(...vectors.map(v=>v.maxY));
  const lowercase=ch>='a'&&ch<='z';
  const digit=ch>='0'&&ch<='9';
  const descender=/[gjpqy]/.test(ch)&&lowercase;
  const ordinaryLower=lowercase&&!descender;
  // Optical curve overshoot is normal. 3 SVG units is an in-house review
  // trigger for one 34–36-unit x-height: not an absolute accept/reject rule.
  const overshoot=ordinaryLower?Math.max(0,bottom-GRID.baseline):0;
  const warnings=[];
  if(ordinaryLower&&overshoot>3)
    warnings.push('body-exceeds-baseline-review');
  if((ch==='i'||ch==='l')&&right-left<5)
    warnings.push('narrow-glyph-fixed-advance-spacing-review');
  if(digit&&ch==='1'&&p.strokes.some(s=>/M25 83 H58/.test(s.d)))
    warnings.push('digit-1-extra-foot-conflicts-with-LWT-p4');
  if(digit&&ch==='4'&&/^M52 83 V17/.test(p.strokes[0]?.d||''))
    warnings.push('digit-4-first-pen-travels-up-conflicts-with-LWT-p4');
  if(digit&&ch==='8'&&p.strokes.length===2)
    warnings.push('digit-8-two-rings-conflicts-with-LWT-p4-one-loop');
  return Object.freeze({
    letter:ch,kind,contacts:p.strokes.length,
    advance:GRID.advance,
    bounds:{left:round(left),right:round(right),top:round(top),bottom:round(bottom)},
    inkWidth:round(right-left),
    bodyBaselineOvershoot:round(overshoot),
    warnings
  });
}
function summary(){
  const letters=[...'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'].map(ch=>metrics(ch));
  const digits=[...'0123456789'].map(ch=>metrics(ch));
  const count=model.validate();
  return Object.freeze({
    scope:'ENGINEERING BASELINE ONLY - not teacher-certified',
    catalogItems:count.items,
    guides:GRID,
    reference:'docs/F26_CHILD_HANDWRITING_LEGIBILITY.md',
    fixedCellAdvance:GRID.advance,
    letters,digits,
    flagged:letters.concat(digits).filter(m=>m.warnings.length)
      .map(m=>({letter:m.letter,notes:m.warnings}))
  });
}
if(require.main===module)process.stdout.write(JSON.stringify(summary(),null,2)+'\n');
module.exports={GRID,pathBounds,metrics,summary};
