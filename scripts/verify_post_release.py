#!/usr/bin/env python3
"""Check post-release sequencing/integrity; never grant editorial approval."""
import argparse
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ORDER = ['M1', 'M2', 'M3', 'Q1']
DONE = {'completed', 'completed_with_source_blocks'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_state(root=ROOT):
    return json.loads((root / 'data/post_release.json').read_text(encoding='utf-8'))


def validate_state(state):
    require(state.get('schema_version') == 1, 'Unsupported post-release schema')
    phases = state['phases']
    require([p['id'] for p in phases] == ORDER, 'Required order: M1 -> M2 -> M3 -> Q1')
    require(len({e['id'] for e in state['errata']}) == len(state['errata']), 'Duplicate erratum ID')
    previous_done = True
    active = []
    for phase in phases:
        status = phase['status']
        require(status in {'planned', 'in_progress'} | DONE, 'Unknown phase status')
        require(status != 'completed_with_source_blocks' or phase['id'] == 'M2',
                'Only M2 can exit with documented source blocks')
        require(status == 'planned' or previous_done, 'Previous phase has not exited')
        if status == 'in_progress':
            active.append(phase['id'])
        if status in DONE:
            require(phase.get('exit_evidence'), 'Completed phase needs exit evidence')
            require(not any(e['phase'] == phase['id'] and e['blocks_phase_exit']
                            and e['status'] != 'resolved' for e in state['errata']),
                    'Blocking erratum remains open')
        previous_done = previous_done and status in DONE
    require(len(active) <= 1, 'Only one phase may be active')
    unfinished = [p['id'] for p in phases if p['status'] not in DONE]
    expected = unfinished[0] if unfinished else 'completed'
    require(state['active_phase'] == expected, 'Active phase disagrees with sequence')
    if active:
        require(active == [expected], 'Wrong phase is in progress')
    if phases[0]['status'] in DONE:
        require(isinstance(state.get('patch_release'), dict), 'M1 requires an archived formal patch')
    if phases[2]['status'] in DONE:
        require(isinstance(state.get('candidate'), dict), 'M3 needs a frozen candidate')
    if phases[3]['status'] in DONE:
        require(isinstance(state.get('q1_review'), dict), 'Q1 needs a final-byte review record')
    require(type(state['final_release_eligible']) is bool, 'Release flag must be boolean')
    require(state['final_release_eligible'] is False or not unfinished,
            'Final release cannot precede Q1')
    return {'active_phase': expected,
            'open_errata': [e['id'] for e in state['errata'] if e['status'] != 'resolved'],
            'final_release_eligible': state['final_release_eligible']}


def safe_file(root, relative):
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts, 'Unsafe project path')
    resolved = (root / p).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), 'Missing project file')
    return resolved


