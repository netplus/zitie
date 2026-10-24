#!/usr/bin/env python3
"""Four-page P1 culture-PDF candidate: frozen v0.5.1 strokes, new reading layout.

Stroke teaching tiles are not re-rendered by a font or image model. Every one
is a vector Form XObject clipped out of the EXACT original published PDF.
The original themed mini-art is a deterministic layout proof, not approved P3 art.
This script deliberately rejects editorial-draft status for any release claim.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from cultural_source_audit import audit

PT_MM=72/25.4
A4=(210*PT_MM,297*PT_MM)
VIN='#9A4049';INK='#2C353B';GRAY='#717B80';PALE='#DDC5C5';WHITE='#FFFEFC'

def fonts():
    names={
      'Kai':'/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf',
      'Song':'/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf',
      'Latin':'/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    }
    for label,path in names.items():
        if not Path(path).is_file():
            raise ValueError(f'Missing system font, must install package: {path}')
        pdfmetrics.registerFont(TTFont('Culture'+label,path))

def original_specimen(page):
    """Display specimen is clipped/colored from original PDF, never invented."""
    clip=fitz.Rect(37.3,107,128.6,198.6)
    pix=page.get_pixmap(matrix=fitz.Matrix(6,6),clip=clip,alpha=False)
    rgb=np.array(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    mask=np.clip((148-rgb[:,:,1].astype(float))*1.9,0,255).astype('uint8')
    mask[(rgb[:,:,0]>220)|(rgb[:,:,1]>153)|(rgb[:,:,2]>159)]=0
    rgba=np.empty((*mask.shape,4),dtype='uint8')
    rgba[:,:,:3]=(49,55,59);rgba[:,:,3]=mask
    im=Image.fromarray(rgba,'RGBA')
    bounds=im.getbbox()
    if not bounds or bounds[2]-bounds[0]<100:
        raise ValueError('Missing source specimen ink')
    buffer=io.BytesIO();im.crop(bounds).save(buffer,format='PNG');buffer.seek(0)
    return buffer

def theme_art(c,kind):
    """Small unique vector illustration proof: P3 curated imagery is NOT DONE."""
    x0,y0,w,h=111*PT_MM,(297-120)*PT_MM,82*PT_MM,75*PT_MM
    c.saveState();c.translate(x0,y0);c.setLineJoin(1)
    def poly(coords,col,width=1.4):
        c.setStrokeColor(HexColor(col));c.setLineWidth(width)
        p=c.beginPath()
        for i,(x,y) in enumerate(coords):
            (p.moveTo if i==0 else p.lineTo)(x*w,y*h)
        c.drawPath(p,stroke=1,fill=0)
    if kind=='river-current':
        for i in range(7):
            yy=(.13+i*.11)*h
            c.setStrokeColor(HexColor(['#B0C5C7','#C0D1D1','#96B6B8'][i%3]))
            c.setLineWidth(1.15+(i%2)*.55)
            p=c.beginPath();p.moveTo(.04*w,yy)
            p.curveTo(.21*w,yy+.052*h,.26*w,yy-.04*h,.44*w,yy+.007*h)
            p.curveTo(.62*w,yy+.046*h,.74*w,yy-.039*h,.96*w,yy+.003*h)
            c.drawPath(p,stroke=1,fill=0)
        poly([(.35,.47),(.50,.46),(.61,.48),(.58,.52),(.42,.52)],'#819794',1.3)
        poly([(.49,.51),(.49,.61)],'#92A5A2',1)
    elif kind=='peaks-and-clouds':
        poly([(.04,.25),(.29,.69),(.41,.5),(.58,.89),(.87,.37),(.95,.45)],'#8C9E9A',2.3)
        poly([(.04,.20),(.27,.50),(.42,.39),(.61,.65),(.96,.20)],'#B9C2BF',2.6)
        for k in range(4):
            poly([(.17,.78-k*.05),(.37,.8-k*.05),(.48,.78-k*.05),
                  (.7,.8-k*.05)],'#D9DFDB',1)
    elif kind=='moon-over-rooftops':
        c.setFillColor(HexColor('#F0D8C0'))
        c.circle(.72*w,.75*h,.15*h,fill=1,stroke=0)
        poly([(.1,.36),(.28,.53),(.45,.37),(.63,.54),(.85,.38)],'#95A4A7',1.9)
        for yy in (.22,.27,.32):
            poly([(.14,yy),(.35,yy+.006),(.64,yy-.01),(.84,yy+.002)],
                 '#BAC9C9',.9)
    elif kind=='seasonal-rooted-tree':
        poly([(.52,.13),(.52,.72),(.41,.83)],'#8B9180',5)
        poly([(.52,.53),(.70,.76)],'#8B9180',3.6)
        poly([(.52,.32),(.29,.46)],'#8B9180',2.5)
        for x,y,r in ((.36,.76,.095),(.54,.8,.12),(.67,.71,.1),
                      (.47,.88,.09),(.75,.83,.065)):
            c.setFillColor(HexColor('#D6DED2'))
            c.circle(x*w,y*h,r*h,fill=1,stroke=0)
    else:
        raise ValueError('Duplicate/unreviewed topic illustration: '+kind)
    c.restoreState()

def verify_editorial(data,source_map):
    if data['schema_version']!=1 or data['review_state']!='editorial_draft_not_for_release':
        raise ValueError('Only explicitly non-released P1 editorial samples allowed')
    entries=data['entries']
    for field in ('main_id','character','theme_key','title','sentence'):
        if len({e[field] for e in entries})!=len(entries):
            raise ValueError(f'Unacceptably repeated {field}')
    for e in entries:
        glyph=source_map.get(e['main_id'])
        if glyph is None or glyph['character']!=e['character']:
            raise ValueError('The editorial glyph is not the official PDF glyph')
        if not glyph['pinyin_from_pdf']:
            raise ValueError('Cannot infer missing character pinyin')
        if len(glyph['steps'])>4:
            raise ValueError('P1 draft layout supports only <=4 strokes; '
                             'complex glyphs require a separately reviewed continuation')
        if len(e['terms'])!=6 or not all(t['status']=='review_pending' for t in e['terms']):
            raise ValueError('Term phonetics have not passed dictionary review')
        if e['quote']['status']!='review_pending':
            raise ValueError('Quote citations must not be auto-promoted')
    return entries

def create(source_path,source_index,editorial,output,proof,theme_painter=None):
    fonts()
    src=fitz.open(source_path)
    glyphs={g['main_id']:g for g in source_index['glyphs']}
    entries=verify_editorial(editorial,glyphs)
    mm=lambda x:PT_MM*x
    W,H=A4
    memory=io.BytesIO()
    c=canvas.Canvas(memory,pagesize=A4,pageCompression=1,invariant=1)
    c.setTitle('文化识字版 · 原PDF源笔顺样板 · 四字 P1')
    c.setAuthor('netplus/zitie - draft not for release')
    def line(x0,y0,x1,y1,col=PALE,width=.22):
        c.setStrokeColor(HexColor(col));c.setLineWidth(mm(width))
        c.line(mm(x0),H-mm(y0),mm(x1),H-mm(y1))
    def text(x,y,label,size=11,face='Kai',col=INK):
        c.setFillColor(HexColor(col));c.setFont('Culture'+face,size)
        c.drawString(mm(x),H-mm(y),label)
    def center(x,y,label,size=11,face='Kai',col=INK):
        c.setFillColor(HexColor(col));c.setFont('Culture'+face,size)
        c.drawCentredString(mm(x),H-mm(y),label)
    def heading(title,x,y,end):
        c.setFillColor(HexColor(VIN))
        c.rect(mm(x),H-mm(y+1),mm(1.1),mm(5),fill=1,stroke=0)
        text(x+3,y+3,title,12,'Kai',VIN)
        pos=x+7+5*len(title)
        if pos<end-2:line(pos,y+2,end,y+2)
    def box(x,y,w=34,h=19.6):
        c.setFillColor(HexColor('#FBF8F7'))
        c.roundRect(mm(x),H-mm(y+h),mm(w),mm(h),mm(1.7),fill=1,stroke=0)
        c.setStrokeColor(HexColor('#E5D8D6'));c.setLineWidth(mm(.15))
        c.roundRect(mm(x),H-mm(y+h),mm(w),mm(h),mm(1.7),fill=0,stroke=1)
    records=[];destinations=[]
    for e in entries:
        g=glyphs[e['main_id']]
        c.setFillColor(HexColor(WHITE));c.rect(0,0,W,H,fill=1,stroke=0)
        c.setStrokeColor(HexColor('#C18F8E'));c.setLineWidth(mm(.25))
        c.rect(mm(9),mm(9),mm(192),mm(279),fill=0,stroke=1)
        for x,y,dx,dy in ((11,11,1,1),(199,11,-1,1),(11,285,1,-1),(199,285,-1,-1)):
            line(x,y,x+6*dx,y,VIN,.38);line(x,y,x,y+6*dy,VIN,.38)
        if pdfmetrics.stringWidth(e['title'],'CultureKai',23)>mm(177):
            raise ValueError('Clipped title: '+e['character'])
        text(18,25,e['title'],23,'Kai',VIN)
        line(18,30,190,30,'#D2A7A4',.4)
        text(19,39,e['subtitle'],10.6,'Kai',GRAY)
        c.setFillColor(HexColor('#F9F7F5'))
        c.circle(mm(59),H-mm(83),mm(29),fill=1,stroke=0)
        center(58,54,g['pinyin_from_pdf'],18,'Latin',VIN)
        c.drawImage(ImageReader(original_specimen(src[g['first_pdf_page']-1])),
                    mm(31),H-mm(111),mm(54),mm(54),mask='auto')
        if theme_painter is None:
            theme_art(c,e['theme_key'])
        else:
            theme_painter(c,e['theme_key'],e['character'])
        heading('字义',18,122,107);heading('经典一隅',115,122,191)
        for j,line_text in enumerate(e['meaning']):
            if pdfmetrics.stringWidth(line_text,'CultureKai',11)>mm(85):
                raise ValueError('Clipped meaning: '+line_text)
            text(20,134+j*8,line_text,11)
        q=e['quote']
        text(118,135,q['text'],14);text(127,146,'——'+q['attribution'],9.5,'Kai',GRAY)
        line(17,157,193,157)
        heading('笔顺提示',18,163,111)
        for j,t in enumerate(g['tips_from_pdf'][:2]):
            if pdfmetrics.stringWidth(t,'CultureKai',9.5)>mm(93):
                raise ValueError('Source tip requires a longer continuation page: '+t)
            text(19,175+j*7,t,9.5,'Kai',VIN if j else INK)
        heading('笔顺',18,193,112)
        heading('相关词',121,163,193)
        coords=((28,205),(76,205),(28,246),(76,246))
        placements=[]
        for stroke,(x,y) in zip(g['steps'],coords):
            rect=fitz.Rect(mm(x),mm(y),mm(x+33),mm(y+33))
            placements.append(rect)
            center(x+16.5,y-1.5,str(stroke['index'])+'  '+stroke['name'],9.3,'Kai',VIN)
        for j,term in enumerate(e['terms']):
            x=121+(j%2)*36.3;y=172+(j//2)*21.6
            box(x,y)
            center(x+17,y+7,term['pinyin'],8,'Latin',VIN)
            center(x+17,y+16.1,term['word'],15,'Kai')
        heading('一字一句',121,239,193)
        lines=[];part=''
        for character in e['sentence']:
            if pdfmetrics.stringWidth(part+character,'CultureKai',10.5)>mm(70):
                lines.append(part);part=character
            else:part+=character
        if part:lines.append(part)
        if len(lines)>5:raise ValueError('Literary text does not fit: '+e['character'])
        for j,row in enumerate(lines):
            text(122,250+j*7.3,row,10.5)
        line(17,287,193,287,'#E3D6D4',.18)
        text(18,292,f"ID{g['main_id']:03d} {g['character']} · v0.5.1 PDF p.{g['first_pdf_page']}",
             7,'Song',GRAY)
        text(117,292,'词音/引文待审 · 仅作版式样板',7,'Song',VIN)
        records.append({'main_id':g['main_id'],'character':g['character'],
                        'source_pdf_page':g['first_pdf_page'],
                        'stroke_count':g['stroke_count'],'theme_key':e['theme_key'],
                        'source_steps':[dict(s,preview_rect_pt=[round(v,5) for v in dst])
                                        for s,dst in zip(g['steps'],placements)],
                        'term_review_status':[t['status'] for t in e['terms']],
                        'quote_review_status':q['status']})
        destinations.append(placements)
        c.showPage()
    c.save();memory.seek(0)
    dest=fitz.open(stream=memory.getvalue(),filetype='pdf')
    if len(dest)!=len(records):raise ValueError('Lost a PDF page')
    for idx,(record,rects) in enumerate(zip(records,destinations)):
        for step,dst in zip(record['source_steps'],rects):
            dest[idx].show_pdf_page(dst,src,step['pdf_page']-1,
                                    clip=fitz.Rect(step['rect_pt']),
                                    keep_proportion=False,overlay=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    dest.save(output,garbage=4,deflate=True,no_new_id=True);dest.close();src.close()
    report={'status':'editorial_draft_not_for_release',
            'source_pdf_sha256':source_index['source_pdf_sha256'],
            'candidate_pdf_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'pages':len(records),'source_step_total':sum(r['stroke_count'] for r in records),
            'source_vector_method':'Page.show_pdf_page clip original source 86pt',
            'illustrations':('P1 vector placeholders; P3 unique curated artwork pending'
              if theme_painter is None else 'P3 four independently sourced VECTOR theme drafts; editorial approval pending'),
            'records':records}
    proof.parent.mkdir(parents=True,exist_ok=True)
    proof.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--content',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--proof',type=Path,required=True)
    a=p.parse_args()
    result=create(a.source,audit(a.source,a.manifest),
                  json.loads(a.content.read_text(encoding='utf8')),a.output,a.proof)
    print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
