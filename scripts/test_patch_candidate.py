#!/usr/bin/env python3
"""Regression checks for M1 labels and missing-font failures; no visual claims."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from patch_edition import PatchEdition, register_variant_font
from verify_patch_candidate import ROOT, verify

FONT = '/usr/share/fonts/truetype/arphic/uming.ttc'


class EditionTests(unittest.TestCase):
    def test_version(self):
        e = PatchEdition()
        self.assertEqual(e.identifier, '0.4.1-rc1')
        self.assertIn('v0.4.1-rc1', e.practice_label)

    def test_formal_is_distinct(self):
        e = PatchEdition(mode='formal')
        self.assertEqual(e.identifier, '0.4.1')
        self.assertNotIn('候选', e.label)

    def test_reject_baseline(self):
        with self.assertRaises(ValueError): PatchEdition('0.4.0')

    def test_reject_m3(self):
        with self.assertRaises(ValueError): PatchEdition('0.5.0')

    def test_reject_path_version(self):
        with self.assertRaises(ValueError): PatchEdition('../0.4.1')

    def test_bad_mode(self):
        with self.assertRaises(ValueError): PatchEdition(mode='released')

    def test_bad_rc(self):
        for rc in (0, -1, True):
            with self.assertRaises(ValueError): PatchEdition(rc=rc)

    def test_font_coverage(self):
        forms = [v['form'] for v in json.loads((ROOT/'data/variants.json').read_text())['items']]
        _, audit = register_variant_font(FONT, forms)
        self.assertEqual(audit['checked_form_count'], 32)
        self.assertFalse(audit['visual_approval'])

    def test_missing_font(self):
        with self.assertRaises(ValueError): register_variant_font('/no/such/font.ttf', ['龵'])

    def test_missing_glyph(self):
        with self.assertRaises(ValueError): register_variant_font(FONT, ['\U0010ffff'])

    def test_missing_v007_in_body_font(self):
        with self.assertRaises(ValueError):
            register_variant_font('/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf', ['龵'])

    def test_bad_face(self):
        with self.assertRaises(ValueError): register_variant_font(FONT, ['龵'], -1)


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = ROOT/'build/v0.4.1-rc1'
        self.meta = json.loads((source/'generation.json').read_text())
        shutil.copyfile(source/self.meta['pdf'], self.root/self.meta['pdf'])

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self):
        (self.root/'generation.json').write_text(json.dumps(self.meta))
        return verify(self.root)

    def test_generated(self):
        self.assertEqual(self.run_check()['pages'], 276)

    def test_changed_bytes(self):
        self.meta['sha256'] = '0'*64
        with self.assertRaises(ValueError): self.run_check()

    def test_early_promotion(self):
        self.meta['release_eligible'] = True
        with self.assertRaises(ValueError): self.run_check()

    def test_coverage_regression(self):
        self.meta['variant_font']['checked_form_count'] = 31
        with self.assertRaises(ValueError): self.run_check()

    def test_wrong_version(self):
        self.meta['version'] = '0.4.0-rc1'
        with self.assertRaises(ValueError): self.run_check()


if __name__ == '__main__':
    unittest.main()
