#!/usr/bin/env python3
"""B01 nine-page cultural preview from frozen v0.5.1 source PDF strokes.

Unreviewed editorial words, provisional picture sketches and quote placeholders are
clearly identified; this generator does not approve or publish the finished book.
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
from cultural_b01_editorial_audit import audit as audit_b01, ROOT as PROJECT_ROOT
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
    # Reuse the fail-closed B01 editorial inventory/negative-test contract.
    report = audit_b01(PROJECT_ROOT)
    if (data.get('schema_version') != 1 or data.get('review_state') != 'draft_not_for_release'
            or data.get('source_pdf_sha256') != SOURCE_SHA):
        raise ValueError('B01 cultural pages require the frozen PDF source and unreviewed editorial draft')
    if report['new_characters'] != 9 or report['unreviewed_word_candidates'] != 36:
        raise ValueError('The exact nine B01 editorial source cards are required')
    glyphs = {g['main_id']: g for g in index['glyphs']}
    entries = data['entries']
    if {e['main_id'] for e in entries} != {1,6,11,12,28,29,33,37,40} or len(entries) != 9:
        raise ValueError('B01 preview must show exactly nine previously unrendered glyphs')
    mapped = []
    for e in entries:
        g = glyphs.get(e['main_id'])
        if not g or g['character'] != e['character'] or not 1 <= g['stroke_count'] <= 3:
            raise ValueError('B01 glyph/stroke identity mismatch in published original PDF')
        if len(g['steps']) != g['stroke_count']:
            raise ValueError('Missing original-PDF stroke: ' + e['character'])
        if (e['publication_eligible'] is not False
                or e['stage'] != 'P2_editorial_brief_unreviewed'):
            raise ValueError('Unapproved B01 editorial records cannot be published')
        if e['quote']['text'] is not None or e['quote']['status'] != 'blocked_no_checked_primary_quote':
            raise ValueError('Unreviewed quotation must stay blocked')
        if e['meaning']['status'] != 'review_pending' or e['sentence_review_status'] != 'review_pending':
            raise ValueError('New prose lacks editorial signoff')
        if (e['artwork_brief']['asset_id'] is not None
                or e['artwork_brief']['visual_review_status'] != 'not_started'):
            raise ValueError('B01 art sketches are not finished assets')
        terms = []
        for word in e['terms']:
            if (word['pronunciation_status'] != 'review_pending'
                    or word['source_url'] is not None
                    or word['reviewed_by'] is not None):
                raise ValueError('No B01 sample may promote candidate vocabulary')
            terms.append({'word': word['word'],
                          'pinyin': word['pinyin_display_candidate'],
                          'status': 'review_pending'})
        mapped.append({
            'main_id': e['main_id'], 'character': e['character'],
            'title': e['title'], 'subtitle': e['subtitle'],
            'theme_key': e['theme_key'], 'meaning': e['meaning']['lines'],
            'quote': {'text': None, 'attribution': None, 'status': 'blocked'},
            'terms': terms, 'sentence': e['sentence']})
    return mapped, glyphs

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
    c.setTitle('文化识字版 · B01 九字原PDF笔顺与未审文化正文 · 技术草稿')
    c.setAuthor('netplus/zitie B01 source-locked technical proof, not reviewed')
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
        # Each sketch is an original deterministic vector PLACEHOLDER linked to
        # one B01 theme. These are not published P3 illustrations, and have no
        # path back into the original teaching glyph or its stroke clip.
        BG, INK_ART, LIGHT = '#F5F4EF', '#879C96', '#BDC9C2'
        c.saveState()
        c.setFillColor(HexColor(BG))
        c.roundRect(mm(120), H-mm(104), mm(73), mm(58), mm(2), stroke=0, fill=1)
        def seg(x0, y0, x1, y1, hue=INK_ART, weight=.65):
            line(x0,y0,x1,y1,hue,weight)
        def disc(x,y,r,color=LIGHT):
            c.setFillColor(HexColor(color))
            c.circle(mm(x),H-mm(y),mm(r),stroke=0,fill=1)
        def poly(points,hue=INK_ART,weight=.75,fill=None,close=False):
            path=c.beginPath()
            for i,(x,y) in enumerate(points):
                (path.moveTo if i==0 else path.lineTo)(mm(x),H-mm(y))
            if close:path.close()
            c.setStrokeColor(HexColor(hue));c.setLineWidth(mm(weight))
            if fill:c.setFillColor(HexColor(fill))
            c.drawPath(path,fill=1 if fill else 0,stroke=1)
        if key=='horizon-first-light':
            disc(158,68,11,'#EACBA5')
            seg(124,80,189,80,'#9DAEAA',1.05)
            seg(130,85,182,85,LIGHT,.5)
            for dx,dy in ((-17,0),(-12,-10),(0,-16),(12,-10),(17,0)):
                seg(158+dx*.7,68+dy*.7,158+dx,68+dy,'#D5B995',.55)
            poly([(122,101),(144,93),(165,95),(190,88)],LIGHT,1)
        elif key=='ten-fingers-counting':
            for hand in (0,1):
                x=132+hand*33
                poly([(x,93),(x-2,76),(x+1,68),(x+4,76),
                      (x+5,62),(x+8,59),(x+10,77),
                      (x+12,63),(x+15,62),(x+16,81),
                      (x+19,71),(x+22,74),(x+21,96),
                      (x+13,100),(x+2,99),(x,93)],INK_ART,.7,None,True)
            for i in range(10):disc(127+7*i,102,1.2,'#D0B597')
        elif key=='street-lantern-homecoming':
            poly([(128,97),(150,61),(165,61),(187,97)],LIGHT,.8)
            poly([(150,61),(150,96),(165,96),(165,61)],INK_ART,1)
            disc(137,79,3)
            poly([(135,84),(132,99),(143,99),(140,84)],INK_ART,.8,None,True)
            seg(143,88,148,86)
            seg(148,82,148,91)
            poly([(145,82),(151,82),(153,87),(149,92),(145,87)],'#B3987D',.8,'#E8D6B2',True)
        elif key=='eight-point-window':
            points=[(157+20*math.cos(2*math.pi*i/8+math.pi/8),
                     76+20*math.sin(2*math.pi*i/8+math.pi/8)) for i in range(8)]
            poly(points,INK_ART,1.4,None,True)
            for xx,yy in points:seg(157,76,xx,yy,LIGHT,.6)
            disc(157,76,3,'#D6C3A6')
        elif key=='open-arms-sky':
            disc(157,67,5,'#BFC5B5')
            poly([(157,73),(156,93)],INK_ART,1.6)
            poly([(156,78),(138,70),(125,73)],INK_ART,1.3)
            poly([(156,78),(177,69),(189,73)],INK_ART,1.3)
            poly([(156,93),(147,102)],INK_ART,1.1)
            poly([(156,93),(166,102)],INK_ART,1.1)
            poly([(123,60),(128,57),(132,60)],LIGHT,.7)
            poly([(174,57),(178,55),(182,58)],LIGHT,.7)
        elif key=='craftsman-wood-rule':
            poly([(126,91),(188,91),(185,97),(129,97)],INK_ART,1,None,True)
            seg(135,97,132,102,INK_ART,1);seg(178,97,181,102,INK_ART,1)
            poly([(139,84),(162,84),(164,89),(137,89)],INK_ART,.8,'#D4C5AC',True)
            poly([(146,82),(169,73),(171,76),(149,86)],'#AA9780',1)
            for i in range(3):
                poly([(174+i*4,84),(177+i*3,81),(179+i*3,84)],LIGHT,.6)
        elif key=='potter-wheel-clay':
            poly([(143,97),(177,97)],INK_ART,1.2)
            poly([(148,93),(173,93),(177,96),(143,96)],INK_ART,.85,None,True)
            poly([(151,71),(149,80),(151,87),(169,87),(171,80),(169,71)],'#B79F84',1,'#D8C2A8',True)
            poly([(151,71),(160,73),(169,71)],'#B79F84',1.1)
            poly([(133,72),(144,75),(149,84)],INK_ART,1.4)
            poly([(188,72),(177,75),(172,84)],INK_ART,1.4)
            seg(159,97,159,103,LIGHT,1)
        elif key=='courtyard-greeting':
            poly([(129,99),(129,66),(180,66),(180,99)],INK_ART,1)
            poly([(127,67),(154,57),(184,67)],'#A9B9B0',1.2)
            poly([(140,99),(140,72),(169,72),(169,99)],INK_ART,.9)
            seg(157,68,157,79,'#B69D80')
            disc(157,82,3,'#D8C3A0')
            for dx in (-3,0,3):seg(157,85,157+dx,90,'#B69D80',.5)
            poly([(185,75),(189,72),(191,74)],LIGHT,.7)
        elif key=='linen-in-breeze':
            seg(126,64,187,64,INK_ART,1)
            for x in (140,170):
                seg(x,63,x,68,'#A48B79',1.2)
            poly([(138,68),(150,70),(149,89),(143,94),(136,89)],'#9DB9BC',1,'#D9E7E4',True)
            poly([(169,68),(183,69),(180,83),(185,92),(168,91)],'#C1AB8F',1,'#E4D3BD',True)
            for y in (77,84):seg(141,y,146,y+2,'#B8CCCC',.4)
            poly([(125,98),(145,99),(167,98),(189,99)],LIGHT,.7)
        else:
            raise ValueError('Unknown B01 independent cultural illustration sketch: '+key)
        t(122,110,'文化图构图草案 / 未审定',6.8,'Song',GRAY)
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
        # One-to-three stroke B01 cards use spacious, balanced single rows.
        centers={1:(50,),2:(31,69),3:(17,50,83)}
        if len(steps) not in centers:
            raise ValueError('B01 only includes 1-3 stroke glyphs')
        for step,x in zip(steps,centers[len(steps)]):
            placed.append(tile(glyph,step,x,218))
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
    report={'status':'B01_source_locked_editorial_draft_not_for_release',
            'source_sha256':SOURCE_SHA,
            'output_sha256':sha256(output),
            'pages':len(mapping),'main_ids':len(entries),
            'total_source_strokes':sum(len(glyphs[e['main_id']]['steps']) for e in entries),
            'cover_max_steps':COVER_CAPACITY,
            'continuation_max_steps':CONTINUATION_CAPACITY,
            'tile_mm':TILE_MM,
            'word_pinyin_candidates_not_for_release':36,
            'original_source_stroke_total_expected':22,
            'primary_dictionary_word_readings_approved':0,
            'actual_p3_artwork_finalized':0,
            'page_status':'technical_pdf_only_not_released',
            'uses_only_original_source_pdf_tiles':True,
            'quote_and_term_review':'all_b01_word_readings_unreviewed_and_quotes_blocked',
            'theme_art':'nine unique vector composition sketches; NOT final artwork',
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
