#!/usr/bin/env python3
"""P9.6 negative tests: all 83 fine-name candidates remain source-linked and unreleased."""
from __future__ import annotations
import copy
import unittest
from cultural_p9_fine_name_83_research_atlas import evidence,get,CAND,RISKS,P9_PROOF

class P9FineCandidateReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=get(CAND);cls.r=get(RISKS);cls.p=get(P9_PROOF)
    def altered(self,i,fn):
        parts=[copy.deepcopy(self.c),copy.deepcopy(self.r),copy.deepcopy(self.p)]
        fn(parts[i])
        with self.assertRaises(ValueError):
            evidence(parts[0],parts[1],parts[2])

    def test_all_83_source_ink_source_ids_are_accounted(self):
        a=evidence(self.c,self.r,self.p)
        self.assertEqual((a["original_review_glyphs"],a["source_legacy_unnamed_step_slots"]),(14,83))
        self.assertEqual(a["candidate_name_assessments"],83)
        self.assertEqual(a["fine_names_independently_human_approved"],0)
        self.assertEqual(a["prioritized_exact_stroke_order_conflicts"],2)
        self.assertFalse(a["release_eligible"])

    def test_no_automatic_children_print_approval(self):
        self.altered(0,lambda c:c["safety"].__setitem__("all_83_child_facing_print_eligible",True))
    def test_no_auto_human_editor(self):
        self.altered(0,lambda c:c["character_groups"][0].__setitem__("first_reviewer","LLM"))
    def test_no_auto_publication(self):
        self.altered(0,lambda c:c["character_groups"][0].__setitem__("publication_eligible",True))
    def test_no_fake_GF2001_primary_source_full_pdf_verified(self):
        self.altered(0,lambda c:c["primary_documentary_evidence"][0].__setitem__("primary_full_pdf_visual_page_verified",True))
    def test_cannot_rename_ya_zhushe_without_primary_support(self):
        self.altered(0,lambda c:next(x for x in c["character_groups"] if x["main_id"]==69)["candidate_names"].__setitem__(1,"横钩"))
    def test_cannot_hide_unknown_by_deleting_83rd_step(self):
        self.altered(0,lambda c:c["character_groups"][-1]["candidate_names"].pop())
    def test_cannot_rename_a_stroke_to_different_coarse_digit(self):
        self.altered(0,lambda c:next(x for x in c["character_groups"] if x["main_id"]==69)["candidate_names"].__setitem__(2,"横折"))
    def test_original_legacy_source_pen_name_cannot_be_changed(self):
        self.altered(1,lambda r:r["unknown_fine_name_steps"][0].__setitem__("legacy_name","竖折"))
    def test_original_review_page_source_clip_cannot_be_removed(self):
        self.altered(2,lambda p:p["page_map"][0]["source_steps"].pop())
    def test_stroke_order_disagreement_鬥_cannot_be_erased(self):
        self.altered(0,lambda c:next(x for x in c["high_priority_sequence_discrepancies"] if x["main_id"]==190).__setitem__("independent_lexicon_repeated_code","2112111212"))
    def test_屮_lexicon_digit_vs_fine_name_conflict_cannot_be_erased(self):
        self.altered(0,lambda c:next(x for x in c["high_priority_sequence_discrepancies"] if x["main_id"]==55).__setitem__("coarse_code_from_secondary_written_labels","522"))
    def test_unreviewed_fine_name_cannot_acquire_fake_approval(self):
        self.altered(1,lambda r:r["unknown_fine_name_steps"][-1].__setitem__("approved_fine_name","竖钩"))
    def test_cannot_reuse_one_old_source_main_id_twice(self):
        self.altered(0,lambda c:c["character_groups"][0].__setitem__("main_id",60))

if __name__=="__main__":
    unittest.main(verbosity=2)
