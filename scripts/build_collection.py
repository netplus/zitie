#!/usr/bin/env python3
"""Assemble the configured full-book research draft with P7 navigation and appendices."""
from pathlib import Path
import argparse
import json
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parents[1]
book=json.loads((ROOT/'data/book-config.json').read_text(encoding='utf-8'))

parser=argparse.ArgumentParser()
parser.add_argument('--candidate',action='store_true')
args=parser.parse_args()
mode='candidate' if args.candidate else 'draft'

batches=book['built_batches']
if batches != [f'B{i:02d}' for i in range(1,22)]:
    raise ValueError('P7 full-book draft requires configured B01-B21 coverage')

preface = 'preface_v0.4.0_rc1.pdf' if mode=='candidate' else book['preface_file']
files=[
    preface,
    book['toc_file'],
    *[b+f'_{mode}_A4.pdf' for b in batches],
    book['backmatter_file'],
]
writer=PdfWriter()
page_parts=[]
expected_pages=0
for name in files:
    path=ROOT/'build'/name
    if not path.is_file():
        raise FileNotFoundError(path)
    pages=len(PdfReader(str(path)).pages)
    page_parts.append({'file':name,'pages':pages})
    expected_pages += pages
    writer.append(str(path))

out_name='B01-B21_with_preface_toc_appendices_rc1_A4.pdf' if mode=='candidate' else book['collection_file']
out=ROOT/'build'/out_name
with out.open('wb') as stream:
    writer.write(stream)

actual_pages=len(PdfReader(str(out)).pages)
if actual_pages != expected_pages:
    raise ValueError(f'Collection page mismatch: {actual_pages} != {expected_pages}')
if actual_pages != 276:
    raise ValueError(f'Expected v0.4.0 structured draft to be 276 pages, got {actual_pages}')

summary={
    'version':book['version'],
    'batches':batches,
    'batch_count':len(batches),
    'parts':page_parts,
    'collection_file':out_name,
    'pages':actual_pages,
    'status':'release_candidate_generated_not_archived' if mode=='candidate' else 'structured_research_draft_not_archived',
    'mode':mode,
    'release_eligible':False
}
(ROOT/'build/generation_collection.json').write_text(
    json.dumps(summary,ensure_ascii=False,indent=2)+'\n',
    encoding='utf-8'
)
print(out,'pages',actual_pages)
