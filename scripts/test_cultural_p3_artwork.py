#!/usr/bin/env python3
"""P3 vector draft sources and in-PDF visual uniqueness verification."""
from __future__ import annotations
import argparse,hashlib,json
from itertools import combinations
from pathlib import Path
import fitz,numpy as np
from PIL import Image
from cultural_p3_artwork import read_registry

def crop_art(page):
    m=72/25.4
    px=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),
                       clip=fitz.Rect(111*m,45*m,193*m,120*m),alpha=False)
    image=Image.frombytes('RGB',(px.width,px.height),px.samples)
    return np.asarray(image.resize((100,100),Image.Resampling.BILINEAR),dtype=np.float32)

def validate(pdf,proof,registry):
    assets=read_registry(registry=registry)
    data=json.loads(proof.read_text(encoding='utf8'))
    assert data['status']=='editorial_draft_not_for_release'
    assert data['output_sha256'] if 'output_sha256' in data else data['candidate_pdf_sha256']
    assert data['candidate_pdf_sha256']==hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert data['pages']==4 and data['source_step_total']==15
    assert data['editorial_release_eligible'] is False
    assert data['artwork_is_teaching_ink'] is False
    assert len(data['p3_artwork']['actual_files'])==4
    vectors={}
    by_character={}
    with fitz.open(pdf) as doc:
        assert len(doc)==4
        for page,record in zip(doc,data['records']):
            char=record['character'];key=record['theme_key']
            assert char in ('水','山','月','木')
            assert assets[key]['main_character']==char
            assert len(record['source_steps'])==record['stroke_count']
            assert '笔顺提示' in page.get_text()
            assert '笔顺' in page.get_text()
            assert '词音/引文待审' in page.get_text()
            pix=crop_art(page)
            assert np.abs(pix-255).mean()>4, 'Empty or invisible artwork on '+char
            vectors[char]=pix
            by_character[char]=assets[key]['actual_sha256']
    distances={}
    for (x,a),(y,b) in combinations(vectors.items(),2):
        mae=float(np.abs(a-b).mean())
        distances[x+' vs '+y]=round(mae,3)
        if mae<=2.0:
            raise ValueError('Two character-theme artworks visually too similar: '+x+' '+y)
    assert len(set(by_character.values()))==4
    return {'status':'VISUAL_SOURCE_DRAFT_PASS_NOT_APPROVED',
      'pages':4,'artworks':4,'original_stroke_tiles':15,
      'unique_registered_svg_shas':by_character,
      'pairwise_mean_rgb_mae':distances,
      'minimum_difference':min(distances.values()),
      'source_material_status':'authorial SVG drafts; final editorial/art review pending'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for attr in ('pdf','proof','registry','output'):
        p.add_argument('--'+attr,type=Path,required=True)
    a=p.parse_args()
    result=validate(a.pdf,a.proof,a.registry)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
