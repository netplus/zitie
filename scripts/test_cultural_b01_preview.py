#!/usr/bin/env python3
"""Independent per-tile PDF source equivalence, B01 cultural nine-page preview."""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

from cultural_b01_editorial_audit import audit as audit_b01, ROOT
from cultural_source_audit import audit as audit_original
from build_cultural_sample import original_specimen

EXPECTED = {1:1, 6:2, 11:2, 12:2, 28:3, 29:3, 33:3, 37:3, 40:3}
CHECKSUM = "7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"

def thumbnail(book, page_no, rect):
    pix = book[page_no].get_pixmap(
        matrix=fitz.Matrix(2,2),clip=fitz.Rect(rect),alpha=False)
    bitmap = Image.frombytes("RGB", (pix.width,pix.height), pix.samples)
    return np.asarray(bitmap.resize((160,160),Image.Resampling.BILINEAR),
                      dtype=np.float32)

def verify(source:Path,manifest:Path,content:Path,pdf:Path,proof:Path):
    draft_status = audit_b01(ROOT)
    canonical = audit_original(source,manifest)
    assert canonical["source_pdf_sha256"] == CHECKSUM
    assert draft_status["new_characters"] == 9
    assert draft_status["new_pages_rendered"] == 0  # P2 ledger not retroactively promoted
    meta = json.loads(proof.read_text(encoding="utf-8"))
    briefs = json.loads(content.read_text(encoding="utf-8"))["entries"]
    by_id = {glyph["main_id"]:glyph for glyph in canonical["glyphs"]}
    source_ids = {x["main_id"] for x in briefs}
    assert source_ids == set(EXPECTED) and len(briefs) == 9
    assert meta["status"] == "B01_source_locked_editorial_draft_not_for_release"
    assert meta["source_sha256"] == CHECKSUM
    assert meta["output_sha256"] == hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert (meta["main_ids"], meta["pages"], meta["total_source_strokes"]) == (9,9,22)
    assert meta["original_source_stroke_total_expected"] == 22
    assert meta["word_pinyin_candidates_not_for_release"] == 36
    assert meta["primary_dictionary_word_readings_approved"] == 0
    assert meta["actual_p3_artwork_finalized"] == 0
    assert meta["page_status"] == "technical_pdf_only_not_released"
    assert meta["uses_only_original_source_pdf_tiles"] is True
    assert meta["tile_mm"] >= 30
    assert len(meta["page_map"]) == 9
    errors = []
    observed=defaultdict(list)
    with fitz.open(source) as original, fitz.open(pdf) as draft:
        assert len(draft)==9
        for pno, (e, record) in enumerate(zip(briefs,meta["page_map"])):
            glyph = by_id[e["main_id"]]
            assert record["main_id"] == e["main_id"]
            assert record["character"] == glyph["character"] == e["character"]
            assert record["theme_key"] == e["theme_key"]
            assert record["part"] == record["parts"] == 1
            assert record["editorial_state"] == "draft_unreviewed"
            assert len(record["source_steps"]) == EXPECTED[e["main_id"]]
            page = draft[pno]
            assert abs(page.rect.width-595.276) < .4
            assert abs(page.rect.height-841.89) < .4
            text = page.get_text()
            for phrase in ("笔顺提示", "笔顺", "相关字词", "一字一句",
                           "经典引文待核验", "文化图构图草案", e["title"],
                           "非正式稿"):
                assert phrase in text, (glyph["character"],phrase)
            for term in e["terms"]:
                assert term["word"] in text, term["word"]
                assert term["pinyin_display_candidate"] in text, term["word"]
                assert term["pronunciation_status"] == "review_pending"
            assert text.find("笔顺提示") < text.find("笔顺", text.find("笔顺提示")+1)
            if e["character"] == "一":
                # Regression: the old forced 48x48mm sizing stretched this
                # original PDF single-stroke ink mask into a giant wedge.
                sample = Image.open(original_specimen(original[glyph["first_pdf_page"]-1]))
                src_ratio = sample.width / sample.height
                crop = page.get_pixmap(matrix=fitz.Matrix(2,2),
                    clip=fitz.Rect(34*72/25.4,62*72/25.4,
                                   82*72/25.4,110*72/25.4),alpha=False)
                a=np.asarray(Image.frombytes("RGB",(crop.width,crop.height),crop.samples))
                ink=np.where((a[:,:,0]<175)&(a[:,:,1]<175)&(a[:,:,2]<175))
                assert len(ink[0])>100,'Original one-stroke main glyph missing'
                glyph_ratio=(ink[1].max()-ink[1].min()+1)/(ink[0].max()-ink[0].min()+1)
                assert abs(glyph_ratio/src_ratio-1)<.30,(src_ratio,glyph_ratio)
            if glyph["pinyin_from_pdf"]:
                assert glyph["pinyin_from_pdf"] in text
                assert record["source_reading_state"] == "published_source"
            else:
                assert "读音待审核" in text
                assert record["source_reading_state"] == "blocked_no_source_pdf_reading"
            boxes=[]
            for entry in record["source_steps"]:
                source_step = glyph["steps"][entry["index"]-1]
                for k in ("index","name","pdf_page","rect_pt"):
                    assert entry[k] == source_step[k],(glyph["character"],k)
                target = fitz.Rect(entry["preview_rect_pt"])
                assert page.rect.contains(target)
                assert abs(target.width - 31*72/25.4) < .3
                assert abs(target.height - 31*72/25.4) < .3
                assert target.y1 < 275*72/25.4
                assert not any(target.intersects(b) for b in boxes)
                boxes.append(target)
                observed[e["main_id"]].append(entry["index"])
                x=thumbnail(original,entry["pdf_page"]-1,entry["rect_pt"])
                y=thumbnail(draft,pno,entry["preview_rect_pt"])
                diff=float(np.abs(x-y).mean())
                if diff>=9.5:
                    raise AssertionError((glyph["character"],entry["index"],diff))
                errors.append(diff)
        assert set(observed)==set(EXPECTED)
        for mid,seq in observed.items():
            assert seq==list(range(1,EXPECTED[mid]+1))
    assert len(errors)==22
    return {"result":"PASS","page_count":9,"independent_original_source_steps_checked":len(errors),
            "max_rgb_mae":round(max(errors),4),
            "original_pdf_sha256":CHECKSUM,
            "source_steps_per_main_id":{str(k):EXPECTED[k] for k in sorted(EXPECTED)},
            "no_child_publication_approval":True,
            "human_visual_review_required":True}

def main():
    ap=argparse.ArgumentParser()
    for opt in ("source","manifest","content","pdf","proof"):
        ap.add_argument("--"+opt,required=True,type=Path)
    a=ap.parse_args()
    print(json.dumps(verify(a.source,a.manifest,a.content,a.pdf,a.proof),
                     ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
