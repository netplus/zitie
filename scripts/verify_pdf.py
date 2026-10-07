#!/usr/bin/env python3
"""Check A4 dimensions, draft labels, pagination and grid counts; not semantics."""
import argparse
import json
import math
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def stroke_count(entry):
    if isinstance(entry.get('stroke_count'),int):
        return entry['stroke_count']
    if isinstance(entry.get('stroke_names'),list):
        return len(entry['stroke_names'])
    review=entry.get('fine_stroke_names_review') or {}
    if isinstance(review.get('adjudicated_names'),list):
        return len(review['adjudicated_names'])
    if isinstance(entry.get('stroke_names_candidate'),list):
        return len(entry['stroke_names_candidate'])
    raise ValueError(entry['character']+': no stroke count for PDF verification')

plan=load('data/batches.json')
choices=[item['id'] for item in plan['frozen_batches']]
parser=argparse.ArgumentParser()
parser.add_argument('--batch',choices=choices,default='B01')
args=parser.parse_args()

batch=load(f'data/{args.batch}.json')
reader=PdfReader(str(ROOT/f'build/{args.batch}_draft_A4.pdf'))
expected_pages=sum(max(1,math.ceil(stroke_count(e)/6)) for e in batch['entries'])
assert len(reader.pages)==expected_pages, (args.batch,len(reader.pages),expected_pages)

page_index=0
for e in batch['entries']:
    n=stroke_count(e)
    parts=max(1,math.ceil(n/6))
    for part in range(parts):
        p=reader.pages[page_index]; page_index+=1
        assert abs(float(p.mediabox.width)-595.276)<.1 and abs(float(p.mediabox.height)-841.89)<.1
        txt=p.extract_text()
        assert '笔顺练字帖' in txt
        assert '编写稿' in txt
        step_count=min(6,n-part*6)
        # One header grid, one grid per displayed cumulative step, and 32 practice grids.
        assert p.get_contents().get_data().count(b' re')==33+step_count
        if parts>1:
            assert f'第{part+1}/{parts}页' in txt
        if not e.get('pinyin'):
            assert '读音：本项目不单列' in txt

print(f'PDF structural preflight: {args.batch}, {expected_pages} A4 pages; max 6 cumulative steps/page; 32 practice cells/page.')
