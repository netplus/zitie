#!/usr/bin/env python3
"""P2 B01 education-source scope checks; never equate HSK listing with dictionary review."""
from __future__ import annotations
import json
import re
import unittest
from pathlib import Path
from urllib.parse import parse_qs,urlsplit

from cultural_b01_editorial_audit import ROOT

SOURCE=ROOT/"data/cultural_edition/p2_b01_mainland_education_evidence_20261025.json"
BRIEFS=ROOT/"data/cultural_edition/p2_b01_editorial_briefs_20261025.json"
EXPECTED={
    "土地":(8156,"tǔdì","四级","8150"),
    "土壤":(8159,"tǔrǎng","高等","8150"),
    "口水":(4787,"kǒushuǐ","高等","4780"),
}

def audit(doc,briefs):
    if (doc["schema_version"]!=1 or doc["release_eligible"] is not False
            or doc["jurisdiction"]!="Chinese mainland"):
        raise ValueError("Mainland teaching references never authorize publication")
    scope=doc["direct_hsk_word_rows"]
    if len(scope)!=3 or {r["word"] for r in scope}!=set(EXPECTED):
        raise ValueError("Exactly three B01 direct HSK educational rows expected")
    index={x["word"]:x for e in briefs["entries"] for x in e["terms"]}
    for row in scope:
        word=row["word"]; no,pinyin,level,offset=EXPECTED[word]
        if (row["number"],row["pinyin_orthographic"],row["level"])!=(no,pinyin,level):
            raise ValueError("HSK educational row evidence changed")
        path=urlsplit(row["source_url"])
        parsed=parse_qs(path.query)
        if (path.scheme!="https" or path.hostname!="admin.chinesetest.cn"
                or not path.path.endswith("standardsAction.do")
                or parsed.get("means")!=["getStandardWordsList"]
                or parsed.get("pager.offset")!=[offset]):
            raise ValueError("Cannot locate original HSK source rows")
        if (row["status"]!="mainland_exam_listing_verified_non_normative"
                or row["publication_approved"] is not False
                or row["reviewed_by"] is not None):
            raise ValueError("HSK educational reference is not a reviewed dictionary entry")
        token=index[word]
        if token["pronunciation_status"]!="review_pending" or token["source_url"] is not None:
            raise ValueError("P2 word must stay unapproved in candidate manuscript")
        if token["pinyin_display_candidate"].replace(" ","")!=pinyin:
            raise ValueError("HSK observed word form and manuscript candidate differ")
    yi=doc["yi_pinyin_policy"]
    if (yi["subject"]!="一" or yi["standard_character_reading"]!="yī"
            or yi["orthography_standard"]!="GB/T 16159-2012"
            or yi["orthography_exact_example"]!={"word":"第一","source":"dì-yī",
                   "section":"1.5.4 数词序数正词法",
                   "note":"Lexical orthography has hyphen; per-character learner pronunciation line is not identical to lexicographic whole-word spelling"}
            or yi["approved_for_children"] is not False or yi["reviewed_by"] is not None):
        raise ValueError("No yī sandhi or word formatting may be silently approved")
    if not yi["educational_source"].startswith("https://dxs.moe.gov.cn/"):
        raise ValueError("B01 '一' source note lost its traceable attribution")
    for token in next(x for x in briefs["entries"] if x["character"]=="一")["terms"]:
        if not token["reading_risk"].startswith("yi_"):
            raise ValueError("Original/surface sandhi risk must not be erased")
        if token["pronunciation_status"]!="review_pending":
            raise ValueError("No '一' surface-tone token may be auto-certified")
    return {"status":"NON_NORMATIVE_MAINLAND_EVIDENCE_ONLY",
            "direct_hsk_rows":3,"approved_mainland_dictionary_words":0,
            "approved_yi_sandhi_cards":0}

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.doc=json.loads(SOURCE.read_text(encoding="utf8"))
        self.briefs=json.loads(BRIEFS.read_text(encoding="utf8"))
    def test_checked_source_scope(self):
        self.assertEqual(audit(self.doc,self.briefs)["direct_hsk_rows"],3)
    def test_cannot_approve_HSK(self):
        self.doc["direct_hsk_word_rows"][0]["publication_approved"]=True
        with self.assertRaisesRegex(ValueError,"not a reviewed"):audit(self.doc,self.briefs)
    def test_silent_orthographic_hyphen_erasure_rejected(self):
        self.doc["yi_pinyin_policy"]["orthography_exact_example"]["source"]="dì yī"
        with self.assertRaisesRegex(ValueError,"formatting"):audit(self.doc,self.briefs)
    def test_candidate_phonetics_not_auto_reviewed(self):
        x=next(e for e in self.briefs["entries"] if e["character"]=="土")
        x["terms"][0]["pronunciation_status"]="reviewed"
        with self.assertRaisesRegex(ValueError,"stay unapproved"):audit(self.doc,self.briefs)

if __name__=="__main__":
    unittest.main(verbosity=2)
