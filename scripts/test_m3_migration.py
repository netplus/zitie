#!/usr/bin/env python3
"""Reject unsafe mappings, unreviewed art and component-only sequence shortcuts."""
import copy
import json
import unittest
from pathlib import Path
from m3_model import ROOT, read_model
from m3_migration import (RECORD, CACHE, canonical_hash, validate_case, verify_outline,
                          read_migrations, sequence_pages)
from verify_m2_closeout import load


class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=read_model();_,cls.scope,cls.policy,_,cls.by_id=cls.model
        cls.records=load(ROOT,RECORD)['cases']

    def reject(self,edit,index=0):
        case=copy.deepcopy(self.scope['migration_cases'][index]);b,e=copy.deepcopy(self.by_id[case['main_id']])
        r=copy.deepcopy(self.records[index]);edit(case,b,e,r)
        with self.assertRaises(ValueError):validate_case(case,b,e,r,self.policy)

    def test_six_complete_contexts(self):self.assertEqual(len(read_migrations(self.model)),6)
    def test_ten_pages(self):self.assertEqual(sum(len(sequence_pages(r)) for r in self.records),10)
    def test_all_44_steps(self):self.assertEqual(sum(r['stroke_count'] for r in self.records),44)
    def test_all_steps_cumulative(self):
        for r in self.records:
            steps=[s for p in sequence_pages(r) for s in p]
            self.assertEqual([s['step'] for s in steps],list(range(1,r['stroke_count']+1)))
            for s in steps:self.assertEqual(s['visible_indices'],list(range(1,s['step']+1)))
    def test_max_six_steps(self):
        for r in self.records:self.assertTrue(all(1<=len(p)<=6 for p in sequence_pages(r)))
    def test_continuation_keeps_first_six(self):
        for r in self.records:
            pages=sequence_pages(r)
            if len(pages)>1:self.assertEqual(pages[1][0]['visible_indices'],list(range(1,8)))
    def test_guo_non_contiguous(self):self.assertEqual(self.records[4]['indices'],[1,2,8])
    def test_qu_non_contiguous(self):self.assertEqual(self.records[5]['indices'],[1,4])
    def test_jin_last(self):self.assertEqual(self.records[3]['indices'],[5,6,7])
    def test_men_not_upstream_radical(self):
        r=self.records[1];obj=json.loads((ROOT/CACHE/'4EEC.json').read_text())
        self.assertNotEqual([i+1 for i in obj['radStrokes']],r['indices'])
        self.assertEqual(r['indices'],[3,4,5])
    def test_source_evidence_immutable(self):
        before=copy.deepcopy(self.model)
        read_migrations(self.model)
        self.assertEqual(before,self.model)
    def test_wrong_target(self):self.reject(lambda c,b,e,r:r.update(whole_character='源'))
    def test_wrong_component(self):self.reject(lambda c,b,e,r:r.update(component='人'))
    def test_wrong_id(self):self.reject(lambda c,b,e,r:r.update(main_id=1))
    def test_duplicate_index(self):self.reject(lambda c,b,e,r:c.update(indices=[1,1]))
    def test_reverse_index(self):self.reject(lambda c,b,e,r:c.update(indices=[2,1]))
    def test_zero_index(self):self.reject(lambda c,b,e,r:c.update(indices=[0,1]))
    def test_out_of_range(self):self.reject(lambda c,b,e,r:c.update(indices=[1,11]))
    def test_boolean_index(self):self.reject(lambda c,b,e,r:c.update(indices=[True,2]))
    def test_no_component_only_mode(self):self.reject(lambda c,b,e,r:r.update(render_full_sequence=False))
    def test_no_bogus_attached_form(self):self.reject(lambda c,b,e,r:r.update(formal_attached_form_claimed=True))
    def test_no_bogus_fine_names(self):self.reject(lambda c,b,e,r:r.update(fine_stroke_names_claimed=True))
    def test_missing_positive_review(self):self.reject(lambda c,b,e,r:e['position_migration_review'].update(result='pending'))
    def test_unreviewed_art(self):self.reject(lambda c,b,e,r:r['vector_review'].update(result='pending'))
    def test_bad_source_page(self):self.reject(lambda c,b,e,r:r['source_row'].update(pdf_page=1))
    def test_bad_mapping_hash(self):self.reject(lambda c,b,e,r:r.update(mapping_review_sha256='0'*64))
    def test_bad_evidence_hash(self):self.reject(lambda c,b,e,r:r.update(evidence_sha256='0'*64))
    def test_wrong_evidence(self):self.reject(lambda c,b,e,r:r.update(evidence='sources/catalog.json'))
    def test_lost_timing_constraint(self):self.reject(lambda c,b,e,r:c.update(full_whole_character_sequence_required=False),4)
    def test_truncated_ping(self):self.reject(lambda c,b,e,r:r.update(whole_order_code='4311321'),2)
    def test_incomplete_flag(self):self.reject(lambda c,b,e,r:e['position_migration_review']['whole_character'].update(stored_whole_order_code_complete=False),2)
    def test_tampered_outline(self):
        r=self.records[0];raw=(ROOT/CACHE/'539F.json').read_bytes()
        with self.assertRaises(ValueError):verify_outline(raw+b' ',r)
    def test_whole_stroke_count_mismatch(self):
        r=copy.deepcopy(self.records[0]);r['stroke_count']=9
        with self.assertRaises(ValueError):verify_outline((ROOT/CACHE/'539F.json').read_bytes(),r)
    def test_all_target_membership_marks(self):
        for r in self.records:
            marked=[s['step'] for p in sequence_pages(r) for s in p if s['is_target_component']]
            self.assertEqual(marked,r['indices'])


if __name__=='__main__':unittest.main()
