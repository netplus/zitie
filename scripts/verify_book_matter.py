#!/usr/bin/env python3
"""Verify P7 book-matter structure and navigation metadata; not semantic approval."""
import json
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

meta=load('build/generation_book_matter.json')
collection=load('build/generation_collection.json')
variants=load('data/variants.json')['items']

assert meta['toc_pages']==2
assert meta['backmatter_pages']==13
assert meta['main_index_main_ids']==list(range(1,202)), 'Main-radical index must be sorted 1..201'
expected_variants=[v['id'] for v in variants]
assert meta['variant_ids']==expected_variants
assert meta['legacy_variant_ids']==expected_variants[:27]
assert expected_variants==[f'V{i:03d}' for i in range(1,33)]
assert meta['legacy_variant_ids']==[f'V{i:03d}' for i in range(1,28)]

toc=PdfReader(str(ROOT/'build'/meta['toc_file']))
back=PdfReader(str(ROOT/'build'/meta['backmatter_file']))
full=PdfReader(str(ROOT/'build'/collection['collection_file']))
assert len(toc.pages)==2
assert len(back.pages)==13
assert len(full.pages)==collection['pages']==276
assert collection['release_eligible'] is False

back_text='\n'.join((p.extract_text() or '') for p in back.pages)
for token in ('201主部首索引','常用附形与位置变体索引','原27项对应表','来源与字段复核说明','版本、勘误与发布状态'):
    assert token in back_text, token
for vid in ('V001','V027','V032'):
    assert vid in back_text, vid

print('P7 book-matter preflight: 201 main IDs sorted; V001-V032 present; V001-V027 legacy subset present; 276 pages; release still fail-closed.')
