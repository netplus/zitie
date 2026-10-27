#!/usr/bin/env python3
"""P9 validate that fake normative coverage, missing pen names and a false 子 pass fail."""
from __future__ import annotations
import copy
import unittest
from cultural_p9_primary_open_cases_audit import read,CASES,verify

class StrictP9Cases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.base=read(CASES)
    def test_valid_source_linked_queue(self):
        r=verify(self.base)
        self.assertEqual((r["outside_8105_cases"],r["fine_stroke_names_missing"],
                          r["specific_name_vs_official_code_risks"]),(37,83,1))
        self.assertEqual(r["human_approved_corrections"],0)
    def test_cannot_add_fake_GF3002_page(self):
        r=copy.deepcopy(self.base)
        r["out_of_scope_characters"][0]["other_normative_primary_row_pdf_page"]=117
        with self.assertRaises(ValueError):verify(r)
    def test_cannot_replace_unknown_with_auto_guessed_names(self):
        r=copy.deepcopy(self.base)
        r["unknown_fine_name_steps"][0]["approved_fine_name"]="横撇"
        with self.assertRaises(ValueError):verify(r)
    def test_no_quiet_deletion_of_rare_characters(self):
        r=copy.deepcopy(self.base)
        r["out_of_scope_characters"].pop()
        with self.assertRaises(ValueError):verify(r)
    def test_missing_pen_name_records_are_not_optional(self):
        r=copy.deepcopy(self.base)
        r["unknown_fine_name_steps"].pop()
        with self.assertRaises(ValueError):verify(r)
    def test_cannot_fake_independent_second_review(self):
        r=copy.deepcopy(self.base)
        r["unknown_fine_name_steps"][0]["second_reviewer"]="automated"
        with self.assertRaises(ValueError):verify(r)
    def test_zi_second_name_cannot_be_autocorrected_as_approved(self):
        r=copy.deepcopy(self.base)
        r["fine_name_vs_official_coarse_conflicts"][0]["approved_new_label"]="竖钩"
        with self.assertRaises(ValueError):verify(r)
    def test_source_ink_coordinates_locked(self):
        r=copy.deepcopy(self.base)
        r["unknown_fine_name_steps"][0]["source_rect_pt"][0]+=1
        with self.assertRaises(ValueError):verify(r)

if __name__=="__main__":unittest.main(verbosity=2)
