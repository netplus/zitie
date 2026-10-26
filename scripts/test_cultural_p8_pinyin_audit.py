#!/usr/bin/env python3
"""Deliberate bad edits MUST cause phase-one Pinyin review rejection."""
from __future__ import annotations
import copy
import unittest
from pathlib import Path
from cultural_p8_pinyin_audit import read_json,validate,QUEUE,CANDIDATES,ROOT
from cultural_source_audit import audit as audit_pdf

class PronunciationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=audit_pdf(
            ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf",
            ROOT/"deliverables/manifest.json")
        cls.queue=read_json(QUEUE)
        cls.candidates=read_json(CANDIDATES)

    def setUp(self):
        self.q=copy.deepcopy(self.queue)

    def check_rejected(self,fragment):
        with self.assertRaisesRegex(ValueError,fragment):
            validate(self.q,self.index,self.candidates,ROOT)

    def test_complete_unapproved_baseline(self):
        report=validate(self.q,self.index,self.candidates,ROOT)
        self.assertEqual(report["main_glyph_reading_slots"],201)
        self.assertEqual(report["all_word_or_component_slots"],812)
        self.assertEqual(report["approved_word_readings"],0)
        self.assertEqual(report["source_main_radicals_without_independent_pinyin"],43)
        self.assertEqual(len(report["secondary_frequent_char_reading_conflicts"]),6)

    def test_auto_promote_word_cannot_pass(self):
        term=next(x for x in self.q["entries"] if x["kind"]=="lexical_word")
        term["publication_approved"]=True
        self.check_rejected("silently approved")

    def test_auto_promote_source_glyph_cannot_pass(self):
        row=next(x for x in self.q["entries"] if x["kind"]=="main_glyph")
        row["normative_pinyin"]="yī"
        self.check_rejected("invent a normative")

    def test_missing_word_review_slot_cannot_pass(self):
        self.q["entries"].pop()
        self.check_rejected("1013 independently")

    def test_replace_word_candidate_cannot_pass(self):
        row=next(x for x in self.q["entries"] if x["kind"]=="lexical_word"
                 and x["original_candidate_py"] is not None)
        row["original_candidate_py"]="not_sourced"
        self.check_rejected("drifted")

    def test_change_frozen_pinyin_cannot_pass(self):
        row=next(x for x in self.q["entries"] if x["kind"]=="main_glyph"
                 and x["candidate_from_frozen_source_pdf"] is not None)
        row["candidate_from_frozen_source_pdf"]="invalid"
        self.check_rejected("original PDF")

    def test_remove_polyphonic_warning_cannot_pass(self):
        row=next(x for x in self.q["entries"] if x.get("headword")=="得"
                 and x.get("main_id")==41)
        row["reviews_required"].remove("multiple_readings_unresolved")
        self.check_rejected("improperly assigned")

    def test_silent_machine_word_promotion_cannot_pass(self):
        row=next(x for x in self.q["entries"]
                 if x.get("origin_source_class")=="algorithmic_per_character_draft")
        row["reviews_required"].remove("unreliable_character_by_character_join")
        self.check_rejected("risk was erased")

    def test_drop_six_cross_source_conflicts_cannot_pass(self):
        row=next(x for x in self.q["entries"] if x.get("kind")=="main_glyph"
                 and x["character"]=="长")
        row["risks"].remove("different_from_secondary_frequent_character_reading")
        self.check_rejected("Known six")

    def test_only_one_editor_cannot_publish(self):
        row=next(x for x in self.q["entries"] if x["kind"]=="lexical_word")
        row["reviewer_id"]="arbitrary"
        self.check_rejected("silently approved")

if __name__=="__main__":
    unittest.main(verbosity=2)
