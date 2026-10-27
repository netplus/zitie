#!/usr/bin/env python3
"""P10: integrate only registered authored artwork into the frozen P9 260-page A4 proof.

No PDF glyph specimen, source stroke, candidate pronunciation or editorial
source is redrawn. The frozen P9 PDF is READ-ONLY; this produces a new DRAFT.
Art replaces only upper-right P9 review cards on registered character pages.
Every replacement reprints the normative-review warning below the illustration.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import fitz
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from build_cultural_fullbook import PageArtist, W, H, mm, MM
from build_cultural_sample import fonts
from cultural_p10_art_review import (
    ROOT, SOURCE_PDF, P9_PDF, P9_SHA, SHA, ART_DIR, STUDIES,
    audit_ledger, hash_file, make_ledger, paint_svg,
)

P9_PROOF=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/201-main-1045-stroke-full-page-provenance.json"
P9_STROKES=ROOT/"data/cultural_edition/p9_201_original_stroke_crosscheck.json"
PANEL=fitz.Rect(mm(118),mm(51),mm(193),mm(107))

def identity_evidence(proof:dict,p9:dict,ledger:dict)->dict:
    if (proof.get("source_pdf_sha256")!=SHA
        or proof.get("output_pdf_sha256")!=P9_SHA
        or proof.get("strict_pinyin_review_mode") is not True
        or proof.get("strict_P9_normative_stroke_review_mode") is not True
        or proof.get("output_pdf_pages")!=260
        or proof.get("reading_candidates_printed")!=0
        or proof.get("source_main_readings_printed")!=0
        or len(proof.get("page_map",[]))!=254
        or sum(len(p["source_steps"]) for p in proof["page_map"])!=1045):
        raise ValueError("P10 must take its immutable 260-page source from the strict P8/P9 review master")
    if (p9.get("frozen_source_pdf_sha256")!=SHA
        or len(p9.get("entries",[]))!=201
        or ledger.get("release_eligible") is not False):
        raise ValueError("P9 normative review evidence or P10 art safeguards changed")
    first={p["main_id"]:p for p in proof["page_map"] if p["part"]==1}
    if len(first)!=201 or set(first)!=set(range(1,202)):
        raise ValueError("One P10 art slot for each of the original 201 characters is required")
    if {p["main_id"] for p in p9["entries"]}!=set(range(1,202)):
        raise ValueError("P9 stroke source IDs drifted")
    return first

def make_overlay(mid:int,evidence:dict,root:Path=ROOT)->bytes:
    fonts()
    rare=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
    if not rare.is_file():raise ValueError("P10 art proof needs a packaged rare-CJK font")
    if "CultureRare" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CultureRare",str(rare),subfontIndex=0))
    char,scene,filename,description,motifs=STUDIES[mid]
    content=io.BytesIO()
    c=canvas.Canvas(content,pagesize=(W,H),pageCompression=1,invariant=1)
    a=PageArtist(c)
    a.rect(118,51,75,68,"#FFFEFC")
    paint_svg(c,root/"data/cultural_edition/artwork/p10_studies"/filename,119,52,73,53)
    a.rect(118,105,75,13,"#FFFEFC")
    a.label(120,109.7,"独立笔顺复核 · 新插画仅供美术审阅",7.3,"Kai","#943E48")
    a.label(120,115.9,"尚未完成权威源及独立二审",7.3,"Kai","#943E48")
    c.save()
    return content.getvalue()

def generate(out_path:Path,metadata_path:Path,root:Path=ROOT)->dict:
    root=Path(root)
    if (hash_file(root/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf")!=SHA
        or hash_file(root/"deliverables/drafts/cultural-v0.9-stroke-review/zitie-201-P9-normative-stroke-review-UNREVIEWED.pdf")!=P9_SHA):
        raise ValueError("Immutable released source or normative master has changed")
    ledger=make_ledger(root);audit_ledger(ledger)
    proof=json.loads((root/P9_PROOF.relative_to(ROOT)).read_text(encoding="utf8"))
    p9=json.loads((root/P9_STROKES.relative_to(ROOT)).read_text(encoding="utf8"))
    first=identity_evidence(proof,p9,ledger)
    p9_by_id={r["main_id"]:r for r in p9["entries"]}
    mapped=[]
    out_path.parent.mkdir(parents=True,exist_ok=True)
    with fitz.open(root/P9_PDF.relative_to(ROOT)) as book:
        for mid in sorted(STUDIES):
            card=first[mid];number=card["preview_pdf_page"]
            if (card["character"]!=STUDIES[mid][0]
                or p9_by_id[mid]["character"]!=STUDIES[mid][0]):
                raise ValueError("An illustration no longer matches the original source ID")
            target=book[number-1]
            # No source ink exists at PANEL: steps on the first character page
            # begin in the lower left. Text removal is local to the old warning.
            target.add_redact_annot(PANEL,fill=(1,1,1))
            target.apply_redactions(images=0,graphics=0,text=0)
            layer=make_overlay(mid,p9_by_id[mid],root)
            with fitz.open(stream=layer,filetype="pdf") as overlay:
                target.show_pdf_page(target.rect,overlay,0,overlay=True,keep_proportion=False)
            mapped.append({
                "main_id":mid,"character":STUDIES[mid][0],
                "replaced_card_pdf_page":number,"scene_key":STUDIES[mid][1],
                "scene_file":STUDIES[mid][2],
                "scene_sha256":hash_file(root/"data/cultural_edition/artwork/p10_studies"/STUDIES[mid][2]),
                "inset_rect_mm":[119,52,73,53],
                "P9_card_replaced_with_explicit_pending_notice":True,
                "art_human_review_approved":False,
            })
        book.set_metadata({
           "title":"P10 文化识字插画融合试装校对母稿，未审勿印",
           "author":"netplus/zitie",
           "subject":"P8/P9严格禁音，原PDF1045笔不变；P10仅插入未审文化主题画",
           "keywords":"P10,201,1045,source-locked,art studies,UNREVIEWED",
        })
        book.save(out_path,garbage=4,deflate=True,no_new_id=True)
    qa={
        "schema_version":1,
        "result":"P10_201_GLYPH_INTEGRATED_ART_DIRECTION_DRAFT_NOT_FOR_PUBLICATION",
        "source_v051_pdf_sha256":SHA,
        "source_P9_pdf_sha256":P9_SHA,
        "source_P9_pdf_pages":260,
        "output_pdf_sha256":hash_file(out_path),
        "output_pdf_bytes":out_path.stat().st_size,
        "output_pdf_pages":260,
        "source_main_glyphs":201,
        "source_stroke_tiles_expected_untouched":1045,
        "source_batch_count":21,
        "main_pinyin_approved_and_printed":0,
        "candidate_terms_pinyin_printed":0,
        "P10_art_studies_integrated":len(mapped),
        "unillustrated_201_main_ids":201-len(mapped),
        "artwork_human_approvals":0,
        "original_source_modified":False,
        "paper_print_approval":False,
        "release_eligible":False,
        "page_artwork_register":mapped,
    }
    metadata_path.parent.mkdir(parents=True,exist_ok=True)
    metadata_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in qa.items() if k!="page_artwork_register"},ensure_ascii=False,indent=2))
    return qa

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--qa",required=True,type=Path)
    args=parser.parse_args()
    generate(args.output,args.qa)

if __name__=="__main__":
    main()
