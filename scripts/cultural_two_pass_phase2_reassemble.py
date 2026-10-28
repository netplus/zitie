#!/usr/bin/env python3
"""Two-pass cultural book, stage TWO: final reassembly of 260 A4 review pages.

The 8 individually authored scenes remain explicitly UNAPPROVED. For the 193
other characters we insert uniquely worded, character-linked ART STORYBOARDS,
never misleadingly describe algorithmic placeholders as finished paintings.
The 114 stage-one teaching-hint corrections and all 1045 original P9 pen
vector tiles remain pixel-identical. This is a finished 260-PAGE ENGINEERING
REVIEW MANUSCRIPT, NOT an approved children's textbook or P6 release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import fitz

from cultural_fullbook_model import ROOT, SHA, checked_drafts
from cultural_two_pass_phase1_safety import (
    BASE_SHA, NEW as PASS1_NEW, OLD as PASS1_OLD,
    P9, SOURCE, SOURCE_SHA, digest, verified_proof,
)

PANEL=fitz.Rect(118*72/25.4,51*72/25.4,193*72/25.4,106*72/25.4)
MM=72/25.4
VERSION="cultural-v0.11-two-pass-260-editorial-review"
RELEASE=False
TITLE="文化识字 · 两轮修订260页整书校对稿"

PALETTE=(
  ((.52,.36,.31),(.989,.974,.955)),
  ((.36,.48,.47),(.973,.981,.967)),
  ((.58,.44,.34),(.988,.978,.963)),
  ((.47,.43,.58),(.979,.977,.989)),
  ((.39,.50,.42),(.972,.981,.972)),
  ((.55,.38,.43),(.985,.973,.969)),
  ((.42,.49,.57),(.977,.983,.988)),
)

def read(root:Path,rel:str):
    return json.loads((root/rel).read_text(encoding="utf8"))

def load_cards(root:Path=ROOT):
    root=Path(root)
    manuscripts=checked_drafts(root)
    a=read(root,"data/cultural_edition/p10_study_inventory.json")
    if (a.get("source_pdf_sha256")!=SOURCE_SHA
        or a.get("release_eligible") is not False
        or set(manuscripts)!=set(range(1,202))
        or len(a.get("entries",[]))!=8):
        raise ValueError("201 editorial source IDs and eight still-unapproved art studies required")
    studies={x["main_id"]:x for x in a["entries"]}
    if (len(studies)!=8 or any(x.get("publication_eligible") is not False
        or x.get("art_direction_status")!="unreviewed"
        or x.get("visual_human_first_review") is not None
        or x.get("visual_human_second_review") is not None
        for x in studies.values())):
        raise ValueError("P10 scene inventory may not claim final art approvals")
    result={}
    for mid,manuscript in manuscripts.items():
        if (manuscript.get("main_id")!=mid
            or manuscript.get("release_eligible") is not False
            or manuscript.get("editorial_status")!="candidate_not_reviewed"
            or any(x.get("review_status") not in ("review_pending","blocked")
                    and x.get("reading_review")!="unreviewed_candidate"
                    for x in manuscript["terms"])):
            raise ValueError("Unreviewed P8/201 editorial context changed")
        result[mid]={
            "main_id":mid,"character":manuscript["character"],
            "theme_key":manuscript["theme_key"],
            "title":manuscript["title"],
            "word_example_count":len(manuscript["terms"]),
            "art_brief":manuscript.get("art_brief"),
            "illustration_study_available":mid in studies,
            "P10_scene_human_approved":False,
            "publication_eligible":False,
        }
    if sum(x["word_example_count"] for x in result.values())!=812:
        raise ValueError("P8 812 editorial examples lost in second pass")
    absent={i:r for i,r in result.items() if i not in studies}
    if len(absent)!=193 or any(not isinstance(r["art_brief"],str)
                               or len(r["art_brief"].strip())<6 for r in absent.values()):
        raise ValueError("All 193 undrawn pictures need a real, independently authored semantic storyboard")
    if len({r["art_brief"] for r in absent.values()})!=193:
        raise ValueError("No identical generic composition can stand in for two different characters")
    return result,studies

def lines_for(content:str,font:fitz.Font,size:float,max_pts:float):
    lines=[];run=""
    for ch in content.strip():
        if font.text_length(run+ch,fontsize=size)<=max_pts:
            run+=ch
        else:
            if not run: raise ValueError("A composed glyph cannot fit a scene-brief row")
            lines.append(run);run=ch
    if run:lines.append(run)
    return lines

def draw_storyboard_card(page:fitz.Page,mid:int,row:dict,font:fitz.Font):
    scene=row["art_brief"];accent,background=PALETTE[(mid//10)%len(PALETTE)]
    raw_rect=PANEL
    page.add_redact_annot(raw_rect,fill=(1,1,1))
    page.apply_redactions(images=0,graphics=0,text=0)
    # A warm fine-lined typographic storyboard, not a substitute drawing.
    page.draw_rect(raw_rect,color=(.83,.78,.72),fill=background,width=.65)
    page.draw_rect(fitz.Rect(121*MM,55*MM,122.2*MM,99*MM),
                   color=accent,fill=accent,width=0)
    page.insert_text((125*MM,61*MM),"画意分镜 · 插图待绘",
                     fontname="china-s",fontsize=9.5,color=accent)
    page.draw_line((125*MM,64*MM),(188*MM,64*MM),color=(.78,.72,.67),width=.75)
    page.insert_text((125*MM,73*MM),f"ID{mid:03d} · 独立构思",
                     fontname="china-s",fontsize=8.3,color=(.40,.42,.43))
    wrapped=lines_for(scene,font,9.1,63*MM)
    if not 1<=len(wrapped)<=4:
        raise ValueError(f"ID{mid:03d} storyboard is too long for legible 75mm panel")
    y=83
    for ln in wrapped:
        page.insert_text((125*MM,y*MM),ln,fontname="china-s",fontsize=9.1,
                         color=(.25,.30,.31))
        y+=6.3
    if y>108:
        raise ValueError("Storyboard text overlaps the source-review warning")
    page.insert_text((125*MM,102*MM),"题材说明 · 尚非完成插画",
                     fontname="china-s",fontsize=7.0,color=(.53,.45,.42))
    # Preserve an explicit warning where the earlier P9 review-card label was.
    page.draw_rect(fitz.Rect(118*MM,106*MM,193*MM,117.5*MM),
                   color=None,fill=(.999,.995,.988),width=0)
    page.insert_text((120*MM,112*MM),"规范笔形、读音及插画均须独立审查",
                     fontname="china-s",fontsize=7.2,color=(.57,.28,.32))
    after=page.get_text()
    if ("画意分镜" not in after or "插图待绘" not in after
        or "规范笔形、读音及插画均须独立审查" not in after
        or scene not in after.replace("\n","")):
        raise ValueError(f"ID{mid:03d} has unreadable or missing original cultural visual brief")
    return wrapped

def cover_upgrade(page:fitz.Page):
    phrase="笔顺规范校对母稿"
    if page.get_text().count(phrase)!=1 or len(page.search_for(phrase))!=1:
        raise ValueError("The frozen six-page introduction changed unexpectedly")
    rect=fitz.Rect(72,269,480,307)
    if not rect.contains(page.search_for(phrase)[0]):
        raise ValueError("Cover title changed position, refusing blind erasure")
    page.add_redact_annot(rect,fill=(1,1,1))
    page.apply_redactions(images=0,graphics=0,text=0)
    page.insert_text((74,296),"两轮修订 · 260页整书校对稿",
                     fontname="china-s",fontsize=19.0,color=(.54,.28,.32))
    if "两轮修订" not in page.get_text() or phrase in page.get_text():
        raise ValueError("Full-book cover version not updated")

def generate(stage1_pdf:Path,stage1_qa:Path,output:Path,qa:Path,root:Path=ROOT):
    root=Path(root)
    stage1=read(root,stage1_qa.as_posix()) if not stage1_qa.is_absolute() else json.loads(stage1_qa.read_text(encoding="utf8"))
    if (stage1.get("source_cultural_v010_draft_sha256")!=BASE_SHA
        or stage1.get("output_pdf_pages")!=260
        or stage1.get("misleading_already_normative_verified_claims_removed")!=114
        or stage1.get("original_cumulative_pen_tiles_exactly_unchanged")!=1045
        or stage1.get("release_eligible") is not False
        or digest(stage1_pdf)!=stage1.get("output_draft_sha256")
        or digest(root/SOURCE.relative_to(ROOT))!=SOURCE_SHA):
        raise ValueError("Phase 2 must use the actual verified phase-one PDF, not stale P9 data")
    _,page_refs=verified_proof(root)
    by_first={r["main_id"]:r for r in page_refs.values() if r["part"]==1}
    if len(by_first)!=201 or set(by_first)!=set(range(1,202)):
        raise ValueError("All 201 original main-character page locations required")
    manuscripts,studies=load_cards(root)
    font=fitz.Font("china-s")
    rows=[];touched={1};output.parent.mkdir(parents=True,exist_ok=True)
    with fitz.open(stage1_pdf) as book:
        if len(book)!=260:
            raise ValueError("Source is not the expected 260 A4 pages")
        cover_upgrade(book[0])
        for mid in sorted(manuscripts):
            row=manuscripts[mid];entry=by_first[mid];pnum=entry["preview_pdf_page"]
            p=book[pnum-1]
            if row["character"]!=entry["character"] or f"ID{mid:03d}" not in p.get_text():
                raise ValueError("Second pass art cannot be placed on a mismatched source glyph")
            original_source_steps=entry["source_steps"]
            if any(PANEL.intersects(fitz.Rect(s["preview_rect_pt"])) for s in original_source_steps):
                raise ValueError(f"A supposed illustration panel intersects original ink ID{mid}")
            if mid in studies:
                # The eight source-locked SVG panels are left untouched.
                if "新插画仅供美术审阅" not in p.get_text():
                    raise ValueError("An existing authored artwork study was silently replaced")
                status="individually_authored_svg_study_unapproved"
                lines=[]
            else:
                if "独立笔顺复核" not in p.get_text():
                    raise ValueError("An expected P9 review card is absent")
                lines=draw_storyboard_card(p,mid,row,font)
                touched.add(pnum)
                status="character_specific_storyboard_pending_professional_painting"
            rows.append({
                "main_id":mid,"character":row["character"],"batch_id":entry["batch_id"],
                "pdf_page":pnum,"theme_key":row["theme_key"],
                "published_art":False,
                "asset_status":status,
                "artwork_original_description":row["art_brief"],
                "visual_brief_lines":lines,
                "original_pen_tiles_touched":False,
                "human_art_or_pronunciation_approved":False,
                "release_eligible":False,
            })
        meta={
          "title":TITLE,
          "author":"netplus/zitie",
          "subject":"两轮完成260页全量校对排版；114处笔顺假已核提示隔离；201个场景关联；1045源笔画保真；出版未批准",
          "keywords":"260,A4,201,1045,1013,pass1,pass2,storyboard-not-painting,UNREVIEWED",
        }
        book.set_metadata(meta)
        book.save(output,garbage=4,deflate=True,no_new_id=True)
    with fitz.open(stage1_pdf) as first,fitz.open(output) as final:
        if len(first)!=260 or len(final)!=260:
            raise ValueError("Stage two changed full-book physical page count")
        untouched=0
        matrix=fitz.Matrix(.70,.70)
        for idx in range(260):
            if idx+1 in touched:continue
            a=first[idx].get_pixmap(matrix=matrix,alpha=False)
            b=final[idx].get_pixmap(matrix=matrix,alpha=False)
            if (a.width,a.height,a.samples)!=(b.width,b.height,b.samples):
                raise ValueError(f"Unexpected change outside 193 storyboard cards on p{idx+1}")
            untouched+=1
        if untouched!=66 or len(touched)!=194:
            raise ValueError("Stage two modified the wrong number of pages")
        if sum(PASS1_OLD in x.get_text() for x in final)!=0:
            raise ValueError("A phase-one false normative claim reappeared")
        if sum(PASS1_NEW in x.get_text() for x in final)!=114:
            raise ValueError("Phase-one 114 review warnings disappeared")
        source_ink_count=0
        for entry in page_refs.values():
            pnum=entry["preview_pdf_page"]
            for step in entry["source_steps"]:
                clip=fitz.Rect(step["preview_rect_pt"]);m=fitz.Matrix(1.25,1.25)
                before=first[pnum-1].get_pixmap(matrix=m,clip=clip,alpha=False)
                after=final[pnum-1].get_pixmap(matrix=m,clip=clip,alpha=False)
                if (before.width,before.height,before.samples)!=(after.width,after.height,after.samples):
                    raise ValueError(f"Character ID{entry['main_id']:03d} original red-gray pen {step['index']} changed")
                source_ink_count+=1
        if source_ink_count!=1045:
            raise ValueError("Full original source ink coverage incomplete")
        if len(final.get_toc())!=len(first.get_toc()):
            raise ValueError("201-character PDF bookmarks were lost")
    evidence={
      "schema_version":1,
      "result":"TWO_PASSES_COMPLETE_260_PAGE_A4_CULTURAL_EDITORIAL_DRAFT_201_STORYBOARD_LINKS_1045_ORIGINAL_PEN_TILES",
      "phase_one_output_sha256":stage1["output_draft_sha256"],
      "phase_two_pdf_sha256":digest(output),
      "phase_two_pdf_bytes":output.stat().st_size,
      "A4_pages":260,"original_201_glyphs":201,
      "original_word_or_component_examples":812,
      "original_1045_stroke_tiles_pixel_identical":1045,
      "pass1_false_normative_approval_claims_quarantined":114,
      "pass2_novel_character_specific_storyboards":193,
      "pass2_existing_author_svg_studies_unapproved":8,
      "pass2_professional_illustrations_completed_and_approved":0,
      "pass2_pages_with_new_storyboard_or_cover":194,
      "pass2_other_pages_entirely_unchanged":66,
      "original_misleading_zi_second_stroke_caption_still_blocked":True,
      "P8_pronunciations_authoritatively_double_reviewed":0,
      "P9_stroke_geometry_authoritatively_double_reviewed":0,
      "P5_paper_print_approved":False,
      "P6_explicit_user_publication_approval":False,
      "release_eligible":False,
      "individual_201_glyph_page_art_registry":rows,
    }
    qa.parent.mkdir(parents=True,exist_ok=True)
    qa.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in evidence.items() if k!="individual_201_glyph_page_art_registry"},ensure_ascii=False,indent=2))
    return evidence

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pass1-pdf",type=Path,required=True)
    p.add_argument("--pass1-qa",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--qa",type=Path,required=True)
    a=p.parse_args()
    generate(a.pass1_pdf,a.pass1_qa,a.output,a.qa)

if __name__=="__main__":main()
