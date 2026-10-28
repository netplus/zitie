#!/usr/bin/env python3
"""P9.5 source-backed correction: restore 子 stroke #2 fine name 弯钩.

The Ministry 2013 calligraphy guideline and the PEP 2024 primary-school
textbook both use 子 as an example of 弯钩; 小 is the example of 竖钩.
The five-category GF0023 code 521 does not independently determine a
fine teaching name. Do not alter stroke geometry or approve publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import fitz
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RELEASE="deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
SOURCE_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
BASE="deliverables/drafts/cultural-v0.11.1-two-pass-260-CJK-embedded-UNREVIEWED/zitie-cultural-201-two-pass-reassembled-260-UNREVIEWED.pdf"
BASE_SHA="459e29ea0ae030453eaa20f5c4deff9a583f6a337aa532b11e83a74166c8b4f3"
EVIDENCE="data/cultural_edition/p9_zi_wangou_primary_teaching_20261028.json"
RISK="data/cultural_edition/p9_normative_open_cases_37_83.json"
P9_PROOF="deliverables/drafts/cultural-v0.9-stroke-review/201-main-1045-stroke-full-page-provenance.json"
P6="data/cultural_edition/p6_release_human_signoffs.json"
FONT=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
FONT_NAME="PrimaryZiCJK"
PAGE=30
ORIGINAL_TEXTS=(
    "子第二笔名称与现行笔顺五码存在疑点。",
    "旧提示已暂停使用，具体笔形待规范复核。",
    "2  笔名待核",
)
NEW_TEXTS=(
    "先横撇，再写弯钩，最后写横。",
    "“子”的第二笔是弯钩（据教育部笔画名称表）。",
    "原字帖笔形、起收笔细节仍待复核。",
    "2  弯钩",
)
TEXT_RECT=fitz.Rect(49.5,455,319,506)
NAME_RECT=fitz.Rect(145,615,230,642)

def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(root:Path,name:str):
    return json.loads((root/name).read_text(encoding="utf8"))

def validate_evidence(root:Path):
    e=load(root,EVIDENCE);risk=load(root,RISK);p=load(root,P9_PROOF)
    source=load(root,P6)
    case=risk["fine_name_vs_official_coarse_conflicts"]
    if (len(case)!=1 or case[0]["main_id"]!=54
        or case[0]["legacy_name"]!="弯钩"
        or case[0]["candidate_correction_for_first_review"]!="弯钩"
        or case[0]["prior_proposed_correction_now_refuted_by_published_pedagogical_examples"]!="竖钩"
        or case[0]["approved_new_label"] is not None
        or case[0]["first_reviewer"] is not None
        or case[0]["second_reviewer"] is not None
        or case[0]["authoritative_picture_and_geometry_full_approval"] is not False
        or len(risk["out_of_scope_characters"])!=37
        or len(risk["unknown_fine_name_steps"])!=83):
        raise ValueError("P9 evidence is not an authorized fine-name reassessment")
    target=e["subject"]
    sources=e["sources"]
    if (e.get("document_kind")!="P9_ZI_ID054_MOE_2013_AND_PEP_2024_FINE_STROKE_NAME_REASSESSMENT"
        or e.get("frozen_v051_pdf_sha256")!=SOURCE_SHA
        or e.get("frozen_v0111_pdf_sha256")!=BASE_SHA
        or e.get("release_eligible") is not False
        or e.get("publication_eligible") is not False
        or (target["main_id"],target["character"],target["step_index"])!=(54,"子",2)
        or (target["source_old_fine_name"],target["reassessed_fine_name"])!=("弯钩","弯钩")
        or target["GF0023_official_numeric_sequence"]!="521"
        or len(sources)!=2
        or sources[0]["pdf_physical_page_1based"]!=16
        or sources[0]["first_example"]!={"fine_name":"弯钩","character":"子"}
        or sources[0]["contrasting_example"]!={"fine_name":"竖钩","character":"小"}
        or sources[0]["original_page_visually_checked"] is not True
        or sources[1]["printed_page_number"]!=109
        or sources[1]["first_example"]!={"fine_name":"弯钩","character":"子"}
        or sources[1]["independent_full_byte_download"] is not False
        or e["reasoning"]["geometry_as_printed_verified_against_all_normative_figures"] is not False
        or e["reasoning"]["human_first_reviewer"] is not None
        or e["reasoning"]["independent_human_second_reviewer"] is not None
        or p.get("output_pdf_pages")!=260
        or p.get("source_pdf_sha256")!=SOURCE_SHA
        or sum(len(x["source_steps"]) for x in p["page_map"])!=1045
        or source.get("release_eligible") is not False):
        raise ValueError("Ministry/PEP fine-name source and P6 guards do not match")
    parts=[x for x in p["page_map"] if x["main_id"]==54 and x["part"]==1]
    if len(parts)!=1 or parts[0]["preview_pdf_page"]!=PAGE:
        raise ValueError("Original 子 source step identity or PDF page changed")
    for step in parts[0]["source_steps"]:
        ink=fitz.Rect(step["preview_rect_pt"])
        if TEXT_RECT.intersects(ink) or NAME_RECT.intersects(ink):
            raise ValueError("Proposed text redaction intersects a real old-PDF pen tile")
    return e,p

def verify_pixel_scope(before:fitz.Page,after:fitz.Page):
    scale=.80;m=fitz.Matrix(scale,scale)
    a=before.get_pixmap(matrix=m,alpha=False)
    b=after.get_pixmap(matrix=m,alpha=False)
    if (a.width,a.height)!=(b.width,b.height):
        raise ValueError("A4 physical size changed")
    one=np.frombuffer(a.samples,dtype=np.uint8).reshape(a.height,a.width,3)
    two=np.frombuffer(b.samples,dtype=np.uint8).reshape(b.height,b.width,3)
    changed=np.any(one!=two,axis=2)
    yy,xx=np.nonzero(changed)
    if len(xx)<100:raise ValueError("Ministry-backed name correction did not actually render")
    allowed=(TEXT_RECT+(-3,-3,3,3),NAME_RECT+(-3,-3,3,3))
    for x,y in zip(xx,yy):
        pt=fitz.Point(float(x)/scale,float(y)/scale)
        if not any(rect.contains(pt) for rect in allowed):
            raise ValueError(f"Modified text outside two allowed original-ink-free rectangles: {pt}")
    return {
       "changed_rgb_pixels":int(changed.sum()),
       "changed_bbox_pt":[round(float(xx.min())/scale,2),round(float(yy.min())/scale,2),
                          round(float(xx.max()+1)/scale,2),round(float(yy.max()+1)/scale,2)]
    }

def build(output:Path,report:Path,root:Path=ROOT):
    root=Path(root)
    source=root/RELEASE;base=root/BASE
    if (sha(source)!=SOURCE_SHA or sha(base)!=BASE_SHA or
        not FONT.is_file()):
        raise ValueError("Old v0.5.1 / v0.11.1 bytes or the required embedded Chinese font changed")
    evidence,proof=validate_evidence(root)
    output.parent.mkdir(parents=True,exist_ok=True)
    with fitz.open(base) as book:
        if len(book)!=260:raise ValueError("Full 260 pages must remain")
        page=book[PAGE-1]
        text=page.get_text()
        if any(text.count(x)!=1 for x in ORIGINAL_TEXTS):
            raise ValueError("Cannot blindly overlay or change a previously corrected 子 page")
        if not("原PDF笔顺提示·未获规范批准" in text and
               "禁止作为正式教材发行" in text and
               "画意分镜 · 插图待绘" in text):
            raise ValueError("P9 warnings and P10 art storyboard must remain intact")
        for r in (TEXT_RECT,NAME_RECT):
            page.add_redact_annot(r,fill=(1,1,1))
        page.apply_redactions(images=0,graphics=0,text=0)
        page.insert_font(fontname=FONT_NAME,fontfile=str(FONT))
        for y,line,fontsize in ((470,NEW_TEXTS[0],8.3),
                                (483,NEW_TEXTS[1],8.1),
                                (496,NEW_TEXTS[2],8.1)):
            page.insert_text((53.85,y),line,fontname=FONT_NAME,
                             fontsize=fontsize,color=(.48,.30,.33))
        page.insert_text((165,634.5),NEW_TEXTS[3],fontname=FONT_NAME,
                         fontsize=8.8,color=(.54,.26,.32))
        now=page.get_text()
        if (any(x in now for x in ORIGINAL_TEXTS) or
            any(now.count(x)!=1 for x in NEW_TEXTS)):
            raise ValueError("An obsolete name is still visible or the new name failed to render")
        book.set_metadata({
          "title":"文化识字201字·子笔名教育部原表复核·260页未审稿",
          "author":"netplus/zitie",
          "subject":"仅纠正子第二笔教学细名弯钩。GF0023 521的粗数码差异和全1045笔画几何仍需权威复核。",
          "keywords":"P9,子,弯钩,MOE,PEP,260,draft,UNREVIEWED",
        })
        book.save(output,garbage=4,deflate=True,no_new_id=True)
    # Full 260-page audit: 259 pages visually unchanged, ALL 1045 source
    # pen steps compared as raster ink at their frozen physical locations.
    unchanged=0;pen_count=0
    with fitz.open(base) as old,fitz.open(output) as new:
        if len(old)!=260 or len(new)!=260:
            raise ValueError("Page count modified")
        if old.get_toc()!=new.get_toc():
            raise ValueError("Original 201-character PDF bookmarks changed")
        for n in range(260):
            p=old[n];q=new[n]
            if p.rect!=q.rect:raise ValueError("A4 geometry changed")
            if n+1!=PAGE:
                raster=fitz.Matrix(.63,.63)
                a=p.get_pixmap(matrix=raster,alpha=False)
                b=q.get_pixmap(matrix=raster,alpha=False)
                if (a.width,a.height,a.samples)!=(b.width,b.height,b.samples):
                    raise ValueError(f"An unrelated full A4 page unexpectedly changed: {n+1}")
                unchanged+=1
        change=verify_pixel_scope(old[PAGE-1],new[PAGE-1])
        m=fitz.Matrix(1.3,1.3)
        for item in proof["page_map"]:
            pn=item["preview_pdf_page"]
            for step in item["source_steps"]:
                box=fitz.Rect(step["preview_rect_pt"])
                a=old[pn-1].get_pixmap(matrix=m,clip=box,alpha=False)
                b=new[pn-1].get_pixmap(matrix=m,clip=box,alpha=False)
                if (a.width,a.height,a.samples)!=(b.width,b.height,b.samples):
                    raise ValueError(f"Original old-PDF pen ink changed ID{item['main_id']:03d} step{step['index']}")
                pen_count+=1
        if pen_count!=1045 or unchanged!=259:
            raise ValueError("All 201 main IDs and 1045 source pen cards are required")
        if len([x for x in new[PAGE-1].get_fonts(full=True)
                if x[2]=="Type0" and x[1]=="n/a"])>0:
            raise ValueError("New Chinese fine-name font must actually be embedded")
    qa={
      "schema_version":1,
      "result":"PASS_MINISTRY_PEP_ZI_WANGOU_FINE_NAME_RESTORED_260_PAGES_1045_INK_PIXEL_IDENTICAL",
      "source_formal_pdf_sha256":SOURCE_SHA,
      "input_v0111_pdf_sha256":BASE_SHA,
      "output_pdf_sha256":sha(output),
      "output_pdf_bytes":output.stat().st_size,
      "output_A4_pages":260,
      "unmodified_complete_A4_pages_pixel_equal":unchanged,
      "old_pdf_1045_source_ink_tiles_pixel_identical":pen_count,
      "teacher_pedagogical_name_from_MOE":"弯钩",
      "prior_unfounded_竖钩_guess_retracted":True,
      "amended_main_glyph":"子",
      "amended_main_id":54,
      "amended_physical_PDF_page":30,
      "changed_text_only_in_two_source_ink_free_rectangles":True,
      **change,
      "GF0023_5category_code_521_still_logged":True,
      "37_special_radicals_not_yet_normatively_approved":True,
      "83_unknown_specific_pen_names_not_yet_approved":True,
      "exact_201_1045_ink_geometry_human_double_review_complete":False,
      "201_final_professional_illustrations_approved":0,
      "P8_1013_lexical_pronunciations_approved":0,
      "P5_real_paper_print_completed":False,
      "P6_user_release_approved":False,
      "release_eligible":False,
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(qa,ensure_ascii=False,indent=2))
    return qa

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--qa",type=Path,required=True)
    args=ap.parse_args()
    build(args.output,args.qa)

if __name__=="__main__":main()
