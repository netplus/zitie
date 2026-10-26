#!/usr/bin/env python3
"""P9 full-book 201 source glyph, 1045 pen images and normative-review audit."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import fitz

from cultural_p9_stroke_audit import REGISTRY, load, audit_registry
from cultural_p9_primary_gf0023_audit import check as check_GF0023_primary
from cultural_source_audit import audit as audit_pdf
from verify_cultural_p8_review_master import run as audit_P8

def verify(source,manifest,pdf,proof,registry=REGISTRY):
    p8=audit_P8(source,manifest,pdf,proof)
    source_index=audit_pdf(source,manifest)
    norm=audit_registry(load(registry),source_index)
    gf0023=check_GF0023_primary(source_index=source_index,secondary=load(registry))
    page_map=json.loads(Path(proof).read_text(encoding="utf-8"))
    if (page_map.get("strict_P9_normative_stroke_review_mode") is not True
        or page_map.get("GF0023_direct_primary_201_rows_verified")!=164
        or page_map.get("GF0023_complete_fine_name_and_ink_review_approved")!=0
        or page_map.get("P9_fine_stroke_names_generic_count")!=83
        or page_map.get("P9_secondary_code_consistent_glyphs")!=186
        or page_map.get("P9_secondary_code_discrepancy_glyphs")!=1
        or page_map.get("P9_beyond_8105_secondary_scope")!=37
        or page_map.get("P9_no_normatively_approved_stroke_sequence") is not True):
        raise ValueError("No P9 page may imply GF normative double-review signoff")
    source_rows={r["main_id"]:r for r in norm["flagged_for_immediate_review"]}
    records=page_map["page_map"]
    hidden_generic=0
    statuses=0
    with fitz.open(pdf) as book:
        if len(book)!=260:raise ValueError("P9 must retain original 260-page A4 paging")
        for rec in records:
            physical=book[rec["preview_pdf_page"]-1]
            text=physical.get_text()
            if rec["part"]==1:
                statuses+=1
                if (rec["P9_normative_review_status"] is None or
                    rec["artwork_status"]!="P9_fullbook_stroke_normative_review_pending" or
                    "独立笔顺复核" not in text or
                    "尚未完成权威源及独立二审" not in text or
                    "原PDF笔顺提示·未获规范批准" not in text):
                    raise ValueError(f"Page {rec['preview_pdf_page']} falsely implies fully approved stroke order")
                expected=source_rows.get(rec["main_id"])
                if expected is not None and expected["unknown_stroke_names"]:
                    if rec["P9_generic_stroke_labels"]!=expected["unknown_stroke_names"]:
                        raise ValueError("High-risk generic pen names were erased")
            else:
                if "原书逐笔累计源图（只用于规范对照）" not in text:
                    raise ValueError("P9 continuation page lost standard-not-yet-approved warning")
            for step in rec["source_steps"]:
                if step["name"].startswith("第") and step["name"].endswith("笔"):
                    tile=fitz.Rect(step["preview_rect_pt"])
                    clip=fitz.Rect(tile.x0-20,max(0,tile.y0-24),tile.x1+20,tile.y0+13)
                    label=physical.get_text(clip=clip)
                    if "笔形待核" not in label:
                        raise ValueError(f"ID{rec['main_id']:03d} printed a generic 第N笔 instead of pending marker")
                    hidden_generic+=1
    if hidden_generic!=83 or statuses!=201:
        raise ValueError("All 201 standard status headings and 83 missing pen-name warnings required")
    return {
      "result":"PASS_P9_201_STROKE_SOURCE_PAGES_AND_83_PLACEHOLDER_PEN_NAMES_QUARANTINED",
      "pdf_sha256":page_map["output_pdf_sha256"],
      "pdf_pages":260,
      "source_main_glyphs":201,
      "source_strokes_from_immutable_v051_pixel_compared":1045,
      "generic_stroke_labels_masked_but_not_auto_corrected":hidden_generic,
      "all_main_glyph_status_cards":statuses,
      "GF0023_normative_8105_scope_secondary":norm["GF0023_in_scope_by_secondary_membership_only"],
      "GF0023_official_original_pdf_sha256":gf0023["official_pdf_sha256"],
      "GF0023_direct_164_UCS_numeric_rows":gf0023["exact_main_glyphs_with_real_GF0023_row_and_code"],
      "GF0023_primary_and_secondary_code_agreements":gf0023["official_numeric_sequences_crosscheck_independent_reference"],
      "outside_8105_scope":norm["outside_8105_coverage_by_secondary_proxy"],
      "third_party_five_type_consistent_glyphs":norm["secondary_five_type_order_match_no_unknown"],
      "coarse_shape_conflict_pending":norm["secondary_five_type_conflict_requires_adjudication"],
      "strokes_exactly_confirmed_by_direct_official_row_and_human_second_review":0,
      "unreviewed_Pinyin_printed":0,
      "withdrawn_algorithmic_artwork_printed":0,
      "next_corrections":"Generate independent new source only after exact GF0023/GF3002 primary and expert first/second review",
      "parent_p8_status":p8["result"]
    }

def main():
    p=argparse.ArgumentParser()
    for x in ("source","manifest","pdf","proof","output"):
        p.add_argument("--"+x,required=True,type=Path)
    p.add_argument("--registry",type=Path,default=REGISTRY)
    o=p.parse_args()
    result=verify(o.source,o.manifest,o.pdf,o.proof,o.registry)
    o.output.parent.mkdir(parents=True,exist_ok=True)
    o.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
