#!/usr/bin/env python3
"""Byte-bound, layout- and provenance-aware v0.5.0 final-edition preflight.

--preflight checks the locally rebuilt formal PDF before its Git object exists.
Default verifies the exact published PDF, immutable RC3 source, state and manifest.
--render additionally compares all 299 96dpi RGB pixels outside authorized text
edits; it is an automated regression, NOT a new claim of human visual review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import fitz
from build_v050_formal import ROOT, SOURCE, SOURCE_SHA, FORMAL_SHA, FORMAL_BYTES, PAGES, EDITS

REL = 'deliverables/releases/v0.5.0/zitie-v0.5.0-A4.pdf'
REPORT = 'data/evidence/Q1-v0.5.0-final-derivation-20261008.json'
REVIEW = 'reviews/Q1-v0.5.0-formal-QA-20261008.md'


def require(cond: bool, message: str) -> None:
    if not cond: raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_manifest_entry(entry: dict) -> None:
    require(entry['path'] == REL and entry['version'] == '0.5.0' and entry['status'] == 'released',
            'Not the exact formal edition')
    require(entry['release_eligible'] is True, 'Release is not eligible')
    require(entry['sha256'] == FORMAL_SHA and entry['bytes'] == FORMAL_BYTES and entry['pages'] == PAGES,
            'Manifest final bytes differ')
    require(entry.get('source_commit') is None and entry.get('provenance_kind') ==
            'reproducible_edition_from_reviewed_RC3', 'Formal PDF has misleading source provenance')
    require(entry['source_pdf'] == SOURCE and entry['source_pdf_sha256'] == SOURCE_SHA,
            'Formal PDF source derivative differs')
    require(entry['review_record'] == REVIEW and entry['provenance_record'] == REPORT,
            'Missing formal review trail')
    gate = entry['release_gate_snapshot']
    for k in ('scope','primary','cross','metadata','artwork','layout'):
        require(gate.get(k) == 'passed', 'Missing editorial gate: ' + k)
    require(gate.get('unresolved_conflicts') == 0 and gate.get('terminal_fail_closed_disclosed') is True,
            'Source restrictions not preserved')
    require(gate.get('physical_print_test_performed') is False, 'Unperformed print test claimed')


def stripped_drawings(page):
    return [{k:v for k,v in d.items() if k != 'seqno'} for d in page.get_drawings()]


def verify(*, root=ROOT, path=None, preflight=False, render=False, edits_path=None):
    root = Path(root)
    path = Path(path) if path else root/REL
    raw = path.read_bytes()
    require(len(raw) == FORMAL_BYTES and sha(raw) == FORMAL_SHA, 'Published PDF differs from exact reviewed derivative')
    require(sha((root/SOURCE).read_bytes()) == SOURCE_SHA, 'Immutable RC3 source changed')
    if not preflight:
        manifest = json.loads((root/'deliverables/manifest.json').read_text(encoding='utf-8'))
        records = [a for a in manifest['artifacts'] if a['path'] == REL]
        require(len(records) == 1, 'Formal edition missing/duplicated in manifest')
        check_manifest_entry(records[0])
        record = json.loads((root/REPORT).read_text(encoding='utf-8'))
        require(record['formal_sha256'] == FORMAL_SHA and record['source_sha256'] == SOURCE_SHA
                and record['pages'] == PAGES and record['edits'] == EDITS, 'Formal derivation receipt changed')
        state = json.loads((root/'data/post_release.json').read_text(encoding='utf-8'))
        release = state.get('formal_release')
        require(state['active_phase'] == 'completed' and state['final_release_eligible'] is True,
                'Formal release state incomplete')
        require(release is not None and release.get('path') == REL and release.get('sha256') == FORMAL_SHA
                and release.get('provenance_kind') == 'reproducible_edition_from_reviewed_RC3',
                'Formal release state does not match immutable PDF')
    original, final = fitz.open(root/SOURCE), fitz.open(path)
    errors=[]
    changed_pixels = 0
    try:
        require(len(original) == len(final) == PAGES, 'Wrong page count')
        require(original.get_toc() == final.get_toc() and len(final.get_toc()) == 238, 'Bookmarks changed')
        require(sum(len(p.get_links()) for p in final) == 50, 'Internal links changed')
        text = '\n'.join(p.get_text() for p in final)
        require('v0.5.0-rc3' not in text and '发布候选' not in text,
                'Old candidate strings in formal file')
        require('正式版本 v0.5.0' in text and '从RC1源码重新生成' in text,
                'Missing reader-facing provenance/version label')
        regions={i:[] for i in range(1,PAGES+1)}
        if render:
            require(edits_path is not None, 'Rendered diff requires bounded change log from builder')
            edits=json.loads(Path(edits_path).read_text(encoding='utf-8'))
            require(len(edits) == EDITS and set(e['page'] for e in edits) == set(range(1,PAGES+1)),
                    'Unexpected edited pages')
            for e in edits:regions[e['page']].append(e)
            import numpy as np
        for n,(src,dst) in enumerate(zip(original, final),1):
            if src.rect != dst.rect or src.get_links() != dst.get_links():
                errors.append((n,'page size or links changed'))
            a,b=stripped_drawings(src),stripped_drawings(dst)
            if a != b[:len(a)]: errors.append((n,'Original vector drawing modified'))
            if not render:continue
            old_pix = src.get_pixmap(matrix=fitz.Matrix(4/3,4/3),colorspace=fitz.csRGB,alpha=False)
            new_pix = dst.get_pixmap(matrix=fitz.Matrix(4/3,4/3),colorspace=fitz.csRGB,alpha=False)
            a_px=np.frombuffer(old_pix.samples,dtype=np.uint8).reshape(old_pix.height,old_pix.width,3)
            b_px=np.frombuffer(new_pix.samples,dtype=np.uint8).reshape(new_pix.height,new_pix.width,3)
            changed=np.any(a_px!=b_px,axis=2)
            changed_pixels+=int(changed.sum())
            new_spans=[s for blk in dst.get_text('dict')['blocks'] for ln in blk.get('lines',[]) for s in ln['spans']]
            for e in regions[n]:
                oldrect=fitz.Rect(e['rect'])
                hits=[s for s in new_spans if e['new'].strip() in s['text'] and
                      abs(s['bbox'][1]-oldrect.y0)<5 and abs(s['bbox'][0]-oldrect.x0)<60]
                if not hits:
                    errors.append((n,'Inserted text missing',e['new'][:20]));continue
                oldrect |= fitz.Rect(hits[0]['bbox'])
                padding=3.0
                x0=max(0,int((oldrect.x0-padding)*4/3));x1=min(old_pix.width,int((oldrect.x1+padding)*4/3)+1)
                y0=max(0,int((oldrect.y0-padding)*4/3));y1=min(old_pix.height,int((oldrect.y1+padding)*4/3)+1)
                changed[y0:y1,x0:x1] = False
            if changed.any(): errors.append((n,'Pixels changed outside intended labels',int(changed.sum())))
        require(not errors, 'Formal PDF regressed: '+repr(errors[:8]))
    finally:
        original.close();final.close()
    return {'kind':'exact_v0.5.0_formal_edition_preflight', 'pdf':REL,'pages':PAGES,
            'sha256':FORMAL_SHA, 'byte_size':FORMAL_BYTES, 'bookmarks':238,'links':50,
            'original_vectors_preserved':True,'out_of_scope_changes':0, 'rendered':render,
            'changed_pixels_within_edited_labels':changed_pixels if render else None,
            'physical_print_test_performed':False,'release_registered':not preflight}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--file',type=Path)
    p.add_argument('--preflight',action='store_true')
    p.add_argument('--render',action='store_true')
    p.add_argument('--edits',type=Path)
    args=p.parse_args()
    print(json.dumps(verify(path=args.file,preflight=args.preflight,render=args.render,edits_path=args.edits),
                     ensure_ascii=False,indent=2))
