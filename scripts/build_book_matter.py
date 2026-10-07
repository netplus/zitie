#!/usr/bin/env python3
"""Build deterministic P7 table-of-contents and back-matter PDFs.

This is editorial navigation material, not new normative evidence.
"""
import argparse
import json
import math
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
W,H=A4
L,R=42,W-42
INK=HexColor('#282B2D')
RED=HexColor('#BB3D42')
MUTED=HexColor('#74777A')
RULE=HexColor('#D8C2C4')

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def register_font(_path=None):
    # Use ReportLab's built-in CJK CID font instead of relying on distro TTC/CFF
    # files that TTFont cannot load portably on GitHub Actions.
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    return 'STSong-Light'

def txt(c,x,y,s,size=9,color=INK,font='APPENDIX_CJK'):
    c.setFillColor(color); c.setFont(font,size); c.drawString(x,y,str(s))

def right(c,x,y,s,size=9,color=INK,font='APPENDIX_CJK'):
    c.setFillColor(color); c.setFont(font,size); c.drawRightString(x,y,str(s))

def header(c,title,subtitle,page_label):
    txt(c,L,H-48,title,20,RED)
    txt(c,L,H-68,subtitle,9,MUTED)
    right(c,R,H-48,page_label,9,MUTED)
    c.setStrokeColor(RULE); c.setLineWidth(.7); c.line(L,H-80,R,H-80)

def footer(c,note):
    c.setStrokeColor(RULE); c.line(L,35,R,35)
    txt(c,L,22,note,7.5,MUTED)

def stroke_count(e):
    if isinstance(e.get('stroke_count'),int): return e['stroke_count']
    if isinstance(e.get('stroke_names'),list): return len(e['stroke_names'])
    r=e.get('fine_stroke_names_review') or {}
    if isinstance(r.get('adjudicated_names'),list): return len(r['adjudicated_names'])
    if isinstance(e.get('stroke_names_candidate'),list): return len(e['stroke_names_candidate'])
    raise ValueError(e['character']+': missing stroke count')

def page_count(e):
    return max(1,math.ceil(stroke_count(e)/6))

def build_navigation():
    batches=load('data/batches.json')['frozen_batches']
    batch_data={b['id']:load(f"data/{b['id']}.json") for b in batches}
    preface_pages=3
    toc_pages=2
    first_practice_page=preface_pages+toc_pages+1
    current=first_practice_page
    batch_ranges={}
    item_ranges=[]
    for b in batches:
        start=current
        for e in batch_data[b['id']]['entries']:
            pages=page_count(e)
            item_ranges.append({
                'main_id':e['main_id'],'character':e['character'],'batch':b['id'],
                'start':current,'end':current+pages-1,'pages':pages
            })
            current+=pages
        batch_ranges[b['id']]={'start':start,'end':current-1,'title':b['title'],'glyphs':b['main_glyphs']}
    return batches,batch_ranges,item_ranges,current

def build_toc(path,font):
    batches,ranges,items,back_start=build_navigation()
    c=canvas.Canvas(str(path),pagesize=A4,pageCompression=1,invariant=1)
    c.setTitle('循序渐进汉字部首字帖｜目录与导航')
    halves=[batches[:11],batches[11:]]
    for p,rows in enumerate(halves,1):
        header(c,'目录与学习导航','P7全书编排；页码基于当前release-candidate结构生成',f'目录 {p}/2')
        y=H-110
        for b in rows:
            rg=ranges[b['id']]
            txt(c,L,y,b['id'],10,RED)
            txt(c,L+44,y,b['title'],10)
            right(c,R,y,f"{rg['start']}–{rg['end']}",10)
            txt(c,L+44,y-15,b['main_glyphs'],9,MUTED)
            y-=43
        if p==2:
            y-=4
            txt(c,L,y,'卷末导航',11,RED); y-=22
            txt(c,L,y,f'201主部首索引、教学附形/位置变体索引、原27项对应表与来源/版本说明自第 {back_start} 页起。',9)
            y-=18
            txt(c,L,y,'32项变体均为教学候选；GF0011—2022正式附形身份仍source-blocked，不以本索引替代规范原表。',8.5,MUTED)
        footer(c,'目录页只提供学习导航，不改变任何字段review/fail-closed结论。')
        c.showPage()
    c.save()
    if len(PdfReader(str(path)).pages)!=2: raise ValueError('TOC must be exactly 2 pages')
    return 2

