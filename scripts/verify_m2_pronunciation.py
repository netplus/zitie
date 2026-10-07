#!/usr/bin/env python3
"""Check two recorded GF0025 morpheme reopens, not source-reading approval."""
import argparse
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECORD = 'data/evidence/M2-GF0025-pronunciation-20261007.json'
NEW = 'reviewed_M2_GF0025_2021_target_morpheme_pronunciation'
OLD = 'conflict_fail_closed_no_S03_or_S06_target_pronunciation'
EXPECTED = [('B15', 149, '麦', '小麦', 'xiǎomài', ['xiǎo', 'mài'], 105, 99, '6', 888),
            ('B18', 172, '齿', '牙齿', 'yáchǐ', ['yá', 'chǐ'], 164, 158, '7-9', 4758)]
SHA = 'e451fdf0899d9267bbd122db66e7e75bdd2851ad1e6732e47b6e960290d73a63'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(root, path):
    p = Path(path)
    require(not p.is_absolute() and '..' not in p.parts, 'Unsafe record path')
    resolved = (root / p).resolve()
    require(resolved.is_relative_to(root.resolve()), 'Record outside project')
    return json.loads(resolved.read_text(encoding='utf-8'))


def validate_record(r):
    require(r['schema_version'] == 1 and r['phase'] == 'M2', 'Wrong phase/schema')
    s = r['source']
    require(s['source_id'] == 'S11' and s['publication_id'] == 'GF0025—2021', 'Wrong source')
    require((s['pdf_sha256'], s['pdf_pages'], s['pdf_bytes']) == (SHA, 260, 51104405), 'Unreviewed source bytes')
    require(len(r['adopted']) == 2, 'Wrong adoption count')
    require(r['remaining_characters'] == list('尢弋彳毋邑黾阜黍龠'), 'Audit scope drift')
    for key in ('independent_character_entries', 'all_readings_of_character_verified',
                'formal_GF0011_2022_identity_promoted', 'component_name_promoted',
                'structure_promoted', 'entire_GF0025_exclusion_review', 'M2_completed', 'Q1_completed'):
        require(r['boundaries'][key] is False, 'Out-of-scope claim: ' + key)
    for a, expected in zip(r['adopted'], EXPECTED):
        batch, mid, ch, word, printed, syllables, page, original, level, no = expected
        require(a['target'] == {'batch': batch, 'main_id': mid, 'character': ch, 'field': 'pronunciation'}, 'Wrong target')
        loc = a['locator']
        require((loc['word'], loc['printed_pinyin'], loc['syllables']) == (word, printed, syllables), 'Word/pinyin evidence changed')
        require((loc['pdf_page'], loc['printed_page'], loc['level'], loc['table_entry']) == (page, original, level, no), 'Wrong precise locator')
        require(loc['target_character_index'] == loc['target_syllable_index'] == 2, 'Wrong morpheme alignment')
        require(word[1] == ch and a['adopted_reading'] == syllables[1], 'Wrong target syllable/tone')
        require(a['old_pinyin'] is None and a['old_field_status'] == OLD, 'Old blocked state lost')
        require(a['old_review']['result'] == OLD and a['old_review']['phase'] == 'P3', 'Prior review lost')
        n = a['new_review']
        require(n['locator'] == loc and n['target'] == ch and n['adopted_reading'] == syllables[1], 'Review/locator mismatch')
        require(n['phase'] == 'M2' and n['source_id'] == 'S11' and n['pdf_sha256'] == SHA, 'Review source mismatch')
        require(n['evidence_kind'] == 'word_target_morpheme_not_independent_character_entry', 'Morpheme is not standalone entry')
        require(n['result'] == a['application']['new_field_status'] == NEW and n['evidence'] == RECORD, 'Review/status mismatch')
        require(n['visual_review'] is True, 'Missing source review record')
        for k in ('whole_page_viewed', 'target_row_viewed_enlarged', 'target_morpheme_alignment_checked'):
            require(a['visual_review'][k] is True, 'Incomplete visual-review record')
    return True


