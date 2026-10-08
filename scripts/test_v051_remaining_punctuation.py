#!/usr/bin/env python3
"""Negative gates and exact-published-input smoke test for punctuation audit."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from audit_v051_remaining_punctuation import EXPECTED, audit, left_lower, check


class AuditTests(unittest.TestCase):
    def test_expected_metrics_left_lower(self):
        for c, rule in EXPECTED.items():
            with self.subTest(c=c):
                self.assertTrue(left_lower(rule['bbox'],1024,1024))

    def test_reject_historically_centered_period_outline(self):
        self.assertFalse(left_lower((387,263,637,513),1024,1024))

    def test_reject_centered_comma_semicolon_colon(self):
        for bbox in [(400,350,600,650), (380,100,650,600), (300,50,550,700)]:
            with self.subTest(bbox=bbox):
                self.assertFalse(left_lower(bbox,1024,1024))

    def test_reject_changed_advance(self):
        self.assertFalse(left_lower(EXPECTED['，']['bbox'], 900, 1024))

    def test_reject_changed_pdf_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / 'not-release.pdf'
            bad.write_bytes(b'%PDF-1.7\nnot the published file\n')
            with self.assertRaisesRegex(ValueError, 'exact released'):
                audit(bad)

    def test_unchanged_publication(self):
        root = Path(__file__).resolve().parents[1]
        doc = root / 'deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf'
        if not doc.is_file():
            self.skipTest('Smoke test requires a checked-out repository with published PDF')
        result = audit(doc)
        self.assertFalse(result['reissue_required_by_this_audit'])
        self.assertEqual(result['pages'],299)
        self.assertEqual([result['characters'][s]['fonts']['UMingCN-0'] for s in '，；：'],[173,83,202])


if __name__ == '__main__':
    unittest.main(verbosity=2)
