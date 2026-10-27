#!/usr/bin/env python3
"""P10 strict-review integrated proof: full-source stroke and unchanged-page QA.

The 260-page P10 artifact remains a DRAFT even if all checks pass; artistic
quality, licensing, source phonetics, pen-shape norms and paper printing require
independent reviewer signoffs.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageOps, ImageStat

from cultural_p10_art_review import ROOT, SHA, P9_SHA, STUDIES
from build_cultural_p10_integrated import P9_PROOF, P9_PDF, identity_evidence

def compare(source_pdf:Path,candidate_pdf:Path,metadata_path:Path,output_report:Path,root:Path=ROOT):
    root=Path(root)
    base=json.loads((root/P9_PROOF.relative_to(ROOT)).read_text(encoding="utf8"))
    meta=json.loads(Path(metadata_path).read_text(encoding="utf8"))
    art=meta.get("page_artwork_register",[])
    if (meta.get("source_v051_pdf_sha256")!=SHA or
        meta.get("source_P9_pdf_sha256")!=P9_SHA or
        meta.get("source_main_glyphs")!=201 or
        meta.get("source_stroke_tiles_expected_untouched")!=1045 or
        meta.get("output_pdf_pages")!=260 or
        meta.get("artwork_human_approvals")!=0 or
        meta.get("release_eligible") is not False or
        meta.get("main_pinyin_approved_and_printed")!=0 or
        meta.get("candidate_terms_pinyin_printed")!=0 or
        len(art)!=len(STUDIES) or
        meta.get("unillustrated_201_main_ids")!=201-len(STUDIES)):
        raise ValueError("P10 cannot bypass the independent stroke, Pinyin, art or book-release gates")
    if hashlib.sha256(Path(source_pdf).read_bytes()).hexdigest()!=P9_SHA:
        raise ValueError("P9 immutable input proof differs from frozen original")
    if hashlib.sha256(Path(candidate_pdf).read_bytes()).hexdigest()!=meta["output_pdf_sha256"]:
        raise ValueError("P10 rendered PDF differs from source registry output")
    modified={x["replaced_card_pdf_page"] for x in art}
    if (len(modified)!=len(STUDIES)
        or {x["main_id"] for x in art}!=set(STUDIES)
        or any(x["art_human_review_approved"] is not False for x in art)):
        raise ValueError("P10 inserted wrong, missing or prematurely approved artwork")
    glyphs={x["main_id"]:x for x in base["page_map"] if x["part"]==1}
    if set(glyphs)!=set(range(1,202)) or modified!={glyphs[mid]["preview_pdf_page"] for mid in STUDIES}:
        raise ValueError("P10 art placed on wrong character pages")
    all_strokes=0; untouched_pages=0; pixel_differences=[]
    with fitz.open(source_pdf) as source,fitz.open(candidate_pdf) as candidate:
        if len(source)!=260 or len(candidate)!=260:
            raise ValueError("P10 must preserve all 260 pages exactly")
        for number in range(1,261):
            before=source[number-1];after=candidate[number-1]
            if (abs(before.rect.width-after.rect.width)>.00001 or
                abs(before.rect.height-after.rect.height)>.00001):
                raise ValueError("A4 geometry changed")
            if number not in modified:
                # Same top-level document content and illustration absence on
                # all non-P10 pages, not merely equal text/number of steps.
                a=before.get_pixmap(matrix=fitz.Matrix(.65,.65),alpha=False)
                b=after.get_pixmap(matrix=fitz.Matrix(.65,.65),alpha=False)
                if (a.width!=b.width or a.height!=b.height or a.samples!=b.samples):
                    raise ValueError(f"P10 modified a non-art A4 page {number}")
                untouched_pages+=1
            else:
                text=after.get_text()
                if ("独立笔顺复核" not in text or
                    "尚未完成权威源及独立二审" not in text or
                    "原PDF笔顺提示·未获规范批准" not in text):
                    raise ValueError(f"P10 omitted the P9 authoritative-review warning: p{number}")
                x0,y0,x1,y1=(118,51,193,107)
                art_rect=fitz.Rect(x0*72/25.4,y0*72/25.4,x1*72/25.4,y1*72/25.4)
                p=before.get_pixmap(matrix=fitz.Matrix(.7,.7),clip=art_rect,alpha=False)
                q=after.get_pixmap(matrix=fitz.Matrix(.7,.7),clip=art_rect,alpha=False)
                if (p.width,p.height)!=(q.width,q.height):
                    raise ValueError("P10 art pane changed physical geometry")
                diff=np.abs(np.frombuffer(p.samples,dtype=np.uint8).astype(np.int16)-
                            np.frombuffer(q.samples,dtype=np.uint8).astype(np.int16))
                mae=float(diff.mean())
                if mae<12:
                    raise ValueError("P10 new art did not visually replace the old P9 text-only card")
                pixel_differences.append(round(mae,3))
                gray=ImageOps.grayscale(Image.frombytes("RGB",(q.width,q.height),q.samples))
                if ImageStat.Stat(gray).stddev[0]<9:
                    raise ValueError("P10 new artwork is too faint to inspect at page scale")
        for rec in base["page_map"]:
            page_number=rec["preview_pdf_page"]
            for step in rec["source_steps"]:
                clip=fitz.Rect(step["preview_rect_pt"])
                before=source[page_number-1].get_pixmap(matrix=fitz.Matrix(1.35,1.35),
                                                          clip=clip,alpha=False)
                after=candidate[page_number-1].get_pixmap(matrix=fitz.Matrix(1.35,1.35),
                                                            clip=clip,alpha=False)
                if (before.width,before.height)!=(after.width,after.height):
                    raise ValueError("Source cumulative stroke tile physical bounding box changed")
                if before.samples!=after.samples:
                    raise ValueError(f"Original PDF step ink changed: ID{rec['main_id']:03d} {step['index']}")
                all_strokes+=1
    if (all_strokes!=1045 or untouched_pages!=260-len(STUDIES)
        or len(pixel_differences)!=len(STUDIES)):
        raise ValueError("P10 full-book invariant broke")
    result={
        "result":"PASS_P10_INTEGRATED_DRAFT_ALL_1045_ORIGINAL_PEN_IMAGES_PIXEL_IDENTICAL",
        "draft_pdf_sha256":meta["output_pdf_sha256"],
        "unchanged_entire_pages_pixel_equal":untouched_pages,
        "all_pages_a4":260,
        "verified_source_original_stroke_tiles":all_strokes,
        "artist_studies_inserted":len(STUDIES),
        "art_panels_mean_absolute_difference":pixel_differences,
        "p8_pending_readings_printed":0,
        "artwork_human_approved":0,
        "physical_paper_print_confirmed":False,
        "normative_stroke_double_review_confirmed":False,
        "publication_eligible":False,
    }
    output_report.parent.mkdir(parents=True,exist_ok=True)
    output_report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=P9_PDF)
    p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--provenance",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    opt=p.parse_args()
    compare(opt.source,opt.candidate,opt.provenance,opt.output)

if __name__=="__main__":
    main()
