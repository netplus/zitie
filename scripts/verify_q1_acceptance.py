#!/usr/bin/env python3
"""Validate Q1 layout acceptance for the exact RC3 derivative, not a formal release.

Original RC1 generation evidence and local-import snapshot remain immutable.
This validator cannot grant normative approval or mark a candidate as released.
"""
from __future__ import annotations
import copy
import hashlib
import json
import unittest
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RECORD = 'data/evidence/Q1-RC3-acceptance-20261008.json'
PDF = 'deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3-finalcheck.pdf'
SHA = 'd54184705c6849d6617c7ea201a659d77796cad9b05792782032b320127bbb27'
SOURCE_REVIEW = 'reviews/q1-local-20261008/Q1-page-review-rc3.json'
INTEGRITY = 'reviews/q1-local-20261008/Q1-final-integrity.json'
ORIGINAL_Q1 = 'data/q1_review.json'
ORIGINAL_LOCAL = 'data/q1_local_review.json'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def load(root, path):
    root = Path(root).resolve()
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root) and resolved.is_file() and not (root/path).is_symlink(),
            'Unsafe or missing review file: ' + path)
    return json.loads(resolved.read_text(encoding='utf-8'))


def check_summary(approval, local, visual, integrity):
    require(approval.get('kind') == 'Q1_RC3_layout_acceptance_not_formal_publication',
            'Wrong acceptance kind')
    require(approval.get('reviewed_pdf') == PDF and approval.get('sha256') == SHA
            and approval.get('pages') == 299, 'Acceptance not bound to RC3 finalcheck')
    require(approval.get('review_file') == SOURCE_REVIEW and approval.get('integrity_file') == INTEGRITY,
            'Wrong evidence paths')
    require(approval.get('source_provenance') == 'locally_reviewed_pdf_derivative_not_rebuilt_from_source',
            'False source-build provenance')
    require(approval.get('checked_pages') == list(range(1, 300))
            and approval.get('second_renderer_pages') == visual['second_renderer_pages']
            and approval.get('grayscale_pages') == visual['grayscale_pages'],
            'Review coverage does not match actual visual evidence')
    require(approval.get('blocking_findings') == 0 and approval.get('source_fields_promoted') == 0,
            'Blocking layout or unauthorized normative changes')
    require(approval.get('physical_print_test_performed') is False
            and approval.get('color_print_recommended') is True,
            'Physical printing or grayscale limitation concealed')
    require(approval.get('Q1_layout_accepted') is True
            and approval.get('final_release_eligible') is False
            and approval.get('formal_release_completed') is False
            and approval.get('formal_pdf_generated') is False,
            'Layout acceptance was misrepresented as a formal release')
    require(approval.get('historical_RC1_Q1_queue_unchanged') is True
            and approval.get('original_local_review_record_remains_historical') is True,
            'Historical record was silently reassigned')
    require(local['reviewed_pdf'] == PDF and local['sha256'] == SHA and local['pages'] == 299
            and local['Q1_completed'] is False and local['release_eligible'] is False
            and local['local_visual_review_complete'] is True
            and local['checked_pages'] == list(range(1, 300))
            and local['blocking_layout_findings_remaining'] == 0,
            'Original local review snapshot has changed')
    require(len(visual['page_results']) == 299
            and [x['page'] for x in visual['page_results']] == list(range(1, 300)),
            'Original visual record has missing or duplicate pages')
    require(all(x['source_full_page_visually_read'] is True
                and x['unmodified_regions_pixel_match'] is True
                and x['nontext_vector_geometry_and_colors_unchanged'] is True
                and x['remaining_layout_findings'] == []
                for x in visual['page_results']),
            'Original page-by-page visual review incomplete')
    changed = set(visual['changed_nonversion_pages'])
    require(len(changed) == 83
            and all(visual['page_results'][p-1]['rc3_modified_content_visually_rechecked'] is True
                    for p in changed), 'Modified RC3 content lacks a visual recheck')
    require(sum(x['rc3_full_page_poppler_crosschecked'] is True for x in visual['page_results']) == 41,
            'Second renderer checks incomplete')
    require(sum(x['grayscale_simulation_visually_read'] is True for x in visual['page_results']) == 4,
            'Grayscale simulation checks incomplete')
    require(visual['result']['blocking_layout_findings_remaining'] == 0,
            'Outstanding layout blocker in historical review')
    checks=integrity['machine_checks']
    require(checks['pages'] == checks['pages_passed'] == 299
            and checks['glyph_zero_findings'] == 0
            and checks['text_outside_page_findings'] == 0
            and checks['links'] == 50 and checks['bookmarks'] == 238
            and checks['base_RGB96_review_hash_matches'] == 299
            and checks['nontext_drawing_equal_RC2_pages'] == 299,
            'Final file integrity verification incomplete')
    require(len(integrity['page_results']) == 299
            and all(x['passed'] for x in integrity['page_results']),
            'Final PDF has a machine-checked page failure')
    for v,m in zip(visual['page_results'],integrity['page_results']):
        require(v['page'] == m['page'] and v['rc3_rgb96_sha256'] == m['rgb96_sha256'],
                'Finalcheck differs visually from reviewed RC3')
    require(integrity['physical_print_test_performed'] is False
            and integrity['normative_fields_promoted_this_round'] == 0,
            'Historical print or source-policy boundary changed')


