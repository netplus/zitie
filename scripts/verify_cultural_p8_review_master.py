#!/usr/bin/env python3
"""P8: full-book PDF must not contain unreviewed child-facing pronunciations."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from cultural_p8_pinyin_audit import read_json,validate,QUEUE,CANDIDATES,ROOT
from cultural_source_audit import audit as audit_source
from verify_cultural_fullbook import verify as verify_pdf

def run(source:Path,manifest:Path,pdf:Path,proof:Path,
        queue:Path=QUEUE,candidates:Path=CANDIDATES,root:Path=ROOT):
    actual_source=audit_source(source,manifest)
    p8=validate(read_json(queue),actual_source,read_json(candidates),root)
    legacy=verify_pdf(source,manifest,pdf,proof,root)
    metadata=read_json(proof)
    if (metadata.get("strict_pinyin_review_mode") is not True or
        metadata.get("all_pronunciation_review_slots")!=1013 or
        metadata.get("reading_candidates_printed")!=0 or
        metadata.get("word_examples_readings_printed")!=0 or
        metadata.get("source_main_readings_printed")!=0 or
        metadata.get("actual_illustrations_printed")!=0 or
        metadata.get("unreviewed_artwork_omitted") is not True):
        raise ValueError("Strict editorial PDF cannot show unverified pinyin or rough artwork")
    if (legacy.get("original_source_vector_steps_pixel_compared")!=1045 or
        legacy.get("main_id_count")!=201 or
        legacy.get("a4_pdf_pages")!=260 or
        legacy.get("strict_pinyin_review_mode") is not True):
        raise ValueError("P8 audit must retain exactly all 1045 released stroke symbols")
    return {
       "result":"PASS_P8_ALL_1013_PENDING_PINYIN_BLOCKED_FROM_PDF_1045_SOURCE_STROKES_PRESERVED",
       "source_pdf_sha256":p8["frozen_original_pdf_sha256"],
       "new_draft_pdf_sha256":legacy["preview_pdf_sha256"],
       "total_pdf_pages":260,
       "main_glyphs":201,
       "related_terms_or_component_examples":812,
       "original_vector_stroke_tiles_pixel_checked":1045,
       "printable_main_pinyin":0,
       "printable_word_pinyin":0,
       "prior_candidate_pinyin_quarantined":804,
       "prior_unresolved_multireadings_quarantined":8,
       "substantive_secondary_conflicts":p8["secondary_frequent_char_reading_conflicts"],
       "copyrighted_artwork_prematurely_inserted":0,
       "formal_editorial_approval_count":0,
       "open_normative_and_human_double_review_cases":1013,
       "independent_source_and_page_QA":"passed_engineering_only",
       "manual_print_and_lexicon_review":"pending",
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("source","manifest","pdf","proof","output"):
        p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--queue",default=QUEUE,type=Path)
    p.add_argument("--candidates",default=CANDIDATES,type=Path)
    p.add_argument("--root",default=ROOT,type=Path)
    a=p.parse_args()
    report=run(a.source,a.manifest,a.pdf,a.proof,a.queue,a.candidates,a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
