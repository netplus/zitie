#!/usr/bin/env python3
"""Assemble only already-built batch PDFs; no change to editorial status."""
from pathlib import Path
import json
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
book=json.loads((ROOT/'data/book-config.json').read_text(encoding='utf-8'))
files=[book['preface_file']]+[b+'_draft_A4.pdf' for b in book['built_batches']]
writer=PdfWriter()
for name in files:writer.append(str(ROOT/'build'/name))
path=ROOT/'build/B01-B02_with_preface_draft_A4.pdf';writer.write(path)
print(path,'pages',len(PdfReader(path).pages))
