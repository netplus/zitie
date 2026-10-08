#!/usr/bin/env python3
"""Check the exact v0.5.1 Chinese-period/ideographic-comma erratum and its provenance.

A change in embedded punctuation glyph outlines is *not* a change of text or
teaching content. Render mode validates every page against previously published
v0.5.0, allowing only those glyph cells and v0.5.0->v0.5.1 labels to differ.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import fitz
from fontTools.ttLib import TTFont
from build_v051_punctuation import ROOT, FORMAL_SHA, FORMAL_BYTES, SOURCE, SOURCE_SHA, PAGES, EDITS
from fix_uming_cjk_punctuation import fonts_to_correct

PREVIOUS = 'deliverables/releases/v0.5.0/zitie-v0.5.0-A4.pdf'
PREVIOUS_SHA = '10f5177221ff4817ea412f9e5f187e68d59eabfce8f94e2ebf4179f4398f6880'
REL = 'deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf'
RECORD = 'data/evidence/v051-punctuation-derivation-20261008.json'
REVIEW = 'reviews/v051-punctuation-erratum-20261008.md'
KIND = 'reproducible_punctuation_erratum_from_reviewed_RC3'
EXPECTED_OUTLINES = {'。': (261, 81, 511, 331), '、': (246, 83, 500, 310)}
EXPECTED_GLYPH_SUBSETS = {'。': 17, '、': 16}
EXPECTED_OCCURRENCES = {'。': 201, '、': 82}


def require(condition, message):
    if not condition: raise ValueError(message)


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def check_manifest_entry(entry):
    require(entry.get('path') == REL and entry.get('version') == '0.5.1' and entry.get('status') == 'released',
            'Wrong v0.5.1 edition path/version/status')
    require(entry.get('bytes') == FORMAL_BYTES and entry.get('sha256') == FORMAL_SHA and entry.get('pages') == PAGES,
            'Wrong published v0.5.1 PDF bytes')
    require(entry.get('provenance_kind') == KIND and entry.get('source_commit') is None,
            'Erratum must disclose PDF-level source rather than fabricate a source commit')
    require(entry.get('source_pdf') == SOURCE and entry.get('source_pdf_sha256') == SOURCE_SHA,
            'Erratum source must be byte-bound to accepted RC3')
    require(entry.get('previous_release') == PREVIOUS and entry.get('previous_sha256') == PREVIOUS_SHA,
            'Must preserve prior published v0.5.0 identity')
    require(entry.get('release_eligible') is True and entry.get('review_record') == REVIEW
            and entry.get('provenance_record') == RECORD, 'Erratum has no release/review gate')
    gate=entry.get('release_gate_snapshot',{})
    for key in ('scope','primary','cross','metadata','artwork','layout'):
        require(gate.get(key) == 'passed', 'Missing editorial gate: '+key)
    require(gate.get('unresolved_conflicts') == 0 and gate.get('terminal_fail_closed_disclosed') is True
            and gate.get('physical_print_test_performed') is False, 'Erratum misrepresents source or print gate')


def rect_drawings(page):
    return [{k:v for k,v in z.items() if k!='seqno'} for z in page.get_drawings()]


def get_char_outlines(doc):
    counts=Counter()
    for fx, fontfile, targets in fonts_to_correct(doc):
        ft=TTFont(io.BytesIO(doc.xref_stream(fontfile)))
        for char,gid,dx,dy in targets:
            glyph=ft['glyf'][ft.getGlyphOrder()[gid]]
            require((glyph.xMin,glyph.yMin,glyph.xMax,glyph.yMax)==EXPECTED_OUTLINES[char],
                    f'Period/ideographic-comma glyph wrongly positioned in font xref {fx}')
            counts[char]+=1
    require(dict(counts)==EXPECTED_GLYPH_SUBSETS,'Incomplete subset outline correction')
    return dict(counts)


def validate(root=ROOT,*,render=False):
    root=Path(root)
    prev=root/PREVIOUS;new=root/REL;source=root/SOURCE
    require(sha_bytes(prev.read_bytes()) == PREVIOUS_SHA,'Historical published v0.5.0 bytes changed')
    require(sha_bytes(source.read_bytes()) == SOURCE_SHA,'Reviewed RC3 input changed')
    require(new.is_file() and new.stat().st_size == FORMAL_BYTES and sha_bytes(new.read_bytes()) == FORMAL_SHA,
            'v0.5.1 bytes not byte-exact')
    manifest=json.loads((root/'deliverables/manifest.json').read_text(encoding='utf-8'))
    entries=[x for x in manifest['artifacts'] if x.get('path')==REL]
    require(len(entries)==1,'v0.5.1 PDF not uniquely registered')
    check_manifest_entry(entries[0])
    require((root/REVIEW).is_file() and (root/RECORD).is_file(), 'Erratum evidence is missing')
    evidence=json.loads((root/RECORD).read_text(encoding='utf-8'))
    require(evidence['result']['sha256']==FORMAL_SHA and evidence['result']['bytes']==FORMAL_BYTES
            and evidence['source_sha256']==SOURCE_SHA and evidence['previous_sha256']==PREVIOUS_SHA,
            'Erratum provenance record disagrees')
    require(evidence['occurrences_changed']==EXPECTED_OCCURRENCES and evidence['glyph_subsets_changed']==EXPECTED_GLYPH_SUBSETS,
            'Evidence altered punctuation scope')
    state=json.loads((root/'data/post_release.json').read_text(encoding='utf-8'))
    latest=state.get('current_release') or {}
    require(state['active_phase']=='completed' and state['final_release_eligible'] is True,
            'Closed Q1 release baseline regressed')
    require(latest.get('version')=='0.5.1' and latest.get('path')==REL and latest.get('sha256')==FORMAL_SHA,
            'Current release state not updated')
    olddoc=fitz.open(prev);newdoc=fitz.open(new)
    counts=Counter();labels=0;changes=0;unexpected=0;changed_pages=0;errors=[]
    try:
        require(len(olddoc)==len(newdoc)==PAGES,'Unexpected page count')
        require(olddoc.get_toc()==newdoc.get_toc() and len(newdoc.get_toc())==238,'Bookmarks changed')
        require(sum(len(p.get_links()) for p in olddoc)==sum(len(p.get_links()) for p in newdoc)==50,
                'Internal link count changed')
        for n,(oldpage,newpage) in enumerate(zip(olddoc,newdoc),1):
            oldtext,newtext=oldpage.get_text(),newpage.get_text()
            require(oldtext.replace('v0.5.0','v0.5.1')==newtext,
                    f'Unexpected teaching/text edits on page {n}')
            labels+=oldtext.count('v0.5.0')
            require(oldpage.rect==newpage.rect and newpage.get_links()==oldpage.get_links()
                    and rect_drawings(oldpage)==rect_drawings(newpage),f'Page structure/navigation changed on {n}')
            if not render:continue
            import numpy as np
            fac=4/3
            a=oldpage.get_pixmap(matrix=fitz.Matrix(fac,fac),colorspace=fitz.csRGB,alpha=False)
            b=newpage.get_pixmap(matrix=fitz.Matrix(fac,fac),colorspace=fitz.csRGB,alpha=False)
            require((a.width,a.height)==(b.width,b.height),'Rendered bounds changed')
            imga=np.frombuffer(a.samples,dtype=np.uint8).reshape(a.height,a.width,3)
            imgb=np.frombuffer(b.samples,dtype=np.uint8).reshape(a.height,a.width,3)
            diff=np.any(imga!=imgb,axis=2)
            mask=np.zeros(diff.shape,dtype=bool)
            for block in oldpage.get_text('rawdict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        txt=''.join(c['c'] for c in span['chars'])
                        regions=[span['bbox']] if 'v0.5.0' in txt else []
                        if span['font']=='UMingCN-0':
                            for c in span['chars']:
                                if c['c'] in EXPECTED_OCCURRENCES:
                                    counts[c['c']]+=1;regions.append(c['bbox'])
                        for r in regions:
                            rect=fitz.Rect(r);pad=2
                            x0=max(0,int((rect.x0-pad)*fac));x1=min(a.width,int((rect.x1+pad)*fac)+1)
                            y0=max(0,int((rect.y0-pad)*fac));y1=min(a.height,int((rect.y1+pad)*fac)+1)
                            mask[y0:y1,x0:x1]=True
            pix=int(diff.sum());bad=int((diff&~mask).sum())
            changes+=pix;unexpected+=bad
            if pix:changed_pages+=1
            if bad:errors.append((n,bad))
        require(labels==558,'Changed version label count differs')
        if render:
            require(dict(counts)==EXPECTED_OCCURRENCES, 'Changed punctuation occurrence count differs')
            require(not errors and unexpected==0,'Unexpected pixel changes beyond allowed punctuation/version positions')
        return {'kind':'v0.5.1_punctuation_edition_validation','version':'0.5.1',
            'sha256':FORMAL_SHA,'bytes':FORMAL_BYTES,'pages':PAGES,
            'bookmarks':238,'links':50,'version_labels':labels,
            'punctuation':EXPECTED_OCCURRENCES,'subsets':get_char_outlines(newdoc),
            'render':render,'changed_pixels':changes if render else None,
            'pages_with_pixel_changes':changed_pages if render else None,
            'unexpected_pixels':unexpected if render else None,
            'preserved_v050':True,'physical_print_test_performed':False}
    finally:
        olddoc.close();newdoc.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');args=parser.parse_args()
    print(json.dumps(validate(render=args.render),ensure_ascii=False,indent=2))
