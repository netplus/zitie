#!/usr/bin/env python3
"""Check bounded M2 exit and field-specific teaching restrictions, not source truth.

The immutable audit is a dated snapshot, not a claim that sources are exhausted.
Live field changes require a separately reviewed update to the policy/evidence.
Ordinary M3 prose/layout changes are not rejected by whole-file snapshot hashes;
--snapshot is reserved for checking the no-canonical-edit closeout commit itself.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECORD = 'data/evidence/M2-closeout-20261007.json'
POLICY = 'data/teaching-source-policy.json'
SCOPE = 'data/m3_scope.json'
FIELDS = ['exact_2022_item_fields', 'fine_stroke_names', 'position_migration',
          'pronunciation', 'component_name', 'structure']
COUNTS = [201, 14, 2, 9, 28, 37]
RESTRICTIONS = [
    ['no_formal_2022_main_form_attached_form_name_code_claim'],
    ['use_ordinal_step_labels_only', 'no_fine_stroke_name_quiz_or_answer'],
    ['no_verified_migration_demonstration_for_this_target'],
    ['no_forced_pinyin', 'no_pronunciation_quiz_or_answer'],
    ['no_exact_official_component_name_claim'],
    ['no_structure_classification_quiz_or_answer'],
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_file(root, relative):
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts, 'Unsafe project path')
    out = (root / p).resolve()
    require(out.is_relative_to(root.resolve()) and out.is_file(), 'Missing project file')
    return out


def load(root, path):
    return json.loads(safe_file(root, path).read_text(encoding='utf-8'))


def members(group):
    return sorted((mid, ch, part['status'])
                  for part in group['status_groups'] for mid, ch in part['members'])


def validate_record(record, audit, policy):
    require(record['schema_version'] == audit['schema_version'] == policy['schema_version'] == 1,
            'Unsupported schema')
    require(record['scope_fields'] == FIELDS and [g['field'] for g in record['groups']] == FIELDS,
            'M2 must cover all six fields in order')
    require(record['decision'] == 'completed_with_source_blocks', 'Wrong bounded-exit status')
    require(record['scope_audit_complete'] is True, 'Scope audit incomplete')
    for key in ('all_fields_resolved', 'all_sources_exhausted', 'canonical_fields_modified_this_round',
                'historical_artifacts_modified', 'future_Q1_passed'):
        require(record[key] is False, 'Out-of-scope completion claim: ' + key)
    require(record['source_issue_must_remain_open'] == 4, 'Source follow-up must remain open')
    require(record['new_adopted_field_updates_this_round'] == audit['new_normative_promotions_this_round'] == 0,
            'This closeout did not adopt new normative values')
    adopted = [(a['main_id'], a['character'], a['field']) for a in record['adopted_in_cycle']]
    require(adopted == [(72, '瓦', 'position_migration'), (149, '麦', 'pronunciation'),
                        (172, '齿', 'pronunciation')]
            and record['cumulative_adopted_field_updates'] == len(adopted), 'Wrong inherited adoption count')
    require(audit['not_an_exhaustive_search'] is True and audit['source_PDFs_or_fonts_committed'] is False,
            'Incorrect audit/export boundary')
    ids = [s['id'] for s in audit['sources']]
    require(len(ids) == len(set(ids)), 'Duplicate audit source')
    source = {s['id']: s for s in audit['sources']}
    require(source['A2022']['fulltext_acquired'] is False
            and source['A2022']['claim_never_published'] is False, 'Access failure is not an absence proof')
    require(source['ATW']['admissibility'] == 'cross_system_reference_not_direct_mainland_adoption',
            'Cross-system reference cannot silently become adopted evidence')
    require(len(source['ATW']['observed_entries']) == 9, 'Incomplete cross-system observation record')
    require(policy['basis'] == RECORD and policy['do_not_sum_group_counts'] is True,
            'Incorrect policy provenance/counting')
    require(policy['unaffected_verified_fields_remain_usable'] is True
            and policy['not_a_publication_approval'] is True, 'Policy must be field-specific, not release approval')
    require([x['field'] for x in policy['rules']] == FIELDS, 'Incomplete teaching policy')
    for i, (g, rule) in enumerate(zip(record['groups'], policy['rules'])):
        ms = members(g)
        require(g['remaining_count'] == len(ms) == COUNTS[i], 'Wrong remaining count: ' + g['field'])
        mids = [mid for mid, _, _ in ms]
        require(len(set(mids)) == len(mids) and all(type(mid) is int and 1 <= mid <= 201 for mid in mids),
                'Duplicate/invalid main ID')
        require(all(len(ch) == 1 and 'fail_closed' in status for _, ch, status in ms),
                'Unresolved member lacks exact blocked status')
        require(g['audit_sources'] and set(g['audit_sources']) <= set(ids), 'Missing source qualification')
        require(g['reason'].strip() and g['reopen_condition'].strip(), 'Missing decision/reopen condition')
        require(g['disposition'] == 'retained_fail_closed_after_bounded_audit', 'Unsupported disposition')
        require(g['teaching_restrictions'] == rule['restrictions'] == RESTRICTIONS[i],
                'Missing teaching restriction')
        require(rule['main_ids'] == mids, 'Policy member mismatch')
    require([mid for mid, _, _ in members(record['groups'][0])] == list(range(1, 202)),
            'Incomplete 201 main IDs')
    return True


def teaching_restrictions(policy, main_id, requested_fields):
    """Return only restrictions relevant to a requested teaching field.

    Empty output is not editorial approval; the renderer must still require
    the existing positive evidence for that field. Unknown fields fail closed.
    """
    require(type(main_id) is int and 1 <= main_id <= 201, 'Unknown main ID')
    require(isinstance(requested_fields, (list, tuple)) and requested_fields, 'Specify required fields')
    require(set(requested_fields) <= set(FIELDS + ['stroke_order']), 'Unknown teaching field')
    return {rule['field']: rule['restrictions'] for rule in policy['rules']
            if rule['field'] in requested_fields and main_id in rule['main_ids']}


def validate_scope(scope, policy, entries):
    require(scope['schema_version'] == 1 and scope['version'] == '0.5.0', 'Unexpected feature scope')
    require(scope['normative_policy'] == POLICY, 'Missing policy reference')
    require(scope['release_eligible'] is False and scope['Q1_completed'] is False,
            'Feature scope does not grant final release or Q1 approval')
    pairs = scope['comparison_pairs']
    require(len(pairs) == 6 and len({p['id'] for p in pairs}) == 6, 'Expected six distinct comparison groups')
    require(scope['recall_pair_ids'] == [p['id'] for p in pairs], 'Recall scope mismatch')
    for pair in pairs:
        require(len(pair['targets']) == 2, 'A comparison needs two targets')
        require(pair['required_fields'] == ['stroke_order', 'fine_stroke_names'], 'Wrong comparison dependency')
        for target in pair['targets']:
            mid = target['main_id']
            require(entries[mid]['character'] == target['character'], 'Comparison identity mismatch')
            require(not teaching_restrictions(policy, mid, pair['required_fields']), 'Blocked comparison dependency')
    require(len(scope['migration_cases']) == 6, 'Expected six migration cases')
    for case in scope['migration_cases']:
        mid = case['main_id']; e = entries[mid]; review = e['position_migration_review']
        require(case['required_fields'] == ['position_migration'], 'Wrong migration dependency')
        require(not teaching_restrictions(policy, mid, case['required_fields']), 'Blocked migration dependency')
        require(review['result'].startswith('reviewed'), 'Migration lacks a reviewed mapping')
        require(case['character'] == e['character'] and case['whole_character'] == review['whole_character']['character'],
                'Migration target mismatch')
        require(case['indices'] == review['component_stroke_indices_in_whole_character'], 'Migration indices changed')
        require(case['full_whole_character_sequence_required'] is review['full_whole_character_sequence_required'],
                'Whole-character timing requirement lost')
        require(case['evidence'] == review['evidence'], 'Migration evidence mismatch')
    packages = scope['work_packages']
    require([p['id'] for p in packages] == ['F01', 'F02', 'F03', 'F04', 'F05'], 'Feature packages drift')
    require(all(p['status'] in ('planned', 'in_progress', 'completed') for p in packages), 'Unknown feature status')
    require(scope['features_completed'] == sum(p['status'] == 'completed' for p in packages), 'Inflated feature completion')


def verify(root=ROOT, snapshot=False):
    root = Path(root)
    record = load(root, RECORD); audit = load(root, record['source_audit']); policy = load(root, POLICY)
    validate_record(record, audit, policy)
    require(hashlib.sha256(safe_file(root, record['source_audit']).read_bytes()).hexdigest() == record['source_audit_sha256'],
            'Source audit hash mismatch')
    require(hashlib.sha256(safe_file(root, RECORD).read_bytes()).hexdigest() == policy['basis_sha256'], 'Policy basis hash mismatch')
    entries = {}
    for i in range(1, 22):
        path = f'data/B{i:02}.json'
        for e in load(root, path)['entries']:
            require(e['main_id'] not in entries, 'Duplicate canonical ID')
            entries[e['main_id']] = e
        if snapshot:
            require(hashlib.sha256(safe_file(root, path).read_bytes()).hexdigest() == record['canonical_snapshot_sha256'][path],
                    'Canonical bytes changed in no-edit closeout')
    require(sorted(entries) == list(range(1, 202)), 'Incomplete canonical scope')
    for group in record['groups']:
        field = group['field']; actual = []
        for mid, e in entries.items():
            status = (e['target_identity_review']['exact_2022_item_fields_resolution']['status']
                      if field == FIELDS[0] else e.get('field_status', {}).get(field, ''))
            if 'fail_closed' in status:
                actual.append((mid, e['character'], status))
        require(sorted(actual) == members(group), 'Live field changed without policy/evidence reconciliation: ' + field)
    for adopted in record['adopted_in_cycle']:
        safe_file(root, adopted['evidence'])
    for path in record['new_changes_impact_review']:
        safe_file(root, path)
    state = load(root, 'data/post_release.json')
    m2 = next(p for p in state['phases'] if p['id'] == 'M2')
    require(m2['status'] == 'completed_with_source_blocks' and RECORD in m2['exit_evidence'], 'M2 exit record missing')
    # Later M3/Q1 progress does not require changing this historical M2 record.
    scope = load(root, SCOPE)
    validate_scope(scope, policy, entries)
    for case in scope['migration_cases']:
        safe_file(root, case['evidence'])
    return {'kind': 'M2_exit_and_teaching_policy_consistency_not_source_approval',
            'M2': 'completed_with_source_blocks', 'all_fields_resolved': False,
            'remaining_by_field': dict(zip(FIELDS, COUNTS)), 'new_normative_adoptions_this_round': 0,
            'cumulative_M2_adoptions': 3, 'M3_feature_packages_completed': scope['features_completed'],
            'checked_M3_pairs': len(scope['comparison_pairs']), 'checked_M3_migrations': len(scope['migration_cases']),
            'snapshot_bytes_checked': snapshot, 'visual_review_performed_by_checker': False}


class ExitTests(unittest.TestCase):
    def setUp(self):
        self.record = load(ROOT, RECORD)
        self.audit = load(ROOT, self.record['source_audit'])
        self.policy = load(ROOT, POLICY)

    def reject(self, fn):
        r, a, p = copy.deepcopy((self.record, self.audit, self.policy))
        fn(r, a, p)
        with self.assertRaises(ValueError): validate_record(r, a, p)

    def test_valid_record(self): self.assertTrue(validate_record(self.record, self.audit, self.policy))
    def test_missing_scope(self): self.reject(lambda r,a,p: r['groups'].pop())
    def test_wrong_count(self): self.reject(lambda r,a,p: r['groups'][2].update(remaining_count=3))
    def test_duplicate_id(self):
        self.reject(lambda r,a,p: r['groups'][0]['status_groups'][0]['members'].__setitem__(1, [1,'一']))
    def test_invalid_status(self): self.reject(lambda r,a,p: r['groups'][0]['status_groups'][0].update(status='reviewed'))
    def test_no_source(self): self.reject(lambda r,a,p: r['groups'][1].update(audit_sources=[]))
    def test_unknown_source(self): self.reject(lambda r,a,p: r['groups'][1].update(audit_sources=['invented']))
    def test_no_reopen_condition(self): self.reject(lambda r,a,p: r['groups'][2].update(reopen_condition=''))
    def test_all_resolved_claim(self): self.reject(lambda r,a,p: r.update(all_fields_resolved=True))
    def test_exhaustive_claim(self): self.reject(lambda r,a,p: r.update(all_sources_exhausted=True))
    def test_never_published_claim(self): self.reject(lambda r,a,p: a['sources'][0].update(claim_never_published=True))
    def test_inflated_adoptions(self): self.reject(lambda r,a,p: r.update(cumulative_adopted_field_updates=9))
    def test_new_adoption_claim(self): self.reject(lambda r,a,p: r.update(new_adopted_field_updates_this_round=1))
    def test_early_Q1(self): self.reject(lambda r,a,p: r.update(future_Q1_passed=True))
    def test_policy_missing_rule(self): self.reject(lambda r,a,p: p['rules'].pop())
    def test_policy_missing_restriction(self): self.reject(lambda r,a,p: p['rules'][1].update(restrictions=[]))
    def test_policy_missing_member(self): self.reject(lambda r,a,p: p['rules'][3]['main_ids'].pop())
    def test_field_specific(self): self.assertEqual(teaching_restrictions(self.policy, 55, ['stroke_order']), {})
    def test_blocked_fine_name(self): self.assertIn('fine_stroke_names', teaching_restrictions(self.policy, 55, ['fine_stroke_names']))
    def test_blocked_sound(self): self.assertIn('pronunciation', teaching_restrictions(self.policy, 201, ['pronunciation']))
    def test_adopted_sound_usable(self): self.assertEqual(teaching_restrictions(self.policy, 149, ['pronunciation']), {})
    def test_2022_still_blocked(self): self.assertIn('exact_2022_item_fields', teaching_restrictions(self.policy, 149, ['exact_2022_item_fields']))
    def test_unknown_field(self):
        with self.assertRaises(ValueError): teaching_restrictions(self.policy, 149, ['unknown'])
    def test_unknown_id(self):
        with self.assertRaises(ValueError): teaching_restrictions(self.policy, 0, ['stroke_order'])


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.scope = load(ROOT, SCOPE)
        # Tests must not assume that live work packages stay unfinished forever.
        for package in self.scope['work_packages']:
            package['status'] = 'planned'
        self.scope['features_completed'] = 0
        self.policy = load(ROOT, POLICY)
        self.entries = {e['main_id']: e for i in range(1, 22)
                        for e in load(ROOT, f'data/B{i:02}.json')['entries']}

    def reject(self, fn):
        scope = copy.deepcopy(self.scope)
        fn(scope)
        with self.assertRaises(ValueError): validate_scope(scope, self.policy, self.entries)

    def test_scope_valid(self): validate_scope(self.scope, self.policy, self.entries)
    def test_migration_indices(self): self.reject(lambda s: s['migration_cases'][4].update(indices=[1, 2, 3]))
    def test_noncontinuous_timing(self): self.reject(lambda s: s['migration_cases'][4].update(full_whole_character_sequence_required=False))
    def test_migration_evidence(self): self.reject(lambda s: s['migration_cases'][0].update(evidence='invented.json'))
    def test_blocked_comparison(self):
        self.reject(lambda s: s['comparison_pairs'][0]['targets'].__setitem__(0, {'main_id':55,'character':'屮'}))
    def test_inflated_features(self): self.reject(lambda s: s.update(features_completed=5))
    def test_wrong_identity(self): self.reject(lambda s: s['comparison_pairs'][0]['targets'][0].update(character='X'))
    def test_scope_cannot_publish(self): self.reject(lambda s: s.update(release_eligible=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--snapshot', action='store_true', help='Check no canonical byte changed in this closeout snapshot')
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls)
                                   for cls in (ExitTests, ScopeTests))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)
    print(json.dumps(verify(snapshot=args.snapshot), ensure_ascii=False, indent=2))
