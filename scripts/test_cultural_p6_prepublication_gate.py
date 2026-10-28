#!/usr/bin/env python3
"""P6 negative tests: no automated publishing of incomplete educational book."""
from __future__ import annotations

import copy
import unittest

from cultural_p6_prepublication_gate import (
    ART, ART_QA, MANIFEST, P6_SIGNOFF, P8, P9_RISK, P9_SOURCE, PROOF,
    ROOT, audit_inputs, load, markdown, release_required
)

class P6ReleaseSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=[load(ROOT,x) for x in (P8,P9_SOURCE,P9_RISK,ART,MANIFEST,PROOF,ART_QA,P6_SIGNOFF)]
        cls.result=audit_inputs(*cls.sources)

    def bad(self,index,change):
        inputs=list(self.sources)
        target=copy.deepcopy(inputs[index])
        change(target)
        inputs[index]=target
        with self.assertRaises(ValueError):
            audit_inputs(*inputs)

    def test_real_report_complete_but_not_release_ready(self):
        report=self.result
        self.assertEqual((report["original_main_glyphs"],report["total_P8_pronunciation_slots_pending"],
                          report["original_vector_stroke_steps_pixel_QA_passed"]),(201,1013,1045))
        self.assertEqual(len(report["per_glyph_reviews"]),201)
        self.assertEqual((report["P9_out_of_GF0023_scope_require_other_authority"],
                          report["P9_fine_stroke_labels_missing"]),(37,83))
        self.assertEqual((report["P10_individual_scene_studies_unapproved"],
                          report["P10_professional_illustrations_undrawn"]),(8,193))
        self.assertFalse(report["release_eligible"])
        self.assertTrue("逐字验收入口" in markdown(report))

    def test_fake_p8_pronunciation_approval_rejected(self):
        self.bad(0,lambda x:x["entries"][0].__setitem__("publication_approved",True))

    def test_missing_lexical_slot_rejected(self):
        self.bad(0,lambda x:x["entries"].pop())

    def test_p9_unreviewed_geometry_not_approved(self):
        self.bad(1,lambda x:x["entries"][0].__setitem__("drawn_geometry_verified",True))

    def test_p9_missing_stroke_names_cannot_disappear(self):
        self.bad(2,lambda x:x["unknown_fine_name_steps"].pop())

    def test_outside_GF0023_cannot_be_fake_passed(self):
        self.bad(2,lambda x:x["out_of_scope_characters"][0].__setitem__("status","approved"))

    def test_p10_unreviewed_artwork_cannot_be_signed_by_algorithm(self):
        self.bad(3,lambda x:x["entries"][0].__setitem__("visual_human_first_review","algorithm"))

    def test_archived_draft_cannot_be_silently_published(self):
        self.bad(4,lambda x:x["artifacts"][-1].__setitem__("status","released"))

    def test_earlier_unreviewed_cultural_draft_cannot_be_published(self):
        self.bad(4,lambda x:next(e for e in x["artifacts"]
                          if e.get("version")=="cultural-v0.7.1-source-visual-draft")
                 .__setitem__("release_eligible",True))

    def test_v011_two_pass_draft_cannot_be_published(self):
        self.bad(4,lambda x:next(e for e in x["artifacts"]
                          if e.get("version")=="cultural-v0.11-two-pass-201-260-editorial-draft")
                 .__setitem__("status","released"))

    def test_zi_old_wrong_竖钩_replacement_candidate_rejected(self):
        self.bad(2,lambda x:x["fine_name_vs_official_coarse_conflicts"][0]
                 .__setitem__("candidate_correction_for_first_review","竖钩"))

    def test_zi_primary_school_MOE_name_evidence_cannot_disappear(self):
        self.bad(2,lambda x:x["fine_name_vs_official_coarse_conflicts"][0]
                 .__setitem__("verified_ministry_teaching_fine_name",None))

    def test_1045_source_stroke_integrity_cannot_be_weakened(self):
        self.bad(6,lambda x:x.__setitem__("verified_source_original_stroke_tiles",1044))

    def test_260_page_provenance_cannot_claim_all_art_done(self):
        self.bad(5,lambda x:x.__setitem__("unillustrated_201_main_ids",0))

    def test_fake_physical_printer_review_cannot_release(self):
        self.bad(7,lambda x:x.__setitem__("independent_print_reviewer","AI"))

    def test_fake_user_publication_decision_cannot_release(self):
        self.bad(7,lambda x:x.__setitem__("explicit_user_P6_release_decision",True))

    def test_strict_release_flag_must_be_rejected(self):
        with self.assertRaises(ValueError):
            release_required(self.result)

if __name__=="__main__":
    unittest.main(verbosity=2)
