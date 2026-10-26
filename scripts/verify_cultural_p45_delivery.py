#!/usr/bin/env python3
"""P4.5 all-glyph: 201 visible SVGs + 812 readings + 1045 original PDF strokes."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import fitz
import numpy as np

from cultural_p45_asset_pack import checked_assets
from cultural_fullbook_model import ROOT,make_plan,SHA
from cultural_source_audit import audit
from verify_cultural_fullbook import verify as verify_original_strokes

def verify(source,manifest,pdf,proof,art_registry,art_dir,root=ROOT):
    q=verify_original_strokes(source,manifest,pdf,proof,root)
    p=json.loads(Path(proof).read_text(encoding="utf-8"))
    rows=make_plan(audit(source,manifest),root)["entries"]
    generated,legacy=checked_assets(art_registry,art_dir,root)
    if (p.get("generated_distinct_svg_artwork_drafts")!=197 or
            p.get("full_artwork_svg_drafts")!=201 or
            p.get("reading_candidates_printed")!=804 or
            p.get("blocked_ambiguous_readings")!=8 or
            p.get("word_readings_approved")!=0 or
            p.get("illustration_art_approved")!=0 or
            p.get("new_publication_approvals")!=0):
        raise ValueError("Unreviewed illustration/pinyin scope or approval gate changed")
    pages={x["main_id"]:x for x in p["page_map"] if x["part"]==1}
    if len(pages)!=201:raise ValueError("One or more cultural source covers missing")
    checks=0;bad=0;catalogue={};vectors=set()
    with fitz.open(pdf) as book:
        for row in rows:
            mid=row["main_id"]
            preview=pages[mid]
            physical=book[preview["preview_pdf_page"]-1]
            text=physical.get_text()
            if "拼音候选未审" not in text:
                raise ValueError("Publication-risk warning lost from a reading page")
            candidate=row["manuscript"]["terms"]
            for term in candidate:
                if term["pinyin"] is None:
                    bad+=1
                    if "多音待核" not in text:raise ValueError("Ambiguous reading was printed as a fact")
                else:
                    checks+=1
                    if term["pinyin"] not in text:
                        raise ValueError(f"ID{mid:03d} word missing pinyin candidate: {term['word']}")
            if mid in generated:
                expected=generated[mid]
                if (preview["artwork_status"]!="new_source_linked_svg_draft_unreviewed" or
                    preview["artwork_asset_sha256"]!=expected["sha256"]):
                    raise ValueError("Generated cultural illustration provenance lost")
            else:
                if mid not in (39,64,77,88) or preview["artwork_status"]!="existing_p3_svg_draft_unreviewed":
                    raise ValueError("Cannot silently replace original four registered culture pictures")
                expected=legacy[row["manuscript"]["theme_key"]]
                if preview["artwork_asset_sha256"]!=expected["actual_sha256"]:
                    raise ValueError("Original P3 SVG asset checksum changed")
            rectangle=fitz.Rect([n*(72/25.4) for n in (110.5,42,193.5,114)])
            pixel=physical.get_pixmap(matrix=fitz.Matrix(1.4,1.4),
                                      clip=rectangle,alpha=False)
            digest=hashlib.sha256(pixel.samples).hexdigest()
            if digest in vectors:
                raise ValueError("Two main IDs show exactly identical cultural art raster")
            vectors.add(digest)
            arr=np.frombuffer(pixel.samples,dtype=np.uint8)
            if arr.size<10000 or float(np.std(arr))<5:
                raise ValueError("Blank or nearly blank cultural SVG visual panel")
            catalogue[str(mid)]={
                "character":row["character"],
                "pdf_cover_page":preview["preview_pdf_page"],
                "actual_svg_source_sha256":preview["artwork_asset_sha256"],
                "panel_preview_rgb_sha256":digest,
                "reading_candidate_slots":len(candidate),
                "ambiguous_readings":sum(1 for t in candidate if t["pinyin"] is None)}
    if checks!=804 or bad!=8 or len(vectors)!=201:
        raise ValueError("812 terms / 201 visually distinguishable vector compositions required")
    return {
        "result":"PASS_201_VISIBLE_SVG_DRAFTS_AND_812_SOURCE_GROUNDED_READING_SLOTS",
        "all_original_pdf_strokes":q["original_source_vector_steps_pixel_compared"],
        "main_glyphs":201,"page_count":p["output_pdf_pages"],
        "distinct_rendered_visual_panels":len(vectors),
        "unique_new_svg":197,"retained_legacy_svg":4,
        "candidate_transcriptions_printed_unapproved":checks,
        "polyphonic_or_ambiguous_transcriptions_blocked":bad,
        "word_and_art_publication_approved":0,
        "original_v051_pdf_sha256":SHA,
        "pdf_sha256":p["output_pdf_sha256"],
        "human_art_review_pending":True,
        "human_pronunciation_review_pending":True,
        "per_main_id":catalogue}
def main():
    ap=argparse.ArgumentParser()
    for key in ("source","manifest","pdf","proof","art-registry","art-dir","output"):
        ap.add_argument("--"+key,type=Path,required=True)
    ap.add_argument("--root",type=Path,default=ROOT)
    a=ap.parse_args()
    data=verify(a.source,a.manifest,a.pdf,a.proof,a.art_registry,a.art_dir,a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in data.items() if k!="per_main_id"},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
