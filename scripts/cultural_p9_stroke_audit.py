#!/usr/bin/env python3
"""P9: independently cross-check frozen 201 main glyphs / 1045 stroke steps.

The 5-category sequence reference is a separately authored CC0 dataset, NOT
proof of GF0023 authoritative correctness. Full names, rendered pen geometry,
radical scope, consecutive folds and teaching hints require primary evidence.
"""
from __future__ import annotations
import argparse
import collections
import json
import re
from pathlib import Path

from cultural_source_audit import audit as source_audit

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
REGISTRY=ROOT/"data/cultural_edition/p9_201_original_stroke_crosscheck.json"
SOURCE=ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
MANIFEST=ROOT/"deliverables/manifest.json"
COARSE={"横":"1","提":"1","竖":"2","竖钩":"2","撇":"3","点":"4","捺":"4"}
NUMBERED=re.compile(r"^第([1-9]\d?)笔$")

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def category(name:str)->str:
    if NUMBERED.fullmatch(name): return "?"
    return COARSE.get(name,"5")

def audit_registry(data:dict,source:dict):
    if (data.get("schema_version")!=1 or
        data.get("document_kind")!="P9_SECONDARY_STROKE_CROSSCHECK_NOT_AUTHORITY_PROOF"
        or data.get("frozen_source_pdf_sha256")!=SOURCE_SHA or
        source.get("source_pdf_sha256")!=SOURCE_SHA or
        source.get("main_ids")!=201 or source.get("total_source_steps")!=1045):
        raise ValueError("P9 cannot change frozen source, identity or authority scope")
    refs=data.get("entries",[])
    if (len(refs)!=201 or
        {x["main_id"] for x in refs}!=set(range(1,202)) or
        len({x["character"] for x in refs})!=201):
        raise ValueError("Exactly 201 original main characters required")
    official={g["main_id"]:g for g in source["glyphs"]}
    stats=collections.Counter()
    warnings=[]
    queue=[]
    for item in refs:
        mid=item["main_id"];g=official[mid]
        if g["character"]!=item["character"] or len(item["source_step_records"])!=g["stroke_count"]:
            raise ValueError("P9 main identity or expected number of teaching steps changed")
        raw=item["source_step_records"]
        # Validate every upstream clip / actual PDF teaching-page label, not
        # a fabricated stroke sequence downloaded from a third-party font.
        for a,b in zip(raw,g["steps"]):
            if (a["index"]!=b["index"] or a["name"]!=b["name"] or
                a["source_pdf_page"]!=b["pdf_page"] or
                a["source_rect_pt"]!=b["rect_pt"] or
                a["source_kind"]!="immutable_v051_vector"):
                raise ValueError(f"Original step clip, type or order drifted: ID{mid:03d}")
        derived="".join(category(s["name"]) for s in g["steps"])
        ref=item["secondary_reference_five_type_code"]
        if (item["source_five_type_code_candidate"]!=derived
            or not re.fullmatch(r"[12345]+",ref)
            or len(ref)!=g["stroke_count"]
            or item["secondary_reference_stroke_count"]!=g["stroke_count"]):
            raise ValueError("Original-to-secondary coarse comparison has changed")
        unknown=sum(category(s["name"])=="?" for s in g["steps"])
        diffs=[] if unknown else [i+1 for i in range(len(ref)) if derived[i]!=ref[i]]
        if (item["generic_numbered_stroke_names"]!=unknown or
            item["differing_main_stroke_indexes"]!=diffs):
            raise ValueError("At-risk pen names or five-type conflicts were hidden")
        status=("blocked_generic_stroke_names" if unknown else
                "requires_five_type_discrepancy_adjudication" if diffs else
                "secondary_five_type_agrees_not_approved")
        if item["independent_reference_status"]!=status:
            raise ValueError("Cannot promote third-party stroke database to normative pass")
        if (item["definitive_GF0023_standard_sequence"] is not None or
            item["definitive_GF3002_standard_sequence"] is not None or
            item["independent_primary_standard_verification"] is not False or
            item["individual_stroke_names_verified"] is not False or
            item["drawn_geometry_verified"] is not False or
            item["pedagogical_hints_verified"] is not False or
            item["reviewer_a"] is not None or item["reviewer_b"] is not None or
            item["publication_eligible"] is not False):
            raise ValueError("No P9 character is approved without exact original norm and independent review")
        if bool(item["in_secondary_8105_character_list"])!=(
            item["normative_scope_status"]=="GF0023_SCOPE_POSSIBLE_NOT_YET_PRIMARY_VERIFIED"):
            raise ValueError("A rare component was silently classified GF0023-covered")
        stats["total_glyphs"]+=1;stats["source_strokes"]+=g["stroke_count"]
        stats["secondary_8105_in_scope"]+=int(item["in_secondary_8105_character_list"])
        stats["outside_secondary_8105"]+=int(not item["in_secondary_8105_character_list"])
        stats["missing_fine_names"]+=unknown
        stats["unresolved_label_glyphs"]+=int(unknown>0)
        stats["fully_named_glyphs"]+=int(unknown==0)
        stats["secondary_five_type_matches"]+=int(not unknown and not diffs)
        stats["secondary_five_type_disagreements"]+=int(bool(diffs))
        stats["coarse_incomplete"]+=int(bool(unknown))
        if g["tips_from_pdf"]:
            stats["source_prompt_sections_checked"]+=1
        if unknown or diffs or not item["in_secondary_8105_character_list"]:
            queue.append({
              "main_id":mid,"character":g["character"],
              "source_page":g["first_pdf_page"],
              "GF0023_scope_secondary":item["in_secondary_8105_character_list"],
              "source_steps":g["stroke_count"],
              "source_stroke_names":[s["name"] for s in g["steps"]],
              "unknown_stroke_names":unknown,
              "secondary_coarse_code":ref,
              "source_label_derived_code":derived,
              "coarse_differing_step_numbers":diffs,
              "source_pdf_tips":g["tips_from_pdf"],
              "normative_evidence_pdf_page":None,
              "first_review_signoff":None,"second_review_signoff":None,
              "status":"BLOCKED_PRIMARY_STANDARD_OR_HUMAN_VERIFICATION_REQUIRED",
            })
    if dict(data["summary"])!={
      "source_strokes":1045,"glyph_count":201,
      "GF0023_secondary_scope_count":164,
      "outside_8105_secondary_scope_count":37,
      "undifferentiated_stroke_labels":83,
      "unlabeled_characters":14,
      "fully_named_glyphs":187,
      "matching_five_type_records":186,
      "conflicting_five_type_records":1,
      "original_and_reference_count_disagreements":0,
      "original_and_reference_shape_missing":0}:
        raise ValueError("P9 secondary baseline stats differ from the frozen source")
    expected={
      "total_glyphs":201,"source_strokes":1045,
      "secondary_8105_in_scope":164,"outside_secondary_8105":37,
      "missing_fine_names":83,"unresolved_label_glyphs":14,
      "fully_named_glyphs":187,"secondary_five_type_matches":186,
      "secondary_five_type_disagreements":1,"coarse_incomplete":14,
      "source_prompt_sections_checked":201,
    }
    if dict(stats)!=expected:
        raise ValueError("P9 full-source verification drifted from independent reference baseline: "+str(stats))
    conflict=next(item for item in refs if item["main_id"]==54)
    if (conflict["character"]!="子" or conflict["source_five_type_code_candidate"]!="551"
        or conflict["secondary_reference_five_type_code"]!="521"
        or conflict["differing_main_stroke_indexes"]!=[2]
        or [step["name"] for step in conflict["source_step_records"]] !=["横撇","弯钩","横"]):
        raise ValueError("The 子 hook naming/classification discrepancy requires review")
    if len({row["main_id"] for row in queue})!=len(queue):
        raise ValueError("Repeated blocking row in P9 editorial queue")
    return {
      "result":"P9_FULL_201_1045_STROKE_SOURCE_AUDITED_INDEPENDENT_NORMATIVE_STILL_NOT_APPROVED",
      "original_pdf_sha256":SOURCE_SHA,
      "source_pdf_pages":299,
      "main_ids":201,
      "original_stroke_form_xobjects_total":1045,
      "recorded_fine_name_steps":962,
      "unknown_or_generic_fine_name_steps":83,
      "unknown_name_main_glyphs":14,
      "GF0023_in_scope_by_secondary_membership_only":164,
      "outside_8105_coverage_by_secondary_proxy":37,
      "all_source_and_secondary_stroke_counts_agree":True,
      "secondary_five_type_order_match_no_unknown":186,
      "secondary_five_type_conflict_requires_adjudication":1,
      "secondary_five_type_missing_named_steps":14,
      "source_pedagogical_tips_extracted":201,
      "flagged_for_immediate_review":queue,
      "strokes_independently_proved_correct_from_official_primary_GF_pdf":0,
      "human_double_approved_strokes":0,
      "separate_corrected_source_authorized":False,
      "original_pdf_modified":False,
      "note":"Source PDF consistency and secondary 1-5 shape-code agreement do not prove exact GF0023 stroke correctness. Official original page/evidence and second-reviewer signoff still required."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,default=SOURCE)
    ap.add_argument("--manifest",type=Path,default=MANIFEST)
    ap.add_argument("--registry",type=Path,default=REGISTRY)
    ap.add_argument("--output",type=Path,required=True)
    opt=ap.parse_args()
    result=audit_registry(load(opt.registry),source_audit(opt.source,opt.manifest))
    opt.output.parent.mkdir(parents=True,exist_ok=True)
    opt.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="flagged_for_immediate_review"},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
