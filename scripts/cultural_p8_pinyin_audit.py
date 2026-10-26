#!/usr/bin/env python3
"""P8 phase-one independent pronunciation audit: 201 main IDs + 812 terms.

A source-PDF copied reading, a third-party frequent-reading cross-check, and
a third-party GF0025 word-list transcription are useful EVIDENCE LOCATIONS,
never a proof of correctness for a printed Mainland children's copybook.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path

from cultural_source_audit import audit as audit_pdf
from cultural_fullbook_model import ROOT, SHA, checked_drafts, make_plan

QUEUE=ROOT/"data/cultural_edition/p8_all_1013_pinyin_review_queue.json"
CANDIDATES=ROOT/"data/cultural_edition/v07_all_201_reading_candidates.json"
CURRENT_BOOK=ROOT/"deliverables/drafts/cultural-v0.7.1-visual-source-draft/all-glyph-page-provenance.json"
EXPECTED_SOURCES={
  "legacy_unreviewed_candidate":72,
  "HSK_transcription_exact_headword":351,
  "community_phrase_dictionary":72,
  "algorithmic_per_character_draft":309,
  "multiple_standard_readings":8,
}
COMMON_REQUIRED={
  "review_state":"primary_source_and_independent_review_required",
  "reviewer_id":None,"second_reviewer_id":None,"reviewed_on":None,
  "normative_source_title":None,"normative_source_link":None,
  "normative_page_or_locator":None,
  "publication_approved":False,"print_eligible":False,
}
def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(queue:dict,source_index:dict,candidates:dict,root:Path=ROOT):
    if (queue.get("schema_version")!=1 or
        queue.get("frozen_source_pdf_sha256")!=SHA or
        queue.get("edition_status")!="strict_review_queue_not_lexicographic_publication"):
        raise ValueError("P8 review queue cannot change original PDF or publication status")
    if (source_index.get("source_pdf_sha256")!=SHA or
        source_index.get("main_ids")!=201 or
        source_index.get("total_source_steps")!=1045):
        raise ValueError("Original 201/1045 source identity must be frozen")
    if (candidates.get("document_kind")!="201_glyph_reading_candidates_not_authoritative" or
        candidates.get("source_original_pdf_sha256")!=SHA or len(candidates.get("entries",[]))!=812):
        raise ValueError("Versioned 812 unreviewed candidates missing")
    all_rows=queue["entries"]
    if len(all_rows)!=1013 or len({x["review_slot"] for x in all_rows})!=1013:
        raise ValueError("1013 independently addressable review slots required")
    glyphs={x["main_id"]:x for x in source_index["glyphs"]}
    if set(glyphs)!=set(range(1,202)):
        raise ValueError("201 original main glyphs were truncated")
    main_slots={};word_slots={}
    for row in all_rows:
        for key,want in COMMON_REQUIRED.items():
            if row.get(key)!=want:
                raise ValueError(f"Unreviewed Pinyin {row['review_slot']} was silently approved or lost source")
        if row["kind"]=="main_glyph":
            mid=row["main_id"];src=glyphs.get(mid)
            if (not src or mid in main_slots or
                row["review_slot"]!=f"MAIN-{mid:03d}" or
                row["character"]!=src["character"] or
                row["candidate_from_frozen_source_pdf"]!=src["pinyin_from_pdf"] or
                row["legacy_page_number"]!=src["first_pdf_page"]):
                raise ValueError("Main glyph reading or identity differs from released original PDF")
            if row.get("normative_pinyin") is not None or row.get("exact_national_dictionary_entry") is not None:
                raise ValueError("Cannot invent a normative word/character reading")
            main_slots[mid]=row
        elif row["kind"] in ("lexical_word","component_character_example"):
            mid=row["main_id"];idx=row["term_position"]
            key=(mid,idx)
            if key in word_slots or row["review_slot"]!=f"TERM-{mid:03d}-{idx}":
                raise ValueError("Repeated or invalid term review identity")
            for field in ("word_sense_context","speech_form_pinyin","orthographic_word_pinyin",
                          "character_aligned_pinyin","normative_exact_headword"):
                if row.get(field) is not None:
                    raise ValueError("No inferred phonetics may be presented as approved national reference")
            word_slots[key]=row
        else:
            raise ValueError("Unsupported Pinyin review record type")
    if len(main_slots)!=201 or len(word_slots)!=812:
        raise ValueError("All 201 original readings and 812 word slots are required")
    manifests=checked_drafts(root)
    if set(manifests)!=set(range(1,202)):
        raise ValueError("Original 201 manuscripts missing")
    source_tiers=collections.Counter()
    unprinted_candidates=0
    primary_risks=collections.Counter()
    for r in candidates["entries"]:
        mid=r["main_id"];idx=r["word_index"];key=(mid,idx)
        manuscript=manifests[mid]
        if idx>=len(manuscript["terms"]):
            raise ValueError("A candidate word index points outside its cultural manuscript")
        row=word_slots.get(key)
        if (row is None or row["headword"]!=r["word"] or
            row["character"]!=manuscript["character"] or
            row["original_candidate_py"]!=r["pinyin_candidate"] or
            row["origin_source_class"]!=r["source_class"] or
            row["origin_source_id"]!=r["source_key"] or
            row["origin_entry_ids"]!=r["source_entry_ids"]):
            raise ValueError("One of 812 pronunciation records drifted from the original candidate")
        if r["pinyin_candidate"] is not None:
            unprinted_candidates+=1
        source_tiers[r["source_class"]]+=1
        for tag in row.get("reviews_required",[]):
            primary_risks[tag]+=1
        if r["source_class"]=="multiple_standard_readings" and (
           r["pinyin_candidate"] is not None or
           "multiple_readings_unresolved" not in row["reviews_required"]):
            raise ValueError("Ambiguous headword improperly assigned an unreviewed reading")
        if r["source_class"]=="algorithmic_per_character_draft" and (
           "unreliable_character_by_character_join" not in row["reviews_required"]):
            raise ValueError("Machine syllable joining risk was erased")
    if dict(source_tiers)!=EXPECTED_SOURCES:
        raise ValueError("Pronunciation provenance source counts changed without review")
    if unprinted_candidates!=804:
        raise ValueError("804 prior candidates + 8 blocked ambiguous readings expected")
    mismatches=[]
    for mid,row in main_slots.items():
        if "different_from_secondary_frequent_character_reading" in row["risks"]:
            mismatches.append({
              "main_id":mid,"character":row["character"],
              "original_pdf_reading":row["candidate_from_frozen_source_pdf"],
              "secondary_unofficial_most_common":row["external_frequent_reading_crosscheck"],
              "status":"needs_exact_headword_sense_and_authoritative_adjudication"})
    if {e["character"] for e in mismatches}!={"子","干","卜","长","斗","艮"}:
        raise ValueError("Known six cross-source reading differences were silently lost")
    if len(queue.get("normative_overview",[]))!=3:
        raise ValueError("Normative rule identification and headword evidence must remain separate")
    counts=queue["counts"]
    if (counts["review_slots_total"]!=1013 or
        counts["source_main_glyph_readings"]["source_pinyin_supplied"]!=158 or
        counts["source_main_glyph_readings"]["source_pinyin_absent"]!=43 or
        counts["source_main_glyph_readings"]["third_party_8105_not_covered"]!=37 or
        counts["source_main_glyph_readings"]["different_from_8105_frequent_reading"]!=6 or
        counts["publication_approved"]!=0):
        raise ValueError("Historical review baseline claims changed without evidence")
    return {
      "result":"P8_1013_EVIDENCE_SLOTS_AUDITED_ZERO_EDUCATIONAL_PUBLICATION_APPROVALS",
      "frozen_original_pdf_sha256":SHA,
      "main_glyph_reading_slots":201,
      "main_source_pdf_pinyin_values":158,
      "source_main_radicals_without_independent_pinyin":43,
      "all_word_or_component_slots":812,
      "machine_or_unapproved_pinyin_candidates_quarantined":804,
      "source_polyphonic_candidate_gaps":8,
      "secondary_frequent_char_reading_conflicts":mismatches,
      "unapproved_word_source_tiers":dict(source_tiers),
      "priority_risks":dict(primary_risks),
      "approved_word_readings":0,
      "approved_main_glyph_readings":0,
      "authoritative_printing_state":"BLOCKED_UNTIL_INDEPENDENT_PRIMARY_EVIDENCE_AND_TWO_REVIEWER_SIGNATURES",
      "phase_two_stroke_audit":"pending",
      "phase_three_professional_artwork":"pending",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--queue",type=Path,default=QUEUE)
    p.add_argument("--candidates",type=Path,default=CANDIDATES)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--output",type=Path,required=True)
    opts=p.parse_args()
    source=audit_pdf(opts.source,opts.manifest)
    report=validate(read_json(opts.queue),source,read_json(opts.candidates),opts.root)
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:value for key,value in report.items() if key!="priority_risks"},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
