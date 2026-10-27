#!/usr/bin/env python3
"""P10 preliminary *entire-book* P5 electronic/gray layout screening.

This is NOT a physical-paper check, independent literacy/content review or
P6 publication. It reads only the frozen P9 editorial master and its proof.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageOps, ImageStat

from cultural_p10_art_review import ROOT, SHA, P9_SHA, audit_ledger, make_ledger

P9=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/zitie-201-P9-normative-stroke-review-UNREVIEWED.pdf"
P9_PROOF=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/201-main-1045-stroke-full-page-provenance.json"
SOURCE=ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"

def scan(output_dir:Path,root:Path=ROOT):
    root=Path(root)
    assert audit_ledger(make_ledger(root))["undrawn_remaining"]==197
    source=root/SOURCE.relative_to(ROOT)
    pdf=root/P9.relative_to(ROOT)
    provenance=root/P9_PROOF.relative_to(ROOT)
    if hashlib.sha256(source.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Released 299-page v0.5.1 was touched")
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=P9_SHA:
        raise ValueError("P9 PDF changed while P10 art is under review")
    proof=json.loads(provenance.read_text(encoding="utf8"))
    pages=proof.get("page_map",[])
    if (proof.get("source_pdf_sha256")!=SHA
        or proof.get("strict_pinyin_review_mode") is not True
        or proof.get("strict_P9_normative_stroke_review_mode") is not True
        or proof.get("output_pdf_sha256")!=P9_SHA
        or len(pages)!=254
        or sum(len(r["source_steps"]) for r in pages)!=1045):
        raise ValueError("P9 provenance no longer gives exactly 201 glyphs and 1045 strokes")
    by_batch=collections.defaultdict(list)
    seen=set();firsts=[];continuations=[]
    for rec in pages:
        p=rec["preview_pdf_page"]
        if p in seen or not 7<=p<=260:
            raise ValueError("Source page duplicated, missing or outside valid A4 book")
        seen.add(p)
        if rec["part"]==1:
            firsts.append(rec["main_id"])
        else:
            continuations.append(p)
        by_batch[rec["batch_id"]].append(p)
    if (seen!=set(range(7,261))
        or len(firsts)!=201 or set(firsts)!=set(range(1,202))
        or len(continuations)!=53 or len(by_batch)!=21):
        raise ValueError("Whole-book page coverage, 201 index or continuation is incomplete")
    output_dir.mkdir(parents=True,exist_ok=True)
    gallery=output_dir/"P5-grayscale-21-batches"
    gallery.mkdir(parents=True,exist_ok=True)
    previews=output_dir/"P5-per-page"
    previews.mkdir(parents=True,exist_ok=True)
    errors=[];gray_stats=[]
    w,h=178,251;gap=10;cols=5
    # One visual image per physical page + 21 entire-batch montages;
    # all source page numbers are taken from P9's original provenance.
    thumbnails={}
    with fitz.open(pdf) as book:
        if len(book)!=260:raise ValueError("P9 frozen master does not have 260 pages")
        for page_number,page in enumerate(book,1):
            if not(594<=page.rect.width<=597 and 840<=page.rect.height<=843):
                errors.append(f"p{page_number}: non-A4 physical media box")
            extracted=page.get_text()
            if not extracted.strip():
                errors.append(f"p{page_number}: empty page text")
            if "\uFFFD" in extracted or "\x00" in extracted:
                errors.append(f"p{page_number}: tofu or null replacement in text stream")
            for blk in page.get_text("dict")["blocks"]:
                if blk.get("type")!=0:continue
                x0,y0,x1,y1=blk["bbox"]
                if x0<-.8 or y0<-.8 or x1>page.rect.width+.8 or y1>page.rect.height+.8:
                    errors.append(f"p{page_number}: text block outside printable media box")
                    break
            pix=page.get_pixmap(matrix=fitz.Matrix(.55,.55),alpha=False)
            image=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
            grayscale=ImageOps.grayscale(image)
            sigma=ImageStat.Stat(grayscale).stddev[0]
            if sigma<7:
                errors.append(f"p{page_number}: nearly blank grayscale page")
            gray_stats.append(round(sigma,2))
            preview=grayscale.resize((w,h),Image.Resampling.LANCZOS)
            preview.convert("RGB").save(previews/f"p-{page_number:03d}-gray.png")
            thumbnails[page_number]=preview
        for batch,nums in sorted(by_batch.items()):
            rows=(len(nums)+cols-1)//cols
            sheet=Image.new("RGB",(gap+cols*(w+gap),gap+rows*(h+28)),"#EEEDEB")
            draw=ImageDraw.Draw(sheet)
            for k,physical in enumerate(nums):
                x=gap+k%cols*(w+gap);y=gap+k//cols*(h+28)
                sheet.paste(thumbnails[physical].convert("RGB"),(x,y))
                draw.text((x,y+h+4),f"{batch} / p.{physical}",fill="#1A2022")
            sheet.save(gallery/f"{batch}-all-pages-gray.png",optimize=True)
    if errors:
        raise ValueError("P5 fullbook screen inspection errors:\n"+"\n".join(errors[:35]))
    report={
       "result":"PASS_P10_P5_ELECTRONIC_ALL_260_PAGE_GRAYSCALE_AND_LAYOUT_PRE_SCREEN_ONLY",
       "source_pdf_sha256":SHA,"frozen_P9_pdf_sha256":P9_SHA,
       "a4_pages_electronically_rendered":260,
       "source_main_id_review_pages":201,"source_1045_strokes_retained":1045,
       "continuation_pages":53,"front_matter_pages":6,
       "batch_grayscale_contact_sheets":21,
       "all_pages_have_printable_text":True,
       "no_out_of_media_text_blocks":True,
       "gray_sigma_min":min(gray_stats),"gray_sigma_max":max(gray_stats),
       "paper_hardware_tested":False,
       "physically_printed_pages":0,
       "editorial_approved_pinyin_slots":0,
       "professionally_approved_illustrations":0,
       "human_source_stroke_double_review_complete":False,
       "P6_release_eligible":False,
       "note":"This is preliminary electronic screening of the prior P9 art-free proof, not final P5 acceptance or approval of a published teaching book."
    }
    (output_dir/"P5-all-260-electronic-screening-UNREVIEWED.json").write_text(
       json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    scan(args.output_dir)
