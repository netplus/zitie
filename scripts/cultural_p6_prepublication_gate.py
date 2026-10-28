#!/usr/bin/env python3
"""P6 unified fail-closed publication gate for the 201-glyph cultural book.

This command does NOT authorize a publication, issue an editorial signature, or
modify any PDF. It reconciles separate P8/P9/P10/P5 evidence and pinpoints every
remaining gate, including an explicit user P6 decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
P9_SHA="8178a8d7bdf5258625efa0b74e7b82c0146c24da802f006f2135f17705e7fd89"
DRAFT_VERSION="cultural-v0.10-eight-art-source-review-draft"
EXPECTED_DRAFT_SHA="fb2388fe0d5642b35fe3560ff5733c653335074cba9460003d5388d4f42a361f"
SOURCE="deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
P9="deliverables/drafts/cultural-v0.9-stroke-review/zitie-201-P9-normative-stroke-review-UNREVIEWED.pdf"
ART="data/cultural_edition/p10_study_inventory.json"
P8="data/cultural_edition/p8_all_1013_pinyin_review_queue.json"
P9_RISK="data/cultural_edition/p9_normative_open_cases_37_83.json"
P9_SOURCE="data/cultural_edition/p9_201_original_stroke_crosscheck.json"
MANIFEST="deliverables/manifest.json"
P6_SIGNOFF="data/cultural_edition/p6_release_human_signoffs.json"
ART_QA="deliverables/drafts/cultural-v0.10-eight-art-p9-risk-UNREVIEWED/all-1045-source-ink-qa.json"
PROOF="deliverables/drafts/cultural-v0.10-eight-art-p9-risk-UNREVIEWED/page-provenance.json"

def load(root:Path,relative:str):
    return json.loads((root/relative).read_text(encoding="utf8"))

def file_sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit_inputs(p8:dict,p9:dict,risk:dict,art:dict,manifest:dict,
                 proof:dict,art_qa:dict,signoffs:dict)->dict:
    if (p8.get("frozen_source_pdf_sha256")!=SOURCE_SHA
        or p8.get("edition_status")!="strict_review_queue_not_lexicographic_publication"
        or len(p8.get("entries",[]))!=1013):
        raise ValueError("P8 source-locked 1013-review queue missing or changed")
    p8_rows=p8["entries"]
    slots={r.get("review_slot") for r in p8_rows}
    if len(slots)!=1013 or None in slots:
        raise ValueError("Duplicate/missing pronunciation review slot")
    if any(r.get("print_eligible") is not False or
           r.get("publication_approved") is not False or
           r.get("reviewer_id") is not None or
           r.get("second_reviewer_id") is not None or
           r.get("review_state")!="primary_source_and_independent_review_required"
           for r in p8_rows):
        raise ValueError("Unapproved P8 sound/word was silently promoted")
    main_audio={};terms=Counter()
    for r in p8_rows:
        mid=r.get("main_id")
        if not isinstance(mid,int) or not 1<=mid<=201:
            raise ValueError("Invalid canonical P8 main ID")
        if r.get("kind")=="main_glyph":
            if r.get("review_slot")!=f"MAIN-{mid:03d}" or mid in main_audio:
                raise ValueError("Missing/duplicated P8 main character pronunciation")
            main_audio[mid]=r
        elif r.get("kind") in ("lexical_word","component_character_example"):
            if r.get("review_slot")!=f"TERM-{mid:03d}-{r.get('term_position')}":
                raise ValueError("P8 exact word pronunciation identity differs")
            terms[mid]+=1
        else:
            raise ValueError("Unexpected pronunciation audit kind")
    if len(main_audio)!=201 or sum(terms.values())!=812:
        raise ValueError("Full P8 201/812 coverage lost")

    if (p9.get("frozen_source_pdf_sha256")!=SOURCE_SHA or
        len(p9.get("entries",[]))!=201 or
        risk.get("source_v051_sha256")!=SOURCE_SHA or
        risk.get("release_eligible") is not False):
        raise ValueError("P9 201-character normative audit source changed")
    original_p9={r.get("main_id"):r for r in p9["entries"]}
    if len(original_p9)!=201 or set(original_p9)!=set(range(1,202)):
        raise ValueError("P9 canonical characters or IDs are missing")
    if (sum(r["stroke_count"] for r in original_p9.values())!=1045
        or sum(r["generic_numbered_stroke_names"] for r in original_p9.values())!=83):
        raise ValueError("P9 all-1045 source steps and 83 pending fine labels lost")
    if any(r.get("publication_eligible") is not False or
           r.get("individual_stroke_names_verified") is not False or
           r.get("drawn_geometry_verified") is not False or
           r.get("pedagogical_hints_verified") is not False or
           r.get("reviewer_a") is not None or r.get("reviewer_b") is not None
           for r in original_p9.values()):
        raise ValueError("Unverified P9 ink, fine pen names or tips were falsely signed")
    scope=risk.get("out_of_scope_characters",[])
    unknown=risk.get("unknown_fine_name_steps",[])
    conflicts=risk.get("fine_name_vs_official_coarse_conflicts",[])
    if (len(scope)!=37 or len({r["main_id"] for r in scope})!=37
        or len(unknown)!=83
        or len({(r["main_id"],r["step_index"]) for r in unknown})!=83
        or len(conflicts)!=1 or conflicts[0].get("main_id")!=54
        or conflicts[0].get("candidate_correction_for_first_review")!="弯钩"
        or conflicts[0].get("verified_ministry_teaching_fine_name")!="弯钩"
        or conflicts[0].get("prior_proposed_correction_now_refuted_by_published_pedagogical_examples")!="竖钩"
        or conflicts[0].get("approved_new_label") is not None):
        raise ValueError("P9 exception register missing 37/83/子 cases")
    if any(r.get("status")!="blocked_primary_normative_original_row_missing" or
           r.get("publication_eligible") is not False for r in scope):
        raise ValueError("Rare radical lacks actual verified GF3002 primary evidence")
    if any(r.get("status")!="blocked_unidentified_fine_name" or
           r.get("publication_eligible") is not False for r in unknown):
        raise ValueError("83 source stroke fine labels remain independently unverified")

    if (art.get("source_pdf_sha256")!=SOURCE_SHA or art.get("release_eligible") is not False
        or len(art.get("entries",[]))!=8):
        raise ValueError("P10 still has only eight individually authored studies")
    actual_art={r.get("main_id"):r for r in art["entries"]}
    if len(actual_art)!=8 or any(mid not in original_p9 for mid in actual_art):
        raise ValueError("Repeated/wrong P10 artwork source IDs")
    for mid,r in actual_art.items():
        if (r.get("character")!=original_p9[mid]["character"]
            or r.get("art_direction_status")!="unreviewed"
            or r.get("semantic_review_status")!="pending"
            or r.get("visual_human_first_review") is not None
            or r.get("visual_human_second_review") is not None
            or r.get("publication_eligible") is not False):
            raise ValueError("Unreviewed P10 artwork was incorrectly approved")
    if (art_qa.get("verified_source_original_stroke_tiles")!=1045
        or art_qa.get("all_pages_a4")!=260
        or art_qa.get("artist_studies_inserted")!=8
        or art_qa.get("disputed_child_facing_pen_name_quarantines")!=1
        or art_qa.get("publication_eligible") is not False):
        raise ValueError("Latest cultural source-locked art integration QA changed")
    if (proof.get("source_v051_pdf_sha256")!=SOURCE_SHA
        or proof.get("source_P9_pdf_sha256")!=P9_SHA
        or proof.get("output_pdf_sha256")!=EXPECTED_DRAFT_SHA
        or proof.get("P10_art_studies_integrated")!=8
        or proof.get("unillustrated_201_main_ids")!=193
        or proof.get("source_stroke_tiles_expected_untouched")!=1045
        or proof.get("disputed_stroke_tip_quarantines")!=1
        or proof.get("release_eligible") is not False):
        raise ValueError("P10 260-page draft provenance invalid")

    items=manifest.get("artifacts",[])
    matching=[x for x in items if x.get("version")==DRAFT_VERSION]
    if (len(matching)!=1
        or matching[0].get("sha256")!=EXPECTED_DRAFT_SHA
        or matching[0].get("pages")!=260
        or matching[0].get("status")!="draft"
        or matching[0].get("release_eligible") is not False
        or any(str(x.get("version","")).startswith("cultural-")
               and (x.get("status")!="draft" or x.get("release_eligible") is not False)
               for x in items)):
        raise ValueError("Candidate was silently released or its append-only manifest drifted")
    if (signoffs.get("schema_version")!=1
        or signoffs.get("document_kind")!="P6_PHYSICAL_PRINT_AND_USER_EXPLICIT_RELEASE_APPROVAL_REQUIRED"
        or signoffs.get("target_draft_sha256")!=EXPECTED_DRAFT_SHA
        or signoffs.get("target_pdf_pages")!=260
        or signoffs.get("physical_A4_color_and_grayscale_print_session") is not None
        or signoffs.get("printer_and_paper_record") is not None
        or signoffs.get("independent_print_reviewer") is not None
        or signoffs.get("parental_age_appropriateness_approval") is not None
        or signoffs.get("editorial_committee_approval") is not None
        or signoffs.get("explicit_user_P6_release_decision") is not None
        or signoffs.get("release_eligible") is not False):
        raise ValueError("Never forge a physical print or formal user P6 publication approval")

    rows=[]
    for mid in range(1,202):
        stroke=original_p9[mid]
        count=stroke["stroke_count"]
        if len(stroke["source_step_records"])!=count:
            raise ValueError("A canonical P9 step has been deleted")
        glyph=stroke["character"]
        rows.append({
            "main_id":mid,"character":glyph,
            "batch_id":stroke["batch_id"],
            "original_source_stroke_count":count,
            "original_step_provenance_present":True,
            "pinyin_main_review":"blocked_exact_headword_evidence_and_two_reviewers",
            "pinyin_word_or_component_examples_pending":terms[mid],
            "stroke_order_and_geometry_review":"blocked_normative_original_following_images_and_human_review",
            "specific_stroke_names_missing":stroke["generic_numbered_stroke_names"],
            "outside_GF0023_scope":not stroke["in_secondary_8105_character_list"],
            "stroke_label_conflict_pending":mid==54,
            "cultural_artwork_stage":(
                "unapproved_art_direction_study" if mid in actual_art
                else "undrawn_no_publishable_image"),
            "human_editors_two_reviewers_complete":False,
            "real_paper_print_approved":False,
            "publication_eligible":False,
        })
    if sum(r["pinyin_word_or_component_examples_pending"] for r in rows)!=812:
        raise ValueError("812 lexical review slots did not map to the 201 exact page IDs")
    return {
        "schema_version":1,
        "result":"P6_PUBLICATION_BLOCKED_INPUTS_TRACED_AND_RELEASE_CONDITIONS_NOT_SATISFIED",
        "source_formal_v051_sha256":SOURCE_SHA,
        "frozen_P9_draft_sha256":P9_SHA,
        "P10_archived_unreviewed_candidate_sha256":EXPECTED_DRAFT_SHA,
        "cultural_candidate_A4_pages":260,
        "original_main_glyphs":201,
        "original_vector_stroke_steps_pixel_QA_passed":1045,
        "related_term_reading_slots":812,
        "total_P8_pronunciation_slots_pending":1013,
        "P9_all_glyph_shapes_and_pedagogy_human_approved":0,
        "P9_original_normative_8105_scope_by_official_GF0023":164,
        "P9_out_of_GF0023_scope_require_other_authority":37,
        "P9_fine_stroke_labels_missing":83,
        "P9_zi_second_step_dispute_quarantined_in_candidate":True,
        "P9_zi_second_step_MOE_fine_name_evidence":"弯钩",
        "P9_zi_竖钩_candidate_retracted_from_current_review":True,
        "P10_individual_scene_studies_unapproved":8,
        "P10_professional_illustrations_undrawn":193,
        "P10_final_art_signoffs":0,
        "P5_real_paper_print_approval":False,
        "P6_explicit_user_publication_approval":False,
        "release_eligible":False,
        "blocking_groups":{
            "P8_word_and_glyph_pronunciations":1013,
            "P9_1045_stroke_geometry_and_tip_review":201,
            "P9_outside_GF0023_scope":37,
            "P9_fine_stroke_labels":83,
            "P10_unapproved_or_missing_illustrations":201,
            "P5_real_paper_and_accessibility_review":1,
            "P6_user_authorization":1,
        },
        "per_glyph_reviews":rows,
    }

def load_and_audit(root:Path=ROOT):
    root=Path(root)
    if file_sha(root/SOURCE)!=SOURCE_SHA or file_sha(root/P9)!=P9_SHA:
        raise ValueError("Historical 299-page release/P9 review PDF modified")
    inputs=[load(root,x) for x in (P8,P9_SOURCE,P9_RISK,ART,MANIFEST,PROOF,ART_QA,P6_SIGNOFF)]
    result=audit_inputs(*inputs)
    candidate=root/next(x["path"] for x in inputs[4]["artifacts"]
                        if x.get("version")==DRAFT_VERSION)
    if file_sha(candidate)!=EXPECTED_DRAFT_SHA:
        raise ValueError("Frozen P10.2 source draft bytes differ from immutable manifest")
    # Newer drafts are allowed ONLY when their page-level QA is itself frozen.
    # They never inherit expert approval merely because v0.10 passed earlier.
    final_versions=(
        "cultural-v0.11-two-pass-201-260-editorial-draft",
        "cultural-v0.11.1-two-pass-260-CJK-embedded-editorial-draft",
    )
    for index,final_version in enumerate(final_versions):
        newer=[x for x in inputs[4]["artifacts"] if x.get("version")==final_version]
        if len(newer)>1:
            raise ValueError("Duplicate two-pass 260-page archive entries")
        if not newer:
            continue
        entry=newer[0]
        candidate=root/entry["path"]
        if (entry.get("status")!="draft" or
            entry.get("release_eligible") is not False or
            entry.get("pages")!=260 or
            file_sha(candidate)!=entry.get("sha256")):
            raise ValueError("Two-pass 260-page manuscript must remain immutable and UNREVIEWED")
        folder=candidate.parent
        detail=load(root,(folder/"source-201-art-1045-ink-QA.json").relative_to(root).as_posix())
        p1=load(root,(folder/"phase1-114-tip-corrections-QA.json").relative_to(root).as_posix())
        if (detail.get("phase_two_pdf_sha256")!=entry["sha256"] or
            detail.get("A4_pages")!=260 or
            detail.get("original_201_glyphs")!=201 or
            detail.get("original_1045_stroke_tiles_pixel_identical")!=1045 or
            detail.get("pass1_false_normative_approval_claims_quarantined")!=114 or
            detail.get("pass2_novel_character_specific_storyboards")!=193 or
            detail.get("pass2_existing_author_svg_studies_unapproved")!=8 or
            detail.get("pass2_professional_illustrations_completed_and_approved")!=0 or
            detail.get("release_eligible") is not False or
            p1.get("output_draft_sha256")!=detail.get("phase_one_output_sha256") or
            p1.get("release_eligible") is not False):
            raise ValueError("Two-pass manuscript cannot be promoted without 201/1045/114/193 source QA")
        if index==1 and detail.get("portable_full_CJK_font_embedded") is not True:
            raise ValueError("Final v0.11.1 requires real embedded CJK fonts for cross-platform reading")
        result["latest_two_pass_fullbook_sha256"]=entry["sha256"]
        result["latest_two_pass_A4_pages"]=260
        result["latest_two_pass_character_specific_storyboard_slots"]=193
        result["latest_two_pass_author_svg_unapproved"]=8
        result["latest_two_pass_P6_release_eligible"]=False
        result["latest_two_pass_fully_embedded_CJK"]=index==1
    # v0.11.2 is a separate, source-reviewed correction of the previous
    # unfounded 子 fine-name "竖钩" suspicion. It is NOT a P6 approval.
    corrected_version="cultural-v0.11.2-MOE-zi-wangou-review-draft"
    corrected=[x for x in inputs[4]["artifacts"] if x.get("version")==corrected_version]
    if len(corrected)>1:
        raise ValueError("Duplicate source-backed 子 naming candidate")
    if corrected:
        entry=corrected[0]
        candidate=root/entry["path"]
        src_name="data/cultural_edition/p9_zi_wangou_primary_teaching_20261028.json"
        source=load(root,src_name)
        qa=load(root,(candidate.parent/"zi-MOE-PEP-1045-source-ink-QA.json").relative_to(root).as_posix())
        if (entry.get("status")!="draft"
            or entry.get("release_eligible") is not False
            or entry.get("pages")!=260
            or file_sha(candidate)!=entry.get("sha256")
            or entry.get("parent_draft_sha256")!="459e29ea0ae030453eaa20f5c4deff9a583f6a337aa532b11e83a74166c8b4f3"
            or source.get("subject",{}).get("reassessed_fine_name")!="弯钩"
            or source.get("release_eligible") is not False
            or qa.get("result")!="PASS_MINISTRY_PEP_ZI_WANGOU_FINE_NAME_RESTORED_260_PAGES_1045_INK_PIXEL_IDENTICAL"
            or qa.get("output_pdf_sha256")!=entry["sha256"]
            or qa.get("output_A4_pages")!=260
            or qa.get("old_pdf_1045_source_ink_tiles_pixel_identical")!=1045
            or qa.get("unmodified_complete_A4_pages_pixel_equal")!=259
            or qa.get("teacher_pedagogical_name_from_MOE")!="弯钩"
            or qa.get("prior_unfounded_竖钩_guess_retracted") is not True
            or qa.get("exact_201_1045_ink_geometry_human_double_review_complete") is not False
            or qa.get("37_special_radicals_not_yet_normatively_approved") is not True
            or qa.get("83_unknown_specific_pen_names_not_yet_approved") is not True
            or qa.get("release_eligible") is not False
            or qa.get("P6_user_release_approved") is not False):
            raise ValueError("P6: source-based 子 弯钩 re-evaluation must remain fully traced and unreleased")
        result["latest_primary_zi_name_corrected_draft_sha256"]=entry["sha256"]
        result["latest_zi_fine_name_MOE_pedagogical_example"]="弯钩"
        result["previous_zi_竖钩_guess_retracted"]=True
        result["P9_all_ink_geometry_normative_approval"]=False
    return result

def release_required(result:dict):
    if result.get("release_eligible") is not True:
        raise ValueError("P6 RELEASE BLOCKED: editorial double review, 193 paintings, print and user's explicit approval missing")
    raise ValueError("P6 requires a separately reviewed publish operation, never an implicit audit-side release")

def markdown(result:dict)->str:
    lines=[
       "# P6 文化识字全书出版阻断总账（独立可复算校对稿）",
       "",
       "> **不可发行。** 目前只有201字文化正文草稿、8张待审插画，以及原书1045步矢量来源一致性的工程检查。",
       "> 1013读音、201字原笔迹规范细部与提示、201张最终插画、实纸打印及用户P6签核均未获批。",
       "",
       "| 门禁 | 当前实测 | 放行要求 |",
       "|---|---:|---|",
       "| P8拼音及词义读法 | 0/1013审核 | 逐词精确原文来源/义项及独立双审 |",
       "| P9规范笔形/书写提示 | 0/201主字批准 | 1045步逐笔权威形态与规范正确性 |",
       "| GF0023外37特殊部件 | 0/37附适用原始规范 | 各自规范原表页码和实形核对 |",
       "| 83处欠具体笔名 | 0/83审核 | GF2001等细笔名和来源原图人工双审 |",
       "| P10专业主题插画 | 0/201正式批准 | 现仅8张未审SVG、193张尚缺 |",
       "| P5纸张实测/无障碍 | 0次已签核 | A4实纸彩灰验证、打印审阅签字 |",
       "| P6用户发布授权 | 未批准 | 独立明确批准后才可生成release |",
       "",
       "## 逐字验收入口",
       "",
       "| 源ID | 字 | 批次 | 原笔数 | 待读词音 | 欠细笔名 | 超出GF0023 | 插画 |",
       "|---|---|---|---:|---:|---:|---|---|",
    ]
    for x in result["per_glyph_reviews"]:
        lines.append(f"| {x['main_id']:03d} | {x['character']} | {x['batch_id']} | "
                     f"{x['original_source_stroke_count']} | {x['pinyin_word_or_component_examples_pending']} | "
                     f"{x['specific_stroke_names_missing']} | "
                     f"{'需另审' if x['outside_GF0023_scope'] else '范围内五码已核'} | "
                     f"{'方向稿待审' if x['cultural_artwork_stage']=='unapproved_art_direction_study' else '未绘'} |")
    lines+=["", "审稿结果：**BLOCKED**。所有声、笔形、图案、打印及P6审定不得由自动检查替代。", ""]
    return "\n".join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--require-release-ready",action="store_true")
    args=parser.parse_args()
    result=load_and_audit()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"P6-all-gates-201-review-matrix-BLOCKED.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (args.output_dir/"P6-all-gates-201-review-matrix-BLOCKED.md").write_text(
        markdown(result),encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k!="per_glyph_reviews"},ensure_ascii=False,indent=2))
    if args.require_release_ready:
        release_required(result)

if __name__=="__main__":
    main()
