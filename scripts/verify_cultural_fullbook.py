#!/usr/bin/env python3
"""Independent P4.2 PDF audit of all 201 entries / 1045 original vector steps.

Inspect exact source page, crop, label, order, output placement and pixel
equivalence. This never approves unreviewed cultural vocabulary or artwork.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

from cultural_fullbook_model import make_plan, ROOT, SHA
from cultural_source_audit import audit

def image_at(book,page,rect,size=120):
    pix=book[page].get_pixmap(
        matrix=fitz.Matrix(1.6,1.6),clip=fitz.Rect(rect),alpha=False)
    image=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
    return np.asarray(image.resize((size,size),Image.Resampling.BILINEAR),
                      dtype=np.float32)

def verify(source:Path,manifest:Path,pdf:Path,proof:Path,root:Path=ROOT):
    original_index=audit(source,manifest)
    plan=make_plan(original_index,root)
    report=json.loads(proof.read_text(encoding="utf-8"))
    if report["status"]!="P4_2_201_GLYPH_FULL_BOOK_ENGINEERING_DRAFT_NOT_RELEASE":
        raise ValueError("All-book preview cannot be promoted to a formal edition")
    if report["source_pdf_sha256"]!=SHA:
        raise ValueError("Full-book original source checksum changed")
    if report["output_pdf_sha256"]!=hashlib.sha256(pdf.read_bytes()).hexdigest():
        raise ValueError("Full-book proof PDF checksum mismatch")
    if report["output_pdf_bytes"]!=pdf.stat().st_size:
        raise ValueError("PDF file size disagrees with provenance")
    if (report["content_glyphs"],report["cumulative_original_source_stroke_tiles"],
        report["batch_count"])!=(201,1045,21):
        raise ValueError("P4.2 201/1045/21 source coverage incomplete")
    if (report["front_matter_pages"],report["missing_cultural_editorial_content"],
        report["cultural_draft_glyphs"],report["unique_existing_svg_artwork_drafts"])!=(6,0,201,4):
        raise ValueError("Front matter or editorial provenance coverage changed")
    if (report.get("unique_new_svg_artwork_drafts")!=197 or
        report.get("unique_total_svg_artwork_drafts")!=201 or
        report.get("lexical_evidence_rows")!=812):
        raise ValueError("Full cultural draft requires 201 actual SVG artwork and 812 lexical evidence rows")
    if report.get("provisional_pinyin_candidates")!=plan["provisional_pinyin_candidates"]:
        raise ValueError("Provisional pronunciation evidence was lost in PDF export")
    generated=pdf.parent/"cultural-v07-svg-registry.json"
    if not generated.is_file():
        raise ValueError("197 SVG evidence registry missing from PDF build folder")
    art_data=json.loads(generated.read_text(encoding="utf8"))
    if (art_data.get("review_state")!="original_vector_drawings_unapproved_for_release" or
        len(art_data.get("artworks",[]))!=197):
        raise ValueError("Unreviewed scene provenance must contain 197 drawings")
    import re
    art_index={}
    drawing_shas=set()
    artwork_dir=pdf.parent/"cultural-v07-svg"
    for v in art_data["artworks"]:
        mid=v["main_id"]
        if mid in art_index:
            raise ValueError("Duplicate cultural art main ID")
        if (v["professional_art_approval"] is not False or
            v["editorial_status"]!="original_vector_draft_not_approved" or
            not re.fullmatch(r"ID\d{3}\.svg",v["file"])):
            raise ValueError("Scene artwork claims approval or unsafe path")
        raw=(artwork_dir/v["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=v["artwork_sha256"]:
            raise ValueError("Cultural illustration asset checksum mismatch")
        if any(tag in raw.lower() for tag in (b"<script",b"<image",b"<text",b"href=",b"url(",b"https:")):
            raise ValueError("SVG image includes unsafe external data or text")
        if v["artwork_sha256"] in drawing_shas:
            raise ValueError("Two supposedly independent art assets share exact bytes")
        drawing_shas.add(v["artwork_sha256"])
        art_index[mid]=v
    if len(art_index)!=197:
        raise ValueError("Only 197 new SVGs may substitute for four established drafts")
    if (report["illustration_art_approved"]!=0 or
        report["word_readings_approved"]!=0 or
        report["new_publication_approvals"]!=0 or
        report["attached_forms_included"]!=0):
        raise ValueError("Incomplete cultural material cannot enter released book")
    original={x["main_id"]:x for x in original_index["glyphs"]}
    plan_by_id={x["main_id"]:x for x in plan["entries"]}
    expected_pages=6+sum(e["page_parts"] for e in plan["entries"])
    if report["output_pdf_pages"]!=expected_pages:
        raise ValueError("Unexpected total all-book PDF page count")
    records=report["page_map"]
    if len(records)!=expected_pages-6:
        raise ValueError("Physical book page map omits a cultural page")
    seen=defaultdict(list);page_counts=Counter();failures=[]
    pixel_scores=[];source_readings=0
    with fitz.open(source) as old,fitz.open(pdf) as new:
        if len(new)!=expected_pages:raise ValueError("Physical PDF page count incomplete")
        for p in new:
            if abs(p.rect.width-595.276)>.5 or abs(p.rect.height-841.89)>.5:
                raise ValueError("Non-A4 page in full cultural PDF")
        for n in range(2,6):
            if not new[n].get_links():
                raise ValueError("At least one 201-glyph index page lost its clickable links")
        links=report["index_links"]
        if len(links)!=201 or len(set(x["target_pdf_page"] for x in links))!=201:
            raise ValueError("All 201 index targets must exist and be unique")
        for link in links:
            assert 3<=link["index_pdf_page"]<=6
            assert 7<=link["target_pdf_page"]<=len(new)
            assert any(l["page"]+1==link["target_pdf_page"]
                       for l in new[link["index_pdf_page"]-1].get_links())
        toc=new.get_toc()
        title_ids=[x[1] for x in toc if x[0]==2 and x[1].startswith("ID")]
        if len(title_ids)!=201 or len(set(title_ids))!=201:
            raise ValueError("Bookmarks do not cover the 201 main source glyphs")
        for expected_pageno,rec in enumerate(records,7):
            if rec["preview_pdf_page"]!=expected_pageno:
                raise ValueError("Source step or text page map out of PDF order")
            mid=rec["main_id"];src=original[mid];target=plan_by_id[mid]
            if rec["character"]!=src["character"] or rec["batch_id"]!=target["batch_id"]:
                raise ValueError("Original character or batch in PDF was changed")
            if rec["parts"]!=target["page_parts"]:
                raise ValueError("Long-glyph continuation count is inaccurate")
            if rec["content_status"] not in ("unreviewed","not_started","original_source_strokes_only"):
                raise ValueError("A not-yet-reviewed reading page became approved")
            if (rec["all_word_candidates_unreviewed"] is not True
                or rec["quote_citation_approval"] is not False):
                raise ValueError("Unverified quoted words must not be presented as approved")
            if rec["part"]==1:
                if mid in art_index:
                    if rec.get("artwork_svg_sha256")!=art_index[mid]["artwork_sha256"]:
                        raise ValueError("Printed scene SVG checksum and PDF source registry disagree")
                    if rec["artwork_status"]!="unique_original_svg_draft_unreviewed":
                        raise ValueError("New actual illustration was replaced with an art placeholder")
                elif rec["artwork_status"]!="four_svg_draft_unreviewed":
                    raise ValueError("Four original registered SVG illustrations must remain source-locked")
            page=new[expected_pageno-1]
            wording=page.get_text()
            if "\x00" in wording or "\ufffd" in wording:
                raise ValueError(f"Missing embedded Unicode glyph on PDF page {expected_pageno} ID{mid:03d}")
            for fixed in ("笔顺","禁止作为正式教材发行"):
                if fixed not in wording:
                    raise ValueError("PDF lost important teaching/disclaimer text")
            if rec["part"]==1:
                page_counts[mid]+=1
                if rec["page_kind"]!="source_main_cultural_reading":
                    raise ValueError("Main source glyph page identity wrong")
                if "笔顺提示" not in wording or "原图逐笔示范" not in wording:
                    raise ValueError("Teaching guide is not displayed before full stroke order")
                if wording.index("笔顺提示")>=wording.index("原图逐笔示范"):
                    raise ValueError("Stroke teaching hints must precede cumulative steps")
                if rec["printed_pinyin_from_original_source"]!=src["pinyin_from_pdf"]:
                    raise ValueError("PDF print single-glyph pinyin was not source-locked")
                if src["pinyin_from_pdf"] is None:
                    if "本页不单列读音" not in wording:
                        raise ValueError("Missing source pinyin was invented")
                else:
                    source_readings+=1
                    if src["pinyin_from_pdf"] not in wording:
                        raise ValueError("Released PDF adopted pinyin missing")
                if target["manuscript"]:
                    if target["manuscript"]["quote_candidate"] is None:
                        if "读字想一想" not in wording:
                            raise ValueError("No authored reflection in place of unsupported quote")
                    elif "经典一隅" not in wording:
                        raise ValueError("Located classical quotation section vanished")
                    if target["manuscript"]["title"] not in wording:
                        raise ValueError("Existing original cultural manuscript missing")
                    for term in target["manuscript"]["terms"]:
                        if term["word"] not in wording:
                            raise ValueError(f"Missing PDF word/example: ID{mid:03d} {target['character']} "
                                             f"page {expected_pageno} word={term['word']!r} "
                                             f"extracted_sample={wording[-300:]!r}")
                        if term["pinyin"] is None:
                            tag=("字例·待审" if target["manuscript"].get("term_kind")=="component_examples"
                                 else "读音待核")
                            if tag not in wording:
                                raise ValueError(f"ID{mid:03d} {rec['character']} PDF page {expected_pageno}: "
                                                 f"missing {tag} on unsupported word/example {term['word']}")
                        if term["pinyin"] is not None and term["pinyin"] not in wording:
                            raise ValueError("Previously drafted word Pinyin was lost")
                else:
                    raise ValueError("Every main glyph must now have its own authored cultural manuscript")
            else:
                if rec["page_kind"]!="original_stroke_continuation" or "笔顺续页" not in wording:
                    raise ValueError("Original source step continuation missing")
                if len(rec["source_steps"])>15:
                    raise ValueError("Continuation exceeds fifteen 31mm original source tiles")
            boxes=[]
            for step in rec["source_steps"]:
                expected=src["steps"][step["index"]-1]
                for attr in ("index","name","pdf_page","rect_pt"):
                    if step[attr]!=expected[attr]:
                        raise ValueError(f"Source step mutated ID{mid:03d} {step['index']} {attr}")
                dst=fitz.Rect(step["preview_rect_pt"])
                expected_size=31*72/25.4
                if (not page.rect.contains(dst) or
                    abs(dst.width-expected_size)>.4 or
                    abs(dst.height-expected_size)>.4 or
                    dst.y1>282*72/25.4):
                    raise ValueError("Stroke thumbnail is clipped or unexpectedly rescaled")
                if any(dst.intersects(previous) for previous in boxes):
                    raise ValueError("Two source stroke tiles overlap")
                boxes.append(dst)
                seen[mid].append(step["index"])
                before=image_at(old,step["pdf_page"]-1,step["rect_pt"])
                after=image_at(new,expected_pageno-1,step["preview_rect_pt"])
                mae=float(np.abs(before-after).mean())
                if mae>=9.5:
                    failures.append((mid,step["index"],round(mae,4)))
                pixel_scores.append(mae)
            if len(rec["source_steps"])==0 or (rec["part"]==1 and len(rec["source_steps"])>6):
                raise ValueError("Cover/continuation source tile capacity violated")
        if len(page_counts)!=201 or any(x!=1 for x in page_counts.values()):
            raise ValueError("Every original main glyph must have exactly one culture cover")
        if set(seen)!=set(range(1,202)):
            raise ValueError("Not all 201 source glyphs have teaching stroke images")
        for mid,source_steps in seen.items():
            if source_steps!=list(range(1,original[mid]["stroke_count"]+1)):
                raise ValueError("Cumulative source step order was lost for main ID "+str(mid))
    if len(pixel_scores)!=1045 or failures:
        raise ValueError("1045 original-PDF vector tile pixels mismatch: "+repr(failures[:12]))
    mapped_total=sum(len(v) for v in seen.values())
    counts=Counter(x["batch_id"] for x in plan["entries"])
    return {
        "result":"PASS_SOURCE_LOCKED_201_GLYPHS_1045_STROKES_DRAFT_ONLY",
        "source_pdf_sha256":SHA,
        "preview_pdf_sha256":report["output_pdf_sha256"],
        "a4_pdf_pages":report["output_pdf_pages"],
        "front_pages":6,
        "cultural_glyph_pages":len(records),
        "continuation_pages":report["continuation_pages"],
        "batch_count":len(counts),
        "main_id_count":len(seen),
        "original_source_vector_steps_pixel_compared":mapped_total,
        "max_normalized_rgb_mae_255":round(max(pixel_scores),4),
        "average_normalized_rgb_mae_255":round(float(np.mean(pixel_scores)),4),
        "source_pdf_pinyin_adoptions_reused":source_readings,
        "pending_cultural_articles":0,
        "unreviewed_cultural_drafts":201,
        "new_fullbook_character_articles":185,
        "unverified_related_word_examples":report["unreviewed_related_word_or_character_examples"],
        "linked_index_targets":len(report["index_links"]),
        "actual_svg_artwork_drafts":201,
        "new_svg_artwork_drafts_with_sha_proof":197,
        "provisional_word_or_example_pinyin_candidates":report["provisional_pinyin_candidates"],
        "word_or_example_evidence_rows":812,
        "no_published_cultural_articles":True,
        "full_page_visual_editorial_review":"requires_human_editorial_review",
    }

def main():
    p=argparse.ArgumentParser()
    for field in ("source","manifest","pdf","proof"):
        p.add_argument("--"+field,required=True,type=Path)
    p.add_argument("--root",default=ROOT,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    report=verify(args.source,args.manifest,args.pdf,args.proof,args.root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
