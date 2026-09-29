#!/usr/bin/env python3
"""A4 research copybook builder. Default publication is fail-closed."""
import argparse
import hashlib
import html
import json
import math
import re
from pathlib import Path
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import ControlBoundsPen
from fontTools.svgLib.path import parse_path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pypdf import PdfReader, PdfWriter
from validate_project import load, validate

ROOT = Path(__file__).resolve().parents[1]
W,H = A4
LEFT,RIGHT = 36,W-36
COL = {'red':'#BB3D42','previous':'#5F6264','ink':'#282B2D',
       'trace':'#D47275','pale':'#B9BBBC','border':'#C99A9D','guide':'#E0C5C7','muted':'#74777A'}

class Pen(BasePen):
    def __init__(self, path): super().__init__(None); self.path=path
    def _moveTo(self,p): self.path.moveTo(*p)
    def _lineTo(self,p): self.path.lineTo(*p)
    def _curveToOne(self,a,b,c): self.path.curveTo(*a,*b,*c)
    def _closePath(self): self.path.close()
    def _endPath(self): pass

def setup_fonts(cjk, latin):
    for name,path in [('CJK',cjk),('Latin',latin)]:
        if not Path(path).is_file(): raise ValueError('Provide an installed font: '+path)
        pdfmetrics.registerFont(TTFont(name,path))

def text(c,x,y,value,size=11,color='ink',font='CJK',center=False,width=None):
    face=pdfmetrics.getFont(font).face
    missing={ch for ch in value if not ch.isspace() and ord(ch) not in face.charToGlyph}
    if missing: raise ValueError('Missing font glyphs: '+''.join(sorted(missing)))
    if width is not None and pdfmetrics.stringWidth(value,font,size)>width:
        raise ValueError('Text overflows fixed layout: '+value)
    c.setFont(font,size); c.setFillColor(HexColor(COL[color]))
    if center: c.drawCentredString(x,y,value)
    else: c.drawString(x,y,value)

def grid(c,x,y,size):
    c.saveState(); c.setStrokeColor(HexColor(COL['border'])); c.setLineWidth(.65)
    c.rect(x,y,size,size)
    c.setStrokeColor(HexColor(COL['guide'])); c.setLineWidth(.4); c.setDash(2,2)
    c.line(x+size/2,y,x+size/2,y+size); c.line(x,y+size/2,x+size,y+size/2)
    c.restoreState()

def prepare(data,count):
    strokes=data.get('strokes',[])
    if len(strokes)!=count: raise ValueError('Vector count mismatch')
    bounds=[]
    for stroke in strokes:
        p=ControlBoundsPen(None); parse_path(stroke,p)
        if not p.bounds or not all(math.isfinite(n) for n in p.bounds): raise ValueError('Invalid path')
        bounds.append(p.bounds)
    box=(min(b[0] for b in bounds), min(b[1] for b in bounds), max(b[2] for b in bounds), max(b[3] for b in bounds))
    if max(box[2]-box[0],box[3]-box[1])<=0: raise ValueError('Empty glyph')
    return strokes,box

def glyph(c,data,x,y,size,color='red',step=None):
    strokes,(a,b,d,e)=data
    scale=.81*size/max(d-a,e-b)
    c.saveState(); c.translate(x+size/2-(a+d)*scale/2,y+size/2-(b+e)*scale/2); c.scale(scale,scale)
    for i,s in enumerate(strokes[:len(strokes) if step is None else step+1]):
        paint=color if step is None else ('red' if i==step else 'previous')
        c.setFillColor(HexColor(COL[paint])); path=c.beginPath(); parse_path(s,Pen(path)); c.drawPath(path,stroke=0,fill=1)
    c.restoreState()

def make_page(c,e,data,page_number,draft,batch):
    n=len(e['stroke_names'])
    if n>6: raise ValueError('This initial renderer supports <=6 strokes; extend by pagination, never shrink.')
    text(c,LEFT,H-49,e['character']+'｜笔顺练字帖',25)
    text(c,RIGHT-120,H-46,batch['batch_id']+' / A4 / 田字格',10,color='muted',font='CJK')
    text(c,LEFT,H-80,'姓名：________________',11,color='muted')
    text(c,RIGHT-200,H-80,'日期：______年____月____日',11,color='muted')
    c.setStrokeColor(HexColor(COL['red'])); c.setLineWidth(1.1); c.line(LEFT,H-94,RIGHT,H-94)
    grid(c,LEFT,642,94); glyph(c,data,LEFT,642,94)
    text(c,155,709,e['pinyin'],24,font='Latin')
    text(c,155,686,str(n)+'画 · 独体字',13)
    text(c,155,663,e['tips'][0],11.5,width=RIGHT-155)
    text(c,155,642,e['tips'][1],11.5,color='red',width=RIGHT-155)
    text(c,LEFT,606,'01  看笔顺',14,color='red')
    text(c,300,607,'红色：新写的一笔',9,color='red')
    text(c,427,607,'深灰：此前笔画',9,color='previous')
    size=86
    starts=[(LEFT+RIGHT-size)/2] if n==1 else [LEFT+i*(RIGHT-LEFT-size)/(n-1) for i in range(n)]
    for i,x in enumerate(starts):
        text(c,x+size/2,575,str(i+1)+'  '+e['stroke_names'][i],12,center=True)
        grid(c,x,477,size); glyph(c,data,x,477,size,step=i)
        if i<n-1:
            x1,x2=x+size+9,starts[i+1]-9
            if x2>x1+4:
                c.setStrokeColor(HexColor(COL['border'])); c.setLineWidth(.7); c.line(x1,520,x2,520)
                c.line(x2-3,523,x2,520); c.line(x2-3,517,x2,520)
    text(c,LEFT,454,'先按顺序读笔画，再用手指书空。格间箭头表示阅读顺序。',10,color='muted')
    text(c,LEFT,425,'02  描红、描淡字、独立写',14,color='red')
    text(c,LEFT,405,'第1行描红，第2行描淡字；后两行看范字，再在空格中练写。',10,color='muted')
    cell=(RIGHT-LEFT-7*6)/8
    for row in range(4):
        y=326-row*(cell+13)
        for col in range(8):
            x=LEFT+col*(cell+6); grid(c,x,y,cell)
            if row<2 or col==0: glyph(c,data,x,y,cell,['trace','pale','ink','ink'][row])
    text(c,LEFT,89,'写完检查：'+e['check'],10,color='muted',width=RIGHT-LEFT)
    c.setStrokeColor(HexColor(COL['guide'])); c.line(LEFT,74,RIGHT,74)
    label=batch['draft_label'] if draft else '已通过本工程发布门槛。'
    text(c,LEFT,58,label,8,color='red' if draft else 'muted')
    text(c,LEFT,43,'依据：GF0023—2020，第'+str(e['primary_printed_page'])+'页；矢量：Hanzi Writer / Arphic PL。',8,color='muted')
    text(c,LEFT,29,'打印：A4纵向，实际大小 / 100%；建议彩色。',8,color='muted')
    text(c,RIGHT-40,29,f"{batch['batch_id']} / {page_number:02}",8,color='muted',font='Latin')
    c.showPage()

