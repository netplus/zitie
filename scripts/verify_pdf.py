#!/usr/bin/env python3
"""Check count, dimensions, visible draft label and grid rectangles; not semantics."""
import json
from pathlib import Path
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
batch=json.loads((ROOT/'data/B01.json').read_text(encoding='utf-8'))
reader=PdfReader(str(ROOT/'build/B01_draft_A4.pdf'))
assert len(reader.pages)==len(batch['entries'])==10
for p,e in zip(reader.pages,batch['entries']):
    assert abs(float(p.mediabox.width)-595.276)<.1 and abs(float(p.mediabox.height)-841.89)<.1
    txt=p.extract_text()
    assert e['character']+'｜笔顺练字帖' in txt
    assert '编写稿' in txt and '第二权威来源' in txt
    # One header grid, one per stroke and 32 practice grids. Glyphs use paths, not rectangles.
    assert p.get_contents().get_data().count(b' re')==33+len(e['stroke_names'])
print('PDF structural preflight: 10 A4 pages, each 32 practice cells; draft labels retained.')
