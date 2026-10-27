#!/usr/bin/env python3
"""P9 primary-scope and missing-fine-pen-name review register: fail closed.

Every row is linked to the frozen P9 source-page and drawing crop, but none is
approved by code. Applicable primary standard rows must be checked by a person.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT/"data/cultural_edition/p9_normative_open_cases_37_83.json"
SECONDARY=ROOT/"data/cultural_edition/p9_201_original_stroke_crosscheck.json"
GF0023=ROOT/"data/cultural_edition/p9_GF0023_direct_primary_164.json"
SRC_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"

def read(path:Path): return json.loads(path.read_text(encoding="utf8"))

def verify(reg=None,secondary=None,gf=None)->dict:
    reg=reg if reg is not None else read(CASES)
    sec=secondary if secondary is not None else read(SECONDARY)
    gf=gf if gf is not None else read(GF0023)
    if (reg.get("document_kind")!="P9_SOURCE_LOCKED_37_83_AND_COARSE_CONFLICT_ACTIONABLE_REVIEW_CASES_NOT_APPROVAL"
        or reg.get("schema_version")!=1
        or reg.get("source_v051_sha256")!=SRC_SHA
        or reg.get("GF0023_full_original_sha256")!=gf.get("actual_official_GF0023_pdf_sha256")
        or reg.get("release_eligible") is not False
        or reg.get("first_reviewer") is not None
        or reg.get("independent_second_reviewer") is not None):
        raise ValueError("P9 primary-source table cannot auto-publish or use invented approvals")
    expected=sec["entries"]
    by_id={x["main_id"]:x for x in expected}
    if len(by_id)!=201 or len(expected)!=201 or sum(x["stroke_count"] for x in expected)!=1045:
        raise ValueError("Frozen P9 source identity count corrupted")
    official={x["main_id"]:x for x in gf["entries"]}
    if len(official)!=164 or len(reg["applicable_primary_standards"])!=3:
        raise ValueError("P9 GF0023 official 164 exact rows or applicable normative references lost")
    out=reg.get("out_of_scope_characters",[])
    unlabeled=reg.get("unknown_fine_name_steps",[])
    conflict=reg.get("fine_name_vs_official_coarse_conflicts",[])
    scope_ids={x["main_id"] for x in expected if not x["in_secondary_8105_character_list"]}
    if (len(scope_ids)!=37 or len(out)!=37 or len({x["main_id"] for x in out})!=37
        or {x["main_id"] for x in out}!=scope_ids
        or official.keys()!=by_id.keys()-scope_ids):
        raise ValueError("37 characters outside GF0023 do not exactly match frozen source")
    for row in out:
        old=by_id[row["main_id"]]
        if (row["character"]!=old["character"] or
            row["source_stroke_count"]!=old["stroke_count"] or
            row["secondary_five_category_reference"]!=old["secondary_reference_five_type_code"] or
            row["other_normative_primary_row_pdf_page"] is not None or
            row["first_reviewer"] is not None or row["second_reviewer"] is not None or
            row["status"]!="blocked_primary_normative_original_row_missing" or
            row["publication_eligible"] is not False):
            raise ValueError("An out-of-scope radical was falsely marked authoritative")
        steps=row["original_step_refs"]
        if len(steps)!=old["stroke_count"]:
            raise ValueError("An out-of-scope radical lost a source stroke")
        for a,b in zip(steps,old["source_step_records"]):
            if (a["step"]!=b["index"] or a["original_name"]!=b["name"] or
                a["source_pdf_page"]!=b["source_pdf_page"] or
                a["source_rect_pt"]!=b["source_rect_pt"]):
                raise ValueError("Old PDF original ink step rectangle changed")
    unknown={(r["main_id"],s["index"]): (r,s) for r in expected for s in r["source_step_records"]
             if s["name"].startswith("第") and s["name"].endswith("笔")}
    if (len(unknown)!=83 or len({mid for mid,i in unknown})!=14 or
        len(unlabeled)!=83 or
        {(r["main_id"],r["step_index"]) for r in unlabeled}!=set(unknown)):
        raise ValueError("83 missing name steps were omitted or duplicated")
    for row in unlabeled:
        old,step=unknown[(row["main_id"],row["step_index"])]
        if (row["character"]!=old["character"] or
            row["legacy_name"]!=step["name"] or
            row["source_pdf_page"]!=step["source_pdf_page"] or
            row["source_rect_pt"]!=step["source_rect_pt"] or
            row["source_five_code_digit"]!=old["secondary_reference_five_type_code"][step["index"]-1] or
            row["approved_fine_name"] is not None or
            row["primary_fine_shape_standard_page"] is not None or
            row["primary_textbook_page"] is not None or
            row["source_vector_contact_shape_examined"] is not False or
            row["first_reviewer"] is not None or row["second_reviewer"] is not None or
            row["status"]!="blocked_unidentified_fine_name" or
            row["publication_eligible"] is not False):
            raise ValueError("An unreviewed fine stroke-name field was misrepresented")
    if len(conflict)!=1:raise ValueError("The 子 second-pen critical risk is missing")
    row=conflict[0];old=by_id[54];digit=official[54]
    if (row["main_id"]!=54 or row["character"]!="子" or row["step_index"]!=2 or
        row["legacy_name"]!="弯钩" or row["legacy_five_type_by_old_names"]!="551"
        or row["official_GF0023_five_type_sequence"]!=digit["GF0023_official_five_type_code"] or
        row["official_GF0023_five_type_sequence"]!="521" or
        row["official_GF0023_primary_pdf_page"]!=digit["GF0023_original_pdf_page_1based"] or
        row["source_pdf_page"]!=old["source_step_records"][1]["source_pdf_page"] or
        row["source_rect_pt"]!=old["source_step_records"][1]["source_rect_pt"] or
        row["candidate_correction_for_first_review"]!="竖钩" or
        row["approved_new_label"] is not None or
        row["first_reviewer"] is not None or row["second_reviewer"] is not None or
        row["status"]!="blocked_pending_authoritative_geometry_and_two_human_reviews" or
        row["do_not_modify_issued_v051"] is not True or
        row["publication_eligible"] is not False):
        raise ValueError("子 stroke 2 source-label conflict requires authority and two humans")
    return {
        "result":"PASS_P9_37_SCOPE_83_UNNAMED_STEPS_1_DISPUTED_NAME_ALL_TRACEABLE_BUT_BLOCKED",
        "original_source_main_glyphs":201,"frozen_pen_steps":1045,
        "GF0023_direct_original_rows":164,"outside_8105_cases":37,
        "fine_stroke_names_missing":83,"affected_glyphs":14,
        "specific_name_vs_official_code_risks":1,"human_approved_corrections":0,
        "primary_GF3002_special_radical_rows_verified":0,
        "original_pdf_modified":False,"release_eligible":False,
    }

if __name__=="__main__":
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
