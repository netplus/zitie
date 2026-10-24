#!/usr/bin/env python3
"""Audit actual source PDF cumulative stroke tiles: 201 IDs, 1045 strokes.

No OCR, no generative stroke geometry. Fail closed on missing/extra tiles and
on a disagreement with the frozen v0.5.1 manifest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
import fitz

EXPECTED_SHA256 = '7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90'
EXPECTED_PAGES, EXPECTED_IDS, EXPECTED_STROKES, EXPECTED_TEACHING_PAGES = 299, 201, 1045, 258
TITLE = re.compile(r'^ID(\d{3})\s+(.+)$')
COUNT = re.compile(r'^(\d+)画\s*·\s*主部首$')
STEP = re.compile(r'^([1-9]\d?)  (\S.*)$')

def source_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def source_step_rectangles(page:fitz.Page) -> list[fitz.Rect]:
    """Get actual 86pt source teaching tiles; never the 60pt exercise cells."""
    boxes=[]
    for path in page.get_drawings():
        for item in path['items']:
            if item[0]!='re':continue
            rect=fitz.Rect(item[1])
            if abs(rect.width-86)<.15 and abs(rect.height-86)<.15 and abs(rect.y0-278.88977)<.3:
                boxes.append(rect)
    boxes.sort(key=lambda box:box.x0)
    if len(boxes)!=len(set((round(r.x0,2),round(r.y0,2)) for r in boxes)):
        raise ValueError(f'Duplicate source teaching tile on PDF page {page.number+1}')
    return boxes

def page_steps(page:fitz.Page)->list[tuple[int,str]]:
    steps=[]
    for line in page.get_text().splitlines():
        m=STEP.fullmatch(line.strip())
        if m and m.group(2) not in ('看笔顺','描红、描淡字、独立写'):
            steps.append((int(m.group(1)),m.group(2)))
    return steps

def extract_basics(page:fitz.Page)->tuple[int,str|None,list[str]]:
    lines=[line.strip() for line in page.get_text().splitlines()]
    ix=next((i for i, line in enumerate(lines) if COUNT.fullmatch(line)),None)
    if ix is None:raise ValueError(f'Missing review stroke count on page {page.number+1}')
    n=int(COUNT.fullmatch(lines[ix]).group(1))
    pinyin=lines[ix-1]
    if any(s in pinyin for s in ('读音待核','本页不标注','本页不单列读音')):
        pinyin=None
    tips=[]
    for line in lines[ix+1:]:
        if line=='01  看笔顺':break
        tips.append(line)
    if not 1<=len(tips)<=3:raise ValueError(f'Invalid source tips on page {page.number+1}')
    return n,pinyin,tips

def audit(source:Path,manifest:Path|None=None)->dict:
    checksum=source_sha256(source)
    if checksum!=EXPECTED_SHA256:raise ValueError('Official v0.5.1 PDF checksum mismatch')
    if manifest:
        artifacts=json.loads(manifest.read_text(encoding='utf8'))['artifacts']
        entries=[x for x in artifacts if x.get('path')==
          'deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf']
        if len(entries)!=1 or entries[0]['sha256']!=checksum or entries[0]['status']!='released':
            raise ValueError('Frozen source does not match manifest')
    doc=fitz.open(source)
    try:
        if len(doc)!=EXPECTED_PAGES:raise ValueError('Source must be 299 A4 pages')
        bookmarks=[]
        for _,title,page in doc.get_toc():
            m=TITLE.fullmatch(title)
            if m:bookmarks.append((int(m.group(1)),m.group(2),page))
        if (len(bookmarks)!=EXPECTED_IDS or
            sorted(k for k,_,_ in bookmarks)!=list(range(1,EXPECTED_IDS+1))):
            raise ValueError('Exactly 201 unique source ID bookmarks required')
        seen=set();glyphs=[]
        for mid,char,first in bookmarks:
            n,pinyin,tips=extract_basics(doc[first-1]);steps=[]
            for pi in range(math.ceil(n/6)):
                page_no=first+pi; page=doc[page_no-1]
                expected=list(range(pi*6+1,min(n,(pi+1)*6)+1))
                boxes=source_step_rectangles(page);labels=page_steps(page)
                if len(boxes)!=len(expected) or [x[0] for x in labels]!=expected:
                    raise ValueError(f'ID{mid:03d} {char}, page {page_no}: '
                                     f'wrong tile/label count or sequence')
                if page_no in seen:raise ValueError(f'Overlapping PDF source page {page_no}')
                seen.add(page_no)
                for (idx,name),box in zip(labels,boxes):
                    steps.append({'index':idx,'name':name,'pdf_page':page_no,
                                  'rect_pt':[round(v,5) for v in box]})
            glyphs.append({'main_id':mid,'character':char,'first_pdf_page':first,
                           'stroke_count':n,'pinyin_from_pdf':pinyin,
                           'tips_from_pdf':tips,'steps':steps})
        total=sum(g['stroke_count'] for g in glyphs)
        if total!=EXPECTED_STROKES or len(seen)!=EXPECTED_TEACHING_PAGES:
            raise ValueError(f'Expected 1045 steps / 258 pages, got {total}/{len(seen)}')
        return {'status':'source_verified_only','source_pdf_sha256':checksum,
                'source_pdf_pages':len(doc),'main_ids':len(glyphs),
                'total_source_steps':total,'source_teaching_pages':len(seen),
                'glyphs':sorted(glyphs,key=lambda g:g['main_id'])}
    finally:
        doc.close()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.source,args.manifest)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='glyphs'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
