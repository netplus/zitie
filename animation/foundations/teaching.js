/* F2.2 content-only tutoring notes for the independent foundations book.
 * Verifiable Pinyin spelling rules are distinct from classroom mnemonics.
 * This file NEVER certifies the engineering SVG stroke sequence.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitieFoundationTeaching=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const sources=Object.freeze({
    spelling:'GB/T 16159—2012 汉语拼音正词法基本规则，6.5 标调；教育部汉语拼音教学资料',
    recognition:'教育部汉语拼音教学案例：辨别形近字母、四线三格与声调',
    geometry:'工程字形观察提示；不是国家统一的拼音笔顺标准'
  });
  const special={
    initials:{
      b:['左竖右圆，和 d 成对辨认。','b 的竖在左，圆弧在右；辨形不等于审定了运笔先后。','recognition'],
      d:['左圆右竖，和 b 成对辨认。','d 的圆弧在左，竖在右；注意上伸到上格。','recognition'],
      p:['竖在左、圆在右，下伸到下格。','p 与 q 的下伸竖位置相反，观察圆弧位于哪一侧。','recognition'],
      q:['圆在左、竖在右，下伸到下格。','q 与 p 的下伸竖位置相反，注意下伸方向和上下界。','recognition'],
      n:['一门 n：观察一个拱形。','n 与 m 对照，看清拱形数量、起止位置与间距。','recognition'],
      m:['两门 m：观察两个拱形。','m 比 n 多一个拱形，保持相邻笔形的疏密均匀。','recognition'],
      zh:['zh 是两个字母的声母组合。','z 与 h 紧凑排列，字母清晰，别把 zh 写成单个新符号。','recognition'],
      ch:['ch 是两个字母的声母组合。','c 与 h 紧凑排列，注意 h 的上伸部。','recognition'],
      sh:['sh 是两个字母的声母组合。','s 与 h 紧凑排列，注意 h 的上伸部。','recognition'],
      y:['y 下伸到下格。','观察下伸部分；整体认读音节 yu、yue 中还有 ü 的省点拼写规则。','recognition'],
      w:['w 的两个下折要清晰。','与元音 u 相区分；写成整体认读音节 wu 时不要拆作两次读。','recognition']
    },
    finals:{
      a:['单韵母 a：形状与字母 o 区分。','采用教学中常见的单层 a；注意它的圆弧和右侧短竖。','recognition'],
      i:['i 的点与声调不是叠加关系。','给 i 标一、二、三、四声时，写 ī、í、ǐ、ì，省去原来的点。','spelling'],
      u:['u 与 ü 的差别在两点。','不带点写 u；不要把单韵母 u 和 ü 混为一谈。','recognition'],
      'ü':['ü 两点必须保留。','单独写 ü 或练习 üe、ün 时保留两点；只有符合拼写规则的音节才省点。','spelling'],
      'üe':['üe 中的 ü 保留两点。','单独练习本韵母时不省略；在 yue 等拼写形式中依规则去点。','spelling'],
      'ün':['ün 中的 ü 保留两点。','韵母独立练习时保留两点；yun 等拼写形式要区别于普通的 un。','spelling'],
      iu:['iu 标声调，标在后面的 u 上。','例如 liú：后面的 u 上写声调，不标在前面的 i 上。','spelling'],
      ui:['ui 标声调，标在后面的 i 上。','例如 shuǐ：后面的 i 上写声调，同时去掉 i 原来的点。','spelling']
    },
    syllables:{
      yu:['yu 是整体认读音节。','相关 ü 在 y 后省去两点写 yu；不能因此误读成普通 u。','spelling'],
      yue:['yue 是整体认读音节。','它对应的 üe 在 y 后按拼写规则省点，字母写成 yue。','spelling'],
      yuan:['yuan 是整体认读音节。','相关 ü 在 y 后按拼写规则省点，字母写成 yuan。','spelling'],
      yun:['yun 是整体认读音节。','相关 ün 在 y 后按拼写规则省点，字母写成 yun。','spelling'],
      yi:['yi 要整体认读。','不要把它当作需要逐字母读出的两个单独声音。','recognition'],
      wu:['wu 要整体认读。','注意两个字母的形态与间距，读音作为一个音节掌握。','recognition']
    }
  };
  const tones={
    a:['ā、á、ǎ、à 对应一到四声。','先认元音 a，再观察调号形状和方向。'],
    o:['ō、ó、ǒ、ò 对应一到四声。','四声符号要放在同一个元音 o 上。'],
    e:['ē、é、ě、è 对应一到四声。','四声符号要放在同一个元音 e 上。'],
    i:['ī、í、ǐ、ì：标调时 i 去点。','写调号时省去 i 原来的点，不叠写点和调号。'],
    u:['ū、ú、ǔ、ù 对应一到四声。','区别 u 与 ü；本组只有 u，不带两点。'],
    'ü':['ǖ、ǘ、ǚ、ǜ：ü 两点不消失。','在 ü 上再写声调，两个点仍保留；请留意标调位置。']
  };
  const approvedCategories=new Set(['letters','numbers','initials','finals','syllables','tones','words']);
  function build(headline,detail,source){
    if(!sources[source])throw Error('Invalid tutoring evidence type');
    return Object.freeze({headline,detail,source,label:
      source==='spelling'?'拼写与标调规则':
      source==='recognition'?'辨形教学提示（非笔顺标准）':
      '字形观察（工程示范）'});
  }
  function tipFor(group,entry){
    const key=typeof group==='string'?group:group?.key;
    const text=typeof entry==='string'?entry:entry?.text;
    if(!approvedCategories.has(key)||typeof text!=='string'||!text)
      throw Error('Invalid foundation teaching entry');
    const fixed=special[key]?.[text];
    if(fixed)return build(...fixed);
    if(key==='letters')return build(
      text+'：注意英文大写与小写的高度差。',
      '英文字母练习和拼音字母在教学中可能采用不同字形；逐笔轨迹只是工程示范。',
      'geometry');
    if(key==='numbers')return build(
      text+'：居中书写，大小统一。',
      '使用独立方格观察形态与间距；本字帖尚未审核数字的标准手写笔顺。',
      'geometry');
    if(key==='initials')return build(
      text+'：辨认占格和外形。',
      '检查上伸、下伸、圆弧与相邻笔形的关系；动作轨迹不是国家笔顺标准。',
      'recognition');
    if(key==='finals')return build(
      text+'：把每个字母写清楚，间距均匀。',
      /ng$/.test(text)?'鼻韵母末尾是 ng，注意写完整；不要和仅以 n 收尾的韵母混淆。':
      /n$/.test(text)?'本韵母以 n 收尾；注意与 ang、eng、ing 等 ng 结尾韵母区分。':
      '先正确拼读和辨认字形，再练习字母组合；书写动作仍需对照教材。',
      'recognition');
    if(key==='syllables')return build(
      text+'：整体认读音节。',
      '作为一个音节整体认读；不要简单拆成若干独立拼读部分。',
      'recognition');
    if(key==='tones'){
      const normalized=text.normalize('NFD');
      const base=normalized.startsWith('u\u0308')?'ü':normalized.charAt(0);
      const parts=tones[base];
      if(!parts)throw Error('Unlisted four-tone family');
      return build(parts[0],parts[1],'spelling');
    }
    return build(
      text+'：先读词语，再描摹。',
      '检查每个音节的声调和词语的连写或空格；真实书写笔迹仅保存在本机。',
      'recognition');
  }
  return Object.freeze({sources,tipFor});
});
