#!/usr/bin/env python3
"""Negative import tests. Passing these checks does not confer publication approval."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import verify_q1_import as q

class EntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((q.ROOT/"deliverables/manifest.json").read_text())
        cls.entry = next(x for x in manifest["artifacts"] if x.get("provenance_kind") == q.KIND)
    def rejects(self, field, value):
        entry=copy.deepcopy(self.entry);entry[field]=value
        with self.assertRaises(ValueError): q.validate_entry(q.ROOT, entry)
    def test_valid_entry(self): self.assertTrue(q.validate_entry(q.ROOT, self.entry))
    def test_provenance_kind(self): self.rejects("provenance_kind","compiled")
    def test_unsafe_path(self): self.rejects("path","../outside.pdf")
    def test_unapproved_pdf(self): self.rejects("path","deliverables/drafts/v0.5.0-rc9/new.pdf")
    def test_wrong_hash(self): self.rejects("sha256","0"*64)
    def test_wrong_bytes(self): self.rejects("bytes",123)
    def test_wrong_pages(self): self.rejects("pages",300)
    def test_wrong_version(self): self.rejects("version","0.5.0")
    def test_wrong_variant(self): self.rejects("variant_kind","formal")
    def test_fake_commit(self): self.rejects("source_commit","a"*40)
    def test_missing_commit_marker(self):
        entry=copy.deepcopy(self.entry);entry.pop("source_commit")
        with self.assertRaises(ValueError): q.validate_entry(q.ROOT,entry)
    def test_fake_tree(self): self.rejects("source_tree","a"*40)
    def test_fake_run(self): self.rejects("workflow_run_id",1)
    def test_fake_artifact(self): self.rejects("artifact_id",1)
    def test_release_status(self): self.rejects("status","released")
    def test_release_grant(self): self.rejects("release_eligible",True)
    def test_wrong_provenance_record(self): self.rejects("provenance_record","reviews/other.json")
    def test_wrong_review_record(self): self.rejects("review_record","reviews/other.md")
    def test_record_hash_rejection(self):
        with patch.object(q,"RECORD_SHA","0"*64):
            with self.assertRaises(ValueError): q.validate_entry(q.ROOT,self.entry)
    def test_safe_path_no_parent(self):
        with self.assertRaises(ValueError):q.safe_file(q.ROOT,"../outside")
    def test_safe_path_no_absolute(self):
        with self.assertRaises(ValueError):q.safe_file(q.ROOT,"/etc/passwd")
    def test_missing_file(self):
        with self.assertRaises(ValueError):q.safe_file(q.ROOT,"missing")
    def test_whole_import(self):
        result=q.verify()
        self.assertEqual(result["imported_variants"],3)
        self.assertEqual(result["local_historical_visual_pages"],299)
        self.assertFalse(result["Q1_completed"])
        self.assertFalse(result["release_eligible"])
        self.assertFalse(result["remote_CI_executed"])
    def test_empty_fixture_no_import(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"deliverables").mkdir()
            (root/"deliverables/manifest.json").write_text('{"artifacts":[]}')
            self.assertEqual(q.verify(root)["status"],"not_imported")
    def test_record_without_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"deliverables").mkdir()
            (root/"deliverables/manifest.json").write_text('{"artifacts":[]}')
            record=root/q.RECORD;record.parent.mkdir(parents=True);record.write_text('{}')
            with self.assertRaises(ValueError):q.verify(root)

if __name__ == "__main__": unittest.main()