def verify(root=ROOT):
    root = Path(root)
    r = load(root, RECORD)
    validate_record(r)
    audit = load(root, r['bounded_probe_audit'])
    require(audit['pdf_sha256'] == SHA and audit['adopted_count'] == 2 and audit['remaining_count'] == 9, 'Audit mismatch')
    require([p['character'] for p in audit['bounded_probes']] == r['remaining_characters'], 'Missing bounded probes')
    for probe in audit['bounded_probes']:
        require(probe['entire_source_absence_claimed'] is False and probe['canonical_status_changed'] is False,
                'A bounded negative is not an exclusion or promotion')
    require(audit['exclusions']['not_applicable_targets_reopened'] is False, 'NA was converted to a missing reading')
    for a in r['adopted']:
        d = load(root, 'data/' + a['target']['batch'] + '.json')
        entry = next(e for e in d['entries'] if e['main_id'] == a['target']['main_id'])
        history = entry.get('pronunciation_review_history', [])
        require(a['old_review'] in history, 'Previous P3 review not preserved')
        current = entry['pronunciation_review']
        require(current == a['new_review'] or a['new_review'] in history, 'Adopted M2 review lost')
        require(entry['field_status']['pronunciation'] == entry['pinyin_status'] == current['result'], 'Live status/review mismatch')
        require(entry['pinyin'] == current['adopted_reading'], 'Live reading/review mismatch')
    catalog = load(root, 'sources/catalog.json')
    registered = [s for s in catalog['sources'] if s['id'] == 'S11']
    require(len(registered) == 1 and registered[0]['sha256'] == SHA and registered[0]['evidence'] == RECORD,
            'Source catalogue mismatch')
    data = [e for i in range(4, 22) for e in load(root, f'data/B{i:02d}.json')['entries']]
    statuses = [e['field_status']['pronunciation'] for e in data]
    reviewed = sum(s.startswith('reviewed') for s in statuses)
    na = sum(s.startswith('not_applicable') for s in statuses)
    blocked = [e['character'] for e in data if 'fail_closed' in e['field_status']['pronunciation']]
    require(reviewed + na + len(blocked) == len(data) == 171, 'Unclassified pronunciation state')
    return {'kind': 'M2_pronunciation_evidence_consistency_not_visual_approval',
            'adopted': {a['target']['character']: a['adopted_reading'] for a in r['adopted']},
            'current_B04_B21': {'reviewed': reviewed, 'not_applicable': na, 'fail_closed': len(blocked), 'blocked_characters': blocked},
            'entire_source_absence_claimed': False, 'visual_review_performed_by_checker': False}


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.r = load(ROOT, RECORD)

    def reject(self, change):
        r = copy.deepcopy(self.r)
        change(r)
        with self.assertRaises(ValueError):
            validate_record(r)

    def test_valid(self): self.assertTrue(validate_record(self.r))
    def test_live_adoption(self): self.assertEqual(verify()['adopted'], {'麦': 'mài', '齿': 'chǐ'})
    def test_wrong_source_hash(self): self.reject(lambda r: r['source'].update(pdf_sha256='0'*64))
    def test_wrong_publication(self): self.reject(lambda r: r['source'].update(publication_id='GF0011—2022'))
    def test_wrong_page(self): self.reject(lambda r: r['adopted'][0]['locator'].update(pdf_page=104))
    def test_printed_page_confusion(self): self.reject(lambda r: r['adopted'][0]['locator'].update(printed_page=105))
    def test_wrong_entry(self): self.reject(lambda r: r['adopted'][0]['locator'].update(table_entry=887))
    def test_wrong_level(self): self.reject(lambda r: r['adopted'][1]['locator'].update(level='6'))
    def test_wrong_word(self): self.reject(lambda r: r['adopted'][1]['locator'].update(word='牙膏'))
    def test_first_syllable(self): self.reject(lambda r: r['adopted'][0]['locator'].update(target_syllable_index=1))
    def test_first_character(self): self.reject(lambda r: r['adopted'][1]['locator'].update(target_character_index=1))
    def test_wrong_tone(self): self.reject(lambda r: r['adopted'][0].update(adopted_reading='mǎi'))
    def test_wrong_target_id(self): self.reject(lambda r: r['adopted'][1]['target'].update(main_id=173))
    def test_missing_old_review(self): self.reject(lambda r: r['adopted'][0]['old_review'].update(phase='M2'))
    def test_missing_enlarged_review(self): self.reject(lambda r: r['adopted'][0]['visual_review'].update(target_row_viewed_enlarged=False))
    def test_standalone_promotion(self): self.reject(lambda r: r['boundaries'].update(independent_character_entries=True))
    def test_other_readings_promotion(self): self.reject(lambda r: r['boundaries'].update(all_readings_of_character_verified=True))
    def test_formal_identity_promotion(self): self.reject(lambda r: r['boundaries'].update(formal_GF0011_2022_identity_promoted=True))
    def test_exhaustive_absence(self): self.reject(lambda r: r['boundaries'].update(entire_GF0025_exclusion_review=True))
    def test_premature_M2_completion(self): self.reject(lambda r: r['boundaries'].update(M2_completed=True))
    def test_premature_Q1(self): self.reject(lambda r: r['boundaries'].update(Q1_completed=True))
    def test_additional_unsupported_adoption(self): self.reject(lambda r: r['adopted'].append(copy.deepcopy(r['adopted'][0])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EvidenceTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
