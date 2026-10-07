#!/usr/bin/env python3
"""Verify the generated P7 RC1 PDF without promoting it to formal release."""
import json
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
pdf=ROOT/'build/B01-B21_with_preface_toc_appendices_rc1_A4.pdf'
meta=json.loads((ROOT/'build/generation_collection.json').read_text(encoding='utf-8'))
reader=PdfReader(str(pdf))

assert meta['mode']=='candidate'
assert meta['release_eligible'] is False
assert meta['pages']==276
assert len(reader.pages)==276

texts=[p.extract_text() or '' for p in reader.pages]
joined='\n'.join(texts)

for forbidden in ('编写稿','前言初稿','编写中'):
    hits=[]
    for page_no,text in enumerate(texts,1):
        if forbidden in text:
            pos=text.index(forbidden)
            hits.append({'page':page_no,'context':text[max(0,pos-40):pos+80].replace('\\n',' / ')})
    assert not hits, f'RC1 still contains draft label {forbidden}: {hits}'

candidate_markers=sum('发布候选稿 RC1' in t for t in texts)
assert candidate_markers==258, candidate_markers

assert 'GF0011—2022逐项精确字段' in joined
assert '201 source_blocked_fail_closed' in joined
assert '当前release' in joined
assert '0；deliverables/releases/仍为空' in joined
assert '201主部首索引' in joined
assert '常用附形与位置变体索引' in joined
assert '原27项对应表' in joined

print(json.dumps({
    'status':'RC1_pdf_preflight_passed',
    'pages':len(reader.pages),
    'candidate_practice_page_markers':candidate_markers,
    'release_eligible':False,
    'formal_release':False
},ensure_ascii=False,indent=2))
