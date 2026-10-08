#!/usr/bin/env python3
"""Negative tests for v0.5.1 punctuation-only release and font safety."""
import copy
import io
import unittest
import fitz
from fontTools.ttLib import TTFont
from pathlib import Path
from build_v051_punctuation import ROOT, SOURCE
from fix_uming_cjk_punctuation import patch_ttf, fonts_to_correct, ORIGINAL_BBOX, PUNCT
from verify_v051_punctuation import check_manifest_entry, EXPECTED_OUTLINES, EXPECTED_GLYPH_SUBSETS
import json

class V051Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=fitz.open(ROOT/SOURCE)
        cls.fonts=list(fonts_to_correct(cls.doc))
        cls.entry=json.loads((ROOT/'deliverables/manifest.json').read_text())['artifacts'][-1]

    @classmethod
    def tearDownClass(cls): cls.doc.close()

    def test_manifest_valid(self):check_manifest_entry(self.entry)

    def test_manifest_negative_fields(self):
        for key,bad in [('path','deliverables/releases/v0.5.0/bad.pdf'),('version','0.5.0'),
                        ('status','release_candidate'),('bytes',1234),('sha256','0'*64),
                        ('provenance_kind','pretend_source_generated'),('source_commit','a'*40),
                        ('previous_sha256','b'*64),('release_eligible',False)]:
            with self.subTest(field=key):
                v=copy.deepcopy(self.entry);v[key]=bad
                with self.assertRaises(ValueError):check_manifest_entry(v)

    def test_manifest_negative_gate(self):
        for name,value in [('layout','pending'),('physical_print_test_performed',True),
                           ('unresolved_conflicts',1),('terminal_fail_closed_disclosed',False)]:
            with self.subTest(gate=name):
                v=copy.deepcopy(self.entry);v['release_gate_snapshot'][name]=value
                with self.assertRaises(ValueError):check_manifest_entry(v)

    def test_unique_targets(self):
        self.assertEqual(len(self.fonts),18)
        from collections import Counter
        c=Counter(char for x,ff,gg in self.fonts for char,gid,dx,dy in gg)
        self.assertEqual(dict(c),EXPECTED_GLYPH_SUBSETS)
        self.assertTrue(all('UMingCN' in self.doc.extract_font(x)[0] for x,ff,gg in self.fonts))

    def test_glyph_binary_surgery_preserves_other_bytes(self):
        fx,ff,targets=self.fonts[0]
        src=self.doc.xref_stream(ff)
        for char,gid,dx,dy in targets:
            before=TTFont(io.BytesIO(src));old=before['glyf'][before.getGlyphOrder()[gid]]
            self.assertEqual((old.xMin,old.yMin,old.xMax,old.yMax),ORIGINAL_BBOX[char])
            output,b0,b1,changes=patch_ttf(src,gid,dx,dy)
            self.assertEqual(b1,EXPECTED_OUTLINES[char]);self.assertLessEqual(changes,24)
            self.assertEqual(len(output),len(src))
            self.assertEqual(before['head'].unitsPerEm,TTFont(io.BytesIO(output))['head'].unitsPerEm)
            src=output

    def test_no_layout_or_font_width_change(self):
        for fx,ff,targets in self.fonts[:3]:
            raw=self.doc.xref_stream(ff);old=TTFont(io.BytesIO(raw))
            for char,gid,dx,dy in targets:
                g=old.getGlyphOrder()[gid];before=old['hmtx'][g]
                patched,*_=patch_ttf(raw,gid,dx,dy)
                after=TTFont(io.BytesIO(patched))['hmtx'][g]
                self.assertEqual(before,after)
                raw=patched

if __name__=='__main__':unittest.main(verbosity=2)