def verify(root=ROOT):
    root=Path(root)
    approval=load(root,RECORD)
    local=load(root,ORIGINAL_LOCAL)
    visual=load(root,SOURCE_REVIEW)
    integrity=load(root,INTEGRITY)
    check_summary(approval,local,visual,integrity)
    raw=(root/PDF).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SHA and len(PdfReader(root/PDF).pages) == 299,
            'Accepted PDF bytes or page count differ')
    manifest=load(root,'deliverables/manifest.json')
    match=[x for x in manifest['artifacts'] if x['path'] == PDF]
    require(len(match) == 1 and match[0]['sha256'] == SHA
            and match[0]['status'] == 'release_candidate' and match[0]['release_eligible'] is False
            and match[0]['provenance_kind'] == 'locally_reviewed_pdf_derivative',
            'Accepted PDF not archived as a distinct candidate')
    prior=load(root,ORIGINAL_Q1)
    require(prior['sha256'] == '3b26fd0a85b063b83f7090f9b38735908b6e64dc763614c12f17e4f727ef556a'
            and prior['Q1_completed'] is False and prior['checked_pages'] == [],
            'Historical RC1 review queue has changed')
    return {'kind':'verified_Q1_RC3_layout_acceptance_not_formal_release',
            'pages':299,'second_renderer_pages':41,'grayscale_simulation_pages':4,
            'blocking_layout_findings':0,'finalcheck_sha256':SHA,
            'formal_publication_is_outside_this_Q1_gate':True}


class AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.approval=load(ROOT,RECORD)
        cls.local=load(ROOT,ORIGINAL_LOCAL)
        cls.visual=load(ROOT,SOURCE_REVIEW)
        cls.integrity=load(ROOT,INTEGRITY)

    def test_acceptance(self):
        check_summary(self.approval,self.local,self.visual,self.integrity)

    def reject(self, change, name):
        a=copy.deepcopy(self.approval); l=copy.deepcopy(self.local)
        v=copy.deepcopy(self.visual); i=copy.deepcopy(self.integrity)
        change(a,l,v,i)
        with self.assertRaises(ValueError,msg=name):
            check_summary(a,l,v,i)

    def test_wrong_final_pdf(self):
        self.reject(lambda a,l,v,i:a.update(sha256='0'*64),'hash mismatch')

    def test_incomplete_pages(self):
        self.reject(lambda a,l,v,i:a['checked_pages'].pop(),'page incomplete')

    def test_silent_source_rewrite(self):
        self.reject(lambda a,l,v,i:a.update(source_provenance='clean_git_build'),'source provenance')

    def test_missing_second_renderer(self):
        self.reject(lambda a,l,v,i:v['page_results'][0].update(rc3_full_page_poppler_crosschecked=False),
                    'cross-render incomplete')

    def test_changed_page_not_rechecked(self):
        self.reject(lambda a,l,v,i:v['page_results'][118].update(rc3_modified_content_visually_rechecked=False),
                    'changed page')

    def test_missing_grayscale(self):
        self.reject(lambda a,l,v,i:v['page_results'][33].update(grayscale_simulation_visually_read=False),
                    'grayscale incomplete')

    def test_glyph_findings(self):
        self.reject(lambda a,l,v,i:i['machine_checks'].update(glyph_zero_findings=1),
                    'glyph mismatch')

    def test_wrong_render_hash(self):
        self.reject(lambda a,l,v,i:i['page_results'][198].update(rgb96_sha256='0'*64),
                    'pixel hash mismatch')

    def test_hidden_print_claim(self):
        self.reject(lambda a,l,v,i:a.update(physical_print_test_performed=True),
                    'fake print test')

    def test_premature_release(self):
        self.reject(lambda a,l,v,i:a.update(final_release_eligible=True),
                    'formal release not ready')

    def test_unresolved_layout(self):
        self.reject(lambda a,l,v,i:v['page_results'][75]['remaining_layout_findings'].append('overlap'),
                    'unresolved layout')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    args=p.parse_args()
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AcceptanceTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
