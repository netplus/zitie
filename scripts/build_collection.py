#!/usr/bin/env python3
"""Assemble already-built batch PDFs into the configured full-book research draft."""
from pathlib import Path
import json
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parents[1]
book=json.loads((ROOT/'data/book-config.json').read_text(encoding='utf-8'))

batches=book['built_batches']
if batches != [f'B{i:02d}' for i in range(1,22)]:
    raise ValueError('P7 full-book draft requires configured B01-B21 coverage')

files=[book['preface_file']]+[b+'_draft_A4.pdf' for b in batches]
writer=PdfWriter()
expected_pages=0
for name in files:
    path=ROOT/'build'/name
    if not path.is_file():
        raise FileNotFoundError(path)
    reader=PdfReader(str(path))
    expected_pages += len(reader.pages)
    writer.append(str(path))

out=ROOT/'build'/book['collection_file']
with out.open('wb') as stream:
    writer.write(stream)

actual_pages=len(PdfReader(str(out)).pages)
if actual_pages != expected_pages:
    raise ValueError(f'Collection page mismatch: {actual_pages} != {expected_pages}')

summary={
    'version':book['version'],
    'batches':batches,
    'batch_count':len(batches),
    'preface_file':book['preface_file'],
    'collection_file':book['collection_file'],
    'pages':actual_pages,
    'status':'research_draft_not_archived',
    'release_eligible':False
}
(ROOT/'build/generation_collection.json').write_text(
    json.dumps(summary,ensure_ascii=False,indent=2)+'\n',
    encoding='utf-8'
)
print(out,'pages',actual_pages)
