#!/usr/bin/env python3
"""Reject mismatched print QA sample pages, scaling, or fabricated paper-test claims."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import fitz
from build_v051_print_qa import SOURCE, SOURCE_SHA256, SOURCE_PAGES, build

ROOT=Path(__file__).resolve().parents[1]
QA_REL=Path('qa/print/v0.5.1/v051-print-acceptance-samples-A4.pdf')
EVIDENCE_REL=Path('data/evidence/v051-print-qa-preflight-20261009.json')

def sha(raw):return hashlib.sha256(raw).hexdigest()

def verify(repo=ROOT):
    repo=Path(repo)
    evidence=json.loads((repo/EVIDENCE_REL).read_text(encoding='utf-8'))
    src=repo/SOURCE
    packet=repo/QA_REL
    assert sha(src.read_bytes())==SOURCE_SHA256
    assert sha(packet.read_bytes())==evidence['packet_sha256']
    assert evidence['source_sha256']==SOURCE_SHA256
    assert evidence['physical_print_test_performed'] is False
    assert evidence['source_pages']==list(SOURCE_PAGES)
    assert evidence['packet_pages']==11
    with tempfile.TemporaryDirectory(prefix='v051-print-qa-') as tmp:
        rebuilt=Path(tmp)/'samples.pdf'
        result=build(repo,rebuilt)
        assert result['sha256']==evidence['packet_sha256'], 'Print QA packet rebuild is not byte identical'
        old=fitz.open(src);a=fitz.open(packet);b=fitz.open(rebuilt)
        try:
            assert len(a)==len(b)==11
            assert all(abs(a[i].rect.width-old[n-1].rect.width)<.02 and abs(a[i].rect.height-old[n-1].rect.height)<.02 for i,n in enumerate(SOURCE_PAGES,1))
            assert all(abs(page.rect.width-595.2756)<.02 and abs(page.rect.height-841.8898)<.02 for page in a)
            for i,original in enumerate(SOURCE_PAGES,1):
                assert a[i].get_text()==old[original-1].get_text(), ('Text change on page',original)
                matrix=fitz.Matrix(1,1)
                ours=a[i].get_pixmap(matrix=matrix,alpha=False).samples
                theirs=old[original-1].get_pixmap(matrix=matrix,alpha=False).samples
                assert ours==theirs, ('Vector image changed on source page',original)
                assert ours==b[i].get_pixmap(matrix=matrix,alpha=False).samples
            assert '100 mm' in a[0].get_text()
            assert '尚未打印' in a[0].get_text()
        finally:old.close();a.close();b.close()
    return {'pages_checked':10,'calibration_mm':100,'sheet_pages':11,
            'sha256':evidence['packet_sha256'],'source_unchanged':True,
            'physical_print_test_performed':False,'result':'passed'}

class PrintQA(unittest.TestCase):
    def test_document(self):
        self.assertEqual(verify()['result'],'passed')
    def test_source_page_list_exact(self):
        self.assertEqual(SOURCE_PAGES,(1,2,6,34,263,264,265,284,292,299))
    def test_source_hash_format(self):
        self.assertEqual(len(SOURCE_SHA256),64)
    def test_no_source_overwrite(self):
        with self.assertRaises(ValueError):build(ROOT,ROOT/SOURCE)
    def test_invalid_source_fails(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);p=d/SOURCE;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'wrong')
            with self.assertRaises(ValueError):build(d,d/'out.pdf')

if __name__=='__main__':unittest.main(verbosity=2)
