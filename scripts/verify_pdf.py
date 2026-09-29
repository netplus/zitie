#!/usr/bin/env python3
"""Check count, dimensions, visible draft label and grid rectangles; not semantics."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--batch',choices=['B01','B02'],default='B01');args=parser.parse_args()
batch=json.loads((ROOT/f'data/{args.batch}.json').read_text(encoding='utf-8'))
reader=PdfReader(str(ROOT/f'build/{args.batch}_draft_A4.pdf'))
assert len(reader.pages)==len(batch['entries'])==10
for p,e in zip(reader.pages,batch['entries']):
    assert abs(float(p.mediabox.width)-595.276)<.1 and abs(float(p.mediabox.height)-841.89)<.1
    txt=p.extract_text()
    assert e['character']+'｜笔顺练字帖' in txt
    assert '编写稿' in txt and batch['draft_label'] in txt
    # One header grid, one per stroke and 32 practice grids. Glyphs use paths, not rectangles.
    assert p.get_contents().get_data().count(b' re')==33+len(e['stroke_names'])
print('PDF structural preflight: 10 A4 pages, each 32 practice cells; draft labels retained.')
