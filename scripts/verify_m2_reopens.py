#!/usr/bin/env python3
"""Check M2 evidence consistency, not original-page or editorial approval."""
import argparse
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECORD = 'data/evidence/M2-wa-ping-position-20261007.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_record(record):
    r = record
    require(r['schema_version'] == 1 and r['phase'] == 'M2', 'Wrong evidence phase')
    require(r['target'] == {'batch': 'B05', 'main_id': 72, 'character': '瓦',
                            'field': 'position_migration'}, 'Wrong target')
    source = r['source']
    require(source['source_id'] == 'S02' and source['publication_id'] == 'GF0023—2020', 'Wrong publication')
    require(source['pdf_sha256'] == '0ff0890afc34c5e486edeebafb05350dec69a7bf0d1d75044d7d3f7b722ec3d0', 'Unreviewed source bytes')
    target, whole, a = r['independent_target'], r['whole_character'], r['adjudication']
    require((target['pdf_page'], target['printed_page'], target['table_no'], target['ucs'])
            == (13, 7, '0108', '074E6'), 'Wrong independent locator')
    require((whole['pdf_page'], whole['printed_page'], whole['table_no'], whole['ucs'])
            == (228, 222, '2051', '074F6'), 'Wrong whole-character locator')
    code = whole['stored_whole_order_code']
    require(whole['stored_whole_order_code_complete'] is True, 'Truncated whole-character record')
    require(len(code) == whole['stroke_count'] == 10 and set(code) <= set('12345'), 'Invalid whole code/count')
    require(code == ''.join(a['source_lines']) == a['complete_order_code'] == '4311321554', 'Two source lines not preserved')
    indices = a['component_stroke_indices']
    require(all(type(i) is int for i in indices) and indices == [7, 8, 9, 10], 'Invalid component indices')
    require(''.join(code[i-1] for i in indices) == target['order_code'] == a['component_order_code'] == '1554', 'Projected component differs')
    require(len(indices) == target['stroke_count'] == 4, 'Component count mismatch')
    require(a['visual_pages'] == [13, 228] and a['target_rows_viewed_enlarged'] is True, 'Missing visual-review record')
    require(a['formal_GF0011_2022_identity_promoted'] is False and a['fine_stroke_names_changed'] is False, 'Out-of-scope promotion')
    old, new = r['old_review'], r['new_review']
    require(old['whole_character']['stored_whole_order_code'] == '4311321'
            and old['whole_character']['stored_whole_order_code_complete'] is False, 'Old blocked record lost')
    require(new['whole_character'] == whole and new['component_stroke_indices_in_whole_character'] == indices, 'Review/mapping mismatch')
    require(new['phase'] == 'M2' and new['result'] == r['application']['new_field_status'], 'Status/evidence mismatch')
    require(new['mapping_kind'] == a['mapping_kind'] == 'contiguous'
            and new['verified_position'] == a['position'] == 'right', 'Wrong mapping kind/position')
    require(new['stroke_changes'] == a['stroke_changes'] == [], 'Unsupported stroke change')
    return True


def verify(root=ROOT):
    r = json.loads((root / RECORD).read_text(encoding='utf-8'))
    validate_record(r)
    data = json.loads((root / 'data/B05.json').read_text(encoding='utf-8'))
    entry = next(e for e in data['entries'] if e['main_id'] == 72)
    history = entry.get('position_migration_review_history', [])
    require(r['old_review'] in history, 'Prior P4 review not retained')
    # Later legitimate reopens may supersede this review, but must retain it.
    current = entry['position_migration_review']
    require(current == r['new_review'] or r['new_review'] in history, 'Adopted M2 review missing')
    require(entry['field_status']['position_migration'] == current['result'], 'Live status/review mismatch')
    require(entry['whole_character_context']['formal_variant_promoted'] is False, 'Unapproved formal variant')
    entries = [e for p in sorted((root / 'data').glob('B[0-9][0-9].json'))
               for e in json.loads(p.read_text(encoding='utf-8'))['entries']]
    require(len(entries) == 201 and len({e['main_id'] for e in entries}) == 201, 'Main coverage changed')
    # B01-B03 keep status in the review object, not a field_status map.
    statuses = [(e['character'], e.get('field_status', {}).get(
        'position_migration', e.get('position_migration_review', {}).get('result', ''))) for e in entries]
    unresolved = [ch for ch, s in statuses if 'fail_closed' in s]
    reviewed = sum(s.startswith('reviewed') for _, s in statuses)
    require(reviewed + len(unresolved) == 201, 'Unclassified live migration status')
    coverage = json.loads((root / 'data/coverage.json').read_text(encoding='utf-8'))
    frozen = coverage['phase1_content_progress']['p4_identity_position_migration']['position_migration_cumulative']
    require((frozen['reviewed'], frozen['conflict_fail_closed']) == (198, 3), 'Historical P4 snapshot changed')
    manifest = json.loads((root / 'deliverables/manifest.json').read_text(encoding='utf-8'))
    for artifact in manifest['artifacts']:
        if artifact['status'] == 'released' and artifact['version'] in ('0.4.0', '0.4.1'):
            require(artifact['release_gate_snapshot']['terminal_fail_closed']['position_migration'] == 3,
                    'Historical release snapshot changed')
    return {'kind': 'M2_evidence_consistency_not_visual_approval', 'adopted_mapping': '瓦→瓶[7,8,9,10]',
            'current_working_position_migration': {'reviewed': reviewed, 'fail_closed': unresolved},
            'historical_release_snapshot_unchanged': True, 'visual_review_performed_by_checker': False}


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.r = json.loads((ROOT / RECORD).read_text(encoding='utf-8'))

    def reject(self, change):
        r = copy.deepcopy(self.r)
        change(r)
        with self.assertRaises(ValueError):
            validate_record(r)

    def test_valid_record(self): self.assertTrue(validate_record(self.r))
    def test_live_adoption(self): self.assertIn('current_working_position_migration', verify())
    def test_truncated_code(self): self.reject(lambda r: r['whole_character'].update(stored_whole_order_code='4311321'))
    def test_incomplete_flag(self): self.reject(lambda r: r['whole_character'].update(stored_whole_order_code_complete=False))
    def test_wrong_page(self): self.reject(lambda r: r['whole_character'].update(pdf_page=227))
    def test_wrong_target(self): self.reject(lambda r: r['target'].update(character='每'))
    def test_unreviewed_source(self): self.reject(lambda r: r['source'].update(pdf_sha256='0'*64))
    def test_wrong_indices(self): self.reject(lambda r: r['adjudication'].update(component_stroke_indices=[6,7,8,9]))
    def test_duplicate_index(self): self.reject(lambda r: r['adjudication'].update(component_stroke_indices=[7,8,8,10]))
    def test_reversed_indices(self): self.reject(lambda r: r['adjudication'].update(component_stroke_indices=[10,9,8,7]))
    def test_no_source_lines(self): self.reject(lambda r: r['adjudication'].update(source_lines=['4311321']))
    def test_wrong_component(self): self.reject(lambda r: r['independent_target'].update(order_code='1525'))
    def test_no_visual_record(self): self.reject(lambda r: r['adjudication'].update(visual_pages=[]))
    def test_no_formal_promotion(self): self.reject(lambda r: r['adjudication'].update(formal_GF0011_2022_identity_promoted=True))
    def test_no_fine_name_promotion(self): self.reject(lambda r: r['adjudication'].update(fine_stroke_names_changed=True))
    def test_prior_record_retained(self): self.reject(lambda r: r['old_review']['whole_character'].update(stored_whole_order_code='4311321554'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EvidenceTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
