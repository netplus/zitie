#!/usr/bin/env python3
"""P4.2: generate a complete 201-main-glyph cultural reading engineering PDF.

This is NOT the final artwork, dictionary-approved phonetics, or formal book.
All 1045 cumulative stroke cards are embedded with show_pdf_page() *directly*
from the frozen v0.5.1 released PDF; never redraw or synthesize teaching ink.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path

import fitz
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image
import numpy as np

from build_cultural_sample import fonts, original_specimen
from cultural_fullbook_model import make_plan, CAPACITY_FIRST, CAPACITY_MORE, ROOT, SHA
from cultural_p3_artwork import read_registry, paint_scene
from cultural_p45_asset_pack import checked_assets, paint as paint_cultural_scene
from cultural_source_audit import audit

MM=72.0/25.4
W,H=210*MM,297*MM
BASE_PAGES=6                 # Cover, instructions and four navigation pages
TOC_ENTRIES_PER_PAGE=54      # 3 columns x 18 entries
TOC_PAGES=4
TILE_MM=31.0
RED="#943E48";INK="#2E383D";GRAY="#657177";PALE="#D8B6B8"
FAINT="#F8F5F1";WHITE="#FFFEFC"
COVER_X=(17.0,50.0,83.0)
MORE_X=(17.5,53.5,89.5,125.5,161.5)
MORE_Y=(105.0,164.0,223.0)

def mm(value): return float(value)*MM

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def paginate(plan:dict):
    page=BASE_PAGES+1
    for glyph in plan["entries"]:
        glyph["first_preview_pdf_page"]=page
        page+=glyph["page_parts"]
    plan["expected_total_pdf_pages"]=page-1
    plan["expected_glyph_pdf_pages"]=sum(x["page_parts"] for x in plan["entries"])
    plan["expected_continuation_pages"]=sum(x["page_parts"]-1 for x in plan["entries"])
    if plan["expected_glyph_pdf_pages"]<201:
        raise ValueError("No main ID may be omitted in all-book paging")
    return plan

class PageArtist:
    def __init__(self,pdf_canvas):
        self.c=pdf_canvas

    def rect(self,x,y,w,h,color=WHITE,stroke=None,radius=0):
        c=self.c
        c.setFillColor(HexColor(color))
        if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(mm(.25))
        if radius:c.roundRect(mm(x),H-mm(y+h),mm(w),mm(h),mm(radius),
                              stroke=int(bool(stroke)),fill=1)
        else:c.rect(mm(x),H-mm(y+h),mm(w),mm(h),stroke=int(bool(stroke)),fill=1)

    def line(self,x0,y0,x1,y1,color=PALE,width=.2):
        c=self.c;c.setStrokeColor(HexColor(color));c.setLineWidth(mm(width))
        c.line(mm(x0),H-mm(y0),mm(x1),H-mm(y1))

    def runs(self,text,face):
        """Use embedded original Kaishu except rare Hanzi absent from it.

        Official 201 main radicals include U+4E5B and uncommon forms that
        cannot be rendered by the legacy 7574-glyph Arphic simplified Kai font.
        AR PL UMing fallback is also locally installed; never draw a tofu/null.
        """
        primary="Culture"+face
        base=pdfmetrics.getFont(primary).face.charWidths
        rare=pdfmetrics.getFont("CultureRare").face.charWidths
        out=[]
        for ch in str(text):
            font=primary if ord(ch) in base else "CultureRare"
            if ord(ch) not in rare and font=="CultureRare":
                raise ValueError(f"No installed embeddable font covers U+{ord(ch):04X} {ch}")
            if out and out[-1][0]==font:
                out[-1]=(font,out[-1][1]+ch)
            else:
                out.append((font,ch))
        return out

    def text_width(self,text,face,size):
        return sum(pdfmetrics.stringWidth(run,font,size)
                   for font,run in self.runs(text,face))

    def label(self,x,y,text,size=10,face="Kai",color=INK,align="left"):
        runs=self.runs(text,face)
        if align!="left":
            width=self.text_width(text,face,size)
            if align=="center":x-=width/MM/2
            elif align=="right":x-=width/MM
        cursor=mm(x)
        self.c.setFillColor(HexColor(color))
        for font,run in runs:
            self.c.setFont(font,size)
            self.c.drawString(cursor,H-mm(y),run)
            cursor+=pdfmetrics.stringWidth(run,font,size)

    def rows(self,text,width,size=9.2,face="Kai",max_lines=7):
        value=str(text or "")
        if not value:return []
        result=[]
        for source in value.splitlines():
            part=""
            for ch in source:
                if self.text_width(part+ch,face,size)>mm(width):
                    if not part:raise ValueError("One text glyph exceeds available width")
                    result.append(part);part=ch
                else:part+=ch
            if part:result.append(part)
        if len(result)>max_lines:
            raise ValueError(f"Editorial content needs more space: {value[:36]} ({len(result)} lines)")
        return result

    def fitted(self,x,y,text,maximum_mm,base=18,minimum=12,color=RED):
        size=base
        while size>minimum and self.text_width(text,"Kai",size)>mm(maximum_mm):
            size-=.5
        if self.text_width(text,"Kai",size)>mm(maximum_mm):
            raise ValueError("Cultural title cannot fit even at safe minimum: "+text)
        self.label(x,y,text,size,"Kai",color)

    def section(self,x,y,label,end):
        self.rect(x,y-1,1.1,5,RED)
        self.label(x+3,y+3,label,10.5,"Kai",RED)
        width=self.text_width(label,"Kai",10.5)/MM
        start=x+3+width+3
        if start<end-2:self.line(start,y+1.7,end,y+1.7)

    def page_border(self,page,source_note=""):
        self.rect(0,0,210,297,WHITE)
        c=self.c
        c.setLineWidth(mm(.23));c.setStrokeColor(HexColor("#C8A4A4"))
        c.rect(mm(9),mm(9),mm(192),mm(279),fill=0,stroke=1)
        self.line(17,285,193,285,"#D7CDCC")
        for x,y,dx,dy in ((11,11,1,1),(199,11,-1,1),
                          (11,285,1,-1),(199,285,-1,-1)):
            self.line(x,y,x+4*dx,y,RED,.35)
            self.line(x,y,x,y+4*dy,RED,.35)
        self.label(18,290,source_note or "文化识字版 · 工程待审稿",6.9,"Song",GRAY)
        self.label(193,290,f"{page}  ·  禁止作为正式教材发行",
                   6.9,"Song",RED,"right")

def base_cover(a:PageArtist,plan):
    a.page_border(1,"循序渐进 · 文化识字版 P4.2")
    a.label(27,44,"循 序 渐 进",16,"Song",GRAY)
    a.line(26,52,185,52,PALE,.42)
    a.label(26,83,"文化识字",34,"Kai",RED)
    a.label(26,104,"全量工程稿",28,"Kai",INK)
    a.label(27,129,"以原书真笔顺为骨，以文化阅读为翼",13,"Kai",GRAY)
    a.rect(26,154,157,58,FAINT,None,3)
    a.label(35,169,"201  主字 / 主部首",15,"Kai",RED)
    a.label(35,184,"1045  原书累计笔顺 · 21  批次",12,"Kai",INK)
    a.label(35,198,"201  字独立文化文字初稿 · 内容均待审定",10.5,"Kai",GRAY)
    a.label(27,240,"稿件状态：仅供教学内容审读与排版验收",11,"Kai",RED)
    a.label(27,251,"正文、拼音、插图及引文未经全书审核，不得印作正式教材。",9.3,"Kai",GRAY)
    a.label(27,266,"原 v0.5.1 正式 PDF 不变；附形偏旁另行独立复核。",9.0,"Kai",GRAY)
    a.c.showPage()

def instructions(a:PageArtist,plan):
    a.page_border(2,"201 字全量工程版 · 阅读说明")
    a.label(20,30,"全书说明与审校边界",22,"Kai",RED)
    a.line(20,35,190,35,PALE,.45)
    blocks=[
        ("01  笔顺来源","每笔均取已发行 v0.5.1 的真实累计矢量图。先显示原书笔顺提示，再逐幅展示；既有笔灰色，当前笔红色。"),
        ("02  字音与字词","主字只采用正式PDF的原有单字读音；812个词语或构字字例中804项显示候选拼音，8项多音仍待辨析，全部尚需人工审音。"),
        ("03  文化内容","201个主字均已编写独立主题、释义、短句和相关字词草案；词音、出处和文稿仍需逐项审校，不将初稿当成定稿。"),
        ("04  插图与版权","全书已经绘入201张文化主题矢量画稿：保留原4幅，新增197幅有独立SVG和校验码。程序绘图非专业美术审定，题材与授权仍需人工复核。"),
        ("05  偏旁附形","本工程只覆盖 201 个原书主字/主部首。氵、亻、扌等附形不得借用完整字源图冒名出版。"),
        ("06  页数与导航","页码按笔数动态生成。一个汉字笔画较多时自动连续续页；目录与书签直接跳转到该字的首页。"),
    ]
    y=49
    for head,desc in blocks:
        a.label(20,y,head,12,"Kai",RED)
        for j,line in enumerate(a.rows(desc,166,10.2,max_lines=3)):
            a.label(21,y+8+j*6.3,line,10.2)
        y+=36
    a.line(20,269,190,269)
    a.label(20,278,"工程验收：201 ID / 1045 笔 / 完整分页 / 字节重建一致 / 全页渲染。",9.2,"Kai",GRAY)
    a.c.showPage()

def index_pages(a:PageArtist,plan):
    glyphs=plan["entries"]
    if TOC_PAGES*TOC_ENTRIES_PER_PAGE<201:
        raise ValueError("Full index lacks capacity")
    links=[]
    for page_no in range(TOC_PAGES):
        physical=3+page_no
        a.page_border(physical,"201 主字索引 · 原书批次顺序")
        a.label(17,29,f"全书字目索引  {page_no+1}/{TOC_PAGES}",20,"Kai",RED)
        a.label(18,38,"批次 / 源主 ID / 主字与本书起始页",9,"Kai",GRAY)
        a.line(17,43,193,43,PALE,.35)
        part=glyphs[page_no*TOC_ENTRIES_PER_PAGE:
                    (page_no+1)*TOC_ENTRIES_PER_PAGE]
        for i,row in enumerate(part):
            col=i//18;line=i%18
            x=17.5+59.5*col;y=58+11.8*line
            a.label(x,y,row["batch_id"],7,"Latin",GRAY)
            a.label(x+11,y,row["character"],12,"Kai",RED)
            a.label(x+23,y,f"ID{row['main_id']:03d}",7.3,"Latin",GRAY)
            a.label(x+54,y,str(row["first_preview_pdf_page"]),9,
                    "Latin",INK,"right")
            links.append({"index_pdf_page":physical,
                          "rect_pt":[mm(x),mm(y-8),mm(x+55),mm(y+3.8)],
                          "target_pdf_page":row["first_preview_pdf_page"]})
        if not part:raise ValueError("An empty index page was reserved")
        a.c.showPage()
    return links

def draw_specimen(a:PageArtist,src_doc:fitz.Document,row):
    a.rect(29,63,57,52,FAINT,None,4)
    if row["adopted_source_pinyin"]:
        pinyin=row["adopted_source_pinyin"]
        a.label(57.5,58,pinyin,14,"Latin",RED,"center")
    else:
        a.label(57.5,58,"本页不单列读音",9,"Kai",RED,"center")
    source_page=src_doc[row["first_source_pdf_page"]-1]
    try:
        image=ImageReader(original_specimen(source_page))
        specimen_mode="source_pdf_ink_clipped"
    except ValueError as exc:
        # The historical four-character sample extractor explicitly rejected
        # ink bounding boxes narrower than 100 rendered pixels. It can reject
        # real tiny radicals like 丶, even though the released PDF is valid.
        # Reuse the EXACT SAME PDF page/crop and pigment mask but permit a
        # narrow genuine glyph, never invent a replacement glyph/pen path.
        if "Missing source specimen ink" not in str(exc):
            raise
        crop=fitz.Rect(37.3,107,128.6,198.6)
        pixels=source_page.get_pixmap(matrix=fitz.Matrix(6,6),
                                      clip=crop,alpha=False)
        rgb=np.asarray(Image.frombytes("RGB",
                         (pixels.width,pixels.height),pixels.samples))
        alpha=np.clip((148-rgb[:,:,1].astype(float))*1.9,0,255).astype("uint8")
        alpha[(rgb[:,:,0]>220)|(rgb[:,:,1]>153)|(rgb[:,:,2]>159)]=0
        if np.count_nonzero(alpha)<5:
            raise ValueError(f"ID{row['main_id']:03d} lacks actual source specimen pigment") from exc
        rgba=np.empty((*alpha.shape,4),dtype="uint8")
        rgba[:,:,:3]=(49,55,59);rgba[:,:,3]=alpha
        ink=Image.fromarray(rgba,"RGBA")
        bounds=ink.getbbox()
        if bounds is None:
            raise ValueError(f"ID{row['main_id']:03d} has no visible source ink") from exc
        buffer=io.BytesIO();ink.crop(bounds).save(buffer,format="PNG")
        buffer.seek(0)
        image=ImageReader(buffer)
        specimen_mode="narrow_ink_from_original_pdf_crop"
        print(f"INFO: ID{row['main_id']:03d} {row['character']} source PDF very narrow real ink extracted")
    native_w,native_h=image.getSize()
    if native_w<1 or native_h<1:raise ValueError("Released source main glyph missing")
    scale=min(48/native_w,45/native_h)
    w,h=native_w*scale,native_h*scale
    if abs((w/h)/(native_w/native_h)-1)>1e-10:
        raise ValueError("Source main glyph ratio was distorted")
    a.c.drawImage(image,mm(57.5-w/2),H-mm(109)+mm((45-h)/2),
                  width=mm(w),height=mm(h),mask="auto")
    return specimen_mode

def draw_art_slot(a:PageArtist,row,art_assets,root,full_scenes=None):
    e=row["manuscript"]
    if full_scenes is not None:
        generated,legacy=full_scenes
        info=paint_cultural_scene(a.c,row,generated,legacy,root)
        a.label(123,113,"文化主题矢量画稿 · 未经美术审定",7.0,"Kai",RED)
        return info
    if e and e["artwork_stage"]=="four_unique_svg_drafts_not_approved":
        ref=art_assets.get(e["theme_key"])
        if not ref or ref["main_character"]!=row["character"]:
            raise ValueError("Unverified or wrong four-scene SVG draft")
        paint_scene(a.c,e["theme_key"],row["character"],root=root,assets=art_assets)
        a.label(123,113,"四字独立 SVG 画稿 · 美术待审",7.6,"Kai",RED)
        return "four_svg_draft_unreviewed"
    a.rect(118,51,75,56,"#FAF9F7","#D9D8D3",3)
    if e:
        a.label(123,63,"专属主题画构想",10,"Kai",RED)
        brief=e.get("art_brief")
        if brief:
            lines=a.rows(brief,65,9.1,max_lines=4)
            for i,value in enumerate(lines):
                a.label(123,76+i*6.5,value,9.1,"Kai",INK)
        else:
            a.label(123,81,"原样稿构图待补充",9,"Kai",GRAY)
        a.label(123,102,"原创美术/版权待审",7.5,"Kai",RED)
        return "unique_illustration_concept_not_finished_asset"
    a.label(123,67,"专属插图留白",11,"Kai",GRAY)
    a.label(123,80,"题材、版权与画面待设计",8.7,"Kai",GRAY)
    a.label(123,99,f"ID{row['main_id']:03d}  请勿用通用山水补位",8,"Kai",GRAY)
    return "missing_placeholder_not_an_image"

def stroke_tile(a:PageArtist,step,x,y):
    # ReportLab prints only a label, not the source image; a later immutable
    # PyMuPDF operation embeds the EXACT released-PDF vector Form XObject.
    a.label(x+TILE_MM/2,y-3.0,f"{step['index']}  {step['name']}",
            8.1,"Kai",RED,"center")
    return dict(step,preview_rect_pt=[round(mm(n),5)
                          for n in (x,y,x+TILE_MM,y+TILE_MM)])

def cover_page(a:PageArtist,row,page,src_doc,art_assets,root,full_scenes=None):
    main_id=row["main_id"];e=row["manuscript"]
    a.page_border(page,f"{row['batch_id']}  ·  ID{main_id:03d}  {row['character']}  ·  原PDF p.{row['first_source_pdf_page']}")
    a.label(18,16,f"{row['batch_id']}  ·  ID{main_id:03d}  /  共{row['stroke_count']}笔",
            8,"Kai",GRAY)
    title=e["title"] if e else f"{row['character']} · 字义与文化主题待编"
    a.fitted(18,28,title,174,20,11,RED)
    a.line(18,32,192,32,PALE,.38)
    if e:
        rows=a.rows(e["subtitle"],170,9.5,max_lines=2)
        for i,s in enumerate(rows):a.label(18,40+i*5.3,s,9.5,"Kai",GRAY)
    else:
        a.label(18,42,"文化阅读内容尚未编审；下方笔顺示范完整保留。",9.5,"Kai",GRAY)
    specimen_state=draw_specimen(a,src_doc,row)
    art_state=draw_art_slot(a,row,art_assets,root,full_scenes)
    a.section(17,119,"字义 / 部义",113)
    if e:
        parts=[]
        for text in e["meaning"]:
            parts.extend(a.rows(text,90,9.2,max_lines=3))
        if len(parts)>4:raise ValueError("Full-book meaning overflow: "+row["character"])
        for i,text in enumerate(parts):
            a.label(18,130+i*5.0,text,9.2)
    else:
        a.label(19,132,"字义及独立部义待按权威源审查",9,"Kai",GRAY)
    if e and e["quote_candidate"]:
        a.section(120,119,"古句待核原典",193)
        a.label(121,129,"引文候选 · 不得直接引用",8.3,"Kai",RED)
        pieces=a.rows(e["quote_candidate"],70,9.1,max_lines=2)
        for i,t in enumerate(pieces):a.label(121,139+i*5.4,t,9.1)
    else:
        # No fabricated classics. The scene-caption derives from this ID's
        # own editor's idea and the actual drawn panel above.
        a.section(120,119,"画意联想",193)
        caption=(e.get("art_brief") if e else None) or "看图识字，读懂今天的故事"
        lines=a.rows(caption,68,9.0,max_lines=4)
        for j,t in enumerate(lines):
            a.label(121,130+j*5.6,t,9.0,"Kai",GRAY)
    a.line(17,152,193,152,"#D6CDCD")
    a.section(17,155,"笔顺提示",112)
    tips=[]
    for original_tip in row["source_tips"]:
        tips.extend(a.rows(original_tip,94,8.6,max_lines=5))
    if len(tips)>7:
        raise ValueError("Released PDF pen-order tips cannot fit: "+row["character"])
    for i,text in enumerate(tips):
        a.label(18,165+i*4.65,text,8.6,"Kai",INK if i==0 else RED)
    a.section(17,202,"原图逐笔示范",113)
    a.section(121,155,"相关字词 · 拼音候选未审",193)
    terms=e["terms"] if e else []
    if terms:
        if len(terms)>6:raise ValueError("Too many word cards")
        for i,term in enumerate(terms):
            x=121+(i%2)*36.8;y=164+(i//2)*21.2
            a.rect(x,y,34.6,18.2,"#F9F6F3",None,1.5)
            py=term["pinyin"]
            if py is None:
                a.label(x+17.3,y+6.5,"多音待核",7.2,"Kai",RED,"center")
            else:
                size=7.7
                while size>5.8 and pdfmetrics.stringWidth(py,"CultureLatin",size)>mm(33):
                    size-=.2
                if pdfmetrics.stringWidth(py,"CultureLatin",size)>mm(33):
                    raise ValueError("Word Pinyin needs an editorial linebreak: "+term["word"])
                a.label(x+17.3,y+6.5,py,size,"Latin",RED,"center")
            a.label(x+17.3,y+14.8,term["word"],12.3,"Kai",INK,"center")
    else:
        a.label(122,169,"没有经过词典核实的候选词条",8.7,"Kai",GRAY)
        a.label(122,177,"请勿根据单字自动拼出词音",8.3,"Kai",GRAY)
    a.section(121,235,"一字一句 · 待审",193)
    if e:
        sentence=a.rows(e["sentence"],70,8.9,max_lines=6)
        for i,t in enumerate(sentence):
            a.label(122,246+5.3*i,t,8.9)
    else:
        a.label(122,249,"独立意境短句待撰写",9.2,"Kai",GRAY)
        a.label(122,257,"留白并非漏页",8.5,"Kai",GRAY)
    steps=row["steps"][:CAPACITY_FIRST]
    if len(steps)<=3:
        xs={1:(50,),2:(32,69),3:(17,50,83)}[len(steps)]
        tiles=[stroke_tile(a,st,x,227) for st,x in zip(steps,xs)]
    else:
        tiles=[stroke_tile(a,st,COVER_X[i%3],215 if i<3 else 250)
               for i,st in enumerate(steps)]
    a.c.showPage()
    return tiles,art_state,specimen_state

def continuation_page(a:PageArtist,row,page,part,steps):
    a.page_border(page,f"{row['batch_id']}  ·  ID{row['main_id']:03d}  {row['character']}  ·  笔顺续页")
    a.label(18,28,f"{row['character']} · 笔顺续页",21,"Kai",RED)
    a.line(18,33,192,33,PALE,.38)
    a.label(18,46,
            f"共{row['stroke_count']}笔  /  第{part}/{row['page_parts']}页"
            f"  /  本页{steps[0]['index']}—{steps[-1]['index']}笔",10,"Kai",INK)
    a.label(18,60,"提示：依原书序号逐步完成，灰色为先前笔画，红色为当前笔画。",9.5,"Kai",GRAY)
    a.section(18,67,"源 PDF 笔顺提示",192)
    tips=[]
    for source_tip in row["source_tips"]:
        tips.extend(a.rows(source_tip,168,8.6,max_lines=3))
    if len(tips)>4:raise ValueError("Continued source hints exceed reserved lines")
    for i,t in enumerate(tips):
        a.label(18,78+5*i,t,8.6)
    a.section(18,96,"原书逐笔累计图（续）",192)
    tiles=[]
    for i,st in enumerate(steps):
        tiles.append(stroke_tile(a,st,MORE_X[i%5],MORE_Y[i//5]))
    a.label(18,273,
            f"ID{row['main_id']:03d}  本页完整展示 {len(steps)} 笔，逐笔源矢量未修改。",
            8.4,"Kai",GRAY)
    a.c.showPage()
    return tiles

def render(source:Path,manifest:Path,output:Path,proof:Path,
           root:Path=ROOT,art_registry:Path|None=None,art_dir:Path|None=None):
    root=Path(root)
    fonts()
    font_path=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
    if not font_path.is_file():
        raise ValueError("Missing packaged open font fallback for 201 rare radicals")
    if "CultureRare" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CultureRare",str(font_path),subfontIndex=0))
    source_index=audit(source,manifest)
    plan=paginate(make_plan(source_index,root))
    art=read_registry(root=root)
    if len(art)!=4:raise ValueError("Four original SVG drafts changed unexpectedly")
    if (art_registry is None)!=(art_dir is None):
        raise ValueError("The art source registry and actual SVG dir are an inseparable pair")
    full_scenes=checked_assets(art_registry,art_dir,root) if art_registry else None
    buf=io.BytesIO()
    writer=canvas.Canvas(buf,pagesize=(W,H),pageCompression=1,invariant=1)
    writer.setTitle("循序渐进 文化识字版 P4.5.1 · 201字图文及拼音候选工程稿 · 未审定")
    writer.setAuthor("netplus/zitie cultural full-book P4.2 source-locked engineering proof")
    a=PageArtist(writer)
    base_cover(a,plan)
    instructions(a,plan)
    links=index_pages(a,plan)
    page_map=[];dest_targets=[]
    with fitz.open(source) as source_pdf:
        page=BASE_PAGES+1
        for row in plan["entries"]:
            if row["first_preview_pdf_page"]!=page:
                raise ValueError("Unexpected first-page number in full-book plan")
            tiles,art_state,specimen_state=cover_page(a,row,page,source_pdf,art,root,full_scenes)
            page_map.append({
                "preview_pdf_page":page,"page_kind":"source_main_cultural_reading",
                "main_id":row["main_id"],"character":row["character"],
                "batch_id":row["batch_id"],"part":1,
                "parts":row["page_parts"],"theme_key":row["manuscript"]["theme_key"] if row["manuscript"] else None,
                "content_status":row["content_review"],
                "artwork_status":art_state["art_state"] if isinstance(art_state,dict) else art_state,
                "artwork_asset_sha256":art_state.get("asset_sha256") if isinstance(art_state,dict) else None,
                "source_specimen_render_mode":specimen_state,
                "source_stroke_count":row["stroke_count"],
                "source_first_pdf_page":row["first_source_pdf_page"],
                "printed_pinyin_from_original_source":row["adopted_source_pinyin"],
                "all_word_candidates_unreviewed":True,
                "quote_citation_approval":False,
                "source_steps":tiles,
            })
            page+=1
            remaining=row["steps"][CAPACITY_FIRST:]
            for k in range(0,len(remaining),CAPACITY_MORE):
                part=2+k//CAPACITY_MORE
                substeps=remaining[k:k+CAPACITY_MORE]
                tiles=continuation_page(a,row,page,part,substeps)
                page_map.append({
                    "preview_pdf_page":page,"page_kind":"original_stroke_continuation",
                    "main_id":row["main_id"],"character":row["character"],
                    "batch_id":row["batch_id"],"part":part,"parts":row["page_parts"],
                    "theme_key":None,"content_status":"original_source_strokes_only",
                    "artwork_status":"not_applicable",
                    "source_stroke_count":row["stroke_count"],
                    "source_first_pdf_page":row["first_source_pdf_page"],
                    "printed_pinyin_from_original_source":None,
                    "all_word_candidates_unreviewed":True,
                    "quote_citation_approval":False,
                    "source_steps":tiles,
                })
                page+=1
        writer.save()
        result=fitz.open(stream=buf.getvalue(),filetype="pdf")
        try:
            if len(result)!=plan["expected_total_pdf_pages"] or page-1!=len(result):
                raise ValueError("A4 pages lost while building full cultural book")
            for rec in page_map:
                target=result[rec["preview_pdf_page"]-1]
                for source_step in rec["source_steps"]:
                    target.show_pdf_page(
                        fitz.Rect(source_step["preview_rect_pt"]),
                        source_pdf,source_step["pdf_page"]-1,
                        clip=fitz.Rect(source_step["rect_pt"]),
                        keep_proportion=False,overlay=True)
            toc=[[1,"封面",1],[1,"全书说明",2],[1,"201 主字索引",3]]
            previous_batch=None
            for row in plan["entries"]:
                if row["batch_id"]!=previous_batch:
                    toc.append([1,row["batch_id"]+"  原书批次",
                                row["first_preview_pdf_page"]])
                    previous_batch=row["batch_id"]
                toc.append([2,f"ID{row['main_id']:03d} {row['character']}",
                            row["first_preview_pdf_page"]])
                for p in range(2,row["page_parts"]+1):
                    toc.append([3,f"{row['character']} · 笔顺续页 {p}/{row['page_parts']}",
                                row["first_preview_pdf_page"]+p-1])
            result.set_toc(toc)
            for link in links:
                result[link["index_pdf_page"]-1].insert_link({
                    "kind":fitz.LINK_GOTO,
                    "from":fitz.Rect(link["rect_pt"]),
                    "page":link["target_pdf_page"]-1})
            result.set_metadata({
                "title":"文化识字版 P4.5.1 201字插图与拼音候选工程稿（未审定）",
                "author":"netplus/zitie",
                "subject":"原PDF 1045笔源图溯源；文化内容待审",
                "keywords":"201,1045,editorial draft,source locked",
            })
            output.parent.mkdir(parents=True,exist_ok=True)
            result.save(output,garbage=4,deflate=True,no_new_id=True)
        finally:
            result.close()
    source_steps=sum(len(p["source_steps"]) for p in page_map)
    if source_steps!=1045 or sum(r["page_parts"] for r in plan["entries"])!=len(page_map):
        raise ValueError("All 1045 real original source steps must be present exactly once")
    summary={
        "schema_version":1,"status":"P4_2_201_GLYPH_FULL_BOOK_ENGINEERING_DRAFT_NOT_RELEASE",
        "source_pdf_sha256":SHA,"original_pdf_pages":299,
        "output_pdf_sha256":sha256(output),
        "output_pdf_bytes":output.stat().st_size,
        "output_pdf_pages":plan["expected_total_pdf_pages"],
        "front_matter_pages":BASE_PAGES,
        "content_glyphs":201,
        "content_glyph_pages":plan["expected_glyph_pdf_pages"],
        "continuation_pages":plan["expected_continuation_pages"],
        "cumulative_original_source_stroke_tiles":source_steps,
        "batch_count":21,
        "cultural_draft_glyphs":201,
        "new_character_cultural_drafts":185,
        "missing_cultural_editorial_content":0,
        "unreviewed_related_word_or_character_examples":sum(len(r["manuscript"]["terms"]) for r in plan["entries"]),
        "unique_existing_svg_artwork_drafts":4,
        "generated_distinct_svg_artwork_drafts":197 if full_scenes else 0,
        "full_artwork_svg_drafts":201 if full_scenes else 4,
        "reading_candidates_printed":plan["reading_candidates_displayable"],
        "blocked_ambiguous_readings":plan["reading_ambiguities_not_displayable"],
        "unreviewed_word_reading_examples":812,
        "illustration_art_approved":0,
        "word_readings_approved":0,
        "new_publication_approvals":0,
        "attached_forms_included":0,
        "stroke_source_method":"PyMuPDF Page.show_pdf_page + original 86pt clipped vector Form XObject",
        "source_svg_strokes_generated":0,
        "editorial_disclaimer":"201 cultural articles drafted, ALL new phonetics, quotations, proposed scenes and literary text unreviewed; only original v0.5.1 PDF strokes verified.",
        "original_batch_main_ids":[{"batch_id":f"B{i:02d}",
            "main_ids":[g["main_id"] for g in plan["entries"] if g["batch_id"]==f"B{i:02d}"]}
            for i in range(1,22)],
        "index_links":links,"page_map":page_map,
    }
    proof.parent.mkdir(parents=True,exist_ok=True)
    proof.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("page_map","index_links","original_batch_main_ids")},
                     ensure_ascii=False,indent=2))
    return summary

def main():
    cli=argparse.ArgumentParser()
    for x in ("source","manifest","output","proof"):
        cli.add_argument("--"+x,type=Path,required=True)
    cli.add_argument("--root",type=Path,default=ROOT)
    cli.add_argument("--art-registry",type=Path)
    cli.add_argument("--art-dir",type=Path)
    o=cli.parse_args()
    render(o.source,o.manifest,o.output,o.proof,o.root,o.art_registry,o.art_dir)

if __name__=="__main__":
    main()
