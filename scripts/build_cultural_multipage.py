#!/usr/bin/env python3
"""P4 culture-page pagination: content + official v0.5.1 PDF stroke Form XObjects.

This is a layout prototype, not a completed editorial book. It never invents
strokes, pronunciations, word readings, quotations, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path

import fitz
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from cultural_source_audit import audit
from build_cultural_sample import original_specimen, fonts

MM = 72.0 / 25.4
W, H = 210 * MM, 297 * MM
SOURCE_SHA = '7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90'
INK, RED, GRAY, RULE = '#30373B', '#9A4049', '#738087', '#DDC8C8'
COVER_CAPACITY = 6
CONTINUATION_CAPACITY = 15
COVER_X, COVER_Y = (17, 50, 83), (200, 245)
CONT_X = (17.5, 53.5, 89.5, 125.5, 161.5)
CONT_Y = (105, 161, 217)
TILE_MM = 31

def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_content(data, index):
    if data.get('schema_version') != 1 or data.get('review_state') != 'editorial_draft_not_for_release':
        raise ValueError('P4 requires explicitly unapproved editorial draft')
    glyphs = {g['main_id']: g for g in index['glyphs']}
    entries = data['entries']
    if not entries or len(entries) > 15:
        raise ValueError('P4 technical proof requires 1-15 distinct entries')
    for key in ('main_id', 'character', 'theme_key', 'title', 'sentence'):
        values = [e[key] for e in entries]
        if len(values) != len(set(values)):
            raise ValueError('Repeated character/theme/sentence: ' + key)
    for e in entries:
        g = glyphs.get(e['main_id'])
        if not g or g['character'] != e['character'] or not 5 <= g['stroke_count'] <= 17:
            raise ValueError('P4 example must be exact 5-17-stroke original source glyph')
        if len(g['steps']) != g['stroke_count']:
            raise ValueError('Original source incomplete')
        if len(e.get('terms', [])) > 6:
            raise ValueError('Too many draft related terms')
        if any(t.get('status') not in ('review_pending','blocked') for t in e.get('terms', [])):
            raise ValueError('No P4 draft word has release eligibility')
        if e['quote']['status'] not in ('review_pending', 'blocked'):
            raise ValueError('Quotes cannot be auto-approved')
        if e.get('reading_candidate') and e['reading_candidate'].get('display_in_page') is not False:
            raise ValueError('Reading candidate cannot be silently promoted')
        if not e['title'] or not e['sentence'] or not e['theme_key']:
            raise ValueError('Missing essential cultural context')
    return entries, glyphs

def mm(x): return x * MM

def render(source: Path, manifest: Path, content: Path, output: Path, proof: Path):
    fonts()
    source_index = audit(source, manifest)
    if source_index['source_pdf_sha256'] != SOURCE_SHA:
        raise ValueError('Official source changed')
    data = json.loads(content.read_text(encoding='utf-8'))
    entries, glyphs = verify_content(data, source_index)
    src = fitz.open(source)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(W, H), pageCompression=1, invariant=1)
    c.setTitle('文化识字版 · 5-17笔完整文化页分页技术草稿 · 非正式发行')
    c.setAuthor('netplus/zitie P4 technical proof, not reviewed')
    placements, mapping = [], []

    def t(x,y,string,size=10,face='Kai',color=INK):
        c.setFillColor(HexColor(color));c.setFont('Culture'+face,size)
        c.drawString(mm(x),H-mm(y),string)
    def center(x,y,string,size=10,face='Kai',color=INK):
        c.setFillColor(HexColor(color));c.setFont('Culture'+face,size)
        c.drawCentredString(mm(x),H-mm(y),string)
    def line(x,y,x1,y1,color=RULE,weight=.2):
        c.setLineWidth(mm(weight));c.setStrokeColor(HexColor(color))
        c.line(mm(x),H-mm(y),mm(x1),H-mm(y1))
    def section(x,y,name,x_end):
        c.setFillColor(HexColor(RED));c.rect(mm(x),H-mm(y+3),mm(1.1),mm(5),stroke=0,fill=1)
        t(x+3,y+4,name,11,'Kai',RED)
        l=x+8+len(name)*5
        if l<x_end-2:line(l,y+2,x_end,y+2)
    def border(glyph,part,parts):
        c.setFillColor(HexColor('#FEFDFB'));c.rect(0,0,W,H,stroke=0,fill=1)
        c.setStrokeColor(HexColor('#C59699'));c.setLineWidth(mm(.23))
        c.rect(mm(9),mm(9),mm(192),mm(279),stroke=1,fill=0)
        for x,y,sx,sy in ((11,11,1,1),(199,11,-1,1),(11,285,1,-1),(199,285,-1,-1)):
            line(x,y,x+5*sx,y,RED,.35);line(x,y,x,y+5*sy,RED,.35)
        line(17,285,193,285,color='#E2D5D4')
        t(18,290,f"ID{glyph['main_id']:03d} {glyph['character']} · 正式PDF v0.5.1 p.{glyph['first_pdf_page']}",7,'Song',GRAY)
        t(124,290,f"第{part}/{parts}页 · 内容/读音待审，非正式稿",7,'Song',RED)
    def wrap(text,face,size,max_width):
        rows=[]; row=''
        for ch in text:
            if pdfmetrics.stringWidth(row+ch,'Culture'+face,size)>mm(max_width):
                if not row:raise ValueError('One character wider than available line')
                rows.append(row);row=ch
            else:row+=ch
        if row:rows.append(row)
        return rows
    def artwork(key):
        # Distinct deterministic P4 diagram placeholders, NOT final P3 images.
        c.saveState()
        c.setStrokeColor(HexColor('#A5B8B4'))
        c.setLineWidth(mm(.7))
        if key=='plowed-fields':
            for j in range(6):
                line(121,63+j*8,187,63+j*8,'#C2CEC0',.45)
                line(122+j*11,63,122+j*11,103,'#B1BFAE',.45)
            t(141,58,'四时田畴 · 占位示意',9,'Song',GRAY)
        elif key=='breath-and-scent':
            for i in range(5):
                p=c.beginPath()
                x=mm(120+10*i);y=H-mm(89)
                p.moveTo(x,y)
                p.curveTo(x+mm(9),y+mm(20),x-mm(6),y+mm(31),x+mm(16),y+mm(38))
                c.drawPath(p,fill=0,stroke=1)
            t(137,49,'风与气息 · 占位示意',9,'Song',GRAY)
        elif key=='ancient-reed-pipes':
            for i in range(7):
                x=122+i*9
                line(x,100,x,72-(i%3)*6,'#9CAB99',2.4)
                line(x-2,101,x+2,101,'#A9B8A8',.6)
            t(131,53,'古乐竹管 · 占位示意',9,'Song',GRAY)
        else:
            raise ValueError('Unknown P4 unique illustration theme')
        c.restoreState()
    def tile(glyph, step, x, y, size=TILE_MM):
        # Source tile placed later via PyMuPDF show_pdf_page + clip.
        center(x+size/2,y-2.2,str(step['index'])+' '+step['name'],8.1,'Kai',RED)
        target=[round(mm(v),5) for v in (x,y,x+size,y+size)]
        return dict(step, preview_rect_pt=target)
    def cover(entry,glyph,part,parts,steps):
        border(glyph,part,parts)
        title=entry['title']
        if pdfmetrics.stringWidth(title,'CultureKai',20)>mm(175):
            raise ValueError('Theme title overflow: '+title)
        t(18,24,title,20,'Kai',RED)
        line(18,30,192,30,'#D2A7A4',.35)
        for j,row in enumerate(wrap(entry['subtitle'],'Kai',10.4,175)):
            if j>1:raise ValueError('Subtitle overflows')
            t(18,39+j*6,row,10.4,'Kai',GRAY)
        c.setFillColor(HexColor('#F8F5F2'));c.circle(mm(57),H-mm(84),mm(24),stroke=0,fill=1)
        if glyph['pinyin_from_pdf']:
            center(57,54,glyph['pinyin_from_pdf'],15,'Latin',RED)
            print_reading='published_source'
        else:
            center(57,54,'读音待审核',10,'Kai',RED)
            print_reading='blocked_no_source_pdf_reading'
        c.drawImage(ImageReader(original_specimen(src[glyph['first_pdf_page']-1])),
                    mm(34),H-mm(110),mm(48),mm(48),mask='auto')
        artwork(entry['theme_key'])
        section(17,118,'字义',112)
        for j,para in enumerate(entry['meaning']):
            for k,row in enumerate(wrap(para,'Kai',10.0,91)):
                yy=131+j*11+k*5
                if yy>146:raise ValueError('Meaning too long for cover')
                t(19,yy,row,10)
        section(120,118,'经典一隅',193)
        if entry['quote']['text']:
            for j,row in enumerate(wrap(entry['quote']['text'],'Kai',11.0,70)):
                t(121,131+j*6,row,11)
            if entry['quote']['attribution']:
                for j,row in enumerate(wrap('——'+entry['quote']['attribution'],'Kai',9,69)):
                    t(123,142+j*5,row,9,'Kai',GRAY)
        else:t(121,133,'经典引文待核验',10,'Kai',GRAY)
        line(17,151,193,151)
        section(17,155,'笔顺提示',113)
        line_no=0
        for tip in glyph['tips_from_pdf'][:2]:
            for row in wrap(tip,'Kai',8.7,95):
                y=166+line_no*5.5
                if y>180:raise ValueError('Source tips overflow cover')
                t(18,y,row,8.7,'Kai',RED if line_no else INK)
                line_no+=1
        section(17,184,'笔顺',113)
        section(121,155,'相关字词',193)
        if entry['terms']:
            for j,term in enumerate(entry['terms']):
                x=121+j%2*37;y=165+(j//2)*22
                c.setFillColor(HexColor('#FAF8F6'))
                c.roundRect(mm(x),H-mm(y+19),mm(34.5),mm(19),mm(1.6),stroke=0,fill=1)
                if pdfmetrics.stringWidth(term['pinyin'],'CultureLatin',8)>mm(33):
                    raise ValueError('Pinyin too wide; do not clip '+term['word'])
                center(x+17.25,y+7,term['pinyin'],8,'Latin',RED)
                center(x+17.25,y+15.4,term['word'],13.1,'Kai')
        else:
            t(123,168,'关联词条尚待权威核对',9,'Kai',GRAY)
            t(123,176,'不凭空编造词语',8,'Kai',GRAY)
        section(121,237,'一字一句',193)
        for i,row in enumerate(wrap(entry['sentence'],'Kai',9.6,70)):
            if i>5:raise ValueError('Literary passage overflow')
            t(122,247+i*6,row,9.6)
        placed=[]
        for i,step in enumerate(steps):
            x=COVER_X[i%3];y=COVER_Y[i//3]
            placed.append(tile(glyph,step,x,y))
        return placed,print_reading
    def continuation(entry,glyph,part,parts,steps):
        border(glyph,part,parts)
        t(17,25,entry['character']+' · 笔顺续页',20,'Kai',RED)
        line(17,30,193,30,'#D2A7A4',.35)
        t(18,43,f"ID{glyph['main_id']:03d} · 共{glyph['stroke_count']}笔 · 第{part}/{parts}页",11)
        if glyph['pinyin_from_pdf']:
            t(18,52,glyph['pinyin_from_pdf'],12,'Latin',RED)
        else:t(18,52,'读音待审核（原正式PDF未单列）',9,'Kai',RED)
        for i,tip in enumerate(glyph['tips_from_pdf'][:2]):
            for j,row in enumerate(wrap(tip,'Kai',9,170)):
                t(18,65+i*7+j*5,row,9)
        section(18,86,'笔顺 · 源PDF真实累计图',192)
        t(18,94,f"本页展示第{steps[0]['index']}—{steps[-1]['index']}笔，依次阅读；红色为本笔。",9,'Kai',GRAY)
        tiles=[]
        for i,step in enumerate(steps):
            x=CONT_X[i%5];y=CONT_Y[i//5]
            tiles.append(tile(glyph,step,x,y))
        return tiles

    for entry in entries:
        glyph=glyphs[entry['main_id']]
        steps=glyph['steps']
        remaining=max(0,len(steps)-COVER_CAPACITY)
        parts=1+math.ceil(remaining/CONTINUATION_CAPACITY)
        cover_steps=steps[:COVER_CAPACITY]
        page_tiles,source_reading=cover(entry,glyph,1,parts,cover_steps)
        mapping.append(dict(main_id=glyph['main_id'],character=glyph['character'],part=1,
            parts=parts,phase='reading_page',stroke_count=glyph['stroke_count'],
            source_reading_state=source_reading,editorial_state='draft_unreviewed',
            theme_key=entry['theme_key'],source_steps=page_tiles))
        placements.append(page_tiles)
        c.showPage()
        for i in range(parts-1):
            part_steps=steps[COVER_CAPACITY+i*CONTINUATION_CAPACITY:
                             COVER_CAPACITY+(i+1)*CONTINUATION_CAPACITY]
            tiles=continuation(entry,glyph,i+2,parts,part_steps)
            mapping.append(dict(main_id=glyph['main_id'],character=glyph['character'],part=i+2,
                parts=parts,phase='stroke_continuation',stroke_count=glyph['stroke_count'],
                source_reading_state=source_reading,editorial_state='draft_unreviewed',
                theme_key=entry['theme_key'],source_steps=tiles))
            placements.append(tiles)
            c.showPage()
    c.save()
    draft=fitz.open(stream=buffer.getvalue(),filetype='pdf')
    if len(draft)!=len(mapping):
        raise ValueError('Layout page count lost')
    for page_idx,steps in enumerate(placements):
        for step in steps:
            draft[page_idx].show_pdf_page(
                fitz.Rect(step['preview_rect_pt']),src,step['pdf_page']-1,
                clip=fitz.Rect(step['rect_pt']),keep_proportion=False,overlay=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    draft.save(output,garbage=4,deflate=True,no_new_id=True)
    draft.close();src.close()
    for entry in entries:
        actual=[s['index'] for page in mapping if page['main_id']==entry['main_id']
                for s in page['source_steps']]
        expected=list(range(1,glyphs[entry['main_id']]['stroke_count']+1))
        if actual!=expected:
            raise ValueError('Source stroke order changed in booklet layout')
    report={'status':'P4_source_locked_editorial_draft_not_for_release',
            'source_sha256':SOURCE_SHA,
            'output_sha256':sha256(output),
            'pages':len(mapping),'main_ids':len(entries),
            'total_source_strokes':sum(len(glyphs[e['main_id']]['steps']) for e in entries),
            'cover_max_steps':COVER_CAPACITY,
            'continuation_max_steps':CONTINUATION_CAPACITY,
            'tile_mm':TILE_MM,
            'uses_only_original_source_pdf_tiles':True,
            'quote_and_term_review':'blocked_or_pending',
            'theme_art':'distinct vector placeholders, not final artwork',
            'page_map':mapping}
    proof.parent.mkdir(parents=True,exist_ok=True)
    proof.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='page_map'},ensure_ascii=False,indent=2))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--content',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--proof',type=Path,required=True)
    args=p.parse_args()
    render(args.source,args.manifest,args.content,args.output,args.proof)

if __name__=='__main__':
    main()
