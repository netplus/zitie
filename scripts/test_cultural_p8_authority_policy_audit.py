#!/usr/bin/env python3
"""P8 authority-class regression: reject fake approved pronunciations and draft norm."""
from __future__ import annotations
import copy
import unittest
from cultural_p8_authority_policy_audit import POLICY,QUEUE,audit,load

class P8AuthorityPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load(POLICY)
        cls.queue=load(QUEUE)

    def test_original_full_1013_reference_baseline(self):
        x=audit(self.data,self.queue)
        self.assertEqual((x["count_main_glyphs"],x["count_lexical_slots"]),(201,812))
        self.assertEqual(x["formally_approved_pronunciations"],0)
        self.assertFalse(x["release_eligible"])

    def test_no_promoted_2016_draft(self):
        d=copy.deepcopy(self.data)
        next(a for a in d["authorities"] if a["authority_id"]=="putonghua_yidu_2016_consultation")["effective_status"]="published"
        with self.assertRaises(ValueError):audit(d,self.queue)

    def test_no_unpublished_new_national_gb_standard(self):
        d=copy.deepcopy(self.data)
        next(a for a in d["authorities"] if a["authority_id"]=="orthoepic_gb_plan_20180782_T_360")["publication_automatically_approved"]=True
        with self.assertRaises(ValueError):audit(d,self.queue)

    def test_spelling_cannot_be_exact_sense_evidence(self):
        d=copy.deepcopy(self.data)
        next(a for a in d["authorities"] if a["authority_id"]=="GB_T_16159_2012")["allow_as_exact_pronunciation_evidence"]="always"
        with self.assertRaises(ValueError):audit(d,self.queue)

    def test_1985_source_need_exact_listed_word(self):
        d=copy.deepcopy(self.data)
        next(a for a in d["authorities"] if a["authority_id"]=="putonghua_yidu_1985")["allow_as_exact_pronunciation_evidence"]="all_812_automatically"
        with self.assertRaises(ValueError):audit(d,self.queue)

    def test_1013_audio_slips_cannot_claim_publication(self):
        q=copy.deepcopy(self.queue)
        q["entries"][0]["print_eligible"]=True
        with self.assertRaises(ValueError):audit(self.data,q)

    def test_first_reviewer_cannot_auto_populate(self):
        q=copy.deepcopy(self.queue)
        q["entries"][-1]["reviewer_id"]="autoclassifier"
        with self.assertRaises(ValueError):audit(self.data,q)

    def test_secondary_review_is_not_optional(self):
        q=copy.deepcopy(self.queue)
        q["entries"][-1]["second_reviewer_id"]="automated"
        with self.assertRaises(ValueError):audit(self.data,q)

    def test_six_multireading_conflicts_are_retained(self):
        d=copy.deepcopy(self.data)
        d["blocked_six_source_conflicts"].remove("斗")
        with self.assertRaises(ValueError):audit(d,self.queue)

    def test_duplicate_main_glyph_identity_rejected(self):
        q=copy.deepcopy(self.queue)
        q["entries"][0]["review_slot"]=q["entries"][1]["review_slot"]
        with self.assertRaises(ValueError):audit(self.data,q)

if __name__=="__main__":
    unittest.main(verbosity=2)
