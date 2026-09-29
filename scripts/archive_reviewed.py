#!/usr/bin/env python3
"""Archive previously reviewed CI PDF bytes; never rebuild or modify old PDFs."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]

def main():
    request = json.loads((ROOT/'maintenance/archive-request.json').read_text(encoding='utf-8'))
    version = request['version']
    source = request['source_commit']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not re.fullmatch(r'[0-9a-f]{40}', source):
        raise ValueError('Invalid version or source commit')
    actual_source = (ROOT/'archive-download/SOURCE_COMMIT.txt').read_text().strip()
    if actual_source != source:
        raise ValueError('Downloaded artifact was built from a different source commit')
    subprocess.run(['git','merge-base','--is-ancestor',source,'HEAD'],cwd=ROOT,check=True)
    manifest_path = ROOT/'deliverables/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    prior = {entry['path'] for entry in manifest['artifacts']}
    prepared=[]
    for item in request['files']:
        name=item['name']
        if not re.fullmatch(r'[A-Za-z0-9_.-]+\.pdf', name):
            raise ValueError('Only flat PDF filenames may be archived')
        relative=f'deliverables/drafts/v{version}/{name}'
        destination=ROOT/relative
        if relative in prior or destination.exists():
            raise ValueError('Refusing to replace an archived PDF: '+relative)
        data=(ROOT/'archive-download'/name).read_bytes()
        if not data.startswith(b'%PDF-') or len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError('PDF identity mismatch: '+name)
        if len(PdfReader(ROOT/'archive-download'/name).pages)!=item['pages']:
            raise ValueError('PDF page count mismatch: '+name)
        review_path=Path(item['review_record'])
        if review_path.is_absolute() or '..' in review_path.parts or not (ROOT/review_path).is_file():
            raise ValueError('Missing or invalid review record')
        entry={k:item[k] for k in ['title','batch','pages','bytes','sha256','review_record']}
        entry.update(path=relative,version=version,status='draft',release_eligible=False,
                     source_commit=source,workflow_run_id=request['run_id'],artifact_id=request['artifact_id'])
        prepared.append((destination,data,entry));prior.add(relative)
    for destination,data,entry in prepared:
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as stream:stream.write(data)
        manifest['artifacts'].append(entry)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Archived {len(prepared)} reviewed PDFs as v{version}; previous versions unchanged.')

if __name__=='__main__':main()
