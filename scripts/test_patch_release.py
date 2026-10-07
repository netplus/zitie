#!/usr/bin/env python3
"""Formal-mode regressions; synthetic negative records do not confer approval."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from patch_edition import PatchEdition
from verify_patch_candidate import ROOT, verify
from verify_patch_archive import verify as verify_archive


class FormalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT/'book/front-matter/preface.md').read_text(encoding='utf-8')
        cls.directory = ROOT/'build/v0.4.1'
        cls.meta = json.loads((cls.directory/'generation.json').read_text())

    def test_formal_notice(self):
        text = PatchEdition(mode='formal').preface_text(self.raw)
        self.assertIn('本勘误修订版为 v0.4.1', text)
        self.assertNotIn('本候选版本', text)
        self.assertIn('32项附形/位置变体索引属于教学候选导航', text)

    def test_rc_source_unchanged(self):
        self.assertEqual(PatchEdition().preface_text(self.raw), self.raw)

    def test_missing_notice_fails_closed(self):
        with self.assertRaises(ValueError): PatchEdition(mode='formal').preface_text('前言')

    def test_duplicate_notice_fails_closed(self):
        with self.assertRaises(ValueError): PatchEdition(mode='formal').preface_text(self.raw*2)

    def test_formal_pdf(self):
        self.assertEqual(verify(self.directory, 'formal')['pages'], 276)

    def test_formal_is_not_candidate(self):
        with self.assertRaises(ValueError): verify(self.directory)

    def test_candidate_is_not_formal(self):
        with self.assertRaises(ValueError): verify(ROOT/'build/v0.4.1-rc1', 'formal')

    def test_rename_rc_is_not_promotion(self):
        d = ROOT/'build/v0.4.1-rc1'
        m = json.loads((d/'generation.json').read_text())
        m.update(version='0.4.1', mode='formal', corrected_errata=['E001','E002','E004'])
        with self.assertRaises(ValueError): verify(d, 'formal', metadata=m)

    def reject_metadata(self, key, value):
        m=copy.deepcopy(self.meta); m[key]=value
        with self.assertRaises(ValueError): verify(self.directory, 'formal', metadata=m)

    def test_premature_generated_release(self): self.reject_metadata('release_eligible', True)
    def test_hash_mismatch(self): self.reject_metadata('sha256', '0'*64)
    def test_wrong_mode(self): self.reject_metadata('mode', 'candidate')
    def test_missing_E004(self): self.reject_metadata('corrected_errata', ['E001','E002'])
    def test_unsafe_path(self): self.reject_metadata('pdf', '../a.pdf')


class ArchiveTests(unittest.TestCase):
    def test_live_archive_or_pending(self):
        result=verify_archive()
        self.assertIn(result['status'], ('not_archived','archived_patch_verified'))

    def test_undeclared_release(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'data').mkdir();(root/'deliverables').mkdir()
            (root/'data/post_release.json').write_text(json.dumps({'phases':[{'status':'in_progress'}]}))
            (root/'deliverables/manifest.json').write_text(json.dumps({'artifacts':[{'status':'released','version':'0.4.2'}]}))
            with self.assertRaises(ValueError): verify_archive(root)

    def test_m1_cannot_end_without_release(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'data').mkdir();(root/'deliverables').mkdir()
            (root/'data/post_release.json').write_text(json.dumps({'phases':[{'status':'completed'}]}))
            (root/'deliverables/manifest.json').write_text(json.dumps({'artifacts':[]}))
            with self.assertRaises(ValueError): verify_archive(root)


if __name__ == '__main__': unittest.main()
