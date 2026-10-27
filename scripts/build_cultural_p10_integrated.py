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

ZI_ID=54
ZI_TIPS_RECT=fitz.Rect(mm(17.5),mm(161.0),mm(112),mm(177.5))
ZI_SECOND_CAPTION_RECT=fitz.Rect(mm(50),mm(217.7),mm(81),mm(226.5))

def quarantine_disputed_zi_label(book:fitz.Document,first:dict,p9_by_id:dict)->dict:
    """Quarantine unsafe legacy 子 pen-2 text, NEVER touch original red/gray ink.

    Old source states “第2笔是弯钩，不写成竖钩”, while the actual
    GF0023 original 5-category code is 521. This is an unresolved source
    classification disagreement, not an authorized correction to 竖钩.
    """
    zi=p9_by_id[ZI_ID]
    if (zi["character"]!="子" or zi["source_five_type_code_candidate"]!="551"
        or zi["secondary_reference_five_type_code"]!="521"
        or zi["source_step_records"][1]["name"]!="弯钩"
        or zi["differing_main_stroke_indexes"]!=[2]
        or zi["individual_stroke_names_verified"] is not False
        or zi["publication_eligible"] is not False):
        raise ValueError("Cannot quarantine 子 without confirming exact P9 disputed original evidence")
    number=first[ZI_ID]["preview_pdf_page"]
    page=book[number-1]
    original=page.get_text()
    if ("第2笔是弯钩，不写成竖钩。" not in original
        or "先横撇，再弯钩，最后写横。" not in original
        or "2  弯钩" not in original):
        raise ValueError("Original 子 disputed labels changed: do not redact using stale rectangles")
    page.add_redact_annot(ZI_TIPS_RECT,fill=(1,1,1))
    page.add_redact_annot(ZI_SECOND_CAPTION_RECT,fill=(1,1,1))
    page.apply_redactions(images=0,graphics=0,text=0)
    fonts()
    fallback=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
    if not fallback.is_file():raise ValueError("Missing fallback CJK font")
    if "CultureRare" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CultureRare",str(fallback),subfontIndex=0))
    out=io.BytesIO()
    c=canvas.Canvas(out,pagesize=(W,H),pageCompression=1,invariant=1)
    p=PageArtist(c)
    p.rect(18,161.3,93,16,"#FFFEFC")
    p.label(19,165.8,"子第二笔名称与现行笔顺五码存在疑点。",8.2,"Kai","#943E48")
    p.label(19,171.5,"旧提示已暂停使用，具体笔形待规范复核。",8.2,"Kai","#943E48")
    p.rect(50,218.4,31,8.0,"#FFFEFC")
    p.label(65.5,224,"2  笔名待核",8.1,"Kai","#943E48","center")
    c.save()
    with fitz.open(stream=out.getvalue(),filetype="pdf") as overlay:
        page.show_pdf_page(page.rect,overlay,0,overlay=True,keep_proportion=False)
    final=page.get_text()
    if ("第2笔是弯钩" in final or "先横撇，再弯钩" in final
        or "2  弯钩" in final or "笔名待核" not in final
        or "旧提示已暂停使用" not in final):
        raise ValueError("Disputed original teaching line was not visibly quarantined")
    return {
        "main_id":ZI_ID,"character":"子","preview_pdf_page":number,
        "legacy_second_stroke_name":"弯钩",
        "official_GF0023_code_from_prior_primary_evidence":"521",
        "review_candidate_fine_name":"竖钩",
        "child_facing_correction_approved":False,
        "legacy_tip_suppressed":True,
        "legacy_second_step_caption_suppressed":True,
        "source_original_cumulative_stroke_images_modified":False,
        "first_reviewer":None,"independent_second_reviewer":None,
        "release_eligible":False
    }

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
        zi_quarantine=quarantine_disputed_zi_label(book,first,p9_by_id)
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
        "disputed_stroke_tip_quarantines":1,
        "disputed_zi_second_stroke_quarantine":zi_quarantine,
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
