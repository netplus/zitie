#!/usr/bin/env python3
"""Original, reproducible scene-specific vector drawings for 201-glyph cultural draft.

Each illustration is a non-teaching line-art composition derived from a UNIQUE
human-authored per-character art brief. No remote media/font, copied stock
image, bitmap, text glyph, or generated teaching pen-stroke is used.
All artworks remain design DRAFTS, NOT professional visual approval.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import random
import re
from pathlib import Path

from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT=Path(__file__).resolve().parents[1]
S=72.0/25.4

# Hand-coded non-character pictograms. Every scene combines up to three
# subject-specific motifs, a distinct composition, and restrained background
# wash drawn from mathematical vector shapes.
ICONS={
"sun":'<circle cx="50" cy="48" r="19" fill="#E6C48A" fill-opacity=".64" stroke="#BE9365" stroke-width="2"/>'+
      ''.join(f'<path d="M{50+27*math.cos(math.pi*k/6):.1f} {48+27*math.sin(math.pi*k/6):.1f} L{50+34*math.cos(math.pi*k/6):.1f} {48+34*math.sin(math.pi*k/6):.1f}" stroke="#BF9B67" stroke-width="2"/>' for k in range(12)),
"moon":'<path d="M63 16 C26 11 17 74 57 84 C27 76 38 32 63 16 Z" fill="#E7D9B5" stroke="#98A59C" stroke-width="2"/><circle cx="75" cy="29" r="2" fill="#8D9D97"/>',
"mountain":'<path d="M4 77 L31 35 L45 53 L64 19 L96 77Z" fill="#C7D6C5" stroke="#6B837D" stroke-width="2"/><path d="M21 50L31 35L43 51M53 35L64 19L78 44" fill="none" stroke="#FBF7EE" stroke-width="3"/>',
"river":'<path d="M4 15C45 4 61 47 20 53S39 92 94 77" fill="none" stroke="#8DBABD" stroke-width="10" stroke-linecap="round"/><path d="M5 15C45 4 61 47 20 53S39 92 94 77" fill="none" stroke="#E5EDE8" stroke-width="2"/>',
"bamboo":'<path d="M24 94L29 12M54 94L50 18M78 94L85 15" stroke="#789588" stroke-width="6" fill="none"/>'+
         '<path d="M23 39L35 41M21 64L34 65M45 47L57 47M48 75L61 76M78 43L89 45M74 69L86 70" stroke="#C9A772" stroke-width="3"/>'+
         '<path d="M29 23Q6 5 6 31Q19 29 29 23M52 38Q74 18 69 43Q61 44 52 38M80 56Q56 39 59 62Q70 65 80 56" fill="#A9C1A3" stroke="#718C78" stroke-width="1.2"/>',
"tree":'<path d="M48 95Q50 72 46 51M47 69L23 48M47 60L75 43" fill="none" stroke="#957C66" stroke-width="7" stroke-linecap="round"/>'+
       '<ellipse cx="48" cy="38" rx="29" ry="24" fill="#BBCDAA" stroke="#819986" stroke-width="2"/><ellipse cx="30" cy="46" rx="18" ry="15" fill="#C8D2B3"/><ellipse cx="65" cy="44" rx="21" ry="17" fill="#A5BDA3"/>',
"leaf":'<path d="M12 83Q15 19 90 14Q76 85 12 83Z" fill="#A8C2AA" stroke="#6D9482" stroke-width="2"/><path d="M14 82Q49 46 90 15M38 59L34 36M58 40L74 50" fill="none" stroke="#E6F0DC" stroke-width="2.2"/>',
"flower":'<path d="M51 91V52M51 70Q27 48 24 73Q37 79 51 70M51 78Q72 54 80 76Q68 85 51 78" stroke="#7D9E84" fill="#C3D4B1" stroke-width="3"/>'+
          ''.join(f'<ellipse cx="{50+16*math.cos(k*math.pi/3):.1f}" cy="{37+16*math.sin(k*math.pi/3):.1f}" rx="13" ry="9" transform="rotate({k*60} {50+16*math.cos(k*math.pi/3):.1f} {37+16*math.sin(k*math.pi/3):.1f})" fill="#D7ABB0" stroke="#B58B94" stroke-width="1.2"/>' for k in range(6))+
          '<circle cx="50" cy="37" r="9" fill="#E6C682" stroke="#C2A26A" stroke-width="1.3"/>',
"grass":'<path d="M12 91Q23 59 31 29Q33 68 49 91M44 90Q56 49 77 35Q66 67 70 90M72 91Q84 64 93 57" fill="none" stroke="#86A78B" stroke-width="6" stroke-linecap="round"/><path d="M9 93H93" stroke="#B8C7B1" stroke-width="3"/>',
"wheat":'<path d="M49 95L48 11" stroke="#A88F62" stroke-width="3"/>'+''.join(f'<ellipse cx="{43 if k%2 else 55}" cy="{22+k*9}" rx="8" ry="4" transform="rotate({-26 if k%2 else 26} {43 if k%2 else 55} {22+k*9})" fill="#D9C18B" stroke="#B59A65"/>' for k in range(7)),
"seed":'<path d="M19 78Q50 102 82 77L88 93H13Z" fill="#CFBB9C"/><path d="M49 79L50 44" stroke="#779E79" stroke-width="3"/><path d="M50 58Q17 32 23 15Q44 17 50 58M50 51Q80 17 89 30Q75 51 50 51" fill="#B1CAA8" stroke="#72977E" stroke-width="1.5"/><ellipse cx="49" cy="82" rx="8" ry="5" fill="#C3986F"/>',
"house":'<path d="M18 42L50 15L84 42V88H18Z" fill="#F0E2CB" stroke="#9C8772" stroke-width="3"/><path d="M8 43L50 8L92 43" fill="none" stroke="#967F70" stroke-width="6" stroke-linejoin="round"/><rect x="41" y="59" width="18" height="29" fill="#D3BEA5" stroke="#9B856F" stroke-width="2"/><rect x="24" y="52" width="13" height="15" fill="#C2D9D8" stroke="#8BA8A5"/>',
"door":'<path d="M19 92V20H81V92" fill="none" stroke="#927B68" stroke-width="8"/><rect x="27" y="26" width="46" height="66" fill="#DFC6A6" stroke="#9F886D" stroke-width="2"/><path d="M73 27L46 36V90L73 91" fill="#EAD9BE" stroke="#9D866A" stroke-width="3"/><circle cx="53" cy="64" r="2.8" fill="#B99255"/>',
"bridge":'<path d="M7 70Q50 6 93 70" fill="none" stroke="#B5A18A" stroke-width="12"/><path d="M7 72H93M20 55V73M79 55V73" fill="none" stroke="#867D72" stroke-width="3"/><path d="M8 84Q25 78 43 84T80 84" fill="none" stroke="#9EB9BC" stroke-width="5"/>',
"road":'<path d="M39 95Q7 50 53 39T70 5M59 95Q34 61 74 38T85 5" fill="none" stroke="#B4A590" stroke-width="6"/><path d="M49 95Q25 55 62 38T78 5" fill="none" stroke="#F2E9D8" stroke-width="2" stroke-dasharray="6 7"/>',
"book":'<path d="M6 30Q30 19 50 32Q73 18 94 30V83Q69 74 50 89Q30 74 6 83Z" fill="#F5E9D7" stroke="#928575" stroke-width="2.5"/><path d="M50 32V88M14 42Q31 39 44 46M14 55Q31 52 44 59M56 46Q71 38 87 42M56 60Q72 52 87 56" fill="none" stroke="#C0AA90" stroke-width="2"/>',
"brush":'<path d="M16 82L66 19L77 25L29 88Z" fill="#B59E87" stroke="#8B7969" stroke-width="2"/><path d="M66 19L76 8L84 18L77 25Z" fill="#D0C0A8"/><path d="M16 82L11 94L29 88Z" fill="#4D6060"/><path d="M26 95Q43 99 67 94" fill="none" stroke="#4F6262" stroke-width="3"/>',
"paper":'<path d="M20 11H69L83 27V93H20Z" fill="#F4EEE2" stroke="#A99A86" stroke-width="2"/><path d="M68 11V29H83M29 43H73M29 56H67M29 68H72M29 81H58" fill="none" stroke="#C2B1A0" stroke-width="2"/>',
"hand":'<path d="M23 91C20 76 14 66 14 60Q15 52 21 57L36 71L33 21Q34 13 39 18L44 63L45 13Q47 6 51 14L53 64L60 20Q64 14 67 22L62 67L75 34Q80 27 83 38L74 82Q64 96 45 93Z" fill="#E9D2B8" stroke="#AB927E" stroke-width="2"/>',
"bowl":'<path d="M15 49H85Q82 84 57 86H43Q18 82 15 49Z" fill="#CFD7D0" stroke="#849D93" stroke-width="2.5"/><path d="M37 86L34 93H66L63 86M23 50Q49 40 77 50" fill="none" stroke="#92A6A0" stroke-width="3"/><path d="M36 37Q24 24 39 15M53 37Q44 23 59 12M68 37Q58 21 74 15" fill="none" stroke="#A6B6AE" stroke-width="2.2"/>',
"pot":'<path d="M38 23H63L71 38L68 74Q63 91 50 91Q36 90 32 74L29 38Z" fill="#DAC0A8" stroke="#A98F79" stroke-width="2.5"/><path d="M37 23V14H64V23M30 40H70M39 54Q50 63 63 53M39 66Q50 75 63 65" fill="none" stroke="#AA907B" stroke-width="3"/>',
"lantern":'<path d="M50 6V17M36 20Q50 15 64 20L69 60Q50 78 31 60Z" fill="#DC9A93" stroke="#AD7771" stroke-width="2"/><path d="M30 35H70M31 47H68M37 20Q44 46 37 65M63 20Q56 46 63 65M38 64H62M50 68V91M44 90H56" stroke="#B67F77" stroke-width="2" fill="none"/>',
"lamp":'<path d="M47 80V53M30 91H69M43 80H52" fill="none" stroke="#9B8770" stroke-width="4"/><path d="M26 50L40 24H61L76 50Z" fill="#EED9A7" stroke="#AC9A77" stroke-width="2"/><ellipse cx="50" cy="52" rx="13" ry="5" fill="#F9E6BB"/>',
"wheel":'<circle cx="50" cy="50" r="36" fill="#E6DDCA" stroke="#8A8376" stroke-width="6"/><circle cx="50" cy="50" r="8" fill="#BCA791" stroke="#88796E"/>'+''.join(f'<path d="M50 50L{50+29*math.cos(k*math.pi/4):.1f} {50+29*math.sin(k*math.pi/4):.1f}" stroke="#958574" stroke-width="4"/>' for k in range(8)),
"clock":'<circle cx="50" cy="50" r="38" fill="#F3E8D6" stroke="#988674" stroke-width="3"/><path d="M50 18V25M50 75V82M18 50H25M75 50H82M50 50V30M50 50L66 62" fill="none" stroke="#86786E" stroke-width="4" stroke-linecap="round"/>',
"ruler":'<rect x="8" y="41" width="84" height="19" rx="3" fill="#E0C3A1" stroke="#9C8468" stroke-width="2"/>'+''.join(f'<path d="M{k} 41V{52 if k%10 else 58}" stroke="#967A63" stroke-width="1.5"/>' for k in range(15,91,5)),
"cloth":'<path d="M24 20Q52 11 78 19L72 42Q95 63 76 91L39 79L18 92Q7 72 24 49Z" fill="#D5DFDB" stroke="#829D9C" stroke-width="2"/><path d="M30 24Q34 56 29 79M67 24Q60 55 73 78M29 70Q50 81 75 76" fill="none" stroke="#A5BCB7" stroke-width="2"/>',
"needle":'<path d="M15 79L85 12" fill="none" stroke="#7C9092" stroke-width="4"/><ellipse cx="81" cy="17" rx="4" ry="7" transform="rotate(46 81 17)" fill="#F5EFE0" stroke="#7C9092"/><path d="M14 78Q0 56 31 50T56 84" fill="none" stroke="#B19AA7" stroke-width="2"/>',
"boat":'<path d="M11 63H90L78 82H28Z" fill="#C8AD8D" stroke="#907D69" stroke-width="2"/><path d="M51 61V12L78 55H51Z" fill="#EFDFC8" stroke="#A68F72" stroke-width="2"/><path d="M50 22L26 57H50M10 88Q28 82 46 88T82 88" fill="none" stroke="#92B5B6" stroke-width="3"/>',
"fish":'<path d="M15 51Q50 12 79 45L94 27V73L79 59Q50 91 15 51Z" fill="#A3C3BF" stroke="#6B9697" stroke-width="2.5"/><circle cx="35" cy="49" r="3" fill="#536A69"/><path d="M55 35L60 51L54 65M20 73Q35 80 50 71" fill="none" stroke="#D8E7DD" stroke-width="2"/>',
"bird":'<path d="M12 67Q30 32 53 51Q71 18 91 39Q73 74 51 72Q32 93 12 67Z" fill="#BDC9C8" stroke="#7D9997" stroke-width="2"/><path d="M43 56Q63 35 75 48M84 44L96 50L84 54" stroke="#7D9997" stroke-width="2" fill="none"/><circle cx="71" cy="41" r="3" fill="#5D7270"/>',
"cat":'<path d="M24 39L23 15L40 29Q51 25 65 29L79 13L78 49Q87 66 72 85Q50 94 30 80Q16 66 24 39Z" fill="#D9C8B3" stroke="#9C8877" stroke-width="2"/><circle cx="38" cy="57" r="3" fill="#536D67"/><circle cx="66" cy="57" r="3" fill="#536D67"/><path d="M47 70L53 70M51 70V75M14 65L39 67M63 68L88 66" fill="none" stroke="#9A8A7E" stroke-width="2"/>',
"animal":'<ellipse cx="48" cy="58" rx="29" ry="21" fill="#D2BDA3" stroke="#978675" stroke-width="2"/><path d="M26 73L20 92M65 73L72 93M64 42L80 24L89 32L78 53M81 24L83 10" fill="none" stroke="#988572" stroke-width="5" stroke-linecap="round"/><circle cx="81" cy="33" r="2.5" fill="#4E6462"/>',
"umbrella":'<path d="M7 51Q48 -6 93 51Q72 42 51 51Q29 42 7 51Z" fill="#D4A2A0" stroke="#AE8882" stroke-width="2"/><path d="M51 51V83Q51 98 67 92" fill="none" stroke="#927E70" stroke-width="4"/>',
"star":'<path d="M50 8L61 37L92 37L67 55L78 87L50 68L22 87L33 55L8 37L39 37Z" fill="#E9D59A" stroke="#B39B6E" stroke-width="2"/>',
"footprint":'<ellipse cx="37" cy="65" rx="18" ry="27" transform="rotate(-15 37 65)" fill="#B6A895"/>'+''.join(f'<circle cx="{18+k*11}" cy="{30-k%2*5}" r="{5-k%3}" fill="#B6A895"/>' for k in range(4))+
           '<ellipse cx="71" cy="72" rx="13" ry="19" transform="rotate(15 71 72)" fill="#C8B9A4"/>',
"tool":'<path d="M28 86L73 30" stroke="#A48D77" stroke-width="9" stroke-linecap="round"/><path d="M57 18L79 36M54 15Q75 5 91 28L83 40" fill="#9EAAA7" stroke="#687D7C" stroke-width="4"/><path d="M16 84L39 61" stroke="#B3A090" stroke-width="2"/>',
"arrow":'<path d="M15 80L85 16M61 18L85 16L83 40M17 76L38 82" fill="none" stroke="#A18C76" stroke-width="5" stroke-linecap="round"/><path d="M85 16L72 10L82 28Z" fill="#A8B4AE" stroke="#788D88"/>',
"music":'<path d="M36 71V22L75 13V64" fill="none" stroke="#859895" stroke-width="5"/><ellipse cx="25" cy="75" rx="13" ry="8" transform="rotate(-25 25 75)" fill="#AFC2BF"/><ellipse cx="65" cy="69" rx="13" ry="8" transform="rotate(-25 65 69)" fill="#AFC2BF"/><path d="M36 31L75 23" stroke="#859895" stroke-width="7"/>',
"flowerpot":'<path d="M25 55H76L69 91H34Z" fill="#D6B69F" stroke="#9B897A" stroke-width="2"/><path d="M52 56L52 19M51 46L28 27M52 42L74 25" fill="none" stroke="#8AAB8E" stroke-width="3"/><circle cx="49" cy="18" r="11" fill="#D9ABB0"/><circle cx="27" cy="27" r="8" fill="#E0BEA4"/><circle cx="76" cy="25" r="9" fill="#D2AEC5"/>',
"scroll":'<path d="M25 17H77V84H25Z" fill="#F1E4D1" stroke="#A69B89" stroke-width="2"/><ellipse cx="25" cy="17" rx="9" ry="5" fill="#D5C6AF" stroke="#A69B89"/><ellipse cx="25" cy="84" rx="9" ry="5" fill="#D5C6AF" stroke="#A69B89"/><path d="M39 34H67M39 47H65M39 59H68M39 72H60" fill="none" stroke="#C8B6A1" stroke-width="2"/>',
"wave":'<path d="M5 34Q27 15 49 34T95 34M5 55Q27 36 49 55T95 55M5 76Q27 57 49 76T95 76" fill="none" stroke="#86ADB0" stroke-width="6" stroke-linecap="round"/>',
"wind":'<path d="M4 27Q40 11 74 28Q100 42 75 54M6 52Q35 40 56 59Q81 83 92 64M20 80Q43 72 55 88" fill="none" stroke="#A0B8B5" stroke-width="5" stroke-linecap="round"/>',
"flame":'<path d="M48 7Q70 30 67 49Q79 43 77 30Q105 74 65 90Q25 103 18 75Q12 52 38 34Q29 58 43 62Q56 47 48 7Z" fill="#DFB185" stroke="#B98E71" stroke-width="2"/><path d="M53 47Q65 71 55 85Q35 87 35 69Z" fill="#F0D29A"/>',
"rain":'<path d="M22 33Q10 18 32 11Q49 -2 63 18Q88 12 92 36Z" fill="#CBD8D6" stroke="#89A7A7" stroke-width="2"/>'+
       ''.join(f'<path d="M{k} 52L{k-4} 65M{k+2} 74L{k-3} 86" stroke="#86ADB5" stroke-width="3" stroke-linecap="round"/>' for k in (29,52,76)),
"snow":'<path d="M50 8V92M8 50H92M21 21L79 79M79 21L21 79" fill="none" stroke="#9DBDC4" stroke-width="4"/>'+''.join(f'<circle cx="{50+36*math.cos(k*math.pi/4):.1f}" cy="{50+36*math.sin(k*math.pi/4):.1f}" r="3" fill="#D6E3E6"/>' for k in range(8)),
"compass":'<circle cx="50" cy="50" r="37" fill="#F1E9D9" stroke="#9D907F" stroke-width="2"/><path d="M50 10L59 50L50 91L41 50Z" fill="#C89C91" stroke="#8A7C70" stroke-width="2"/><circle cx="50" cy="50" r="5" fill="#E8D0B1"/>',
"fruit":'<path d="M51 31Q79 5 86 47Q97 83 59 92Q21 103 12 69Q5 29 43 30Z" fill="#D4AE8C" stroke="#AA8875" stroke-width="2"/><path d="M48 32Q53 12 67 8M49 24Q18 0 13 25Q34 33 49 24" fill="#BCD2A8" stroke="#879C80" stroke-width="2"/>',
"ink":'<path d="M13 81Q42 45 74 18Q85 15 79 25Q61 55 35 75Q25 85 13 81Z" fill="#607473" stroke="#4A6464"/><path d="M22 90Q46 86 79 72" stroke="#A4B6AF" stroke-width="2" fill="none"/>',
"rope":'<path d="M11 54C27 5 70 5 84 40C100 71 51 99 25 78C10 66 31 42 49 48C71 56 57 76 42 69" fill="none" stroke="#B29A7F" stroke-width="9" stroke-linecap="round"/><path d="M11 54C27 5 70 5 84 40" fill="none" stroke="#E6D8C1" stroke-width="2.5"/>',
"bell":'<path d="M27 67Q32 49 30 38Q34 19 50 19Q69 19 72 39Q72 55 77 67Z" fill="#D8C49C" stroke="#9F8D67" stroke-width="2"/><circle cx="50" cy="75" r="6" fill="#A58C63"/><path d="M20 67H83M46 17Q50 6 54 17" stroke="#9E8E6D" stroke-width="3"/>',
}
KEYWORDS=[
("竹","bamboo"),("稻","wheat"),("麦","wheat"),("禾","wheat"),("谷粒","wheat"),("穗","wheat"),("种子","seed"),("芽","seed"),
("木尺","ruler"),("刻度","ruler"),("尺","ruler"),("书","book"),("字典","book"),("图册","book"),("家谱","scroll"),
("笔","brush"),("墨","ink"),("纸","paper"),("拓片","scroll"),("古籍","scroll"),("旧卷","scroll"),("手稿","paper"),
("古器","pot"),("陶","pot"),("鼎","pot"),("器皿","pot"),("臼","pot"),("碗","bowl"),("饭","bowl"),("茶","bowl"),
("纺","cloth"),("织","cloth"),("衣","cloth"),("布","cloth"),("线","rope"),("绳","rope"),("针","needle"),
("窗","house"),("屋","house"),("瓦","house"),("檐","house"),("院","house"),("家","house"),("门","door"),
("桥","bridge"),("石阶","road"),("路","road"),("田埂","road"),("道","road"),
("舟","boat"),("船","boat"),("河","river"),("溪","river"),("潮","wave"),("浪","wave"),("海","wave"),("水","river"),
("鱼","fish"),("鸟","bird"),("燕","bird"),("羽","bird"),("鹿","animal"),("牛","animal"),("马","animal"),("羊","animal"),
("狗","animal"),("犬","animal"),("猫","cat"),("鼠","animal"),("虫","cat"),("蝶","flower"),
("山","mountain"),("峰","mountain"),("崖","mountain"),("丘","mountain"),("坡","mountain"),
("太阳","sun"),("日轮","sun"),("晨光","sun"),("朝阳","sun"),("霞","sun"),("日","sun"),
("月","moon"),("夜空","moon"),("星","star"),("灯笼","lantern"),("灯","lamp"),("火","flame"),("炉","flame"),
("雨","rain"),("冰","snow"),("雪","snow"),("风","wind"),("云","wind"),
("树","tree"),("根","tree"),("枝","tree"),("叶","leaf"),("草","grass"),("花","flower"),("果","fruit"),("瓜","fruit"),
("轮","wheel"),("车","wheel"),("钟","clock"),("刻","clock"),("音","music"),("琴","music"),("乐","music"),("铃","bell"),("鼓","music"),
("伞","umbrella"),("脚","footprint"),("足","footprint"),("鞋","footprint"),("行人","footprint"),("手","hand"),
("箭","arrow"),("矛","arrow"),("弓","arrow"),("兵","arrow"),("工具","tool"),("匠","tool"),("工","tool"),
("尺","ruler"),("量","ruler"),("镜","compass"),("方位","compass"),("方向","compass"),("旗","cloth"),
("花香","flower"),("香","flower"),("页","book"),("字卡","paper"),("字形","paper"),("偏旁","paper"),
]
PALETTES=[
("#F9F5ED","#D9E4DB","#B36F66"),("#F5F7F3","#D8E3E1","#A78D69"),
("#FAF6F2","#E0D4CB","#A47B7A"),("#F8F8F4","#CFDDCE","#927E80"),
("#FBF6EE","#D9E4E4","#AD906E"),("#F7F7F3","#E7DACD","#9A7B78"),
("#F9F5F0","#D6DED3","#A48572"),("#F8F7F5","#D9E0E1","#AB817F"),
]

def select_motifs(text,main_id):
    """Human-authored noun phrase -> recognizable original vector subjects."""
    choices=[]
    for word,kind in KEYWORDS:
        if word in text and kind not in choices:
            choices.append(kind)
    # These elements are thematically neutral framing only, not the core art.
    framing=("sun","leaf","paper","wind","moon","grass","rope","wave")
    if not choices:
        choices=["paper","ink"]  # non-common cases: chiefly abstract components
    while len(choices)<3:
        k=framing[(main_id+len(choices)*3)%len(framing)]
        if k not in choices:choices.append(k)
    return choices[:3]

def make_svg(main_id,character,theme,brief):
    if not isinstance(brief,str) or len(brief)<6:
        raise ValueError(f"ID{main_id:03d} missing independently authored composition brief")
    rng=random.Random(0x20261026+main_id*9767)
    subject=select_motifs(brief,main_id)
    if any(icon not in ICONS for icon in subject):
        raise ValueError("Missing original vector pictogram for art motif")
    bg,muted,accent=PALETTES[main_id%len(PALETTES)]
    scene_id=f"culture-{main_id:03d}-{theme}"
    layouts=[
        [(340,303,2.25,0),(135,390,1.05,-13),(630,160,1.14,9)],
        [(500,330,2.25,-6),(170,176,1.2,7),(690,450,1.04,12)],
        [(318,284,2.37,6),(628,340,1.24,-7),(147,167,1.00,0)],
        [(465,260,2.19,3),(170,390,1.2,-6),(640,425,1.12,8)],
        [(290,326,2.2,-4),(590,215,1.27,12),(663,456,1.05,-6)],
        [(385,299,2.27,4),(157,225,1.22,-9),(650,390,1.18,7)],
        [(500,310,2.11,-7),(185,400,1.21,13),(628,161,1.03,0)],
    ]
    placement=layouts[main_id%len(layouts)]
    shapes=[]
    for k in range(8):
        x=70+(k*93+main_id*17)%680
        y=90+(k*59+main_id*13)%450
        rx=28+(k*11)%60
        opacity=".07" if k%2 else ".045"
        shapes.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*.67:.1f}" fill="{muted}" opacity="{opacity}"/>')
    for k in range(6):
        sy=535+k*13+int(rng.random()*7)
        start=-25+rng.random()*35
        end=850-rng.random()*40
        shapes.append(f'<path d="M{start:.1f} {sy:.1f} Q{350+rng.random()*170:.1f} {sy-17-rng.random()*15:.1f} {end:.1f} {sy:.1f}" stroke="{muted}" stroke-opacity=".31" stroke-width="{1.2+(k%3):.1f}" fill="none"/>')
    shapes.append(f'<path d="M40 547Q300 520 460 540T790 530" fill="none" stroke="{accent}" stroke-opacity=".20" stroke-width="2"/>')
    for j,(kind,(x,y,scale,rot)) in enumerate(zip(subject,placement)):
        local_rot=rot+round(rng.random()*8-4,2)
        s=scale*(.96+rng.random()*.07)
        shapes.append(f'<g transform="translate({x} {y}) rotate({local_rot}) scale({s:.4f}) translate(-50 -50)" stroke-linecap="round" stroke-linejoin="round" opacity="{1 if j==0 else .87}">{ICONS[kind]}</g>')
    for k in range(15):
        x=rng.randint(30,790);y=rng.randint(45,580);r=1+(k%3)*.55
        shapes.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{accent}" fill-opacity=".20"/>')
    safe_id=html.escape(scene_id,quote=True)
    xml=(f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="630" viewBox="0 0 820 630" '
         f'data-scene="{safe_id}" role="img" aria-label="Original non-teaching cultural vector sketch">'
         f'<rect width="820" height="630" rx="26" fill="{bg}"/>'
         f'<path d="M30 44Q410 17 791 48" fill="none" stroke="{accent}" stroke-opacity=".19" stroke-width="2"/>'
         +''.join(shapes)+
         f'<path d="M30 597Q410 623 789 592" fill="none" stroke="{accent}" stroke-opacity=".17" stroke-width="2"/>'
         '</svg>\n')
    return xml,subject

def generate_all(rows,directory):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    registry=[];signatures=set()
    for row in rows:
        main_id=row["main_id"];e=row.get("manuscript")
        if not e:
            raise ValueError("No cultural manuscript for main ID"+str(main_id))
        if e.get("artwork_stage")=="four_unique_svg_drafts_not_approved":
            continue
        desc=e.get("art_brief")
        xml,motifs=make_svg(main_id,row["character"],e["theme_key"],desc)
        filename=f"ID{main_id:03d}.svg"
        path=directory/filename
        path.write_text(xml,encoding="utf-8")
        sha=hashlib.sha256(xml.encode()).hexdigest()
        if sha in signatures:raise ValueError("Two generated artwork assets are identical")
        signatures.add(sha)
        registry.append({
            "main_id":main_id,"character":row["character"],
            "file":filename,"art_brief":desc,
            "theme_key":e["theme_key"],"artwork_sha256":sha,
            "motif_icons":motifs,"pixel_bitmap_used":False,
            "source":"Original repo-authored geometrical vector drawing generator",
            "editorial_status":"original_vector_draft_not_approved",
            "professional_art_approval":False,
            "license_review":"internal_originality_and_visual_review_pending",
        })
    if len(registry)!=197 or len(signatures)!=197:
        raise ValueError("Expected exactly 197 unique new vector scene drafts")
    return registry

def paint_generated_scene(canvas,record,base):
    root=Path(base).resolve()
    src=(root/record["file"]).resolve()
    if not src.is_relative_to(root):
        raise ValueError("Artwork path traversal")
    raw=src.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=record["artwork_sha256"]:
        raise ValueError("Artwork SVG changed since source registration")
    forbidden=(b"<text",b"<image",b"<script",b"href=",b"url(",b"http:",b"https:")
    if any(word in raw.lower() for word in forbidden):
        raise ValueError("Artwork contains unsupported/external content")
    drawing=svg2rlg(str(src))
    if drawing is None or drawing.width<=0 or drawing.height<=0:
        raise ValueError("Unable to render unique vector cultural scene")
    canvas.saveState()
    canvas.translate(111*S,184*S)
    canvas.scale((82*S)/drawing.width,(70*S)/drawing.height)
    renderPDF.draw(drawing,canvas,0,0)
    canvas.restoreState()

def write_registry(records,path):
    obj={
      "schema_version":1,
      "scope":"197 new scene-specific non-teaching SVG cultural illustration drafts",
      "review_state":"original_vector_drawings_unapproved_for_release",
      "artworks":records,
    }
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
