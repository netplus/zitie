#!/usr/bin/env python3
"""Regression checks for three terminal edits; no semantic certification."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from fontTools.pens.boundsPen import ControlBoundsPen
from fontTools.svgLib.path import parse_path
from apply_artwork import ROOT, OVERRIDES, apply_artwork

class ArtworkTests(unittest.TestCase):
    def raw(self, ch):
        return (ROOT / 'build/vectors' / f'{ord(ch):04X}.json').read_bytes()

    def custom(self, value):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        p = Path(temp.name) / 'overrides.json'; p.write_text(json.dumps(value), encoding='utf-8'); return p

    def test_exact_target_set(self):
        entries = json.loads(OVERRIDES.read_text())['entries']
        self.assertEqual({(e['character'], e['stroke_index']) for e in entries}, {('日',1),('目',1),('田',1)})

    def test_only_selected_strokes_change(self):
        for ch in '日目田':
            with self.subTest(ch=ch):
                raw = self.raw(ch); old = json.loads(raw); new, audit = apply_artwork(ch, raw)
                self.assertEqual(len(old['strokes']), len(new['strokes']))
                self.assertEqual([i for i,(a,b) in enumerate(zip(old['strokes'], new['strokes'])) if a != b], [1])
                self.assertEqual(audit['modified_stroke_indices'], [1])
                self.assertEqual(audit['source_sha256'], hashlib.sha256(raw).hexdigest())

    def test_true_hook_and_other_characters_unchanged(self):
        for ch in '月水手毛一十人八大工土口山巾火木牛':
            with self.subTest(ch=ch):
                raw=self.raw(ch);new,audit=apply_artwork(ch,raw)
                self.assertEqual(new,json.loads(raw));self.assertEqual(audit['modified_stroke_indices'],[])

    def test_paths_and_median_endpoints(self):
        for ch in '日目田':
            data,_=apply_artwork(ch,self.raw(ch));pen=ControlBoundsPen(None)
            parse_path(data['strokes'][1],pen)
            self.assertIsNotNone(pen.bounds)
            a,b,c,d=pen.bounds;x,y=data['medians'][1][-1]
            self.assertTrue(a <= x <= c and b <= y <= d)

    def test_source_hash_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'source hash'):
            apply_artwork('日',self.raw('日')+b' ')

    def test_old_stroke_hash_mismatch_rejected(self):
        value=json.loads(OVERRIDES.read_text());value['entries'][0]['source_stroke_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'original stroke hash'):
            apply_artwork('日',self.raw('日'),self.custom(value))

    def test_duplicate_edit_rejected(self):
        value=json.loads(OVERRIDES.read_text());value['entries'].append(value['entries'][0])
        with self.assertRaisesRegex(ValueError,'duplicate'):
            apply_artwork('日',self.raw('日'),self.custom(value))

    def test_index_range_rejected(self):
        value=json.loads(OVERRIDES.read_text());value['entries'][0]['stroke_index']=10
        with self.assertRaisesRegex(ValueError,'invalid stroke index'):
            apply_artwork('日',self.raw('日'),self.custom(value))

    def test_unclosed_path_rejected(self):
        value=json.loads(OVERRIDES.read_text());value['entries'][0]['replacement_path']='M 1 1 L 2 2'
        with self.assertRaisesRegex(ValueError,'closed SVG'):
            apply_artwork('日',self.raw('日'),self.custom(value))

    def test_source_files_are_not_rewritten(self):
        before={ch:self.raw(ch) for ch in '日目田月'}
        for ch,raw in before.items():apply_artwork(ch,raw)
        self.assertEqual(before,{ch:self.raw(ch) for ch in before})

if __name__=='__main__':unittest.main()
