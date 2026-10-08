#!/usr/bin/env python3
"""Check committed PDF bytes and recorded status; not a content truth checker."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from pypdf import PdfReader
ROOT = Path(__file__).resolve().parents[1]

def verify(root=ROOT, base_ref=None):
    root = Path(root).resolve()
    manifest = json.loads((root / 'deliverables/manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported deliverable manifest')
    seen = {}
    for item in manifest['artifacts']:
        relative = Path(item['path']); path = root / relative
        if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] != 'deliverables':
            raise ValueError('Unsafe deliverable path')
        if path.is_symlink() or not path.is_file() or path.suffix.lower() != '.pdf':
            raise ValueError('Missing, non-PDF or symlink deliverable: ' + str(relative))
        if item['path'] in seen: raise ValueError('Duplicate deliverable path')
        data = path.read_bytes()
        if not data.startswith(b'%PDF-') or hashlib.sha256(data).hexdigest() != item['sha256'] or len(data) != item['bytes']:
            raise ValueError('PDF bytes do not match manifest: ' + str(relative))
        reader = PdfReader(path)
        if reader.is_encrypted or len(reader.pages) != item['pages']:
            raise ValueError('Page count or encryption mismatch: ' + str(relative))
        for page in reader.pages:
            if abs(float(page.mediabox.width)-595.2756) > 1 or abs(float(page.mediabox.height)-841.8898) > 1:
                raise ValueError('Not portrait A4: ' + str(relative))
        if item.get('provenance_kind') == 'locally_reviewed_pdf_derivative':
            # PDF-level local revisions are imported, not attributed to the RC1 build.
            from verify_q1_import import validate_entry
            validate_entry(root, item)
        elif item.get('provenance_kind') == 'reproducible_edition_from_reviewed_RC3':
            from verify_v050_final import check_manifest_entry
            check_manifest_entry(item)
        elif item.get('provenance_kind') == 'reproducible_punctuation_erratum_from_reviewed_RC3':
            from verify_v051_punctuation import check_manifest_entry
            check_manifest_entry(item)
        elif not isinstance(item.get('source_commit'), str) or not re.fullmatch(r'[0-9a-f]{40}', item['source_commit']):
            raise ValueError('An exact source commit is required')
        review = Path(item['review_record'])
        if review.is_absolute() or '..' in review.parts or not (root / review).is_file():
            raise ValueError('Missing or unsafe review record')
        if item['status'] == 'draft':
            if 'drafts' not in relative.parts or item['release_eligible'] is not False:
                raise ValueError('Draft status cannot be promoted by archiving')
        elif item['status'] == 'release_candidate':
            if 'drafts' not in relative.parts or item['release_eligible'] is not False:
                raise ValueError('Release candidate must remain under drafts and release_eligible=false')
            if '-rc' not in item.get('version',''):
                raise ValueError('Release candidate requires an rc version')
        elif item['status'] == 'released':
            if 'releases' not in relative.parts or item['release_eligible'] is not True:
                raise ValueError('Invalid release location/status')
            gate = item.get('release_gate_snapshot', {})
            for key in ('scope','primary','cross','metadata','artwork','layout'):
                if gate.get(key) != 'passed': raise ValueError('Missing editorial release gate: ' + key)
            if gate.get('unresolved_conflicts') != 0: raise ValueError('Unresolved release conflicts')
        else: raise ValueError('Unknown editorial status')
        seen[item['path']] = item
    actual = {p.relative_to(root).as_posix() for p in (root/'deliverables').rglob('*.pdf')}
    if actual != set(seen): raise ValueError('Unregistered or missing PDFs: ' + repr(actual.symmetric_difference(seen)))
    if base_ref:
        subprocess.run(['git','rev-parse','--verify',base_ref+'^{commit}'],cwd=root,check=True,capture_output=True)
        old = subprocess.run(['git','show',base_ref+':deliverables/manifest.json'],cwd=root,capture_output=True,text=True)
        if old.returncode == 0:
            for item in json.loads(old.stdout)['artifacts']:
                now = seen.get(item['path'])
                if not now or any(now.get(k) != item.get(k) for k in ('sha256','bytes','pages','status','source_commit','release_eligible')):
                    raise ValueError('Historical delivery was removed or rewritten: '+item['path'])
        elif 'does not exist' not in old.stderr and 'exists on disk, but not in' not in old.stderr:
            raise ValueError('Unable to read base manifest: '+old.stderr)
    return {
        'registered_pdfs':len(seen),
        'stored_bytes':sum(i['bytes'] for i in seen.values()),
        'draft_pdfs':sum(i['status']=='draft' for i in seen.values()),
        'candidate_pdfs':sum(i['status']=='release_candidate' for i in seen.values()),
        'released_pdfs':sum(i['status']=='released' for i in seen.values()),
        'note':'Byte, format and status checks only; editorial review remains separate.'
    }

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base-ref')
    print(json.dumps(verify(base_ref=parser.parse_args().base_ref),ensure_ascii=False,indent=2))
