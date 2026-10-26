#!/usr/bin/env python3
"""Negative tests: P9 can't call an original-source duplicate 'nationally verified'."""
from __future__ import annotations
import copy
import unittest
from cultural_source_audit import audit as source_audit
from cultural_p9_stroke_audit import ROOT,REGISTRY,SOURCE,MANIFEST,load,audit_registry

class SourceStrokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=source_audit(SOURCE,MANIFEST)
        cls.data=load(REGISTRY)

    def setUp(self):
        self.data_copy=copy.deepcopy(self.data)

    def reject(self,phrase):
        with self.assertRaisesRegex(ValueError,phrase):
            audit_registry(self.data_copy,self.source)

    def test_verified_baseline_is_evidence_not_publication_approval(self):
        result=audit_registry(self.data_copy,self.source)
        self.assertEqual(result["main_ids"],201)
        self.assertEqual(result["original_stroke_form_xobjects_total"],1045)
        self.assertEqual(result["unknown_or_generic_fine_name_steps"],83)
        self.assertEqual(result["secondary_five_type_order_match_no_unknown"],186)
        self.assertEqual(result["strokes_independently_proved_correct_from_official_primary_GF_pdf"],0)

    def test_empty_original_step_rejected(self):
        self.data_copy["entries"][0]["source_step_records"].pop()
        self.reject("expected number")

    def test_changed_pen_name_rejected(self):
        self.data_copy["entries"][0]["source_step_records"][0]["name"]="点"
        self.reject("clip, type or order drifted")

    def test_permuted_step_index_rejected(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="子")
        row["source_step_records"][1]["index"]=7
        self.reject("clip, type or order drifted")

    def test_source_pdf_sha_rejected(self):
        self.data_copy["frozen_source_pdf_sha256"]="0"*64
        self.reject("cannot change frozen source")

    def test_generic_name_must_not_be_assumed_correct(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="髟")
        row["generic_numbered_stroke_names"]=0
        self.reject("were hidden")

    def test_conflict_must_not_be_deleted(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="子")
        row["differing_main_stroke_indexes"]=[]
        self.reject("were hidden")

    def test_official_gf_claim_without_source_rejected(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="人")
        row["independent_primary_standard_verification"]=True
        self.reject("approved without exact original norm")

    def test_relabel_out_of_scope_radical_rejected(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="龺")
        row["normative_scope_status"]="GF0023_SCOPE_POSSIBLE_NOT_YET_PRIMARY_VERIFIED"
        self.reject("rare component")

    def test_fake_signoff_rejected(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="毛")
        row["reviewer_b"]="bot"
        self.reject("approved without exact original norm")

    def test_cropped_vector_source_page_rejected(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="卜")
        row["source_step_records"][0]["source_pdf_page"]=0
        self.reject("clip, type or order drifted")

    def test_rewrite_reference_code_rejected(self):
        row=next(x for x in self.data_copy["entries"] if x["character"]=="人")
        row["secondary_reference_five_type_code"]="11"
        self.reject("were hidden")

if __name__=="__main__":
    unittest.main(verbosity=2)