def build_backmatter(path,font):
    coverage=load('data/coverage.json')
    variants=load('data/variants.json')
    sources=load('sources/catalog.json')
    _,_,items,_=build_navigation()
    items_by_main_id=sorted(items,key=lambda row: row['main_id'])
    c=canvas.Canvas(str(path),pagesize=A4,pageCompression=1,invariant=1)
    c.setTitle('循序渐进汉字部首字帖｜卷末索引与复核说明')
    page_no=0

    # 201 main-radical index: 34 rows/page => 6 pages.
    rows_per=34
    for chunk_start in range(0,len(items_by_main_id),rows_per):
        page_no+=1
        chunk=items_by_main_id[chunk_start:chunk_start+rows_per]
        header(c,'201主部首索引','按main_id排序；页码对应本版练习页',f'索引 {page_no}/13')
        y=H-104
        txt(c,L,y,'ID',8,RED); txt(c,L+34,y,'主部首',8,RED); txt(c,L+92,y,'批次',8,RED); txt(c,L+145,y,'页码',8,RED)
        y-=18
        for row in chunk:
            txt(c,L,y,f"{row['main_id']:03d}",8)
            txt(c,L+34,y,row['character'],11)
            txt(c,L+92,y,row['batch'],8)
            pg=str(row['start']) if row['start']==row['end'] else f"{row['start']}–{row['end']}"
            txt(c,L+145,y,pg,8)
            y-=19
        footer(c,'索引只定位201个主部首；附形/位置变体另表，不重复计入201。')
        c.showPage()

    # 32 variant teaching candidates: 16/page => 2 pages.
    vars_=variants['items']
    for chunk_start in range(0,len(vars_),16):
        page_no+=1
        chunk=vars_[chunk_start:chunk_start+16]
        header(c,'常用附形与位置变体索引','32项教学候选；正式GF0011—2022附形身份保持source-blocked',f'索引 {page_no}/13')
        y=H-104
        for v in chunk:
            txt(c,L,y,v['id'],8,RED)
            txt(c,L+44,y,f"{v['parent']} → {v['form']}",12)
            txt(c,L+145,y,f"例：{v['example']} / {v['position']}",9)
            txt(c,L+300,y,'教学候选',8,MUTED)
            y-=38
        footer(c,'禁止把本表32项教学候选改写为GF0011—2022正式附形清单。')
        c.showPage()

    # Historical legacy V001-V027 mapping: 14/page => 2 pages.
    legacy=vars_[:27]
    for chunk_start in range(0,len(legacy),14):
        page_no+=1
        chunk=legacy[chunk_start:chunk_start+14]
        header(c,'原27项对应表','历史重点回归集合 V001—V027；当前32项候选范围中的兼容子集',f'索引 {page_no}/13')
        y=H-104
        for v in chunk:
            txt(c,L,y,v['id'],8,RED)
            txt(c,L+44,y,f"{v['parent']} / {v['form']} / {v['example']} / {v['position']}",10)
            y-=39
        footer(c,'原27项是重点回归集合，不等于全书附形/位置变体的完整规范清单。')
        c.showPage()

    # Source / review summary: 2 pages.
    page_no+=1
    header(c,'来源与字段复核说明','只汇总仓库已经持久化的状态，不新增来源结论',f'索引 {page_no}/13')
    y=H-110
    progress=coverage['phase1_content_progress']
    summary=[
        ('P1 笔顺','201/201 reviewed'),
        ('P2 细笔名','157 reviewed + 14 conflict_fail_closed'),
        ('P3 其它字段','普通pending=0；保留精确fail-closed/not-applicable'),
        ('P4 位置迁移','198 reviewed + 3 conflict_fail_closed'),
        ('GF0011—2022逐项精确字段','201 source_blocked_fail_closed'),
        ('P5 内容','201/201 content_ready'),
        ('P6 artwork/layout','201/201 artwork_ready + layout_ready')
    ]
    for k,v in summary:
        txt(c,L,y,k,10,RED); txt(c,L+170,y,v,9); y-=31
    y-=10
    txt(c,L,y,'来源边界',11,RED); y-=24
    lines=[
        '规范原件审读、机器结构检查、矢量匹配和版面视觉QA分别记录；任何一项不能替代其它门槛。',
        'Hanzi Writer仅提供绘图材料，不作为规范笔顺或部首身份依据。',
        'secondary locator/crosscheck只用于定位与风险筛选，不能授予最终reviewed。',
        'GF0011—2022逐项正式主形/附形/名称/编码取得前，相关精确字段继续fail-closed。'
    ]
    for line in lines:
        txt(c,L,y,line,8.5); y-=24
    footer(c,'完整证据路径以data/evidence、reviews、sources及deliverables/manifest.json为准。')
    c.showPage()

    page_no+=1
    header(c,'关键来源台账','来源ID与出版物身份；详细哈希/页数以sources/catalog.json为准',f'索引 {page_no}/13')
    y=H-105
    for s in sources['sources']:
        sid=s.get('id','')
        title=s.get('title') or s.get('publication_id') or ''
        pub=s.get('publication_id','')
        if not (sid or title): continue
        txt(c,L,y,sid,8,RED)
        txt(c,L+45,y,(pub+' '+title)[:42],8.5)
        y-=24
        if y<70: break
    footer(c,'这里只做书目导航；实际字段采用范围须回对应evidence/review。')
    c.showPage()

    # Version/errata record: 1 page.
    page_no+=1
    header(c,'版本、勘误与发布状态','本页记录当前候选结构；正式release另需P7最终门槛',f'索引 {page_no}/13')
    y=H-110
    records=[
      ('v0.1.0','B01阶段稿，历史保留，不覆盖'),
      ('v0.2.0','B01+B02阶段稿'),
      ('v0.2.1','B01+B02内容复核修订稿'),
      ('v0.3.0','201主项全书draft；已归档，仍非正式release'),
      ('当前release','0；deliverables/releases/仍为空')
    ]
    for ver,note in records:
        txt(c,L,y,ver,10,RED); txt(c,L+95,y,note,9); y-=34
    y-=10
    txt(c,L,y,'重开条件',11,RED); y-=25
    txt(c,L,y,'如取得GF0011—2022正式逐项表或等效官方数据，需重开相关source-blocked字段并重新跑P5—P7受影响门槛。',8.5)
    y-=32
    txt(c,L,y,'正式PDF不得由本页状态文字自动升级；以deliverables/manifest.json、目标HEAD CI和最终release记录共同为准。',8.5)
    footer(c,'历史draft不覆盖；新修订使用新版本目录并保留旧字节。')
    c.showPage()

    c.save()
    pages=len(PdfReader(str(path)).pages)
    if pages!=13: raise ValueError(f'Back matter must be 13 pages, got {pages}')
    return pages

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--font',default=None,help='Deprecated; built-in STSong-Light CID font is used for portability.')
    args=p.parse_args()
    font=register_font(args.font)
    out=ROOT/'build'; out.mkdir(exist_ok=True)
    toc=out/'toc_v0.4.0.pdf'
    back=out/'backmatter_v0.4.0.pdf'
    toc_pages=build_toc(toc,font)
    back_pages=build_backmatter(back,font)
    meta={'toc_file':toc.name,'toc_pages':toc_pages,'backmatter_file':back.name,'backmatter_pages':back_pages,
          'status':'P7_release_structure_material_generated_not_yet_archived_or_released'}
    (out/'generation_book_matter.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False))

if __name__=='__main__':
    main()
