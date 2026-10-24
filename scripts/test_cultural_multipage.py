#!/usr/bin/env python3
"""Verify P4 cultural covers and continuations against original PDF source tiles."""
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import fitz,numpy as np
from PIL import Image
from cultural_source_audit import audit

def image(doc,page,rect):
    pix=doc[page].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(rect),alpha=False)
    src=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    return np.asarray(src.resize((160,160),Image.Resampling.BILINEAR),dtype=np.float32)

def verify(source,manifest,content,pdf,proof):
    source_index=audit(source,manifest)
    meta=json.loads(proof.read_text(encoding='utf8'))
    rows=json.loads(content.read_text(encoding='utf8'))['entries']
    by_id={g['main_id']:g for g in source_index['glyphs']}
    words={g['main_id']:g for g in rows}
    assert meta['status']=='P4_source_locked_editorial_draft_not_for_release'
    assert meta['source_sha256']==source_index['source_pdf_sha256']
    assert meta['output_sha256']==hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert (meta['main_ids'],meta['pages'],meta['total_source_strokes'])==(3,5,36)
    assert meta['tile_mm']>=30 and meta['uses_only_original_source_pdf_tiles']
    steps_by_id=defaultdict(list);pages_by_id=defaultdict(list);errors=[]
    with fitz.open(source) as old,fitz.open(pdf) as new:
        assert len(new)==len(meta['page_map'])==5
        for pn,record in enumerate(meta['page_map']):
            glyph=by_id[record['main_id']]
            assert glyph['character']==record['character']==words[record['main_id']]['character']
            assert record['editorial_state']=='draft_unreviewed'
            assert 1<=len(record['source_steps'])<=(6 if record['part']==1 else 15)
            assert abs(new[pn].rect.width-595.276)<.4
            assert abs(new[pn].rect.height-841.89)<.4
            text=new[pn].get_text()
            assert '笔顺' in text and ('待审' in text or '待审核' in text)
            if record['part']==1:
                for phrase in ('笔顺提示','相关字词','一字一句',words[record['main_id']]['title']):
                    assert phrase in text,(glyph['character'],phrase)
                for term in words[record['main_id']]['terms']:
                    assert term['word'] in text and term['pinyin'] in text
            else:assert '续页' in text
            if glyph['pinyin_from_pdf']:
                assert glyph['pinyin_from_pdf'] in text and record['source_reading_state']=='published_source'
            else:
                assert '读音待审核' in text and record['source_reading_state']=='blocked_no_source_pdf_reading'
                assert 'yuè' not in text
            pages_by_id[record['main_id']].append(record)
            boxes=[]
            for st in record['source_steps']:
                reference=glyph['steps'][st['index']-1]
                for k in ('index','name','pdf_page','rect_pt'):
                    assert st[k]==reference[k],(glyph['character'],k)
                dst=fitz.Rect(st['preview_rect_pt'])
                assert new[pn].rect.contains(dst)
                assert abs(dst.width-(31*72/25.4))<.3 and abs(dst.height-(31*72/25.4))<.3
                assert dst.y1<280*72/25.4
                assert not any(dst.intersects(other) for other in boxes)
                boxes.append(dst)
                steps_by_id[record['main_id']].append(st['index'])
                x=image(old,st['pdf_page']-1,st['rect_pt'])
                y=image(new,pn,st['preview_rect_pt'])
                error=float(np.abs(x-y).mean())
                assert error<9.5,(glyph['character'],st['index'],error)
                errors.append(error)
        assert sorted(steps_by_id)==[106,200,201]
        for mid,nums in steps_by_id.items():
            assert nums==list(range(1,by_id[mid]['stroke_count']+1))
        assert [len(x['source_steps']) for x in pages_by_id[106]]==[5]
        assert [len(x['source_steps']) for x in pages_by_id[200]]==[6,8]
        assert [len(x['source_steps']) for x in pages_by_id[201]]==[6,11]
        assert [x['part'] for x in pages_by_id[201]]==[1,2]
    return {'result':'PASS','A4_pages':5,'all_36_source_strokes_checked':len(errors),
            'worst_rgb_mae':round(max(errors),4),'original_pdf_sha256':source_index['source_pdf_sha256'],
            'strokes_per_character':{str(k):len(v) for k,v in steps_by_id.items()},
            'editorial_status':'draft_only'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ('source','manifest','content','pdf','proof'):
        p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(verify(a.source,a.manifest,a.content,a.pdf,a.proof),ensure_ascii=False,indent=2))
