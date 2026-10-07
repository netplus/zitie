#!/usr/bin/env python3
"""Bind an archived M1 formal patch to its generation and impact-review records.

This checks evidence consistency, not whether a human really read a page.
Historical v0.4.0 validation and final v0.5.0/Q1 authorization stay separate.
"""
import json
from pathlib import Path
from verify_patch_candidate import ROOT, require, verify as verify_pdf


def read(root, name):
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts, 'Unsafe evidence path')
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), 'Evidence outside repository')
    return json.loads(resolved.read_text(encoding='utf-8'))


def verify(root=ROOT):
    root = Path(root)
    state = read(root, 'data/post_release.json')
    manifest = read(root, 'deliverables/manifest.json')['artifacts']
    extra = [e for e in manifest if e['status'] == 'released' and e['version'] != '0.4.0']
    patch = state.get('patch_release')
    if not patch:
        require(not extra, 'Undeclared additional release')
        require(state['phases'][0]['status'] != 'completed', 'M1 lacks its formal patch')
        return {'patch_release_verified': False, 'status': 'not_archived'}
    require(patch['version'] == '0.4.1', 'Only the reviewed M1 patch is supported')
    require(patch['path'] == 'deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf',
            'Unexpected patch location')
    require(len(extra) == 1, 'Unverified additional formal release')
    entry = extra[0]
    for key in ('path', 'version', 'status', 'release_eligible', 'pages', 'bytes', 'sha256',
                'source_commit', 'workflow_run_id', 'artifact_id', 'review_record',
                'generation_record', 'evidence'):
        require(entry[key] == patch[key], 'Patch manifest/state mismatch: ' + key)
    require(entry['status'] == 'released' and entry['release_eligible'] is True, 'Not a release entry')
    require((root / entry['review_record']).is_file(), 'Missing patch review')
    metadata = read(root, entry['generation_record'])
    for key in ('version', 'pages', 'bytes', 'sha256', 'source_commit'):
        require(metadata[key] == entry[key], 'Generation/archive mismatch: ' + key)
    require(metadata['mode'] == 'formal', 'Cannot archive candidate as a formal patch')
    # Build metadata deliberately remains release_eligible=false; only the
    # independently reviewed manifest entry is allowed to grant publication.
    result = verify_pdf((root / entry['path']).parent, expected_mode='formal', metadata=metadata)
    qa = read(root, entry['evidence'])
    require(qa['sha256'] == entry['sha256'], 'QA bound to different PDF bytes')
    require(qa['source_commit'] == entry['source_commit'], 'QA/source mismatch')
    require(qa['kind'] == 'M1_formal_patch_impact_review_not_Q1', 'Wrong review scope')
    require(qa['blocking_findings'] == 0, 'Patch has unresolved blocking findings')
    needed = {1, 2, 3, 4, 5, 6, 263, 270, 271, 272, 273, 274, 276}
    require(needed <= set(qa['visual_review']['MuPDF_pages']), 'Incomplete affected-page review')
    require({3, 270, 271, 272, 273, 276} <= set(qa['visual_review']['Poppler_pages']),
            'Missing second-renderer review')
    require(qa['raster_regression']['practice_body_pages'] == list(range(6, 264)),
            'Incomplete practice-body regression')
    require(qa['raster_regression']['practice_body_different_pages'] == [], 'Practice body changed')
    require(qa['raster_regression']['unchanged_backmatter_pages'] == list(range(264, 276)),
            'Back-matter regression incomplete')
    rc = state['patch_candidate']
    require(qa['baseline_rc_sha256'] == rc['sha256'], 'Wrong RC comparison baseline')
    require(any(e['path'] == rc['path'] and e['sha256'] == rc['sha256']
                and e['status'] == 'release_candidate' for e in manifest), 'RC evidence lost')
    gate = entry['release_gate_snapshot']
    for key in ('scope', 'primary', 'cross', 'metadata', 'artwork', 'layout'):
        require(gate[key] == 'passed', 'Missing inherited/patch gate: ' + key)
    require(gate['unresolved_conflicts'] == 0, 'Unresolved blocking conflict')
    require(gate['terminal_fail_closed_disclosed'] is True, 'Boundary disclosure removed')
    require(gate['terminal_fail_closed'] == {'fine_stroke_names': 14, 'position_migration': 3,
                                            'exact_GF0011_2022_item_fields': 201},
            'M1 must not promote normative fields')
    require(gate['patch_errata_resolved'] == ['E001', 'E002', 'E003', 'E004'], 'Incomplete errata closure')
    result.update(patch_release_verified=True, status='archived_patch_verified',
                  release_eligible=True, q1_completed=False)
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
