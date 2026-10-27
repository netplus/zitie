#!/usr/bin/env python3
"""P9.4 independently verify every enlarged pen tile is the same actual P9 vector ink.

This is geometry source fidelity, not approval of Chinese standard stroke order.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

from build_cultural_p9_exception_stroke_atlas import (
    P9_SHA, SHA, P9_SOURCE, ORIGINAL_SOURCE, ROOT, index_records
)

def get_clip(page:fitz.Page,rect:list,matrix:float):
    p=page.get_pixmap(matrix=fitz.Matrix(matrix,matrix),clip=fitz.Rect(rect),alpha=False)
    return Image.frombytes("RGB",(p.width,p.height),p.samples)

def compare(art_pdf:Path,qa_file:Path,root:Path=ROOT):
    report=json.loads(qa_file.read_text(encoding="utf8"))
    plan=index_records(root)
    if (report.get("release_eligible") is not False
        or report.get("human_approved_risk_glyphs")!=0
        or report.get("original_P9_260_page_pdf_sha256")!=P9_SHA
        or report.get("original_released_v051_pdf_sha256")!=SHA
        or report.get("art_review_pdf_pages")!=41
        or report.get("priority_glyphs")!=40
        or report.get("risk_atlas_copied_source_cumulative_steps")!=146
        or len(report.get("page_mapping",[]))!=40
        or len(report.get("individual_copied_steps",[]))!=146):
        raise ValueError("P9 40-priority-character review atlas is incomplete or falsely approved")
    if hashlib.sha256(art_pdf.read_bytes()).hexdigest()!=report["art_review_pdf_sha256"]:
        raise ValueError("Actual P9 atlas differs from artifact/QA digest")
    if [r["main_id"] for r in report["page_mapping"]] != [r["main_id"] for r in plan["entries"]]:
        raise ValueError("A high risk word was removed/replaced")
    by_main={r["main_id"]:r for r in plan["entries"]}
    per_id={}
    errors=[]
    scores=[]
    with fitz.open(art_pdf) as atlas,fitz.open(root/P9_SOURCE.relative_to(ROOT)) as source:
        if len(atlas)!=41 or len(source)!=260:
            raise ValueError("Review atlas or original P9 source PDF lost pages")
        for rec in report["individual_copied_steps"]:
            mid=rec["main_id"];i=rec["index"]
            if mid not in by_main or rec["character"]!=by_main[mid]["character"]:
                raise ValueError("Risk atlas source glyph identity mismatch")
            per_id.setdefault(mid,set()).add(i)
            dest=atlas[rec["review_page"]-1]
            raw=source[rec["P9_source_pdf_page"]-1]
            if not(593<dest.rect.width<597 and 840<dest.rect.height<843):
                raise ValueError("Review page is not A4")
            a=get_clip(raw,rec["original_P9_clip_pt"],39.0/31.0)
            b=get_clip(dest,rec["atlas_tile_rect_pt"],1.0)
            # An exact Form XObject source is copied, but physical destination
            # size may differ by subpixel rounding; resample both conservatively
            # into one square. Any missing stroke/red-current image will fail.
            ar=np.asarray(a.resize((96,96),Image.Resampling.BILINEAR),dtype=np.int16)
            br=np.asarray(b.resize((96,96),Image.Resampling.BILINEAR),dtype=np.int16)
            mae=float(np.abs(ar-br).mean())
            scores.append(round(mae,4))
            if mae>22:
                errors.append((mid,i,round(mae,3)))
            # A copied source pen card must have visible actual ink.
            if float((br<180).any(axis=2).mean())<.003:
                errors.append((mid,i,"no visible source ink"))
        for mid,row in by_main.items():
            wanted=set(range(1,row["stroke_count"]+1))
            if per_id.get(mid)!=wanted:
                raise ValueError(f"Missing physical pen panels for risk glyph ID{mid:03d}")
            text=atlas[row["art_review_pdf_page"]-1].get_text()
            if ("专家逐笔审校" not in text or "第一审核" not in text
                or "独立复核" not in text or
                "待" not in text):
                raise ValueError("One review page lost its visible human-review warning")
    if errors:
        raise ValueError("Source-pixel mismatch or blank tile: "+repr(errors[:12]))
    if len(scores)!=146 or max(scores)>22:
        raise ValueError("Expected 146 independent enlarged source-ink comparisons")
    result={
        "result":"PASS_40_RISK_GLYPHS_146_P9_ORIGINAL_INK_TILES_VISUALLY_MATCH_PROVENANCE",
        "priority_glyphs_review_pages":40,
        "source_vector_pen_cards_compared":146,
        "pdf_pages":41,
        "mean_absolute_RGB_error_max":max(scores),
        "mean_absolute_RGB_error_average":round(sum(scores)/len(scores),4),
        "source_v051_299_page_PDF_untouched":True,
        "normative_fine_shape_correctness_approved":False,
        "human_first_and_second_reviews_signed":False,
        "publication_eligible":False,
    }
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--atlas-pdf",type=Path,required=True)
    parser.add_argument("--qa-file",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    result=compare(a.atlas_pdf,a.qa_file)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
