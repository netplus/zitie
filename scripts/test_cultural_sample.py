#!/usr/bin/env python3
"""Independent PDF vector source-frame equivalence test for P1 cultural sample."""
import argparse,hashlib,json
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from cultural_source_audit import audit

def thumbnail(doc,page,rect,size=200):
    pix=doc[page].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(rect),alpha=False)
    img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    return np.asarray(img.resize((size,size),resample=Image.Resampling.BILINEAR),
                      dtype=np.float32)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--manifest',type=Path)
    p.add_argument('--sample',type=Path,required=True)
    p.add_argument('--proof',type=Path,required=True)
    p.add_argument('--content',type=Path,required=True)
    args=p.parse_args()
    proof=json.loads(args.proof.read_text(encoding='utf8'))
    source_index=audit(args.source,args.manifest)
    content=json.loads(args.content.read_text(encoding='utf8'))
    assert proof['status']=='editorial_draft_not_for_release'
    assert proof.get('source_pdf_sha256',proof.get('released_source_pdf_sha256'))==source_index['source_pdf_sha256']
    assert proof.get('candidate_pdf_sha256',proof.get('preview_sha256'))==hashlib.sha256(args.sample.read_bytes()).hexdigest()
    assert source_index['main_ids']==201 and source_index['total_source_steps']==1045
    assert proof['source_step_total']==15
    glyphs={g['main_id']:g for g in source_index['glyphs']}
    records=proof.get('records',proof.get('entries'))
    with fitz.open(args.source) as original,fitz.open(args.sample) as draft:
        assert len(draft)==len(content['entries'])==len(records)==4
        scores=[]
        for pno,(editorial,row) in enumerate(zip(content['entries'],records)):
            item=glyphs[row['main_id']]
            steps=row.get('source_steps',row.get('steps'))
            assert row['character']==editorial['character']==item['character']
            assert row['stroke_count']==item['stroke_count']==len(steps)
            pg=draft[pno]
            assert abs(pg.rect.width-595.276)<.25 and abs(pg.rect.height-841.89)<.25
            printed=pg.get_text()
            for phrase in (editorial['title'],'笔顺提示','笔顺','字义',
                           '经典一隅','相关词','一字一句',item['tips_from_pdf'][0]):
                assert phrase in printed,(item['character'],phrase)
            for term in editorial['terms']:
                assert term['word'] in printed and term['pinyin'] in printed
            assert '待审' in printed and '练字格' not in printed
            used=[]
            for expected,observed in zip(item['steps'],steps):
                for field in ('pdf_page','rect_pt','name','index'):
                    assert expected[field]==observed[field],(item['character'],field)
                dst=fitz.Rect(observed['preview_rect_pt'])
                assert dst in pg.rect and dst.width>85 and dst.height>85
                assert not any(dst.intersects(other) for other in used)
                used.append(dst)
                first=thumbnail(original,expected['pdf_page']-1,expected['rect_pt'])
                second=thumbnail(draft,pno,observed['preview_rect_pt'])
                score=float(np.abs(first-second).mean())
                assert score<8.0,(item['character'],expected['index'],score)
                scores.append(score)
        print(json.dumps({'status':'PASS','pages':len(draft),'original_stroke_cards':len(scores),
                          'mean_source_pixel_difference':round(float(np.mean(scores)),3),
                          'max_source_pixel_difference':round(max(scores),3),
                          'readability':'requires human review',
                          'source':'v0.5.1 released actual PDF clip'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
