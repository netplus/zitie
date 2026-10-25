#!/usr/bin/env python3
"""P4.2 full-book plan negative tests; never classify draft as publication."""
from __future__ import annotations
import copy
import unittest
from pathlib import Path

from cultural_source_audit import audit as original_audit
from cultural_fullbook_model import ROOT, SHA, make_plan

class FullBookScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=original_audit(
            ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf",
            ROOT/"deliverables/manifest.json")

    def test_all_main_glyphs_and_exactly_frozen_steps(self):
        plan=make_plan(self.source)
        self.assertEqual(plan["source_main_id_count"],201)
        self.assertEqual(plan["source_stroke_total"],1045)
        self.assertEqual(plan["batch_count"],21)
        self.assertEqual(plan["existing_cultural_drafts"],16)
        self.assertEqual(plan["without_new_cultural_content"],185)
        self.assertEqual(sum(x["page_parts"] for x in plan["entries"]),
                         201+sum(x["stroke_count"]>6 for x in plan["entries"]))
        self.assertEqual(plan["new_cultural_release_approved"],0)
        self.assertEqual(plan["complete_artwork_approved"],0)
        self.assertEqual(plan["attached_form_count_included"],0)

    def test_missing_step_rejected(self):
        tampered=copy.deepcopy(self.source)
        one=next(x for x in tampered["glyphs"] if x["stroke_count"]>=5)
        one["steps"].pop()
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            make_plan(tampered)

    def test_missing_main_id_rejected(self):
        tampered=copy.deepcopy(self.source)
        tampered["glyphs"].pop()
        with self.assertRaisesRegex(ValueError,"main IDs"):
            make_plan(tampered)

    def test_wrong_source_pdf_rejected(self):
        tampered=copy.deepcopy(self.source)
        tampered["source_pdf_sha256"]="bad"
        with self.assertRaisesRegex(ValueError,"locked"):
            make_plan(tampered)

    def test_fake_approved_source_rejected(self):
        tampered=copy.deepcopy(self.source)
        tampered["source_teaching_pages"]=0
        with self.assertRaisesRegex(ValueError,"locked"):
            make_plan(tampered)

if __name__=="__main__":
    unittest.main(verbosity=2)
