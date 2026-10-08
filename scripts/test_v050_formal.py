#!/usr/bin/env python3
"""Negative tests for the exact final v0.5.0 derivative and publication gates."""
import copy
import json
import unittest
from build_v050_formal import ROOT, SOURCE, SOURCE_SHA, FORMAL_SHA
from verify_v050_final import REL, check_manifest_entry, verify


class FinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records=json.loads((ROOT/'deliverables/manifest.json').read_text())['artifacts']
        cls.record=next(x for x in records if x['path']==REL)

    def reject(self, **changes):
        entry=copy.deepcopy(self.record); entry.update(changes)
        with self.assertRaises(ValueError):check_manifest_entry(entry)

    def test_registered_exact_final(self):
        self.assertTrue(verify()['release_registered'])

    def test_wrong_version(self):self.reject(version='0.5.0-rc3')
    def test_wrong_hash(self):self.reject(sha256='0'*64)
    def test_wrong_page_count(self):self.reject(pages=298)
    def test_reuse_rc1_source_commit(self):self.reject(source_commit='a'*40)
    def test_false_origin(self):self.reject(provenance_kind='clean_source_rebuild')
    def test_unfrozen_source(self):self.reject(source_pdf_sha256='0'*64)
    def test_wrong_status(self):self.reject(status='release_candidate')
    def test_unreviewed(self):self.reject(release_eligible=False)
    def test_unapproved_print(self):
        gate=dict(self.record['release_gate_snapshot'],physical_print_test_performed=True)
        self.reject(release_gate_snapshot=gate)
    def test_lost_gate(self):
        gate=dict(self.record['release_gate_snapshot'],layout='pending')
        self.reject(release_gate_snapshot=gate)
    def test_unreported_source_block(self):
        gate=dict(self.record['release_gate_snapshot'],terminal_fail_closed_disclosed=False)
        self.reject(release_gate_snapshot=gate)
    def test_exact_source(self):
        self.assertEqual(self.record['source_pdf'], SOURCE)
        self.assertEqual(self.record['source_pdf_sha256'], SOURCE_SHA)
        self.assertEqual(self.record['sha256'],FORMAL_SHA)


if __name__=='__main__':unittest.main()