def verify(root=ROOT):
    state = load_state(root)
    result = validate_state(state)
    baseline = state['baseline']
    raw = safe_file(root, baseline['path']).read_bytes()
    require(len(raw) == baseline['bytes'], 'Baseline size changed')
    require(hashlib.sha256(raw).hexdigest() == baseline['sha256'], 'Baseline bytes changed')
    require(len(PdfReader(root / baseline['path']).pages) == baseline['pages'], 'Baseline pages changed')
    manifest = json.loads((root / 'deliverables/manifest.json').read_text(encoding='utf-8'))
    entries = [x for x in manifest['artifacts'] if x['path'] == baseline['path']]
    require(len(entries) == 1, 'Baseline manifest entry missing or duplicated')
    require(all(entries[0][k] == baseline[k] for k in ('version', 'pages', 'bytes', 'sha256')),
            'Baseline manifest metadata changed')
    require(entries[0]['status'] == 'released', 'Historical release status changed')
    for phase in state['phases']:
        for evidence in phase.get('exit_evidence', []):
            safe_file(root, evidence)
    from verify_patch_archive import verify as verify_patch_archive
    verify_patch_archive(root)
    if state['phases'][1]['status'] in DONE:
        from verify_m2_closeout import verify as verify_m2_closeout
        verify_m2_closeout(root)
    from verify_m3_archive import verify as verify_m3_archive
    verify_m3_archive(root)
    if state.get('q1_local_review_record'):
        # Historical PDF derivative record remains immutable, even after Q1 acceptance.
        from verify_q1_import import verify as verify_q1_import
        verify_q1_import(root)
        local_review = json.loads(safe_file(root, state['q1_local_review_record']).read_text(encoding='utf-8'))
        require(local_review['Q1_completed'] is False and local_review['release_eligible'] is False,
                'Historical local import snapshot has changed')
        require(local_review['reviewed_pdf'] ==
                'deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3-finalcheck.pdf'
                and local_review['sha256'] == 'd54184705c6849d6617c7ea201a659d77796cad9b05792782032b320127bbb27',
                'Local Q1 state must refer to imported RC3 finalcheck bytes')
        require(local_review['checked_pages'] == list(range(1,300))
                and local_review['pending_visual_pages'] == []
                and local_review['inherited_from_actual_previous_review'] is True,
                'Local Q1 evidence coverage was altered')
        if state['phases'][3]['status'] in DONE:
            # Q1 acceptance uses a newer PDF than the immutable RC1 M3 freeze.
            from verify_q1_acceptance import verify as verify_q1_acceptance
            verify_q1_acceptance(root)
            require(state['final_release_eligible'] is False,
                    'Accepted layout is not a final-edition publication')
        else:
            require(state['final_release_eligible'] is False,
                    'Q1 derivative acceptance/CI incomplete')
    candidate = state.get('candidate')
    if candidate:
        require(re.fullmatch(r'[0-9a-f]{40}', candidate['source_commit']), 'Exact candidate source required')
        raw = safe_file(root, candidate['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == candidate['sha256'], 'Candidate bytes changed')
        require(len(PdfReader(root / candidate['path']).pages) == candidate['pages'], 'Candidate pages changed')
    if state['phases'][3]['status'] in DONE:
        review = state['q1_review']
        # RC1 is M3's frozen source checkpoint, not the later visually reviewed RC3.
        require(review['path'] == 'deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3-finalcheck.pdf'
                and review['sha256'] == 'd54184705c6849d6617c7ea201a659d77796cad9b05792782032b320127bbb27',
                'Q1 acceptance must bind the newer reviewed candidate, never historical RC1')
        require(review['record'] == 'data/evidence/Q1-RC3-acceptance-20261008.json'
                and review['provenance_kind'] == 'locally_reviewed_pdf_derivative',
                'Missing Q1 acceptance provenance')
        require(review['checked_pages'] == list(range(1, 300))
                and review['blocking_findings'] == 0
                and review['second_renderer_pages'] == 41
                and review['grayscale_pages'] == 4
                and review['physical_print_test_performed'] is False,
                'Q1 acceptance review incomplete or physical print falsely claimed')
        safe_file(root, review['record'])
    result.update(baseline_sha256=baseline['sha256'],
                  kind='workflow_consistency_not_editorial_approval',
                  visual_review_performed=False)
    return result


class StateTests(unittest.TestCase):
    def setUp(self):
        # Synthetic fixture remains stable when the live project advances.
        self.state = {
            'schema_version': 1, 'active_phase': 'M1',
            'phases': [{'id': p, 'status': 'in_progress' if p == 'M1' else 'planned',
                        'exit_evidence': []} for p in ORDER],
            'errata': [{'id': 'fixture', 'phase': 'M1', 'status': 'open',
                        'blocks_phase_exit': True}],
            'candidate': None, 'final_release_eligible': False,
        }

    def reject(self, change):
        state = copy.deepcopy(self.state)
        change(state)
        with self.assertRaises(ValueError):
            validate_state(state)

    def test_current_state(self):
        self.assertEqual(validate_state(self.state)['active_phase'], 'M1')

    def test_wrong_order(self):
        self.reject(lambda s: s['phases'].reverse())

    def test_unknown_status(self):
        self.reject(lambda s: s['phases'][0].update(status='reviewed'))

    def test_parallel_progress(self):
        self.reject(lambda s: s['phases'][1].update(status='in_progress'))

    def test_no_early_advance(self):
        self.reject(lambda s: s.update(active_phase='M2'))

    def test_no_evidence_free_completion(self):
        self.reject(lambda s: s['phases'][0].update(status='completed'))

    def test_no_open_erratum_completion(self):
        self.reject(lambda s: s['phases'][0].update(status='completed', exit_evidence=['review.md']))

    def test_no_release_before_q1(self):
        self.reject(lambda s: s.update(final_release_eligible=True))

    def test_no_source_block_exit_for_layout(self):
        self.reject(lambda s: s['phases'][3].update(status='completed_with_source_blocks'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StateTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