def frontmatter(path):
    body=ParagraphStyle('body',fontName='CJK',fontSize=11.5,leading=20,spaceAfter=9,wordWrap='CJK',firstLineIndent=23)
    heading=ParagraphStyle('heading',parent=body,fontSize=15,leading=24,spaceBefore=11,spaceAfter=8,firstLineIndent=0,textColor=HexColor(COL['red']),keepWithNext=True)
    title=ParagraphStyle('title',parent=heading,fontSize=25,leading=36,spaceBefore=0)
    note=ParagraphStyle('note',parent=body,fontSize=10,leading=17,firstLineIndent=0,textColor=HexColor(COL['muted']))
    story=[]
    raw=(ROOT/'book/front-matter/preface.md').read_text(encoding='utf-8')
    for block in raw.split('\n\n'):
        block=block.strip()
        if not block or block=='---': continue
        style=body
        if block.startswith('# '): style=title; block=block[2:]
        elif block.startswith('## '): style=heading; block=block[3:]
        elif block.startswith('> '): style=note; block=block[2:]
        elif block.startswith('依据说明') or block.startswith('详细入口'): style=note
        block=re.sub(r'`([^`]+)`',r'\1',block)
        story.append(Paragraph(html.escape(block).replace('\n','<br/>'),style))
    def page(c,doc):
        text(c,42,H-29,'循序渐进汉字部首字帖 · 前言初稿',9,color='muted')
        text(c,42,29,'编写中 v0.2｜201主项为全书目标，不代表正文已全部审定。',8,color='muted')
        text(c,W-68,29,str(doc.page),9,color='muted',font='Latin')
    SimpleDocTemplate(str(path),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=57,bottomMargin=55).build(story,onFirstPage=page,onLaterPages=page)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--draft',action='store_true')
    p.add_argument('--batch',choices=['B01','B02'],default='B01')
    p.add_argument('--font',default='/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf')
    p.add_argument('--latin-font',default='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    args=p.parse_args()
    cat,batches,variants,batch=(load(n) for n in ['data/coverage.json','data/batches.json','data/variants.json',f'data/{args.batch}.json'])
    validate(cat,batches,variants,batch)
    if not args.draft and not batch['release_eligible']: raise SystemExit('Formal publication blocked; use --draft for explicit research output.')
    setup_fonts(args.font,args.latin_font)
    out=ROOT/'build'; out.mkdir(exist_ok=True)
    mode='draft' if args.draft else 'release'
    pdf=out/f'{args.batch}_{mode}_A4.pdf'; c=canvas.Canvas(str(pdf),pagesize=A4,pageCompression=1,invariant=1)
    c.setTitle(args.batch+'笔顺练字帖'+('（编写稿）' if args.draft else ''))
    checks=[]
    for i,e in enumerate(batch['entries'],1):
        fp=out/'vectors'/f'{ord(e["character"]):04X}.json'; raw=fp.read_bytes()
        d=prepare(json.loads(raw),len(e['stroke_names'])); make_page(c,e,d,i,args.draft,batch)
        checks.append({'character':e['character'],'stroke_count':len(d[0]),'sha256':hashlib.sha256(raw).hexdigest(),'practice_cells':32})
    c.save(); pre=out/'preface_v0.2.pdf'; frontmatter(pre)
    writer=PdfWriter()
    for file in [pre,pdf]: writer.append(str(file))
    combined=out/f'{args.batch}_with_preface_{mode}_A4.pdf'
    with combined.open('wb') as stream: writer.write(stream)
    (out/f'generation_{args.batch}.json').write_text(json.dumps({'draft':args.draft,'entries':checks,'practice_pages':10,'preface_pages':len(PdfReader(str(pre)).pages),'visual_review':'pending'},ensure_ascii=False,indent=2),encoding='utf-8')
    print(combined)

if __name__=='__main__':main()
