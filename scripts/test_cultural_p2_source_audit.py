#!/usr/bin/env python3
"""Ensure P2 audit cannot turn foreign dictionary entries into publication approvals."""
import copy, json, unittest
from cultural_p2_source_audit import FIRST, P4, EVIDENCE, validate

class CrossRegionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first = json.loads(FIRST.read_text(encoding='utf-8'))
        cls.p4 = json.loads(P4.read_text(encoding='utf-8'))
        cls.references = json.loads(EVIDENCE.read_text(encoding='utf-8'))

    def test_coverage_and_explicit_discrepancy(self):
        report = validate(self.first, self.p4, self.references)
        self.assertEqual(report['counts']['manuscript_word_placements'], 36)
        self.assertEqual(report['counts']['unique_candidate_words'], 35)
        self.assertEqual(report['counts']['unique_words_with_secondary_direct_entry'], 19)
        self.assertEqual(report['official_mainland_word_pronunciations_approved'], 0)
        differing = [x for x in report['words'] if x['tone_or_reading_conflict']]
        self.assertEqual(len(differing), 1)
        self.assertEqual(differing[0]['draft_pinyin'], 'yuè liang')
        self.assertEqual(differing[0]['secondary_dictionary_pinyin'], 'yuè liàng')
        self.assertFalse(differing[0]['release_eligible'])

    def test_unadopted_character_reading(self):
        report = validate(self.first, self.p4, self.references)
        self.assertEqual(len(report['unpromoted_character_only']), 1)
        self.assertFalse(any(x['word'] == '龠' for x in report['words']))

    def test_review_promotion_rejected(self):
        first = copy.deepcopy(self.first)
        first['entries'][0]['terms'][0]['status'] = 'reviewed'
        with self.assertRaisesRegex(ValueError, 'auto-promoted'):
            validate(first, self.p4, self.references)

    def test_source_approval_rejected(self):
        evidence = copy.deepcopy(self.references)
        evidence['canonical_mainland_review_complete'] = True
        with self.assertRaisesRegex(ValueError, 'cannot authorize'):
            validate(self.first, self.p4, evidence)

    def test_pronunciation_conflict_can_not_be_silenced(self):
        evidence = copy.deepcopy(self.references)
        next(x for x in evidence['entries'] if x['word'] == '月亮')['comparison_to_current_sample'] = 'aligned'
        with self.assertRaisesRegex(ValueError, 'discrepancy improperly labeled'):
            validate(self.first, self.p4, evidence)

    def test_duplicate_direct_entry_rejected(self):
        evidence = copy.deepcopy(self.references)
        evidence['entries'].append(copy.deepcopy(evidence['entries'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate direct'):
            validate(self.first, self.p4, evidence)

if __name__ == '__main__':
    unittest.main(verbosity=2)
