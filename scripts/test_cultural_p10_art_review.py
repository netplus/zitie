#!/usr/bin/env python3
"""P10 regression tests: arbitrary status promotion and graphic source swaps fail."""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from cultural_p10_art_review import (
    ART_DIR, STUDIES, SHA, P9_SHA, audit_ledger, load_studies_inventory,
    check_print_scene, make_ledger, raster_scene, validate_svg,
)

class P10ArtworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=make_ledger()

    def test_all_201_distinct_and_fail_closed(self):
        result=audit_ledger(self.ledger)
        self.assertEqual(result["source_main_id_count"],201)
        self.assertEqual(result["reviewable_scene_studies"],len(STUDIES))
        self.assertEqual(result["undrawn_remaining"],201-len(STUDIES))
        self.assertEqual(self.ledger["immutable_v051_source_sha256"],SHA)
        self.assertEqual(self.ledger["unchanged_P9_draft_sha256"],P9_SHA)
        self.assertFalse(self.ledger["release_eligible"])

    def test_fake_approved_status_is_rejected(self):
        corrupted=copy.deepcopy(self.ledger)
        corrupted["entries"][38]["art_director_approval"]="editor-approved-by-machine"
        with self.assertRaises(ValueError):audit_ledger(corrupted)
        corrupted=copy.deepcopy(self.ledger)
        corrupted["entries"][76]["publication_eligible"]=True
        with self.assertRaises(ValueError):audit_ledger(corrupted)
        corrupted=copy.deepcopy(self.ledger)
        corrupted["professional_illustrations_approved"]=201
        with self.assertRaises(ValueError):audit_ledger(corrupted)

    def test_201_inventory_requires_unique_authored_scenes(self):
        self.assertEqual(set(load_studies_inventory()),set(STUDIES))
        self.assertGreaterEqual(len(STUDIES),4)

    def test_old_programmed_scenes_stay_blocked(self):
        self.assertEqual(
            {x["previous_P45_algorithmic_scene_role"] for x in self.ledger["entries"]},
            {"blocked_legacy_reference_only"})
        self.assertEqual({x["previous_P3_svg_role"] for x in self.ledger["entries"]},
                         {"blocked_legacy_reference_only"})

    def test_missing_image_must_not_be_reported_as_drawn(self):
        corrupted=copy.deepcopy(self.ledger)
        corrupted["entries"][0]["review_state"]="art_direction_study_not_approved"
        with self.assertRaises(ValueError):audit_ledger(corrupted)
        corrupted=copy.deepcopy(self.ledger)
        del corrupted["entries"][-1]
        with self.assertRaises(ValueError):audit_ledger(corrupted)

    def test_scene_swap_and_remote_code_are_rejected(self):
        _,scene,filename,_,motifs=STUDIES[77]
        raw=(ART_DIR/filename).read_bytes()
        self.assertGreaterEqual(validate_svg(raw,scene,motifs)["paths"],18)
        with self.assertRaises(ValueError):
            validate_svg(raw,STUDIES[39][1],motifs)
        with self.assertRaises(ValueError):
            validate_svg(raw.replace(b"<svg ",b'<svg onload="alert(1)" ',1),scene,motifs)
        with self.assertRaises(ValueError):
            validate_svg(raw.replace(b"</svg>",b'<script>alert(1)</script></svg>'),scene,motifs)
        with self.assertRaises(ValueError):
            validate_svg(raw.replace(b"#FAF7EF",b"url(https://example.org/track.png)",1),scene,motifs)

    def test_all_scenes_have_real_gray_preview(self):
        for _,scene,filename,_,motifs in STUDIES.values():
            raw=(ART_DIR/filename).read_bytes()
            self.assertGreaterEqual(validate_svg(raw,scene,motifs)["paths"],18)
            result=check_print_scene(raster_scene(ART_DIR/filename))
            self.assertGreater(result["gray_stddev"],14)
            self.assertLess(result["gray_dark_pixel_fraction"],.78)

if __name__=="__main__":
    unittest.main(verbosity=2)
