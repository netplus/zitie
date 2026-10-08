#!/usr/bin/env python3
"""Small regression suite for the fail-closed handoff loader; no network writes."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import import_q1_handoff as q

class LoaderTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(q.check_extension({'old':('100644','a')},{'old':('100644','a')}),{})
    def test_each_loader_extension(self):
        for p in q.EXTRAS:
            with self.subTest(path=p):
                self.assertEqual(q.check_extension({'old':('100644','a')},
                    {'old':('100644','a'),p:('100644','b')}),{p:('100644','b')})
    def test_changed_baseline_rejected(self):
        with self.assertRaises(ValueError):q.check_extension({'old':('100644','a')},{'old':('100644','b')})
    def test_removed_baseline_rejected(self):
        with self.assertRaises(ValueError):q.check_extension({'old':('100644','a')},{})
    def test_changed_mode_rejected(self):
        with self.assertRaises(ValueError):q.check_extension({'old':('100644','a')},{'old':('100755','a')})
    def test_unknown_extra_rejected(self):
        with self.assertRaises(ValueError):q.check_extension({}, {'unrelated':('100644','a')})
    def test_wrong_zip_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.zip';p.write_bytes(b'PK wrong data')
            with self.assertRaisesRegex(ValueError,'ZIP hash'):q.decode_handoff(p)
    def test_wrong_pdf_rejected_before_parser(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.pdf';p.write_bytes(b'%PDF-wrong data')
            with self.assertRaisesRegex(ValueError,'PDF bytes'):q.decode_handoff(p)
    def test_push_requires_apply_before_git(self):
        with patch.object(q,'run') as r:
            with self.assertRaisesRegex(ValueError,'requires --apply'):
                q.import_package(Path('.'),Path('none'),'test',False,True)
            r.assert_not_called()
    def test_no_main_write(self):
        with patch.object(q,'run',return_value=''):
            with self.assertRaisesRegex(ValueError,'non-main'):
                q.import_package(Path('.'),Path('none'),'main',True,False)
    def test_dirty_worktree_rejected(self):
        with patch.object(q,'run',side_effect=['', ' M README.md']):
            with self.assertRaisesRegex(ValueError,'not clean'):
                q.import_package(Path('.'),Path('none'),'test',False,False)
    def test_wrong_base_rejected(self):
        with patch.object(q,'run',side_effect=['', '', '0'*40]):
            with self.assertRaisesRegex(ValueError,'base tree'):
                q.import_package(Path('.'),Path('none'),'test',False,False)
    def test_digests_are_exact(self):
        for value in (q.PDF_SHA,q.ZIP_SHA,q.PATCH_SHA):
            self.assertRegex(value,r'^[0-9a-f]{64}$')
        for value in (q.BASE,q.BASE_TREE,q.RESULT_TREE):
            self.assertRegex(value,r'^[0-9a-f]{40}$')
    def test_payload_absent_fails(self):
        with self.assertRaises(OSError):q.decode_handoff(Path('/__not_a_real_handoff_file__'))

if __name__=='__main__':unittest.main()
