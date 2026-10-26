#!/usr/bin/env python3
"""Original 197-image scene engine scope, safety and repeatability tests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from cultural_fullbook_model import ROOT,checked_drafts
from cultural_v07_scenes import ICONS,generate_all,make_svg,select_motifs

class VectorSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.drafts=checked_drafts(ROOT)

    def test_complete_201_content_and_unique_phrases(self):
        self.assertEqual(len(self.drafts),201)
        self.assertEqual(len(set(v["theme_key"] for v in self.drafts.values())),201)
        self.assertEqual(len(set(v["sentence"] for v in self.drafts.values())),201)

    def test_exactly_197_new_actual_svg_artworks(self):
        rows=[{"main_id":i,"character":v["character"],
               "manuscript":v} for i,v in sorted(self.drafts.items())]
        with tempfile.TemporaryDirectory() as path:
            objects=generate_all(rows,path)
            self.assertEqual(len(objects),197)
            self.assertEqual(len(set(x["main_id"] for x in objects)),197)
            self.assertEqual(len(set(x["artwork_sha256"] for x in objects)),197)
            self.assertEqual(len({x["theme_key"] for x in objects}),197)
            motif_count=0
            for obj in objects:
                self.assertFalse(obj["professional_art_approval"])
                self.assertEqual(obj["license_review"],"internal_originality_and_visual_review_pending")
                self.assertEqual(len(obj["motif_icons"]),3)
                self.assertEqual(len(set(obj["motif_icons"])),3)
                raw=(Path(path)/obj["file"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),obj["artwork_sha256"])
                self.assertNotIn(b"<image",raw)
                self.assertNotIn(b"<script",raw)
                self.assertNotIn(b"<text",raw)
                self.assertNotIn(b"href=",raw)
                root=ET.fromstring(raw)
                self.assertEqual(root.attrib["data-scene"],
                                 f"culture-{obj['main_id']:03d}-{obj['theme_key']}")
                self.assertTrue(len(root.findall(".//{http://www.w3.org/2000/svg}path"))>=3)
                motif_count+=len(obj["motif_icons"])
            self.assertEqual(motif_count,591)

    def test_deterministic_svg_of_distinct_glyphs(self):
        for k in (1,32,39,77,95,131,170,200,201):
            e=self.drafts[k]
            if e["artwork_stage"]=="four_unique_svg_drafts_not_approved":
                continue
            raw,motif=make_svg(k,e["character"],e["theme_key"],e["art_brief"])
            again,_=make_svg(k,e["character"],e["theme_key"],e["art_brief"])
            self.assertEqual(raw,again)
            self.assertEqual(len(set(motif)),3)

    def test_semantic_render_keywords(self):
        for desc,expected in [
            ("林间梅花鹿斑纹与枝叶缝隙","deer"),
            ("草丛中抱着谷穗的小田鼠","mouse"),
            ("池石上的小龟与背甲纹","turtle"),
            ("草叶上的甲虫与放大镜","bug"),
            ("金色麦穗与田边小路","wheat"),
            ("古代陶酒器与装饰纹样","pot")
        ]:
            self.assertIn(expected,select_motifs(desc,173))

if __name__=="__main__":
    unittest.main(verbosity=2)
