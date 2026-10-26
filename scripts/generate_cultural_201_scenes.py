#!/usr/bin/env python3
"""Produce 197 individual, editable, original vector scene drafts for the full book.

These deliberately do not contain teaching glyphs/stroke outlines. Every image
is produced from the individual editor's scene brief, assigned two semantic
motifs, and tracked by its own SHA-256. Design and licensing reviews remain
PENDING: this is a hand-authored generative illustration *draft system*, not
evidence of 197 professionally drawn/published pictures.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from cultural_fullbook_model import ROOT, SHA, checked_drafts

# Ordered by specificity; two distinct physical motifs are chosen for every
# scene, including uncommon radicals that require a cultural context card.
MOTIFS = [
 ("mouse", r"鼠|老鼠|田鼠"),("turtle",r"龟|甲纹|小龟"),
 ("deer",r"鹿|梅花鹿"),("cow",r"牛|耕牛"),("horse",r"马|马蹄"),
 ("sheep",r"羊|绵羊"),("dog",r"狗|犬"),("cat",r"猫|小猫"),
 ("bird",r"鸟|飞燕|燕|翅|飞鸟|羽毛|归鸟|羽"),("fish",r"鱼|游鱼"),
 ("insect",r"虫|蝶|甲虫|蚂蚁"),("boat",r"舟|船|帆|渡"),
 ("mountain",r"高山|山|峰|丘|谷|岭|崖|岩"),
 ("bridge",r"桥|拱券"),("stream",r"海浪|海|河|溪|湖|潮|水波|池|涟漪|河道|雨后|流水"),
 ("cloud",r"云|雾|霞|天空|蓝天"),("sun",r"太阳|日轮|阳光|朝阳|晨光|日出|夕阳"),
 ("moon",r"月光|明月|月色|月亮|月"),
 ("star",r"星空|星辰|星点|北斗|星"),
 ("rain",r"雨|滴水|水珠|露珠|晨露|雨线|檐滴|雨滴"),
 ("snow",r"雪|冰花|冰|结冰"),
 ("tree",r"树|林|松|根|木|树干|枝|叶脉|枫|银杏"),
 ("bamboo",r"竹|竹林|竹笛|竹筒"),
 ("flower",r"花|桂|花香|梅花"),("grass",r"草|苔|苗|嫩芽|小芽"),
 ("grain",r"稻|麦|谷粒|穗|禾|粮|黍|菜畦|田埂|田垄"),
 ("fruit",r"豆荚|果|瓜|橘|豆芽"),
 ("scroll",r"旧卷|古卷|古籍|拓片|竹简|史书|书法馆|旧书|典籍"),
 ("book",r"书|册|字典|字卡|日记|图册|本子|纸页|纸张|练习|字形"),
 ("brush",r"笔|墨|宣纸|手写|书法|墨线"),
 ("door",r"门|院门|门扉|家门"),("window",r"窗|屋檐|檐|屋|家|庭院|城楼|建筑|楼|古城|城门"),
 ("lantern",r"灯|灯笼|夜色|灯火"),
 ("umbrella",r"伞"),
 ("road",r"路|街|巷|石阶|山路|道路|路径|岔口|旅程|归途"),
 ("sign",r"路标|牌|标记|指向"),
 ("pot",r"陶|器皿|陶罐|器|壶|罐|碗|盘|盆|缶|鼎|鬲|器具|酒器"),
 ("tea",r"茶|蒸汽|热汤|热水"),
 ("clock",r"时辰|刻度|古钟|钟表|时光"),
 ("wheel",r"轮|车|自行车|推车"),
 ("bell",r"铃|琴键|乐|鼓|音|弦|声波"),
 ("tools",r"工具|尺|刀|锤|杵|农具|犁|剪刀|木工|砝码|秤"),
 ("cloth",r"衣|织|布|棉|麻|毛线|丝线|绳|线装|纺|经纬|梳|发丝"),
 ("hand",r"手|指尖|掌心|手指|双手"),
 ("person",r"人|孩|女孩|妇|父|归家|旅人|行人|老人|身影|面孔|笑脸"),
 ("eye",r"眼|目|观察|放大镜|镜子"),
 ("ear",r"耳|听"),
 ("tooth",r"齿|牙"),
 ("heart",r"心|善意|关怀|爱"),
 ("foot",r"脚|足|足迹|鞋印"),
 ("arrow",r"矛|箭|戈|弓"),
 ("puzzle",r"检字|部首|相近|构字|字头|字根|部件|拼图|形体|辨形|字例|书写|笔画|比对"),
 ("stone",r"石|石头|石板|石砖"),
 ("fire",r"火|火焰|火苗|炉灶"),
]
PALS=[
 ("#465E64","#A94D4C","#D8C19A","#F7F5ED"),
 ("#405C55","#B7654A","#BCC8AA","#F8F6EF"),
 ("#56516A","#A75D63","#D9C5AE","#F8F5F1"),
 ("#49636C","#B1834A","#B3C7C1","#F8F6F0"),
 ("#53634E","#A65B4B","#CDD5B8","#F8F5ED"),
 ("#4B5961","#A95F52","#D4C0A7","#FAF6F1"),
]

# Every symbol is vector geometry, independent from original PDF writing ink.
# Coordinates for each symbol are 0..100; a scene combines >=2 subjects.
SYMBOLS={
 "mouse":'<ellipse cx="51" cy="62" rx="27" ry="19"/><circle cx="73" cy="45" r="12"/><circle cx="66" cy="31" r="8"/><circle cx="81" cy="32" r="8"/><circle cx="78" cy="44" r="2" class="a"/><path d="M26 64 Q6 49 4 67 M85 51 l9 2 M84 55 l9 5"/>',
 "turtle":'<ellipse cx="49" cy="61" rx="34" ry="20" class="p"/><path d="M20 61 L49 41 L79 62 L49 80 Z M49 41 V81 M20 61 H79" class="soft"/><circle cx="90" cy="62" r="9"/><circle cx="94" cy="61" r="2" class="a"/><path d="M25 79 l-10 8 M68 79 l10 8"/>',
 "deer":'<path d="M20 76 Q38 52 65 66 L71 87 M25 78 l-5 18 M49 76 l-3 19 M67 58 L73 31 M73 31 L62 19 M72 31 L84 13 M72 39 L89 29" /><ellipse cx="77" cy="56" rx="13" ry="10"/><circle cx="84" cy="55" r="2" class="a"/><circle cx="37" cy="67" r="3" class="a"/><circle cx="49" cy="68" r="3" class="a"/>',
 "cow":'<path d="M18 45 Q42 34 70 43 L75 77 H23 Z M25 76 v20 M65 77 v19 M70 44 l12-21 M18 46 L8 31"/><ellipse cx="72" cy="50" rx="18" ry="14" class="p"/><path d="M64 37 l-10 -17 M79 38 l11 -16"/><circle cx="77" cy="49" r="2" class="a"/>',
 "horse":'<path d="M23 96 L31 64 L23 40 Q38 31 50 17 L73 39 L62 46 L72 71 L66 95 M42 73 l-5 23 M19 44 Q2 54 10 68"/><path d="M32 40 l-10-20 M46 26 l9-16" class="soft"/><circle cx="54" cy="36" r="3" class="a"/>',
 "sheep":'<path d="M18 62 C4 52 18 36 31 44 C27 27 53 24 57 42 C72 28 88 49 77 62 C88 70 72 83 65 72 C55 87 34 82 33 75 Z" class="p"/><path d="M35 80 V96 M63 78 V96"/><ellipse cx="79" cy="63" rx="12" ry="11"/><circle cx="84" cy="62" r="2" class="a"/>',
 "dog":'<path d="M21 50 Q37 38 65 54 L75 79 H26 Z M28 80 l-3 16 M60 80 l2 16 M21 55 Q6 45 11 34"/><path d="M58 52 l9-22 l13 20 l-8 18 Z" class="p"/><circle cx="73" cy="53" r="2" class="a"/>',
 "cat":'<path d="M27 42 L23 18 L44 34 L62 34 L80 17 L79 43 Q94 69 76 82 H28 Q9 65 27 42Z" class="p"/><circle cx="42" cy="55" r="3" class="a"/><circle cx="66" cy="55" r="3" class="a"/><path d="M51 65 l4 3 l4-3 M24 68 L6 63 M25 73 L6 77 M78 67 L95 62 M78 73 l17 4"/>',
 "bird":'<path d="M12 61 Q30 24 50 45 Q68 32 90 57 Q57 45 43 75 Q34 87 12 61 Z" class="p"/><path d="M25 59 Q42 52 54 59 M64 60 l23 5" class="soft"/><circle cx="63" cy="51" r="2.5" class="a"/><path d="M83 56 L97 55 L84 63"/>',
 "fish":'<path d="M13 55 Q46 16 79 52 L97 30 L93 68 L79 54 Q48 92 13 55 Z" class="p"/><path d="M24 55 Q52 43 73 55 M35 41 l8-14 l14 17" class="soft"/><circle cx="29" cy="51" r="2.6" class="a"/>',
 "insect":'<ellipse cx="51" cy="57" rx="19" ry="25" class="p"/><circle cx="50" cy="28" r="13"/><path d="M44 17 Q34 4 26 13 M58 17 Q68 2 77 13 M33 47 L10 40 M32 59 L8 58 M37 75 L14 85 M69 47 L92 41 M70 59 L95 59 M63 75 L88 84 M51 32 V80" class="soft"/>',
 "boat":'<path d="M11 69 L94 69 Q78 91 31 91 Z" class="p"/><path d="M50 65 V12 M48 18 Q26 37 23 62 L48 62 Z M53 22 L80 60 H53 Z" /><path d="M3 98 Q16 91 28 97 T55 98 T85 97" class="soft"/>',
 "mountain":'<path d="M4 90 L35 20 L57 63 L73 37 L98 90 Z" class="p"/><path d="M24 46 L36 21 L47 48 M60 63 L73 36 L85 60" class="soft"/>',
 "bridge":'<path d="M5 83 Q48 9 95 83 L95 94 H83 Q73 65 50 60 Q28 64 18 94 H6 Z" class="p"/><path d="M11 65 H88 M26 59 V80 M72 57 V79" class="soft"/>',
 "stream":'<path d="M1 24 C32 6 42 45 75 29 C89 22 96 20 100 18 M0 51 C27 38 39 77 77 56 C89 50 95 52 100 49 M0 76 C26 66 43 96 80 80 C88 77 96 74 100 72" class="soft"/><circle cx="23" cy="38" r="4" class="a"/><circle cx="79" cy="70" r="3" class="a"/>',
 "cloud":'<path d="M14 72 Q4 49 28 43 Q28 19 51 22 Q72 10 79 37 Q100 40 92 66 Q80 81 60 72 Z" class="p"/><path d="M25 61 Q42 50 60 62 M66 52 Q77 52 81 63" class="soft"/>',
 "sun":'<circle cx="50" cy="50" r="23" class="p"/><path d="M50 2 v17 M50 81 v17 M2 50 h18 M80 50 h18 M17 17 l14 14 M69 69 l14 14 M83 17 L69 31 M17 83 L31 69" class="soft"/>',
 "moon":'<path d="M63 8 C34 25 32 69 70 88 C18 95 6 51 30 22 C42 11 55 9 63 8 Z" class="p"/><circle cx="78" cy="20" r="3" class="a"/><circle cx="87" cy="44" r="2.5" class="a"/>',
 "star":'<path d="M50 4 L63 35 L97 38 L72 60 L79 94 L50 76 L21 94 L28 60 L3 38 L37 35 Z" class="p"/><circle cx="10" cy="9" r="3" class="a"/><circle cx="84" cy="12" r="3" class="a"/>',
 "rain":'<path d="M20 33 Q50 8 78 33 Q70 52 49 55 Q25 52 20 33 Z" class="p"/><path d="M30 68 l-7 17 M52 70 l-8 23 M72 64 l-9 23" class="soft"/>',
 "snow":'<path d="M50 4 V96 M4 50 H96 M16 16 L84 84 M84 16 L16 84 M39 15 L50 4 L61 15 M39 85 l11 11 l11 -11" class="soft"/><circle cx="50" cy="50" r="10" class="p"/>',
 "tree":'<path d="M45 93 V60 L19 70 L10 54 L31 37 Q13 19 36 15 Q52 -2 68 16 Q94 13 86 38 Q101 55 81 64 L57 59 V93 Z" class="p"/><path d="M50 60 L36 40 M53 61 L67 34" class="soft"/>',
 "bamboo":'<path d="M34 98 V9 M54 98 V8 M73 98 V14 M30 41 H58 M49 66 H79 M31 77 H74" class="soft"/><path d="M33 38 Q2 30 15 10 Q40 20 33 38 M56 57 Q89 38 98 48 Q76 69 56 57 M73 23 Q98 3 99 20 Q83 38 73 23" class="p"/>',
 "flower":'<circle cx="50" cy="45" r="10" class="a"/><ellipse cx="50" cy="24" rx="12" ry="16" class="p"/><ellipse cx="71" cy="43" rx="16" ry="12" class="p"/><ellipse cx="50" cy="63" rx="12" ry="16" class="p"/><ellipse cx="29" cy="43" rx="16" ry="12" class="p"/><path d="M50 77 V99 M50 88 Q22 80 18 94 M50 87 Q80 73 88 88" class="soft"/>',
 "grass":'<path d="M50 97 Q35 54 16 42 M50 97 Q51 35 52 12 M50 97 Q71 57 92 44 M50 97 Q34 71 19 70" class="soft"/><ellipse cx="30" cy="62" rx="9" ry="18" class="p"/><ellipse cx="69" cy="64" rx="9" ry="18" class="p"/>',
 "grain":'<path d="M50 96 V12 M48 30 Q18 10 18 30 L46 49 M53 39 Q86 13 86 36 L53 57 M46 56 Q20 42 16 55 L46 73 M53 70 Q85 47 86 63 L54 81" class="p"/>',
 "fruit":'<path d="M50 24 Q29 11 18 34 Q5 67 37 87 Q50 97 63 87 Q92 69 81 38 Q73 13 50 24Z" class="p"/><path d="M50 29 L55 7 M54 16 Q72 3 83 18 Q65 31 54 16" class="soft"/>',
 "scroll":'<path d="M22 17 H80 V85 H22 Q13 84 12 74 V27 Q13 18 22 17 Z" class="p"/><path d="M27 33 H73 M27 44 H69 M27 55 H71 M27 66 H62" class="soft"/><circle cx="21" cy="18" r="8" class="a"/><circle cx="21" cy="84" r="8" class="a"/>',
 "book":'<path d="M8 22 Q31 14 49 29 V88 Q27 77 8 84 Z M49 29 Q72 14 92 21 V84 Q68 77 49 88Z" class="p"/><path d="M15 36 Q30 34 42 41 M15 51 Q31 48 42 55 M56 40 Q72 34 83 35 M56 55 Q71 50 84 52" class="soft"/>',
 "brush":'<path d="M16 84 L74 24 L83 34 L27 92 Z" class="p"/><path d="M69 22 L80 10 L94 24 L83 36 Z" class="a"/><path d="M9 89 Q19 88 23 79 L33 90 Q23 99 8 95" class="soft"/>',
 "door":'<path d="M19 95 V13 H82 V95 M29 94 V24 H72 V95 M50 25 V95" class="p"/><circle cx="42" cy="62" r="2.5" class="a"/><circle cx="60" cy="62" r="2.5" class="a"/>',
 "window":'<path d="M13 92 V44 L49 12 L87 44 V92 Z" class="p"/><path d="M28 88 V49 H73 V88 M49 49 V89 M28 65 H72" class="soft"/>',
 "lantern":'<path d="M49 4 V18 M34 19 H66 M27 32 Q50 16 72 32 V66 Q50 88 27 66 Z M34 77 H66 M49 80 V96" class="p"/><path d="M29 43 H71 M29 60 H71" class="soft"/>',
 "umbrella":'<path d="M7 51 Q50 4 93 51 Q79 47 64 51 Q50 45 35 51 Q20 46 7 51 Z" class="p"/><path d="M50 15 V86 Q50 103 34 89" class="soft"/>',
 "road":'<path d="M36 98 Q46 69 34 44 Q18 21 45 6 M65 98 Q71 69 64 44 Q47 22 68 6" class="soft"/><path d="M51 96 L51 78 M51 62 L52 48 M52 29 L53 21" class="a"/>',
 "sign":'<path d="M47 98 V14 M17 21 H83 L93 36 L83 51 H17 Z" class="p"/><path d="M35 36 H77 l-10-8 M77 36 l-10 8" class="soft"/>',
 "pot":'<path d="M32 17 H72 L69 33 Q91 60 68 91 H31 Q9 58 35 32 Z" class="p"/><path d="M23 49 Q0 41 18 62 Q26 68 32 61 M72 50 Q94 38 86 63 Q80 68 72 63 M37 46 H64 M39 60 H62" class="soft"/>',
 "tea":'<path d="M18 36 H75 V70 Q70 91 49 89 Q24 91 18 70 Z" class="p"/><path d="M75 43 Q101 42 92 67 Q85 75 76 68 M33 20 Q20 8 36 4 M54 21 Q43 10 56 2" class="soft"/>',
 "clock":'<circle cx="50" cy="50" r="42" class="p"/><path d="M50 19 V51 L71 63 M50 10 V17 M50 83 V92 M10 51 H19 M82 51 H90" class="soft"/>',
 "wheel":'<circle cx="50" cy="50" r="40" class="p"/><circle cx="50" cy="50" r="9" class="a"/><path d="M50 11 V41 M50 59 V90 M10 50 H41 M59 50 H90 M22 22 L43 43 M57 57 L78 78 M78 22 L57 43 M43 57 L22 78" class="soft"/>',
 "bell":'<path d="M22 71 Q28 61 29 36 Q32 14 50 14 Q68 14 71 36 Q71 60 78 71 Z" class="p"/><path d="M20 73 H81 M43 83 Q50 95 59 83" class="soft"/><circle cx="50" cy="11" r="5" class="a"/>',
 "tools":'<path d="M12 85 L74 22 L85 33 L22 96 Z M62 18 L81 5 L96 19 L86 30" class="p"/><path d="M16 12 L26 12 L26 71 L16 71 Z M16 20 H23 M16 32 H23 M16 44 H23 M16 56 H23" class="soft"/>',
 "cloth":'<path d="M33 13 L16 26 L7 62 L28 69 L36 51 V93 H75 V51 L83 69 L97 62 L84 26 L66 13 Q51 39 33 13Z" class="p"/><path d="M35 25 Q51 45 65 25 M36 80 H75" class="soft"/>',
 "hand":'<path d="M23 90 L19 51 Q18 42 26 43 L33 67 L33 18 Q32 10 40 12 L44 59 L45 11 Q45 4 54 8 L57 57 L62 18 Q67 11 75 18 L72 63 Q83 45 91 51 Q97 58 82 83 L71 94Z" class="p"/>',
 "person":'<circle cx="50" cy="20" r="12" class="p"/><path d="M50 34 V72 M50 46 L24 61 M50 45 L77 56 M50 72 L29 98 M50 72 L70 98" class="soft"/>',
 "eye":'<path d="M8 49 Q50 6 92 49 Q53 94 8 49Z" class="p"/><circle cx="51" cy="49" r="17" class="soft"/><circle cx="51" cy="49" r="8" class="a"/>',
 "ear":'<path d="M32 70 Q13 50 25 22 Q47 -5 77 24 Q95 55 68 77 Q53 89 55 96 Q31 105 30 79 M42 71 Q30 45 49 34 Q75 20 75 50 Q73 62 60 67" class="p"/>',
 "tooth":'<path d="M30 12 Q48 3 57 15 Q80 3 89 22 Q98 41 76 90 Q64 108 61 72 Q58 53 50 73 Q40 108 30 86 Q5 31 30 12 Z" class="p"/>',
 "heart":'<path d="M50 91 Q-4 57 15 26 Q33 1 50 27 Q72 -1 90 27 Q107 57 50 91Z" class="p"/>',
 "foot":'<path d="M19 50 Q28 21 43 28 Q54 33 51 61 Q72 59 84 69 Q95 88 66 92 H33 Q12 90 19 50Z" class="p"/><circle cx="23" cy="20" r="6"/><circle cx="36" cy="16" r="6"/><circle cx="50" cy="19" r="5"/>',
 "arrow":'<path d="M17 89 L81 25 M63 20 L89 17 L84 43 M75 31 L90 16" class="soft"/><path d="M18 88 l-5 10 l10 -5 Z" class="p"/>',
 "puzzle":'<path d="M11 12 H39 Q31 35 48 38 Q66 35 58 12 H88 V41 Q67 35 66 52 Q68 69 88 60 V88 H57 Q64 66 47 65 Q30 69 39 88 H11 V61 Q33 70 35 51 Q32 33 11 41 Z" class="p"/>',
 "stone":'<path d="M8 86 L25 29 L67 15 L94 67 L72 92 Z" class="p"/><path d="M25 29 L55 65 L94 67 M55 65 L43 90" class="soft"/>',
 "fire":'<path d="M56 3 Q31 37 46 53 Q26 49 23 31 Q-2 65 28 90 Q50 106 70 85 Q95 60 74 38 Q73 59 62 62 Q54 53 56 3Z" class="p"/><path d="M51 50 Q36 73 49 90 Q63 89 65 73 Q60 67 51 50" class="a"/>',
}

def choose_motifs(brief,title,sentence):
    found=[]
    for phrase in (brief, title, sentence):
        for kind,regex in MOTIFS:
            if kind not in found and re.search(regex,phrase):
                found.append(kind)
        if len(found)>=3:break
    if not found:
        raise ValueError("Cannot relate illustration to its original editorial story")
    if len(found)==1:
        # A cultural scene may include one nonassertive atmospheric prop, not
        # a false second claimed lexical interpretation of the radical.
        found.append("cloud" if found[0] not in ("cloud","sun","star") else "tree")
    return found[:3]

def build_scene(glyph,brief,title,sentence):
    mid=glyph["main_id"]
    key=glyph["theme_key"]
    if not key or len(brief)<5:
        raise ValueError("A source-linked semantic illustration brief is required")
    motif=choose_motifs(brief,title,sentence)
    ink,accent,soft,paper=PALS[mid%len(PALS)]
    digest=hashlib.sha256((key+"|"+brief).encode()).digest()
    dy=digest[0]%47-24
    x0=105+digest[1]%32
    y0=185+digest[2]%35
    x1=410+digest[3]%60
    y1=222+digest[4]%36
    sc0=2.49+digest[5]/1300
    sc1=1.90+digest[6]/1680
    waves=[
       (f'<path d="M-8 {532+dy} Q148 {487+dy} 310 {536+dy} T820 {519+dy}" fill="none" stroke="{soft}" stroke-width="6" opacity=".65"/>'),
       (f'<path d="M0 {554+dy} Q180 {521+dy} 346 {565+dy} T825 {532+dy}" fill="none" stroke="{ink}" stroke-width="3" opacity=".16"/>')
    ]
    objects=[]
    coords=[(x0,y0,sc0),(x1,y1,sc1),(325,70,1.12)]
    for i,name in enumerate(motif):
        x,y,size=coords[i]
        if i==2:size=1.10
        objs=SYMBOLS[name]
        objects.append(f'<g data-motif="{name}" transform="translate({x:.1f} {y:.1f}) scale({size:.3f})" '
                       f'stroke="{ink}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round">'
                       +objs+'</g>')
    # Deliberately mild engraving grain: varies per independent scene.
    ticks=[]
    for i in range(14):
        x=(digest[(i+7)%32]*17+i*43)%800+9
        y=(digest[(i+15)%32]*11+i*31)%550+30
        ticks.append(f'<path d="M{x} {y} l{3+(i%5)} {-2-(i%3)}" stroke="{soft}" stroke-width="2" opacity=".30"/>')
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="630" viewBox="0 0 820 630" '
         f'role="img" data-scene="{html.escape(key,quote=True)}" '
         f'aria-label="{html.escape(brief,quote=True)}">'
         f'<title>{html.escape(brief)}</title>'
         '<style>.p{fill:'+paper+'}.a{fill:'+accent+';stroke:'+accent+'}.soft{stroke:'+soft+';fill:none}</style>'
         f'<rect x="0" y="0" width="820" height="630" rx="28" fill="{paper}"/>'
         f'<circle cx="{145+digest[1]%45}" cy="{145+digest[2]%45}" r="119" fill="{soft}" opacity=".10"/>'
         f'<circle cx="{655-digest[3]%56}" cy="{155+digest[4]%40}" r="91" fill="{accent}" opacity=".05"/>'
         +''.join(ticks)+''.join(waves)+''.join(objects)
         +f'<path d="M26 605 H794" stroke="{ink}" stroke-width="3" opacity=".18"/>'
         +'</svg>\n')
    ET.fromstring(svg)
    return svg,motif

def create(output_dir:Path,registry:Path,root:Path=ROOT):
    drafts=checked_drafts(root)
    known={x["main_id"] for x in drafts.values() if x["artwork_stage"]=="four_unique_svg_drafts_not_approved"}
    if known!={39,64,77,88}:
        raise ValueError("Original 4 registered P3 scenes missing")
    output_dir.mkdir(parents=True,exist_ok=True)
    art=[];dups=set();scenes=[]
    for mid in range(1,202):
        d=drafts[mid]
        if mid in known:continue
        desc=d.get("art_brief")
        if not desc:
            raise ValueError(f"Main ID {mid} has no distinctive cultural drawing brief")
        raw,motif=build_scene(d,desc,d["title"],d["sentence"])
        digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if digest in dups:raise ValueError("Duplicate art image across 197 subjects")
        dups.add(digest)
        name=f"ID{mid:03d}-{d['theme_key']}.svg"
        if re.search(r"[^a-zA-Z0-9_.-]",name):
            raise ValueError("Unsafe illustration filename")
        destination=output_dir/name
        destination.write_text(raw,encoding="utf-8")
        art.append({"main_id":mid,"character":d["character"],"theme_key":d["theme_key"],
                    "filename":name,"art_asset_id":f"p45-scene-{mid:03d}",
                    "source_illustration_brief":desc,"motifs":motif,
                    "sha256":digest,"bytes":len(raw.encode("utf-8")),
                    "editorial_state":"vector_draft_unreviewed",
                    "license_review":"internally_generated_pending_art_review",
                    "human_visual_signoff":False,
                    "release_eligible":False})
        scenes.extend(motif)
    if len(art)!=197:
        raise ValueError("Exactly 197 distinct source-linked vector drafts required")
    report={
        "schema_version":1,
        "status":"197_REAL_SVG_DRAFTS_WITH_SOURCE_LINKED_THEMES_NOT_RELEASED",
        "source_pdf_sha256":SHA,
        "total_glyphs":201,
        "existing_svg_artwork_not_replaced":4,
        "generated_unique_svg_scenes":197,
        "generated_png_raster_assets":0,
        "fake_teaching_strokes":0,
        "editorial_approved":0,
        "automated_svg_generator_version":"p45-vector-scene-1",
        "motif_use_counts":dict(sorted(Counter(scenes).items())),
        "entries":art}
    registry.parent.mkdir(parents=True,exist_ok=True)
    registry.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="entries"},ensure_ascii=False,indent=2))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--registry",required=True,type=Path)
    p.add_argument("--root",type=Path,default=ROOT)
    a=p.parse_args()
    create(a.output_dir,a.registry,a.root)
if __name__=="__main__":
    main()
