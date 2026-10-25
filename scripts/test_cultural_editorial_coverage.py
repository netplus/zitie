#!/usr/bin/env python3
"""Coverage fail-closed unit tests for the 201-glyph cultural editorial ledger."""
from __future__ import annotations
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from cultural_editorial_coverage import ROOT,audit

class EditorialCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.temp.name)
        shutil.copytree(ROOT/'data',cls.root/'data')
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def _mutate(self,relative,change):
        path=self.root/'data'/relative
        old=path.read_bytes()
        try:
            obj=json.loads(old)
            change(obj)
            path.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf8')
            return audit(self.root)
        finally:
            path.write_bytes(old)

    def test_exact_201_glyphs_and_work_queue(self):
        result=audit(self.root)
        self.assertEqual(result['counts']['canonical_glyphs'],201)
        self.assertEqual(result['counts']['batches'],21)
        self.assertEqual(result['counts']['P1_sample_reading_pages'],4)
        self.assertEqual(result['counts']['P4_sample_reading_pages'],3)
        self.assertEqual(result['counts']['not_started_glyph_content'],185)
        self.assertEqual(result['counts']['not_rendered_reading_pages'],194)
        self.assertEqual(result['counts']['P2_new_B01_editorial_briefs_unreviewed'],9)
        self.assertEqual(result['counts']['P2_B01_word_candidates_unreviewed'],36)
        self.assertEqual(result['counts']['glyphs_with_any_editorial_brief'],16)
        self.assertEqual(result['counts']['four_illustration_drafts_unreviewed'],4)
        self.assertEqual(result['counts']['published_new_cultural_characters'],0)
    def test_incomplete_main_id_is_rejected(self):
        def mutate(x):x['entries'].pop()
        with self.assertRaises(ValueError):
            self._mutate('cultural_edition/inventory/B15-B21.json',mutate)
    def test_editorial_approval_is_rejected(self):
        def mutate(x):x['entries'][0]['release_eligible']=True
        with self.assertRaisesRegex(ValueError,'cannot be published'):
            self._mutate('cultural_edition/inventory/B01-B07.json',mutate)
    def test_pinyin_adoption_is_rejected(self):
        def mutate(x):x['entries'][0]['original_pdf_pronunciation_adoption_checked_here']=True
        with self.assertRaisesRegex(ValueError,'PDF proof'):
            self._mutate('cultural_edition/inventory/B01-B07.json',mutate)
    def test_direct_exam_is_not_mainland_dictionary_approval(self):
        def mutate(x):x['publication_approved']=True
        with self.assertRaisesRegex(ValueError,'cannot approve'):
            self._mutate('cultural_edition/p2_mainland_exam_evidence_20261024.json',mutate)
    def test_discrepancy_is_not_silenced(self):
        def mutate(x):x['entries'][0]['draft_pinyin_display']='yuè liàng'
        with self.assertRaisesRegex(ValueError,'changed silently'):
            self._mutate('cultural_edition/p2_mainland_exam_evidence_20261024.json',mutate)
    def test_pinyin_cannot_be_silently_changed_from_original(self):
        def mutate(x):x['entries'][0]['original_data_candidate_pinyin']='xī'
        with self.assertRaisesRegex(ValueError,'Unjustified pinyin change'):
            self._mutate('cultural_edition/inventory/B01-B07.json',mutate)
    def test_trusted_exam_host_required(self):
        def mutate(x):x['entries'][0]['source_url']='https://fake.example.com/standardsAction.do?means=getStandardWordsList'
        with self.assertRaisesRegex(ValueError,'Unknown examination source'):
            self._mutate('cultural_edition/p2_mainland_exam_evidence_20261024.json',mutate)

if __name__=='__main__':
    unittest.main(verbosity=2)
