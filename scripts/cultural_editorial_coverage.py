#!/usr/bin/env python3
"""201-glyph editorial coverage and Mainland exam pronunciation corroboration.

No publication approval is inferred from the original 201 glyphs, HSK entries,
Taiwan dictionaries or automatically generated editorial inventory.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit,parse_qs

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/cultural_edition'
SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
PARTS=("B01-B07","B08-B14","B15-B21")
SAMPLES={39:"P1",64:"P1",77:"P1",88:"P1",106:"P4",200:"P4",201:"P4"}
ART_CHARACTERS={"水","山","月","木"}
HSK_ENTRIES={"月亮":(10057,"yuèliang"),"水果":(7543,"shuǐguǒ")}

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def nfc(s):
    return unicodedata.normalize("NFC",s).replace(" ","")

def audit(root=ROOT):
    root=Path(root)
    base=root/"data/cultural_edition"
    all_entries=[]
    for index,part in enumerate(PARTS):
        doc=load(base/"inventory"/(part+".json"))
        if doc.get("schema_version")!=1 or doc.get("scope")!="cultural_editorial_inventory":
            raise ValueError("Invalid editorial part schema")
        if doc.get("part")!=part or doc.get("review_state")!="unreviewed_progress_ledger_only":
            raise ValueError("Incorrect review phase or batch part: "+part)
        if doc.get("original_pdf_sha256")!=SHA:
            raise ValueError("Original PDF source checksum field changed")
        allowed=[f"B{j:02d}" for j in range(index*7+1,index*7+8)]
        batches=Counter(e["batch_id"] for e in doc["entries"])
        if sorted(batches)!=allowed:
            raise ValueError("Editorial chunk omitted or duplicated a batch")
        if any(batches[b]!=(1 if b=="B21" else 10) for b in allowed):
            raise ValueError("Incorrect number of source glyphs in "+part)
        all_entries.extend(doc["entries"])
    if len(all_entries)!=201:
        raise ValueError("201 editorial rows required")
    by_id={}
    for item in all_entries:
        mid=item["main_id"]
        if mid in by_id or not isinstance(mid,int) or not 1<=mid<=201:
            raise ValueError("Duplicate or invalid main ID")
        by_id[mid]=item
    if sorted(by_id)!=list(range(1,202)):
        raise ValueError("Original main-glyph coverage incomplete")
    if len({item["character"] for item in all_entries})!=201:
        raise ValueError("Main-glyph characters repeated")

    # Cross-check actual existing B01-B21 files rather than trusting 201-row ledger.
    candidate_pinyin_count=0
    for number in range(1,22):
        bid=f"B{number:02d}"
        batch=load(root/"data"/(bid+".json"))
        assert batch["batch_id"]==bid
        for row in batch["entries"]:
            i=by_id[row["main_id"]]
            if i["character"]!=row["character"] or i["batch_id"]!=bid:
                raise ValueError("Inventory disagrees with frozen original "+bid)
            candidate=row.get("pinyin") or None
            if i["original_data_candidate_pinyin"]!=candidate:
                raise ValueError("Unjustified pinyin change: "+i["character"])
            if candidate: candidate_pinyin_count+=1

    content=load(base/"first_batch_draft.json")["entries"]
    complex_=load(base/"p4_multipage_prototypes.json")["entries"]
    samples={x["main_id"]:"P1" for x in content}
    samples.update({x["main_id"]:"P4" for x in complex_})
    if samples!=SAMPLES:
        raise ValueError("Editorial sample scope changed; recount it first")
    art=load(base/"p3_artwork_draft_registry.json")
    if {x["main_character"] for x in art["entries"]}!=ART_CHARACTERS:
        raise ValueError("The four artwork candidates are not the approved sample scope")
    coverage=Counter()
    for mid,item in by_id.items():
        expected=samples.get(mid,"not_started")
        if item["reading_page_draft_phase"]!=expected:
            raise ValueError("Draft/page status is incorrect for "+str(mid))
        is_art=item["character"] in ART_CHARACTERS
        art_phase=("unique_vector_draft_editorially_unreviewed" if is_art else "not_started")
        if item["individual_artwork_stage"]!=art_phase:
            raise ValueError("Artwork status incorrectly upgraded or mapped")
        if item["original_pdf_pronunciation_adoption_checked_here"] is not False:
            raise ValueError("Source batch pinyin cannot be treated as adopted without PDF proof")
        if item["quote_approved"] is not False or item["literary_sentence_approved"] is not False:
            raise ValueError("Editorial approval has been claimed without signoff")
        if item["mainland_word_pronunciations_approved"]!=0 or item["release_eligible"] is not False:
            raise ValueError("Sample/word cannot be published from inventory")
        coverage[expected]+=1

    hsk=load(base/"p2_mainland_exam_evidence_20261024.json")
    if hsk.get("publication_approved") is not False:
        raise ValueError("HSK exam information cannot approve mainland word pronunciation")
    if hsk.get("standard_reference",{}).get("standard_id")!="GB/T 16159-2012":
        raise ValueError("Lost formal orthography standard identity")
    if len(hsk["entries"])!=2 or {e["word"] for e in hsk["entries"]}!=set(HSK_ENTRIES):
        raise ValueError("Current Mainland teaching corroboration must have exactly two words")
    first_words={term["word"]:term for x in content for term in x["terms"]}
    secondary=load(base/"p2_direct_lexicon_evidence_20261024.json")
    word_references={x["word"]:x for x in secondary["entries"]}
    for row in hsk["entries"]:
        word=row["word"]
        position,pinyin=HSK_ENTRIES[word]
        if row["row_no"]!=position or nfc(row["provider_pinyin_orthographic"])!=nfc(pinyin):
            raise ValueError("HSK source row/text mismatched")
        if row["draft_pinyin_display"]!=first_words[word]["pinyin"]:
            raise ValueError("Printed teaching pronunciation changed silently")
        uri=urlsplit(row["source_url"])
        args=parse_qs(uri.query)
        if uri.scheme!="https" or uri.hostname!="admin.chinesetest.cn" or not uri.path.endswith("standardsAction.do") or args.get("means")!=["getStandardWordsList"]:
            raise ValueError("Unknown examination source")
        if row["source_status"]!="mainland_exam_listing_verified_non_normative":
            raise ValueError("Examination record wrong source tier")
        if "pending" not in row["editorial_status"]:
            raise ValueError("Mainland exam source must remain pending")
        if row["source_url"].count("pager.offset=")!=1:
            raise ValueError("Cannot locate original HSK page")
    moon=word_references["月亮"]
    if moon["source_pinyin"]!="yuè liàng" or first_words["月亮"]["pinyin"]!="yuè liang":
        raise ValueError("Moon light-tone cross-region evidence must be preserved")

    return {
      "result":"EDITORIAL_COVERAGE_ONLY_NOT_RELEASE",
      "source_pdf_sha256":SHA,
      "counts":{
        "canonical_glyphs":len(by_id),"batches":21,
        "P1_sample_reading_pages":coverage["P1"],
        "P4_sample_reading_pages":coverage["P4"],
        "not_started_glyph_content":coverage["not_started"],
        "four_illustration_drafts_unreviewed":len(ART_CHARACTERS),
        "legacy_model_pinyin_candidates_not_publication_approved":candidate_pinyin_count,
        "mainland_exam_education_support_words":len(hsk["entries"]),
        "mainland_dictionary_entries_signed_off":0,
        "published_new_cultural_characters":0
      },
      "review_order_by_batch":[{
        "batch_id":f"B{i:02d}",
        "glyph_count":sum(x["batch_id"]==f"B{i:02d}" for x in all_entries),
        "unstarted":sum(x["batch_id"]==f"B{i:02d}" and x["reading_page_draft_phase"]=="not_started" for x in all_entries)
      } for i in range(1,22)],
      "pronunciation_conflict":{
        "word":"月亮","draft_display":"yuè liang",
        "taiwan_dictionary":"yuè liàng",
        "mainland_exam_word_form":"yuèliang",
        "classification":"mainland_educational_support_for_neutral_tone; lexicographical signoff still pending",
        "not_final_normative_decision":True},
      "orthography_rule":"GB/T 16159-2012 section 7.1 allows individual character annotations for early-learning materials; this does not certify individual phonetic readings",
      "editorial_draft_only":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
