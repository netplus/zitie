#!/usr/bin/env python3
"""Verify the generated formal v0.4.0 PDF before repository release archiving."""
import json
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
pdf=ROOT/'build/B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf'
meta=json.loads((ROOT/'build/generation_collection.json').read_text(encoding='utf-8'))
reader=PdfReader(str(pdf))

assert meta['mode']=='formal'
assert meta['release_eligible'] is False, 'Generated artifact is not formally released until archival/manifest merge'
assert meta['pages']==276
assert len(reader.pages)==276

texts=[p.extract_text() or '' for p in reader.pages]
joined='\n'.join(texts)

for forbidden in ('编写稿','前言初稿','编写中','发布候选稿 RC1','正式 release 尚未完成'):
    hits=[i for i,t in enumerate(texts,1) if forbidden in t]
    assert not hits, f'Formal PDF still contains pre-release label {forbidden}: pages {hits[:20]}'

assert all('正式发布版 v0.4.0' in texts[i] for i in range(3)), 'All 3 preface pages must be formal'
practice_label='正式发布版 v0.4.0｜保留卷末披露的 fail-closed/source-blocked 边界。'
practice_hits=[i+1 for i,t in enumerate(texts) if practice_label in t]
assert len(practice_hits)==258, len(practice_hits)
assert practice_hits[0]==6 and practice_hits[-1]==263, (practice_hits[0],practice_hits[-1])

assert 'GF0011—2022逐项精确字段' in joined
assert '201 source_blocked_fail_closed' in joined
assert '当前release' in joined
assert 'v0.4.0；正式发布' in joined
assert '201主部首索引' in joined
assert '常用附形与位置变体索引' in joined
assert '原27项对应表' in joined

print(json.dumps({
    'status':'formal_v0.4.0_pdf_preflight_passed',
    'pages':276,
    'formal_preface_pages':3,
    'formal_practice_pages':258,
    'formal_release_archived':False,
    'source_blocked_disclosure_retained':True
},ensure_ascii=False,indent=2))
