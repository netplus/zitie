/* F1 Foundations copybook: self-drawn monoline construction guides.
 * These are independent engineering practice vectors, NOT licensed fonts,
 * real handwriting recordings or teacher-approved stroke-order evidence.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieFoundations=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const lower={
    a:'M56 50 C44 44 18 46 15 64 C12 79 27 87 43 83 C52 81 56 73 56 64 C56 57 56 52 56 49 V83',
    b:'M16 17 V83 C16 64 26 49 39 48 C58 46 63 62 60 73 C57 84 43 87 31 82 C23 79 19 74 16 67',
    c:'M57 51 C42 44 17 48 16 65 C16 81 40 91 57 79',
    d:'M56 50 C44 44 18 46 15 64 C12 79 27 87 43 83 C52 81 56 73 56 64 C56 57 56 52 56 49 V17 V83',
    e:'M17 65 H59 C59 44 29 39 19 56 C9 74 24 88 40 85 C48 84 55 80 59 76',
    f:'M61 21 C47 15 40 22 40 34 V83;M22 49 H58',
    g:'M56 50 C44 44 18 46 15 64 C12 79 27 87 43 83 C52 81 56 73 56 64 C56 57 56 52 56 49 V96 C56 112 32 115 19 100',
    h:'M17 17 V83 C17 68 19 49 38 48 C53 48 58 57 58 68 V83',
    i:'M35 49 V83;M35 30 L35 31',
    j:'M50 49 V96 C50 111 30 114 20 102;M50 30 L50 31',
    k:'M17 17 V83;M58 49 L19 68 L61 83',
    l:'M35 17 V83',
    m:'M10 49 V83 C10 71 11 49 23 49 C33 49 35 56 35 68 V83 C35 70 37 49 49 49 C60 49 63 60 63 70 V83',
    n:'M17 49 V83 C17 69 19 49 37 49 C53 49 58 56 58 69 V83',
    o:'M56 53 C42 43 18 46 16 66 C14 84 35 90 48 81 C61 71 60 59 56 53 Z',
    p:'M16 49 V109 C16 87 16 60 31 51 C45 43 60 50 61 66 C62 80 49 88 36 83 C25 80 19 75 16 67',
    q:'M56 50 C44 44 18 46 15 64 C12 79 27 87 43 83 C52 81 56 73 56 64 C56 57 56 52 56 49 V106 C56 116 43 116 41 110',
    r:'M18 49 V83 C18 69 19 49 38 49 C46 49 52 51 57 53',
    s:'M57 52 C40 43 18 47 18 58 C18 70 59 63 59 76 C59 91 34 90 17 79',
    t:'M37 20 V72 C37 83 45 87 57 82;M22 49 H58',
    u:'M17 49 V69 C17 91 56 91 56 68 V49 V83',
    v:'M15 49 L37 83 L61 49',
    w:'M9 49 L22 83 L35 58 L48 83 L65 49',
    x:'M15 49 L61 83;M61 49 L15 83',
    y:'M13 49 L37 83;M61 49 L28 109',
    z:'M16 49 H60 L16 83 H61'
  };
  const upper={
    A:'M37 17 L9 83;M37 17 L65 83;M21 58 H53',
    B:'M14 17 V83;M14 17 H39 C68 17 66 48 40 49 H14;M14 49 H42 C73 49 69 83 42 83 H14',
    C:'M63 25 C45 11 20 17 13 42 C5 66 24 91 63 75',
    D:'M14 17 V83;M14 17 H33 C77 17 77 83 33 83 H14',
    E:'M14 17 V83;M14 17 H64;M14 50 H54;M14 83 H64',
    F:'M14 17 V83;M14 17 H64;M14 50 H54',
    G:'M63 25 C40 8 12 24 12 50 C12 80 40 91 62 73;M42 54 H63;M63 54 V73',
    H:'M14 17 V83;M62 17 V83;M14 50 H62',
    I:'M38 17 V83;M20 17 H56;M20 83 H56',
    J:'M58 17 V65 C58 95 23 94 17 72;M20 17 H61',
    K:'M14 17 V83;M63 17 L14 55;M34 41 L65 83',
    L:'M14 17 V83;M14 83 H63',
    M:'M11 17 V83;M11 17 L37 56;M63 17 L37 56;M63 17 V83',
    N:'M13 17 V83;M13 17 L62 83;M62 17 V83',
    O:'M37 17 C7 17 7 83 37 83 C67 83 67 17 37 17 Z',
    P:'M14 17 V83;M14 17 H40 C73 17 73 53 41 53 H14',
    Q:'M37 17 C7 17 7 83 37 83 C67 83 67 17 37 17 Z;M45 68 L67 89',
    R:'M14 17 V83;M14 17 H40 C72 17 71 52 40 52 H14;M40 52 L66 83',
    S:'M62 25 C47 10 17 14 17 35 C17 55 63 44 63 66 C63 88 32 91 13 77',
    T:'M37 17 V83;M10 17 H64',
    U:'M14 17 V60 C14 92 61 92 61 60 V17',
    V:'M11 17 L37 83;M64 17 L37 83',
    W:'M8 17 L21 83;M21 83 L37 40;M37 40 L51 83;M51 83 L66 17',
    X:'M12 17 L64 83;M64 17 L12 83',
    Y:'M10 17 L37 52;M64 17 L37 52 V83',
    Z:'M12 17 H63;M63 17 L12 83;M12 83 H64'
  };
  const digits={
    0:'M37 17 C7 17 7 83 37 83 C67 83 67 17 37 17 Z',
    1:'M22 36 L40 17 V83;M25 83 H58',
    2:'M15 31 C16 12 63 11 62 35 C60 51 31 64 15 83 H64',
    3:'M18 24 C48 9 63 23 58 40 C55 49 47 51 36 51;M36 51 C71 45 70 87 37 86 C25 86 16 82 13 76',
    4:'M52 83 V17;M13 62 L51 17;M13 62 H65',
    5:'M61 17 H21 L17 47 C38 39 65 48 61 68 C57 88 29 91 14 78',
    6:'M57 21 C27 10 12 42 15 67 C18 91 60 90 62 68 C64 47 29 42 16 65',
    7:'M13 17 H65 L28 83',
    8:'M37 17 C14 17 14 49 37 49 C60 49 60 17 37 17 Z;M37 49 C8 49 9 85 37 85 C65 85 66 49 37 49 Z',
    9:'M58 48 C46 61 12 57 13 36 C14 15 59 9 61 35 C66 58 58 78 36 84 C28 87 20 84 16 81'
  };
  const initialValues='b p m f d t n l g k h j q x zh ch sh r z c s y w'.split(' ');
  const single='a o e i u ü'.split(' ');
  const compound='ai ei ui ao ou iu ie üe er'.split(' ');
  const nasal='an en in un ün ang eng ing ong'.split(' ');
  const whole='zhi chi shi ri zi ci si yi wu yu ye yue yuan yin yun ying'.split(' ');
  const tones=['ā á ǎ à','ō ó ǒ ò','ē é ě è','ī í ǐ ì','ū ú ǔ ù','ǖ ǘ ǚ ǜ'];
  const words=[
    {text:'māma',meaning:'妈妈'}, {text:'bàba',meaning:'爸爸'},
    {text:'nǐ hǎo',meaning:'你好'}, {text:'xièxie',meaning:'谢谢'},
    {text:'xuéxí',meaning:'学习'}, {text:'shūbāo',meaning:'书包'},
    {text:'péngyou',meaning:'朋友'}, {text:'zǎoshang',meaning:'早上'}
  ];
  const format=(group,values,hint,extra={})=>({
    key:group,name:extra.name||group,hint,kind:extra.kind||'lines',
    entries:values.map((x,i)=>({
      id:group+'-'+i,text:typeof x==='string'?x:x.text,
      meaning:typeof x==='string'?'':x.meaning||''
    }))
  });
  const groups=[
    format('letters',[...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'].map(s=>s+s.toLowerCase()),
      '先练大写，再练小写；注意字母高度与上、下伸部。',{name:'英文字母'}),
    format('numbers',[...'0123456789'],
      '数字在方格中保持大小一致，注意封闭形态与倾斜。',{name:'数字 0—9',kind:'squares'}),
    format('initials',initialValues,
      '小学常用声母教学表，含 y、w；zh / ch / sh 为字母组合。',{name:'拼音声母'}),
    format('finals',single.concat(compound,nasal),
      '顺序为单韵母6、复韵母9、鼻韵母9；ü 的两点不能遗漏。',{name:'拼音韵母'}),
    format('syllables',whole,
      '16组整体认读音节，整体识读，不按声母与韵母拆开练读。',{name:'整体认读'}),
    format('tones',tones,
      '从左到右依次为第一、二、三、四声。i 标声调时去点；ü 保留两点。',{name:'四声练习'}),
    format('words',words,
      '初级词语书写和认读示例；注意标调与分词空格。',{name:'基础词语'})
  ];
  const MARKS={
    '\u0304':'M22 26 H53', // first tone: macron
    '\u0301':'M29 29 L49 16', // second tone: rising
    '\u030c':'M22 17 L37 29 L53 17', // third tone: dipping
    '\u0300':'M24 16 L46 29' // fourth tone: falling
  };
  function parts(text){
    const result=[];
    for(const char of Array.from(text.normalize('NFD'))){
      if(char===' '){result.push({base:' ',marks:[]});continue;}
      if(Object.prototype.hasOwnProperty.call(MARKS,char)||char==='\u0308'){
        const previous=result[result.length-1];
        if(!previous||previous.base===' ')throw Error('Unattached diacritic');
        previous.marks.push(char);
      }else{
        if(!(Object.prototype.hasOwnProperty.call(lower,char)||
             Object.prototype.hasOwnProperty.call(upper,char)||
             Object.prototype.hasOwnProperty.call(digits,char)))
          throw Error('Unknown practice vector: '+char);
        result.push({base:char,marks:[]});
      }
    }
    return result;
  }
  function compose(text,kind='lines'){
    const result=[];
    let x=0;
    for(const part of parts(text)){
      if(part.base===' '){x+=33;continue;}
      const table=kind==='squares'?digits:
        Object.prototype.hasOwnProperty.call(upper,part.base)?upper:lower;
      const ref=table[part.base];
      if(!ref)throw Error('Missing path for '+part.base);
      const hasTone=part.marks.some(mark=>Object.prototype.hasOwnProperty.call(MARKS,mark));
      const strokes=ref.split(';').filter(Boolean);
      if(part.base==='i'&&hasTone)strokes.splice(1); // accented i loses its dot
      for(const d of strokes)result.push({d,x,part:part.base});
      if(part.marks.includes('\u0308')){
        result.push({d:'M24 33 L24 34',x,part:'diaeresis'});
        result.push({d:'M50 33 L50 34',x,part:'diaeresis'});
      }
      for(const mark of part.marks)if(MARKS[mark])
        result.push({d:MARKS[mark],x,part:'tone'});
      x+=76;
    }
    return {strokes:result,width:Math.max(76,x),height:132};
  }
  function validate(){
    if([26,10,23,24,16,6,8].some((n,i)=>groups[i].entries.length!==n))
      throw Error('Foundations category counts drifted');
    const ids=new Set();
    for(const group of groups)for(const item of group.entries){
      if(ids.has(item.id))throw Error('Duplicate ID: '+item.id);
      ids.add(item.id);
      if(compose(item.text,group.kind).strokes.length===0)
        throw Error('Empty vector for '+item.id);
    }
    return {groups:groups.length,items:ids.size};
  }
  validate();
  return Object.freeze({groups,compose,parts,validate});
});
