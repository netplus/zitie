#!/usr/bin/env python3
"""P1 source-only technical atlas: all 201 IDs, all 1045 released-PDF steps.

No cultural words or generated ink. 5 columns × <=3 rows; >15 strokes flow
to a continuation page (e.g. 龠17 -> 15 + 2). This is NOT the final booklet.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math
from pathlib import Path
import fitz
from reportlab.pdfgen import canvas
from cultural_source_audit import audit
from build_cultural_sample import fonts

MM=72/25.4
A4=(210*MM,297*MM)
COLS,MAX_ROWS=5,3
PER_PAGE=COLS*MAX_ROWS
SIDE_MM=31.0
GAP_MM=5.0
ORIGIN_X,ORIGIN_Y=17.5,70
ROW_PITCH_MM=62

def build(source:Path,manifest:Path|None,output:Path,proof:Path,only_id:int|None=None):
    index=audit(source,manifest)
    fonts()
    original=fitz.open(source)
    items=[g for g in index['glyphs'] if only_id is None or g['main_id']==only_id]
    if not items:raise ValueError(f'ID {only_id} not in the official book')
    memory=io.BytesIO();c=canvas.Canvas(memory,pagesize=A4,invariant=1)
    c.setTitle('源PDF全部笔顺图谱 · 自动分页技术验证 · 非出版稿')
    def draw(x,y,string,size=10,face='CultureKai'):
        c.setFont(face,size);c.drawString(x*MM,(297-y)*MM,string)
    def center(x,y,string,size=10,face='CultureKai'):
        c.setFont(face,size);c.drawCentredString(x*MM,(297-y)*MM,string)
    pages=[];total=0
    for glyph in items:
        strokes=glyph['steps']
        for pi in range(math.ceil(len(strokes)/PER_PAGE)):
            group=strokes[pi*PER_PAGE:(pi+1)*PER_PAGE]
            c.setStrokeColorRGB(.68,.46,.49);c.setLineWidth(.7)
            c.rect(10*MM,10*MM,190*MM,277*MM,stroke=1,fill=0)
            draw(17,24,'原 PDF 笔顺原图 · 自动分行测试',17)
            draw(17,41,f"ID{glyph['main_id']:03d}  {glyph['character']}  "
                f"{glyph['stroke_count']}笔 · 源PDF第{glyph['first_pdf_page']}页",12)
            if glyph['pinyin_from_pdf']:
                draw(17,49,glyph['pinyin_from_pdf'],10,'CultureLatin')
            else:
                draw(17,49,'本页不单列读音',10)
            draw(17,60,f"本字第{pi+1}/{math.ceil(len(strokes)/PER_PAGE)}张教学图 · "
                 "灰色先前笔画、红色当前笔画",9)
            boxes=[]
            for k,step in enumerate(group):
                col,row=k%COLS,k//COLS
                x,y=ORIGIN_X+col*(SIDE_MM+GAP_MM),ORIGIN_Y+row*ROW_PITCH_MM
                center(x+SIDE_MM/2,y-4,str(step['index'])+' '+step['name'],8.8)
                boxes.append([x*MM,y*MM,(x+SIDE_MM)*MM,(y+SIDE_MM)*MM])
            draw(17,283,'技术草稿 · 正式 v0.5.1 真实 PDF 累积矢量步骤；不作为文化字帖最终排版',8)
            pages.append({'main_id':glyph['main_id'],'character':glyph['character'],
                'part':pi+1,'total_parts':math.ceil(len(strokes)/PER_PAGE),
                'steps':[dict(step,rect_dest_pt=[round(v,5) for v in box])
                         for step,box in zip(group,boxes)]})
            total+=len(group)
            c.showPage()
    c.save();memory.seek(0)
    rendered=fitz.open(stream=memory.getvalue(),filetype='pdf')
    if len(rendered)!=len(pages):raise ValueError('Atlas page count mismatch')
    for pno,page in enumerate(pages):
        for st in page['steps']:
            rendered[pno].show_pdf_page(fitz.Rect(st['rect_dest_pt']),original,
                st['pdf_page']-1,clip=fitz.Rect(st['rect_pt']),
                keep_proportion=False,overlay=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    rendered.save(output,garbage=4,deflate=True,no_new_id=True)
    rendered.close();original.close()
    if total!=sum(g['stroke_count'] for g in items):
        raise ValueError('Lost source strokes during pagination')
    report={'status':'technical_source_atlas_not_release',
        'source_pdf_sha256':index['source_pdf_sha256'],
        'atlas_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'main_id_count':len(items),'pages':len(pages),'source_steps':total,
        'columns':COLS,'maximum_rows_per_page':MAX_ROWS,
        'minimum_step_cell_mm':SIDE_MM,
        'source_method':'original PDF Form XObject only, no generated glyph ink',
        'page_map':pages}
    proof.parent.mkdir(parents=True,exist_ok=True)
    proof.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='page_map'},ensure_ascii=False,indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--manifest',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--proof',type=Path,required=True)
    p.add_argument('--id',type=int)
    a=p.parse_args()
    build(a.source,a.manifest,a.output,a.proof,a.id)
