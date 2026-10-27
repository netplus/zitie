#!/usr/bin/env python3
"""P8.1: fail-closed official-policy hierarchy for 1,013 pronunciation review slots.

1985 promulgated orthoepic table can be evidence when exact headword/sense
matches. 2016 consultation and 2018-2026 GB PLAN are not final replacements.
Neither orthography nor the 2026 national language law supplies headword sound.
"""
from __future__ import annotations
import copy
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"data/cultural_edition/p8_mainland_pronunciation_authority_20261027.json"
QUEUE=ROOT/"data/cultural_edition/p8_all_1013_pinyin_review_queue.json"
ORIGINAL="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
SOURCES={
    "putonghua_yidu_1985":(
        "published_effective_within_declared_scope",
        "promulgated_official_orthoepical_norm",
        "https://www.moe.gov.cn/jyb_sjzl/ziliao/A19/201001/W020190416497956176438.pdf",
        "only_when_exact_entry_and_sense_verified_with_page"),
    "putonghua_yidu_2016_consultation":(
        "DRAFT_NOT_PROMULGATED_AS_FINAL",
        "public_consultation_draft",
        "https://www.moe.gov.cn/jyb_xwfb/s248/201606/t20160606_248272.html",
        "never_as_promulgated_normative_final"),
    "orthoepic_gb_plan_20180782_T_360":(
        "IN_APPROVAL_NOT_YET_AN_ISSUED_FINAL_STANDARD_AS_OF_CHECK",
        "national_standard_plan_pending",
        "https://std.samr.gov.cn/gb/search/gbDetailed?id=E116673EAD45A3B7E05397BE0A0AC6BF",
        "never_until_a_published_standard_number_and_final_text_are_confirmed"),
    "GB_T_16159_2012":(
        "published_spelling_rule_not_word_sense_dictionary",
        "national_spelling_orthography_rule",
        "https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=5645BD8DB9D8D73053AD3A2397E15E74",
        "never_by_itself_for_any_single_headword"),
    "national_language_law_2026":(
        "in_force_not_an_1013_word_lexicon",
        "enacted_law_general_policy",
        "https://www.moe.gov.cn/jyb_xwfb/gzdt_gzdt/s5987/202512/t20251227_1424750.html",
        "never_by_itself_for_headword"),
}
PENDING_FIELDS={
    "review_state":"primary_source_and_independent_review_required",
    "reviewer_id":None,
    "second_reviewer_id":None,
    "reviewed_on":None,
    "normative_source_title":None,
    "normative_source_link":None,
    "normative_page_or_locator":None,
    "publication_approved":False,
    "print_eligible":False,
}

def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))

def audit(data:dict,queue:dict)->dict:
    if (
        data.get("schema_version")!=1
        or data.get("document_kind")!="P8_2026_MAINLAND_PRONUNCIATION_AUTHORITY_HIERARCHY_NOT_ANY_1013_ENTRY_SIGNOFF"
        or data.get("linked_book_source_sha256")!=ORIGINAL
        or data.get("verified_public_date")!="2026-10-27"
        or data.get("release_eligible") is not False
        or data.get("total_review_slots")!=1013
        or data.get("single_glyph_slots")!=201
        or data.get("word_and_component_example_slots")!=812
        or data.get("approved_lexical_pronunciations")!=0
        or data.get("human_first_reviewers_signed")!=0
        or data.get("independent_second_reviewers_signed")!=0
        or data.get("unapproved_2016_draft_readings_applied_to_child_pages")!=0
        or data.get("unapproved_new_gb_plan_readings_applied_to_child_pages")!=0
        or data.get("blocked_six_source_conflicts")!=["子","干","卜","长","斗","艮"]
    ):
        raise ValueError("P8 reference hierarchy cannot authorize unreviewed syllables")
    references=data.get("authorities")
    if not isinstance(references,list) or len(references)!=len(SOURCES):
        raise ValueError("All five independent roles of P8 norm/law sources required")
    seen=set()
    for a in references:
        identity=a.get("authority_id")
        if identity in seen or identity not in SOURCES:
            raise ValueError("Duplicate/unknown P8 official/draft authority class")
        seen.add(identity)
        status,kind,url,gate=SOURCES[identity]
        if (a.get("effective_status")!=status
            or a.get("document_class")!=kind
            or a.get("source_url")!=url
            or a.get("allow_as_exact_pronunciation_evidence")!=gate
            or a.get("publication_automatically_approved") is not False):
            raise ValueError("P8 evidence incorrectly promotes a draft, GB plan, spelling or law to approved word sound")
    if seen!=set(SOURCES):
        raise ValueError("Missing P8 standard role")
    if (queue.get("frozen_source_pdf_sha256")!=ORIGINAL
        or queue.get("edition_status")!="strict_review_queue_not_lexicographic_publication"
        or len(queue.get("entries",[]))!=1013
        or len({x.get("review_slot") for x in queue["entries"]})!=1013):
        raise ValueError("P8 original 1013 exact review slot contracts no longer hold")
    distribution=Counter()
    approved=0
    main=set()
    for row in queue["entries"]:
        for field,required in PENDING_FIELDS.items():
            if row.get(field)!=required:
                raise ValueError(f"P8 pronunciation slot {row.get('review_slot')} requires exact headword+sense source and two human reviewers")
        mid=row.get("main_id")
        if not isinstance(mid,int) or not 1<=mid<=201:
            raise ValueError("P8 review slot has incorrect original identity")
        if row.get("kind")=="main_glyph":
            if row.get("review_slot")!=f"MAIN-{mid:03d}" or mid in main:
                raise ValueError("Main glyph review identity duplicated")
            main.add(mid)
            distribution["main"]+=1
        elif row.get("kind") in ("lexical_word","component_character_example"):
            idx=row.get("term_position")
            if not isinstance(idx,int) or idx<0:
                raise ValueError("P8 lexical item has invalid source slot")
            if row.get("review_slot")!=f"TERM-{mid:03d}-{idx}":
                raise ValueError("P8 term identity changed")
            distribution["words"]+=1
        else:
            raise ValueError("Unknown P8 phonetic evidence kind")
        approved+=int(bool(row.get("publication_approved")))
    if (len(main),distribution["main"],distribution["words"],approved)!=(201,201,812,0):
        raise ValueError("P8 entire 1013 zero-approval matrix lost records")
    return {
        "result":"PASS_P8_OFFICIAL_1985_VS_2016_DRAFT_AND_UNPUBLISHED_GB_PLAN_ALL_1013_UNAPPROVED",
        "count_main_glyphs":201,
        "count_lexical_slots":812,
        "word_and_glyph_slots":1013,
        "official_1985_orthoepic_source_status":"valid_only_for_exact_listed_item_and_sense",
        "2016_consultation_is_still_draft":True,
        "20180782_T_360_is_still_not_promulgated_final_as_of_20261027":True,
        "latest_language_law_2026_applies_but_is_not_a_word_dictionary":True,
        "formally_approved_pronunciations":0,
        "pinyin_corrections_issued_by_this_audit":0,
        "release_eligible":False,
    }

def main()->None:
    report=audit(load(POLICY),load(QUEUE))
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
