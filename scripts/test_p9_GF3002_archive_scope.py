#!/usr/bin/env python3
"""GF3002 public archived excerpt cannot certify 37 primary stroke sequences."""
import json
import sys
from pathlib import Path

SHA="cb5cb74f108dafed41a3583bc8d33d8dd318d1a21d714923c0f1ced89443cf3e"

def assert_excerpt(report):
    rows=report.get("target_anchors",[])
    if (report.get("result")!="GF3002_ARCHIVE_IS_INCOMPLETE_EIGHT_PAGE_SCANNED_EXCERPT_NO_37_OFFICIAL_ROWS"
        or report.get("archive_copy_pdf_sha256")!=SHA
        or report.get("archive_copy_pdf_pages")!=8
        or report.get("archive_copy_bytes")!=6730497
        or report.get("rare_radical_targets")!=37
        or report.get("pages_with_nonempty_native_text")!=0
        or report.get("targets_with_word_level_UCS_anchors")!=0
        or report.get("source_is_only_eight_page_scanned_excerpt") is not True
        or report.get("archived_copy_has_complete_20902_row_table") is not False
        or report.get("claimed_identical_to_current_ministry_pdf") is not False
        or report.get("new_primary_37_stroke_sequence_approvals")!=0
        or report.get("approved_normative_stroke_shapes")!=0
        or report.get("release_eligible") is not False
        or len(rows)!=37 or any(r["matches"] for r in rows)):
        raise ValueError("A truncated 8-page GF3002 archive was falsely promoted to national normative row approval")
    return True

if __name__=="__main__":
    source=Path(sys.argv[1] if len(sys.argv)>1 else "build/p9-gf3002/qa/GF3002-original-PDF-source-structure-probe.json")
    data=json.loads(source.read_text(encoding="utf8"))
    assert_excerpt(data)
    print("PASS: archived GF3002 is only eight scanned pages with appendix omitted; all 37 out-of-scope source rows remain BLOCKED.")
