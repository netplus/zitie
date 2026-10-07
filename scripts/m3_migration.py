#!/usr/bin/env python3
"""Six whole-character contexts: positive mapping evidence plus reviewed outlines.

All indices are one-based. Upstream radStrokes is deliberately NOT used: it
classifies the whole word's dictionary radical, not the component being taught.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
from build_batch import prepare
from m3_model import ROOT, authorize, digest
from verify_m2_closeout import load, require

RECORD = 'data/artwork/m3-migration.json'
CACHE = 'build/m3-whole-vectors'


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def validate_case(case, batch, entry, record, policy, root=ROOT):
    """Never infer the mapping from a font or from the absence of a block."""
    authorize(root, policy, batch, entry, ['position_migration'])
    review = entry['position_migration_review']; whole = review['whole_character']
    code = whole.get('whole_order_code', whole.get('stored_whole_order_code'))
    require(whole.get('stored_whole_order_code_complete', True) is True, 'Truncated whole-character code')
    require(isinstance(code, str) and code and set(code) <= set('12345'), 'Invalid full order code')
    indices = case['indices']
    require(indices and all(type(i) is int and 1 <= i <= len(code) for i in indices), 'Invalid component index')
    require(indices == sorted(set(indices)), 'Duplicate or reordered component index')
    require(case['main_id'] == entry['main_id'] == record['main_id'], 'Main identity mismatch')
    require(case['character'] == entry['character'] == record['component'], 'Component identity mismatch')
    require(case['whole_character'] == whole['character'] == record['whole_character'], 'Whole identity mismatch')
    require(indices == review['component_stroke_indices_in_whole_character'] == record['indices'], 'Mapping drift')
    require(case['full_whole_character_sequence_required'] is review['full_whole_character_sequence_required'],
            'Timing requirement changed')
    require(record['whole_order_code'] == code and record['stroke_count'] == len(code), 'Incomplete/changed sequence')
    require(record['mapping_kind'] == review['mapping_kind'], 'Mapping kind changed')
    require(record['mapping_review_sha256'] == canonical_hash(review), 'Mapping evidence changed')
    require(record['evidence'] == case['evidence'] == review['evidence'], 'Wrong mapping evidence')
    require(digest(Path(root) / record['evidence']) == record['evidence_sha256'], 'Evidence bytes changed')
    source = record['source_row']
    require(source['pdf_page'] == whole['pdf_page'] and source['printed_page'] == whole['printed_page']
            and source['table_no'] == whole['table_no'] and source['ucs'] == whole['ucs'], 'Wrong source row')
    require(record['render_full_sequence'] is True, 'Component-only sequence is forbidden')
    require(record['fine_stroke_names_claimed'] is False and record['formal_attached_form_claimed'] is False,
            'Out-of-scope field promotion')
    require(record['vector_review']['result'] == 'passed_original_row_shape_and_order_comparison',
            'Outline visual review not complete')
    return code


def verify_outline(raw, record):
    require(hashlib.sha256(raw).hexdigest() == record['vector_sha256'], 'Outline bytes changed')
    sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(sha == record['upstream_blob_sha'], 'Outline Git object mismatch')
    obj = json.loads(raw)
    require(len(obj.get('strokes', [])) == len(obj.get('medians', [])) == record['stroke_count'],
            'Full-character outline count mismatch')
    # Uses the full glyph bounds for every step, never recentered component-only bounds.
    return prepare(obj, record['stroke_count'])


def sequence_pages(record):
    n = record['stroke_count']; members = set(record['indices']); pages = []
    for start in range(1, n + 1, 6):
        pages.append([{'step': i, 'visible_indices': list(range(1, i + 1)),
                       'new_stroke': i, 'is_target_component': i in members}
                      for i in range(start, min(n, start + 5) + 1)])
    return pages


def read_migrations(model, root=ROOT):
    config, scope, policy, batches, by_id = model
    manifest = load(root, RECORD)
    require(manifest['schema_version'] == 1 and manifest['normative_source']['source_id'] == 'S02', 'Wrong artwork manifest')
    require(len(manifest['cases']) == len(scope['migration_cases']) == 6, 'Missing migration case')
    cases = []
    for case, record in zip(scope['migration_cases'], manifest['cases']):
        batch, entry = by_id[case['main_id']]
        validate_case(case, batch, entry, record, policy, root)
        raw = (Path(root)/CACHE/f'{ord(case["whole_character"]):04X}.json').read_bytes()
        art = verify_outline(raw, record)
        cases.append((copy.deepcopy(record), art, sequence_pages(record)))
    return cases
