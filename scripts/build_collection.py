#!/usr/bin/env python3
"""Assemble only already-built batch PDFs; no change to editorial status."""
from pathlib import Path
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
files=['preface_v0.2.pdf','B01_draft_A4.pdf','B02_draft_A4.pdf']
writer=PdfWriter()
for name in files:writer.append(str(ROOT/'build'/name))
path=ROOT/'build/B01-B02_with_preface_draft_A4.pdf';writer.write(path)
print(path,'pages',len(PdfReader(path).pages))
