#!/usr/bin/env python3
"""P4.2 all-201 cultural manuscript routing, strictly separate from publication.

Source PDF supplies the ONLY teaching glyphs, stroke tiles, stroke names,
step order, approved page-local pinyin and tips. Proposed words/quotes/art
are never silently promoted from earlier experimental drafts.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

from cultural_editorial_coverage import audit as editorial_coverage

ROOT=Path(__file__).resolve().parents[1]
SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
P1=ROOT/"data/cultural_edition/first_batch_draft.json"
P4=ROOT/"data/cultural_edition/p4_multipage_prototypes.json"
B01=ROOT/"data/cultural_edition/p2_b01_editorial_briefs_20261025.json"
SPECIAL_ART={"水","山","月","木"}
B01_IDS={1,6,11,12,28,29,33,37,40}
DRAFT_IDS={1,6,11,12,28,29,33,37,40,39,64,77,88,106,200,201}
CAPACITY_FIRST=6
CAPACITY_MORE=15

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def checked_drafts(root:Path):
    base=root/"data/cultural_edition"
    result={}
    for filename,phase in (("first_batch_draft.json","P1"),
                           ("p4_multipage_prototypes.json","P4"),
                           ("p2_b01_editorial_briefs_20261025.json","B01")):
        doc=load(base/filename)
        expected=("draft_not_for_release" if phase=="B01"
                  else "editorial_draft_not_for_release")
        if doc.get("review_state")!=expected:
            raise ValueError("A manuscript was upgraded without publication gate: "+filename)
        if phase=="B01" and doc.get("source_pdf_sha256")!=SHA:
            raise ValueError("P2 B01 source changed")
        for e in doc["entries"]:
            mid=e["main_id"]
            if mid in result:
                raise ValueError("Duplicate cultural manuscript main ID")
            if not isinstance(e.get("character"),str) or len(e["character"])!=1:
                raise ValueError("Invalid one-glyph cultural manuscript")
            if phase=="B01":
                if (e["stage"]!="P2_editorial_brief_unreviewed" or
                    e["publication_eligible"] is not False or
                    e["quote"]["status"]!="blocked_no_checked_primary_quote" or
                    e["quote"]["text"] is not None or
                    e["meaning"]["status"]!="review_pending" or
                    e["sentence_review_status"]!="review_pending"):
                    raise ValueError("B01 publication claims are disallowed")
                terms=[{"word":v["word"],"pinyin":v["pinyin_display_candidate"],
                        "review_status":v["pronunciation_status"]}
                       for v in e["terms"]]
                for v in e["terms"]:
                    if (v["source_url"] is not None or v["reviewed_by"] is not None
                            or v["pronunciation_status"]!="review_pending"):
                        raise ValueError("B01 words are candidate readings only")
                art="unique_scene_brief_no_drawn_asset"
                meaning=e["meaning"]["lines"]
            else:
                if e["quote"]["status"] not in ("review_pending","blocked"):
                    raise ValueError("Unapproved historical quote status was upgraded")
                terms=[{"word":v["word"],"pinyin":v["pinyin"],
                        "review_status":v["status"]} for v in e["terms"]]
                for v in terms:
                    if v["review_status"] not in ("review_pending","blocked"):
                        raise ValueError("Historical words are candidate readings only")
                art=("four_unique_svg_drafts_not_approved"
                     if e["character"] in SPECIAL_ART else
                     "not_drawn_only_technical_scene_placeholder")
                meaning=e["meaning"]
            if not isinstance(meaning,list) or not meaning:
                raise ValueError("Empty candidate semantic draft")
            result[mid]={
                "source_phase":phase,"main_id":mid,"character":e["character"],
                "theme_key":e["theme_key"],"title":e["title"],
                "subtitle":e["subtitle"],"meaning":meaning,
                "quote_candidate":e["quote"].get("text"),
                "quote_status":e["quote"]["status"],"terms":terms,
                "sentence":e["sentence"],"artwork_stage":art,
                "editorial_status":"candidate_not_reviewed",
                "release_eligible":False,
            }
    if set(result)!=DRAFT_IDS:
        raise ValueError("Expected exactly 16 known original cultural manuscripts")
    return result

def make_plan(source_index:dict,root:Path=ROOT)->dict:
    root=Path(root)
    if (source_index.get("source_pdf_sha256")!=SHA or
            source_index.get("main_ids")!=201 or
            source_index.get("total_source_steps")!=1045 or
            source_index.get("source_teaching_pages")!=258):
        raise ValueError("Released-PDF audit does not match the locked 201/1045/258 source")
    ledger=editorial_coverage(root)
    if ledger["counts"]["canonical_glyphs"]!=201 or ledger["counts"]["glyphs_with_any_editorial_brief"]!=16:
        raise ValueError("Cultural editorial backlog diverged: recount it first")
    source={g["main_id"]:g for g in source_index["glyphs"]}
    if len(source)!=201 or set(source)!=set(range(1,202)):
        raise ValueError("Original source main IDs missing or repeated")
    drafts=checked_drafts(root)
    out=[]; all_ids=[]
    for number in range(1,22):
        batch_id=f"B{number:02d}"
        batch=load(root/"data"/f"{batch_id}.json")
        if batch.get("batch_id")!=batch_id:
            raise ValueError("Original batch identity changed")
        members=batch["entries"]
        if len(members)!=(1 if number==21 else 10):
            raise ValueError("Every original batch needs all canonical main glyphs")
        for e in members:
            mid=e["main_id"]
            src=source.get(mid)
            if src is None or src["character"]!=e["character"]:
                raise ValueError("Original PDF/main batch character mismatch")
            if len(src["steps"])!=src["stroke_count"] or not (1<=src["stroke_count"]<=17):
                raise ValueError("Incomplete or unsupported released original stroke sequence")
            if [x["index"] for x in src["steps"]] != list(range(1,src["stroke_count"]+1)):
                raise ValueError("Source step sequence is non-contiguous")
            draft=drafts.get(mid)
            if draft and draft["character"]!=e["character"]:
                raise ValueError("Editorial character does not match source PDF")
            row=dict(
                main_id=mid,character=e["character"],batch_id=batch_id,
                first_source_pdf_page=src["first_pdf_page"],
                adopted_source_pinyin=src["pinyin_from_pdf"],
                source_tips=src["tips_from_pdf"],stroke_count=src["stroke_count"],
                steps=src["steps"],page_parts=1+(max(0,src["stroke_count"]-CAPACITY_FIRST)+CAPACITY_MORE-1)//CAPACITY_MORE,
                manuscript=draft,has_content_draft=bool(draft),
                content_review="unreviewed" if draft else "not_started",
                source_risk="no_pdf_adopted_pinyin" if src["pinyin_from_pdf"] is None else "source_pdf_reading_only",
                art_review="unapproved" if draft else "not_started",
                release_eligible=False,
                attached_form_review="not_included_needs_separate_source",
            )
            out.append(row);all_ids.append(mid)
    if len(out)!=201 or set(all_ids)!=set(range(1,202)) or len(set(all_ids))!=201:
        raise ValueError("Exactly 201 original B01-B21 entries required")
    if sum(x["stroke_count"] for x in out)!=1045:
        raise ValueError("201 original-PDF strokes no longer sum to 1045")
    if sum(bool(x["manuscript"]) for x in out)!=16:
        raise ValueError("Manuscript content stages no longer sum to 16")
    titles=[x["manuscript"]["title"] for x in out if x["manuscript"]]
    scenes=[x["manuscript"]["theme_key"] for x in out if x["manuscript"]]
    sentences=[x["manuscript"]["sentence"] for x in out if x["manuscript"]]
    if (len(set(titles))!=16 or len(set(scenes))!=16 or len(set(sentences))!=16):
        raise ValueError("Existing cultural themes, titles or sentences collide")
    if any(x["manuscript"] and x["manuscript"]["release_eligible"] for x in out):
        raise ValueError("A draft was mistakenly marked releasable")
    if any(x["manuscript"] and x["manuscript"]["artwork_stage"]=="approved" for x in out):
        raise ValueError("No existing illustration has final art signoff")
    counts=Counter(x["batch_id"] for x in out)
    if len(counts)!=21 or any(counts[f"B{i:02d}"]!=(1 if i==21 else 10) for i in range(1,22)):
        raise ValueError("Batch coverage changed")
    return {
        "schema_version":1,"status":"P4_2_ALL_201_SOURCE_ONLY_EDITORIAL_DRAFT",
        "source_pdf_sha256":SHA,"original_source_pdf_pages":299,
        "original_source_teaching_pages":258,
        "source_main_id_count":201,"source_stroke_total":1045,
        "batch_count":21,"existing_cultural_drafts":16,
        "without_new_cultural_content":185,
        "reviewed_word_readings":0,
        "new_cultural_release_approved":0,
        "complete_artwork_approved":0,
        "attached_form_count_included":0,
        "disclaimer":"Engineering coverage, not 201 approved cultural reading pages or attached forms",
        "entries":out,
    }
