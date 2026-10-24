#!/usr/bin/env python3
"""Check all 201 source-ID atlas pages and selected original vector pixels."""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import fitz,numpy as np
from PIL import Image
from cultural_source_audit import audit

def pixels(doc,page,rect):
    pix=doc[page].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(rect),alpha=False)
    img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    return np.asarray(img.resize((180,180),resample=Image.Resampling.BILINEAR),
                      dtype=np.float32)

def validate(source,manifest,atlas,proof):
    verified=audit(source,manifest)
    report=json.loads(proof.read_text(encoding='utf8'))
    assert report['status']=='technical_source_atlas_not_release'
    assert report['source_pdf_sha256']==verified['source_pdf_sha256']
    assert hashlib.sha256(atlas.read_bytes()).hexdigest()==report['atlas_sha256']
    assert report['main_id_count']==201 and report['source_steps']==1045
    assert report['pages']==202 and report['minimum_step_cell_mm']>=30
    glyphs={g['main_id']:g for g in verified['glyphs']}
    by_id=defaultdict(list);scores=[]
    with fitz.open(source) as original,fitz.open(atlas) as output:
        assert len(output)==report['pages']
        for page_no,item in enumerate(report['page_map']):
            mid=item['main_id'];source_glyph=glyphs[mid]
            assert item['character']==source_glyph['character']
            assert item['part']==len(by_id[mid])+1
            by_id[mid].append(item)
            assert item['total_parts']==math.ceil(source_glyph['stroke_count']/15)
            assert 1<=len(item['steps'])<=15
            page=output[page_no]
            assert abs(page.rect.width-595.28)<.5 and abs(page.rect.height-841.89)<.5
            used=[]
            for step in item['steps']:
                base=source_glyph['steps'][step['index']-1]
                for field in ('index','name','pdf_page','rect_pt'):
                    assert base[field]==step[field],(mid,field)
                box=fitz.Rect(step['rect_dest_pt'])
                assert box in page.rect and box.width>=30*72/25.4 and box.height>=30*72/25.4
                assert not any(box.intersects(x) for x in used)
                used.append(box)
                if mid in (1,39,64,77,88,201):
                    src=pixels(original,step['pdf_page']-1,step['rect_pt'])
                    dst=pixels(output,page_no,step['rect_dest_pt'])
                    score=float(np.abs(src-dst).mean())
                    assert score<9.5,(mid,step['index'],score)
                    scores.append(score)
        assert len(by_id)==201
        for mid,pages in by_id.items():
            indices=[s['index'] for page in pages for s in page['steps']]
            assert indices==list(range(1,glyphs[mid]['stroke_count']+1))
        assert len(by_id[201])==2 and [len(p['steps']) for p in by_id[201]]==[15,2]
        assert [x['index'] for x in by_id[201][1]['steps']]==[16,17]
        assert '本页不单列读音' in output[-1].get_text()
    return {'status':'PASS','main_ids':len(by_id),'pages':report['pages'],
            'steps_preserved':report['source_steps'],'min_cell_mm':report['minimum_step_cell_mm'],
            'tested_original_source_tiles':len(scores),
            'maximum_rgb_mae':round(max(scores),3),
            'complex_ID201_paginated_steps':[len(p['steps']) for p in by_id[201]],
            'source_sha256':verified['source_pdf_sha256']}

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for name in ('source','atlas','proof'):
        a.add_argument('--'+name,type=Path,required=True)
    a.add_argument('--manifest',type=Path)
    args=a.parse_args()
    print(json.dumps(validate(args.source,args.manifest,args.atlas,args.proof),
                     ensure_ascii=False,indent=2))
