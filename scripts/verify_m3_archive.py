#!/usr/bin/env python3
"""Bind a full archived candidate to generation, review, configuration and state.

This verifies records, not whether an agent actually inspected a page. Q1 has
its own page-level review and publication gate; RC freezing cannot grant it.
"""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader
from m3_model import ROOT, digest
from m3_candidate import VERSION, validate_metadata, validate_ready
from verify_m2_closeout import load, require, safe_file

PATH = 'deliverables/drafts/v0.5.0-rc1/zitie-v0.5.0-rc1.pdf'
FREEZE = 'data/evidence/M3-candidate-freeze-20261008.json'


def verify(root=ROOT):
    root = Path(root)
    state = load(root, 'data/post_release.json')
    candidate = state.get('candidate')
    entries = [a for a in load(root, 'deliverables/manifest.json')['artifacts'] if a['version'].startswith('0.5.')]
    if candidate is None:
        require(not entries, 'Undeclared v0.5 candidate/release')
        require(state['phases'][2]['status'] != 'completed', 'M3 cannot exit without an archive')
        return {'status': 'not_archived', 'candidate_frozen': False}
    require(candidate['path'] == PATH and candidate['version'] == VERSION, 'Unexpected frozen candidate')
    # Retain the immutable compiled RC1 gate. Separately validate exact local
    # derivative imports; these cannot replace the frozen candidate or release it.
    derivatives = [a for a in entries if a.get('provenance_kind') == 'locally_reviewed_pdf_derivative']
    if derivatives:
        from verify_q1_import import verify as verify_q1_import
        verify_q1_import(root)
    editions = [a for a in entries if a.get('provenance_kind') == 'reproducible_edition_from_reviewed_RC3']
    if editions:
        from verify_v050_final import check_manifest_entry
        require(len(editions) == 1, 'Unexpected number of published v0.5 editions')
        check_manifest_entry(editions[0])
    entries = [a for a in entries if a not in derivatives and a not in editions]
    require(len(entries) == 1, 'Unverified frozen M3 v0.5 artifact')
    item = entries[0]
    for k in ('path', 'version', 'status', 'pages', 'bytes', 'sha256', 'source_commit',
              'source_tree', 'workflow_run_id', 'artifact_id', 'review_record', 'generation_record',
              'freeze_record', 'release_eligible'):
        require(item[k] == candidate[k], 'State/manifest disagreement: ' + k)
    require(item['status'] == 'release_candidate' and item['release_eligible'] is False,
            'Frozen candidate is not a publication grant')
    require(item['freeze_record'] == FREEZE and candidate['candidate_frozen'] is True,
            'Missing freeze contract')
    raw = safe_file(root, PATH).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == item['sha256'] and len(raw) == item['bytes'],
            'Archived bytes changed')
    require(len(PdfReader(root/PATH).pages) == item['pages'] == 299, 'Archived pages changed')
    meta = load(root, item['generation_record']); validate_metadata(meta)
    for key in ('version', 'pages', 'bytes', 'sha256', 'source_commit', 'source_tree'):
        require(meta[key] == item[key], 'Original generation mismatch: ' + key)
    for path, sha in meta['input_sha256'].items():
        require(digest(safe_file(root, path)) == sha, 'Frozen input changed: ' + path)
    freeze = load(root, FREEZE)
    for key in ('sha256', 'source_commit', 'source_tree', 'workflow_run_id', 'artifact_id'):
        require(freeze[key] == item[key], 'Freeze provenance mismatch: ' + key)
    require(freeze['generation_sha256'] == digest(root/item['generation_record']), 'Generation record changed')
    require(freeze['candidate_frozen'] is True and freeze['release_eligible'] is False
            and freeze['Q1_completed'] is False, 'Freeze grants premature publication/Q1')
    require(freeze['boundary_review']['blocking_findings'] == 0, 'Candidate boundary review unresolved')
    require({1,2,3,4,5,286,296,297,298,299} <= set(freeze['boundary_review']['MuPDF_pages']),
            'Candidate wording/navigation/appendix review incomplete')
    require({2,299} <= set(freeze['boundary_review']['Poppler_pages']), 'Candidate mode not cross-rendered')
    require(freeze['body_regression']['pages'] == list(range(6,286))
            and freeze['body_regression']['different_pages'] == [], 'Teaching body regression missing')
    require(freeze['not_full_book_Q1'] is True, 'Boundary review cannot replace Q1')
    safe_file(root, item['review_record'])
    validate_ready(load(root, 'data/m3_scope.json'))
    return {'status':'frozen_candidate_verified','version':VERSION,'pages':299,
            'sha256':item['sha256'],'candidate_frozen':True,'release_eligible':False,'Q1_completed':False}


if __name__ == '__main__':
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
