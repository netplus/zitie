#!/usr/bin/env python3
"""Negative tests for archiving; do not assert calligraphy correctness."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from verify_deliverables import ROOT,verify
class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'deliverables',self.root/'deliverables')
        shutil.copytree(ROOT/'reviews',self.root/'reviews')
        self.path=self.root/'deliverables/manifest.json';self.data=json.loads(self.path.read_text())
    def tearDown(self):self.temp.cleanup()
    def save(self):self.path.write_text(json.dumps(self.data),encoding='utf-8')
    def reject(self):
        self.save()
        with self.assertRaises((ValueError,FileNotFoundError)):verify(self.root)
    def test_valid(self):self.assertGreaterEqual(verify(self.root)['registered_pdfs'],3)
    def test_hash(self):self.data['artifacts'][0]['sha256']='0'*64;self.reject()
    def test_pages(self):self.data['artifacts'][0]['pages']+=1;self.reject()
    def test_bytes(self):self.data['artifacts'][0]['bytes']+=1;self.reject()
    def test_duplicate(self):self.data['artifacts'].append(copy.deepcopy(self.data['artifacts'][0]));self.reject()
    def test_traversal(self):self.data['artifacts'][0]['path']='../outside.pdf';self.reject()
    def test_missing_review(self):self.data['artifacts'][0]['review_record']='reviews/missing.md';self.reject()
    def test_promotion(self):self.data['artifacts'][0]['release_eligible']=True;self.reject()
    def test_unaudited_release(self):self.data['artifacts'][0]['status']='released';self.reject()
    def test_candidate_cannot_be_release_eligible(self):
        item=next(x for x in self.data['artifacts'] if x.get('status')=='release_candidate')
        item['release_eligible']=True
        self.reject()
    def test_candidate_requires_rc_version(self):
        item=next(x for x in self.data['artifacts'] if x.get('status')=='release_candidate')
        item['version']='0.4.0'
        self.reject()
    def test_unregistered(self):self.data['artifacts'].pop();self.reject()
    def test_corrupt(self):
        (self.root/self.data['artifacts'][0]['path']).write_bytes(b'not a pdf');self.reject()
if __name__=='__main__':unittest.main()
