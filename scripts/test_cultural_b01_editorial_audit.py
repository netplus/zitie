#!/usr/bin/env python3
"""Negative tests for P2 B01 review-gated editorial drafts."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from cultural_b01_editorial_audit import ROOT, RELATIVE, audit


class B01EditorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = tempfile.TemporaryDirectory()
        cls.root = Path(cls.sandbox.name)
        shutil.copytree(ROOT / "data", cls.root / "data")

    @classmethod
    def tearDownClass(cls):
        cls.sandbox.cleanup()

    def corrupt(self, rel, change):
        target = self.root / rel
        old = target.read_bytes()
        try:
            doc = json.loads(old)
            change(doc)
            target.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
            audit(self.root)
        finally:
            target.write_bytes(old)

    def test_scope_and_review_state(self):
        report = audit(self.root)
        self.assertEqual(report["new_characters"], 9)
        self.assertEqual(report["unreviewed_word_candidates"], 36)
        self.assertEqual(report["new_pages_rendered"], 0)
        self.assertEqual(report["new_characters_approved"], 0)

    def test_repeated_cultural_theme_rejected(self):
        with self.assertRaisesRegex(ValueError, "Repeated"):
            self.corrupt(RELATIVE, lambda d: d["entries"][1].update(
                theme_key=d["entries"][0]["theme_key"]))

    def test_unverified_quote_cannot_be_attributed(self):
        with self.assertRaisesRegex(ValueError, "quotations"):
            self.corrupt(RELATIVE, lambda d: d["entries"][0]["quote"].update(
                text="未经核实的引文", attribution="某位作者"))

    def test_pinyin_promotion_rejected(self):
        with self.assertRaisesRegex(ValueError, "lack direct mainland"):
            self.corrupt(RELATIVE, lambda d: d["entries"][0]["terms"][0].update(
                pronunciation_status="reviewed"))

    def test_unreviewed_characters_cannot_be_released(self):
        with self.assertRaisesRegex(ValueError, "approved for publication"):
            self.corrupt(RELATIVE, lambda d: d["entries"][1].update(
                publication_eligible=True))

    def test_source_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity"):
            self.corrupt(RELATIVE, lambda d: d["entries"][0].update(
                character="二"))

    def test_b01_ledger_must_not_claim_existing_pdf_page(self):
        with self.assertRaisesRegex(ValueError, "not a rendered"):
            self.corrupt("data/cultural_edition/inventory/B01-B07.json",
                         lambda d: d["entries"][0].update(
                             reading_page_draft_phase="P2"))

    def test_silent_sandhi_risk_deletion_rejected(self):
        with self.assertRaisesRegex(ValueError, "tone sandhi"):
            self.corrupt(RELATIVE, lambda d: d["entries"][0]["terms"][0].update(
                reading_risk="none"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
