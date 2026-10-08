#!/usr/bin/env python3
"""Candidate identity and freeze boundaries; negative tests do not grant QA."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from m3_candidate import CandidateEdition, validate_config, validate_metadata, validate_ready
from m3_model import ROOT, M3Edition
from verify_m3_archive import verify as verify_archive


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = json.loads((ROOT/'build/v0.5.0-rc1/generation.json').read_text())
        cls.config = json.loads((ROOT/'data/m3_candidate.json').read_text())
        cls.scope = json.loads((ROOT/'data/m3_scope.json').read_text())

    def reject(self, key, value):
        m = copy.deepcopy(self.meta); m[key] = value
        with self.assertRaises(ValueError): validate_metadata(m)

    def test_candidate_valid(self): self.assertTrue(validate_metadata(self.meta))
    def test_config_valid(self): self.assertTrue(validate_config(self.config))
    def test_ready(self): self.assertTrue(validate_ready(self.scope))
    def test_modes_separate(self): self.assertNotEqual(CandidateEdition().label, M3Edition().label)
    def test_wrong_version(self): self.reject('version', '0.5.0')
    def test_renamed_preview(self): self.reject('status', 'engineering_preview')
    def test_generated_not_frozen(self): self.reject('candidate_frozen', True)
    def test_no_publication(self): self.reject('release_eligible', True)
    def test_no_Q1(self): self.reject('Q1_completed', True)
    def test_dirty_source(self): self.reject('source_dirty', True)
    def test_exact_commit(self): self.reject('source_commit', 'main')
    def test_exact_tree(self): self.reject('source_tree', 'main')
    def test_path_traversal(self): self.reject('pdf', '../output.pdf')
    def test_wrong_config(self): self.reject('config_path', 'data/m3_book.json')
    def test_page_count(self): self.reject('pages', 288)
    def test_guide_count(self): self.reject('guide_pages', 3)
    def test_toc_count(self): self.reject('toc_pages', 2)
    def test_missing_bookmarks(self): self.reject('bookmarks', self.meta['bookmarks'][:-1])
    def test_missing_links(self): self.reject('toc_links', [])
    def test_font_hashes(self): self.reject('fonts', [])
    def test_environment(self): self.reject('environment', {'packages': {}})
    def test_missing_module(self): self.reject('missing_modules', ['whole_character_migration'])
    def test_inflated_main_count(self): self.reject('main_count', 207)
    def test_config_wrong_mode(self):
        c=copy.deepcopy(self.config);c['status']='engineering_preview'
        with self.assertRaises(ValueError):validate_config(c)
    def test_config_wrong_guidance(self):
        c=copy.deepcopy(self.config);c['guidance']='book/front-matter/m3-guidance.json'
        with self.assertRaises(ValueError):validate_config(c)
    def test_unimplemented_feature(self):
        s=copy.deepcopy(self.scope);s['work_packages'][2]['status']='in_progress'
        with self.assertRaises(ValueError):validate_ready(s)
    def test_unimplemented_case(self):
        s=copy.deepcopy(self.scope);s['migration_cases'][2]['status']='planned'
        with self.assertRaises(ValueError):validate_ready(s)
    def test_unsafe_input(self):
        m=copy.deepcopy(self.meta);m['input_sha256']['../outside']='0'*64
        with self.assertRaises(ValueError):validate_metadata(m)
    def test_undeclared_archive(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'data').mkdir();(r/'deliverables').mkdir()
            (r/'data/post_release.json').write_text(json.dumps({'candidate':None,'phases':[{}, {}, {'status':'in_progress'}]}))
            (r/'deliverables/manifest.json').write_text(json.dumps({'artifacts':[{'version':'0.5.0-rc1'}]}))
            with self.assertRaises(ValueError):verify_archive(r)
    def test_cannot_end_without_archive(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'data').mkdir();(r/'deliverables').mkdir()
            (r/'data/post_release.json').write_text(json.dumps({'candidate':None,'phases':[{}, {}, {'status':'completed'}]}))
            (r/'deliverables/manifest.json').write_text(json.dumps({'artifacts':[]}))
            with self.assertRaises(ValueError):verify_archive(r)


if __name__ == '__main__': unittest.main()
