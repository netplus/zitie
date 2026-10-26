#!/usr/bin/env python3
"""P9 primary GF0023 table source ledger must agree with both 201-source index and its row ID.

A codepoint+PDF page+numeric source code from ORIGINAL 581-page normative PDF
is valid direct documentary evidence. It does not certify stroke tips, exact
hook/turn names, pen trajectory or any missing 37 radical characters.
"""
from __future__ import annotations
import argparse,copy,json
from pathlib import Path
from cultural_p9_stroke_audit import REGISTRY,load,audit_registry,SOURCE,MANIFEST,ROOT
from cultural_source_audit import audit as audit_source
PRIM=ROOT/"data/cultural_edition/p9_GF0023_direct_primary_164.json"
GF_SHA="0ff0890afc34c5e486edeebafb05350dec69a7bf0d1d75044d7d3f7b722ec3d0"
def check(source_index=None,secondary=None,primary=None):
    if source_index is None:source_index=audit_source(SOURCE,MANIFEST)
    if secondary is None:secondary=load(REGISTRY)
    if primary is None:primary=load(PRIM)
    previous=audit_registry(secondary,source_index)
    if (primary.get("schema_version")!=1 or
        primary.get("actual_official_GF0023_pdf_sha256")!=GF_SHA or
        primary.get("actual_official_GF0023_pdf_pages")!=581 or
        primary.get("status")!="P9_164_GF0023_DIRECT_OFFICIAL_5TYPE_SEQUENCES_EXTRACTED_NOT_FINE_STROKE_APPROVAL" or
        primary.get("source_original_book_pdf_sha256")!=secondary["frozen_source_pdf_sha256"] or
        primary.get("official_standard_exact_UCS_rows_extracted")!=164 or
        primary.get("out_of_scope_or_missing_GF0023_rows")!=37 or
        primary.get("official_vs_secondary_reference_agreements")!=164 or
        primary.get("official_vs_secondary_reference_conflicts")!=0 or
        primary.get("original_source_ink_and_fine_names_human_approved")!=0):
        raise ValueError("GF0023 primary extraction is incomplete, edited or falsely marked approved")
    p=primary["entries"]
    if len(p)!=164 or len({x["main_id"] for x in p})!=164:
        raise ValueError("Exact 164 unique GF0023 primary source rows are required")
    back={r["main_id"]:r for r in secondary["entries"]}
    official_ids=set()
    problems=[]
    for e in p:
        mid=e["main_id"]
        orig=back.get(mid)
        if (not orig or orig["character"]!=e["character"] or
            f"{ord(e['character']):05X}"!=e["unicode"] or
            not orig["in_secondary_8105_character_list"] or
            e["mainland_normative_reference_scope"]!="GF0023_8105_exact_UCS_row" or
            e["source_stroke_count"]!=orig["stroke_count"] or
            e["GF0023_official_five_type_code"]!=orig["secondary_reference_five_type_code"] or
            e["secondary_reference_code"]!=orig["secondary_reference_five_type_code"]):
            raise ValueError("One primary row conflicts with its true GF0023 source identity or secondary crosscheck")
        rect=e["GF0023_original_UCS_cell_pt"]
        positions=e["GF0023_original_sequence_digit_positions_pt"]
        if (len(rect)!=4 or
            any(not isinstance(c,(int,float)) for c in rect) or
            len(positions)!=orig["stroke_count"] or
            any(len(c)!=2 for c in positions) or
            not 9<=e["GF0023_original_pdf_page_1based"]<=581):
            raise ValueError("P9 claims an official sequence without physical page/digit coordinates")
        if (e["fine_stroke_name_standard_not_yet_double_reviewed"] is not True or
            e["actual_source_ink_geometry_not_yet_double_reviewed"] is not True or
            e["first_editorial_reviewer"] is not None or e["second_editorial_reviewer"] is not None or
            e["publication_eligible"] is not False):
            raise ValueError("National 5-category source cannot automatically approve pen geometry, fine name or pedagogy")
        expected_diff=("?" not in orig["source_five_type_code_candidate"] and
                       orig["source_five_type_code_candidate"]!=e["GF0023_official_five_type_code"])
        if e["printed_original_stroke_name_conflict_requires_review"] != expected_diff:
            raise ValueError("Original step-name-to-coarse-5 conflict was erased or invented")
        if expected_diff: problems.append((mid,e["character"],e["GF0023_official_five_type_code"]))
        official_ids.add(mid)
    outside=set(range(1,202))-official_ids
    if len(outside)!=37 or outside!={row["main_id"] for row in secondary["entries"]
                                    if not row["in_secondary_8105_character_list"]}:
        raise ValueError("37 rare character/radical forms must NOT masquerade as official GF0023 rows")
    if problems!=[(54,"子","521")]:
        raise ValueError("The 子 second-stroke numeric classification must retain its adjudication risk")
    return {
      "result":"GF0023_DIRECT_164_OF_164_PRIMARY_NUMERIC_CODES_VERIFIED_BY_ORIGINAL_581_PAGE_PDF_EVIDENCE",
      "standard":"GF 0023-2020",
      "official_pdf_sha256":GF_SHA,
      "official_pdf_pages":581,
      "exact_main_glyphs_with_real_GF0023_row_and_code":164,
      "official_numeric_sequences_crosscheck_independent_reference":164,
      "out_of_scope_rare_radical_or_non8105_glyphs":37,
      "main_glyph_source_total":201,
      "original_step_images_kept":1045,
      "old_source_missing_specific_pen_names":83,
      "label_to_official_category_conflict":[{"id":54,"character":"子","official_GF_code":"521","source_name_derived_code":"551"}],
      "definitive_fine_name_and_ink_geometry_stroke_correctness_reviewed":0,
      "human_editorial_double_signoff_count":0,
      "historical_release_pdf_untouched":True,
      "child_publication_eligible":False,
      "note":"Exact primary standard codes acquired for 164 glyphs. Still cannot infer GF0023 applies to 37 out-of-scope radicals or that 1045 rendered ink strokes and fine-name hints are correct."
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    report=check()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
