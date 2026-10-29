#!/usr/bin/env python3
"""P9.6: source-locked 14 glyph / 83 strokes exact-image candidate review.

The PDF contains proposed fine stroke names for qualified reviewers, NEVER
children's accepted stroke names. GF 0023 5-type digits are a crosscheck only;
the original 1045 source ink tiles are never written or modified.

Two independent order discrepancies are shown prominently:
  鬥 old 2112111212 != multiple lexicons 1121211212;
  屮 old 522 matches lexicon digits but conflicts with its fine-name prose.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import defaultdict,Counter
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CAND=ROOT/"data/cultural_edition/p9_83_fine_pen_research_candidates_20261029.json"
RISKS=ROOT/"data/cultural_edition/p9_normative_open_cases_37_83.json"
P9=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/zitie-201-P9-normative-stroke-review-UNREVIEWED.pdf"
P9_PROOF=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/201-main-1045-stroke-full-page-provenance.json"
FORMAL=ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
FORMAL_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
P9_SHA="8178a8d7bdf5258625efa0b74e7b82c0146c24da802f006f2135f17705e7fd89"
FONT=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
FONT_NAME="UnreviewedPenNamesCJK"
W,H=595.2756,841.8898
X=(36,171,306,441)
Y=(240,410,580)
TILE=113
# This is a type classification ONLY; it is not a fine-name decoder.
FIVE_CATEGORY={
  "横":"1","提":"1","竖":"2","竖钩":"2",
  "撇":"3","点":"4","捺":"4","横撇／横钩":"5",
  "竖折":"5","横折":"5","撇点":"5","撇折":"5",
  "横钩":"5","竖弯钩":"5",
}
HIGH_RISK={55:"屮",190:"鬥"}

def get(path:Path):
    return json.loads(path.read_text(encoding="utf8"))

def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def evidence(candidate:dict=None,risk:dict=None,proof:dict=None,root:Path=ROOT):
    root=Path(root)
    candidate=candidate if candidate is not None else get(root/CAND.relative_to(ROOT))
    risk=risk if risk is not None else get(root/RISKS.relative_to(ROOT))
    proof=proof if proof is not None else get(root/P9_PROOF.relative_to(ROOT))
    if (candidate.get("schema_version")!=1
        or candidate.get("document_kind")!="P9_83_REAL_ORIGINAL_STEP_FINE_NAME_RESEARCH_CANDIDATES_NOT_APPROVAL"
        or candidate.get("source_v051_sha256")!=FORMAL_SHA
        or candidate.get("source_P9_original_stroke_review_pdf_sha256")!=P9_SHA
        or candidate.get("expected_missing_specific_names")!=83
        or candidate.get("safety",{}).get("release_eligible") is not False
        or candidate.get("safety",{}).get("all_83_child_facing_print_eligible") is not False
        or candidate.get("safety",{}).get("first_human_reviewer") is not None
        or candidate.get("safety",{}).get("independent_second_human_reviewer") is not None
        or len(candidate.get("character_groups",[]))!=14):
        raise ValueError("The all-83 proposed names must be a strict and unapproved original-source study")
    cases=risk.get("unknown_fine_name_steps",[])
    if (risk.get("source_v051_sha256")!=FORMAL_SHA
        or len(cases)!=83
        or len({(x["main_id"],x["step_index"]) for x in cases})!=83
        or len({x["main_id"] for x in cases})!=14):
        raise ValueError("The original 83 genuine missing source step-name evidence slots disappeared")
    by_key={(x["main_id"],x["step_index"]):x for x in cases}
    pg=proof.get("page_map",[])
    if (proof.get("source_pdf_sha256")!=FORMAL_SHA
        or proof.get("output_pdf_sha256")!=P9_SHA
        or proof.get("output_pdf_pages")!=260
        or len(pg)!=254
        or sum(len(x["source_steps"]) for x in pg)!=1045):
        raise ValueError("P9 original 201-glyph 1045 cumulative source pen PDF changed")
    source={};first={}
    for item in pg:
        mid=item["main_id"]
        if item["part"]==1:first[mid]=item
        for s in item["source_steps"]:
            key=(mid,s["index"])
            if key in source: raise ValueError("Source step repeated across continuation pages")
            source[key]=dict(s,p9_pdf_page=item["preview_pdf_page"])
    seen=set();rows=[];ambiguous=0
    for grp in candidate["character_groups"]:
        mid=grp["main_id"]
        char=grp["character"]
        names=grp["candidate_names"]
        if (mid in seen or mid not in first
            or first[mid]["character"]!=char
            or not isinstance(names,list)
            or len(names)>12 or not names
            or grp.get("approved_fine_names")!=0
            or grp.get("candidate_only") is not True
            or grp.get("first_reviewer") is not None
            or grp.get("second_reviewer") is not None
            or grp.get("publication_eligible") is not False):
            raise ValueError(f"An original unreviewed glyph case was omitted or falsely signed ID{mid:03d}")
        seen.add(mid)
        for index,name in enumerate(names,1):
            key=(mid,index)
            old=by_key.get(key)
            origin=source.get(key)
            if not old or not origin:
                raise ValueError(f"Missing genuine original source step ID{mid:03d} stroke{index}")
            if (name not in FIVE_CATEGORY
                or FIVE_CATEGORY[name]!=old["source_five_code_digit"]
                or old["character"]!=char
                or old["legacy_name"]!=f"第{index}笔"
                or old["source_pdf_page"]<=0
                or origin["name"]!=old["legacy_name"]
                or origin["index"]!=index
                or old["status"]!="blocked_unidentified_fine_name"
                or old["approved_fine_name"] is not None
                or old["first_reviewer"] is not None
                or old["second_reviewer"] is not None):
                raise ValueError(f"One candidate attempted to overwrite the frozen source pen-name or category ID{mid:03d} step{index}")
            rows.append({
                "main_id":mid,"character":char,"step_index":index,
                "source_v051_page":old["source_pdf_page"],
                "source_v051_pen_clip_pt":old["source_rect_pt"],
                "P9_fullbook_pdf_page":origin["p9_pdf_page"],
                "P9_fullbook_tile_clip_pt":origin["preview_rect_pt"],
                "source_legacy_placeholder":old["legacy_name"],
                "original_secondary_coarse_digit_NOT_normative_approval":old["source_five_code_digit"],
                "proposed_fine_name_NOT_approved":name,
                "secondary_exact_headword_url":grp["secondary_url"],
                "source_case":grp["risk"],
                "unresolved_specific_variant":"／" in name,
                "P9_source_ink_will_be_unmodified":True,
                "first_reviewer":None,"independent_second_reviewer":None,
                "children_print_eligible":False,
            })
            ambiguous+=int("／" in name)
    if seen!=set(candidate["expected_ids"]) or len(rows)!=83 or {r["main_id"] for r in rows}!={r["main_id"] for r in cases}:
        raise ValueError("14-glyph 83-pen source proofing keys drifted")
    by_conflict={r["main_id"]:r for r in candidate["high_priority_sequence_discrepancies"]}
    if set(by_conflict)!={55,190}:
        raise ValueError("The 屮 and 鬥 actual source-order contradictions may not be silently dropped")
    dou=by_conflict[190];che=by_conflict[55]
    if (dou["original_old_PDF_visual_and_registry_code"]!="2112111212"
        or dou["independent_lexicon_repeated_code"]!="1121211212"
        or dou["mismatch_step_indexes"]!=[1,3,4,5]
        or dou["status"]!="blocked_normative_primary_GF3002_exact_UCS_row_and_geometry_required"
        or che["original_old_PDF_visual_and_registry_code"]!="522"
        or che["secondary_source_digit_code"]!="522"
        or che["coarse_code_from_secondary_written_labels"]!="252"
        or che["status"]!="blocked_GF3002_exact_row_and_original_pen_geometry_required"):
        raise ValueError("An unresolved stroke-order source disagreement was erased")
    primary=candidate.get("primary_documentary_evidence",[])
    special=[r for r in primary if r.get("original_main_id")==69 and r.get("step_index")==2]
    ya_candidates=next((x["candidate_names"] for x in candidate["character_groups"] if x["main_id"]==69),None)
    if ya_candidates is None or ya_candidates[1]!="竖折":
        raise ValueError("Primary GF2001 5.4's direct 牙 stroke-two example must match its candidate label")
    if (len(special)!=1 or special[0]["proposed_name"]!="竖折"
        or special[0]["table_entry"]!="5.4 竖折横／竖折"
        or special[0]["direct_example"]!="牙"
        or special[0]["full_official_PDF_sha256"] is not None
        or special[0]["primary_full_pdf_visual_page_verified"] is not False):
        raise ValueError("牙 GF2001 example is an indexed source lead, not a verified official original-PDF certificate")
    return {
        "result":"P9_ALL_83_FINE_STROKE_CANDIDATES_LINKED_TO_REAL_OLD_VECTOR_TILES_NOT_APPROVED",
        "original_review_glyphs":14,
        "source_legacy_unnamed_step_slots":83,
        "candidate_name_assessments":len(rows),
        "fine_names_independently_human_approved":0,
        "fine_names_with_slash_variants_unresolved":ambiguous,
        "prioritized_exact_stroke_order_conflicts":2,
        "source_ink_count_in_whole_201_glyph_book":1045,
        "release_eligible":False,
        "records":rows,
        "discrepancies":[che,dou],
    }

def label(page,text,x,y,size=9,color=(.23,.27,.32)):
    page.insert_text((x,y),text,fontname=FONT_NAME,fontsize=size,color=color)

def render_build(out:Path,report:Path,root:Path=ROOT):
    root=Path(root)
    if sha(root/FORMAL.relative_to(ROOT))!=FORMAL_SHA or sha(root/P9.relative_to(ROOT))!=P9_SHA:
        raise ValueError("The formally issued 299-page or 260-page frozen P9 PDF changed")
    if not FONT.is_file():raise ValueError("Bundled embeddable Chinese font absent")
    audit=evidence(root=root)
    data=get(root/CAND.relative_to(ROOT))
    src_doc=fitz.open(root/P9.relative_to(ROOT))
    pdf=fitz.open()
    cover=pdf.new_page(width=W,height=H)
    cover.insert_font(fontname=FONT_NAME,fontfile=str(FONT))
    label(cover,"83笔细笔名 · 原图独立校对册",45,76,19,(.55,.28,.32))
    label(cover,"14个源字形 · 83笔候选 · 0笔获人工独立双审",45,106,12)
    for i,(lead,explain) in enumerate((
        ("原图","全部直接裁剪原正式版对应的P9笔顺矢量，绝不重绘。"),
        ("候选","图册笔名是逐笔研究候选，不是已核准的儿童教学名。"),
        ("重点","牙第2笔竖折有GF2001表5.4直接例字旁证。"),
        ("警示","鬥：旧笔顺2112111212，字典1121211212。"),
        ("警示","屮：旧笔顺522，但字典细笔名次序存在矛盾。"),
        ("出版","GF3002原表缺页、审校双签未完成：禁止正式发行。"),
    )):
        label(cover,lead,46,174+i*36,11,(.66,.31,.28))
        label(cover,explain,108,174+i*36,10)
    label(cover,"GF0023五码不能机械推导弯钩、竖折等具体笔形。",46,490,11,(.55,.28,.32))
    label(cover,"只用于专业审稿，不得把新候选直接写入儿童拼音/笔顺栏。",46,522,10)
    label(cover,"原正式版本 v0.5.1 / 299页；整体201字1045幅源图保持字节不变。",46,558,10)
    label(cover,"P9.6 · 原始字帖溯源 · 不具有教学出版资格",46,772,10,(.66,.31,.28))
    total=0;panels=[]
    byid=defaultdict(list)
    for row in audit["records"]:byid[row["main_id"]].append(row)
    for ix,group in enumerate(data["character_groups"]):
        mid=group["main_id"];char=group["character"]
        page=pdf.new_page(width=W,height=H)
        page.insert_font(fontname=FONT_NAME,fontfile=str(FONT))
        label(page,f"ID{mid:03d} {char} · 共{len(group['candidate_names'])}笔 · 细笔名研究候选",36,49,16,(.55,.28,.32))
        label(page,f"源旧书五类码：{''.join(r['original_secondary_coarse_digit_NOT_normative_approval'] for r in byid[mid])}",36,72,10)
        label(page,"本页笔名仅供复核，尚未获教学规范/独立双人审核。",36,99,10,(.59,.28,.31))
        if mid in HIGH_RISK:
            note=("旧522 / 字典文字顺序另有冲突：请先核原序。" if mid==55
                  else "旧2112111212 / 字典1121211212：禁止按候选直接临摹。")
            label(page,note,36,120,10,(.73,.23,.20))
        elif mid==69:
            label(page,"第2笔“竖折”：GF2001表5.4例字包含“牙”；原墨迹仍待核。",36,120,10,(.36,.45,.39))
        else:
            label(page,"先比较真实红色本笔与先前深灰笔形，再核独立规范原图。",36,120,9)
        for k,record in enumerate(byid[mid]):
            x=X[k%4];y=Y[k//4]
            name=record["proposed_fine_name_NOT_approved"]
            label(page,f"第{k+1}笔",x,y-20,9,(.54,.31,.32))
            if "／" in name:
                tag="待判："+name
            elif mid in HIGH_RISK:
                tag="候选："+name
            else:
                tag="候选："+name
            label(page,tag,x,y-5,8.5,(.38,.41,.45))
            rect=fitz.Rect(x,y,x+TILE,y+TILE)
            page.draw_rect(rect,color=(.83,.72,.71),width=.6)
            clip=fitz.Rect(record["P9_fullbook_tile_clip_pt"])
            page.show_pdf_page(rect,src_doc,record["P9_fullbook_pdf_page"]-1,
                               clip=clip,keep_proportion=False,overlay=True)
            label(page,f"源P9 第{record['P9_fullbook_pdf_page']}页",x,y+TILE+16,7.2,(.4,.47,.47))
            panels.append({**record,"atlas_page":ix+2,"atlas_tile_rect_pt":[x,y,x+TILE,y+TILE]})
            total+=1
        label(page,"规范原表/跟随式示范：______________________",36,763,9)
        label(page,"专业一审：__________    独立二审：__________",36,789,9)
        label(page,"严禁替代儿童正式笔顺示范 | 原旧书1045笔均未改",36,813,9,(.67,.27,.28))
    if total!=83 or pdf.page_count!=15:
        raise ValueError("14 exact original glyphs / 83 source tiles were not printed")
    pdf.set_metadata({
      "title":"P9.6 14字83笔细笔名原图对照（候选，未审勿印）",
      "author":"netplus/zitie",
      "subject":"原1045幅源笔画不变；逐笔细名称研究候选、两起来源冲突、高风险不能教学",
      "keywords":"source-locked,P9,83,14,review,NOT_APPROVED",
    })
    out.parent.mkdir(parents=True,exist_ok=True)
    pdf.save(out,garbage=4,deflate=True,no_new_id=True)
    src_doc.close();pdf.close()
    result={
        "schema_version":1,
        "result":"PASS_P9_14_83_SOURCE_VECTOR_FIDELITY_AND_PENDING_REVIEW",
        "source_formal_299_pdf_sha256":FORMAL_SHA,
        "source_P9_260_pdf_sha256":P9_SHA,
        "review_pdf_sha256":sha(out),
        "review_pdf_pages":15,
        "source_glyphs_reviewed":14,
        "source_unlabeled_strokes_documented":83,
        "independent_secondary_sequence_conflicts":2,
        "unresolved_specific_name_variants":audit["fine_names_with_slash_variants_unresolved"],
        "published_child_approved_fine_names":0,
        "source_1045_cumulative_pen_steps_modified":False,
        "P5_paper_print_certified":False,
        "P6_user_release_approved":False,
        "release_eligible":False,
        "records":panels,
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},ensure_ascii=False,indent=2))
    return result

def visual_verify(out:Path,report:Path,root:Path=ROOT):
    qa=get(report)
    if (qa["review_pdf_sha256"]!=sha(out)
        or qa["review_pdf_pages"]!=15
        or qa["source_glyphs_reviewed"]!=14
        or qa["source_unlabeled_strokes_documented"]!=83
        or qa["independent_secondary_sequence_conflicts"]!=2
        or qa["release_eligible"] is not False
        or len(qa["records"])!=83):
        raise ValueError("Actual P9 high-risk review source scope mismatch")
    scores=[];blank=[]
    source=fitz.open(root/P9.relative_to(ROOT))
    with fitz.open(out) as doc:
        if len(doc)!=15:raise ValueError("Missing a source-review page")
        for r in qa["records"]:
            old=source[r["P9_fullbook_pdf_page"]-1]
            new=doc[r["atlas_page"]-1]
            if not(594<new.rect.width<597 and 840<new.rect.height<843):
                raise ValueError("A4 geometry changed")
            clip=fitz.Rect(r["P9_fullbook_tile_clip_pt"])
            rect=fitz.Rect(r["atlas_tile_rect_pt"])
            a=old.get_pixmap(matrix=fitz.Matrix(1.7,1.7),clip=clip,alpha=False)
            b=new.get_pixmap(matrix=fitz.Matrix(1.7,1.7),clip=rect,alpha=False)
            lhs=np.asarray(Image.frombytes("RGB",(a.width,a.height),a.samples).resize((96,96),Image.Resampling.BILINEAR),dtype=np.int16)
            rhs=np.asarray(Image.frombytes("RGB",(b.width,b.height),b.samples).resize((96,96),Image.Resampling.BILINEAR),dtype=np.int16)
            mae=float(np.abs(lhs-rhs).mean())
            scores.append(mae)
            if float((rhs<180).any(axis=2).mean())<.003:blank.append((r["main_id"],r["step_index"]))
            if mae>24:
                raise ValueError(f"Real source stroke differs from copied atlas ID{r['main_id']:03d} step{r['step_index']}: MAE={mae:.2f}")
        if len(doc.get_toc())!=0:  # TOC isn't required for this standalone 15p audit atlas.
            raise ValueError("Unexpected inherited publication-ready TOC")
        for i,p in enumerate(doc):
            if i and ("候选" not in p.get_text() and "待判" not in p.get_text()):
                raise ValueError("Fine-name candidate labels went missing")
            if i and "专业一审" not in p.get_text():
                raise ValueError("Reviewer signoff lines missing")
    source.close()
    if len(scores)!=83 or blank:raise ValueError(f"Blank source strokes or wrong count: {blank}")
    return {
       "result":"PASS_83_SOURCE_TILE_PIXEL_VISUAL_MATCH_NO_CHILD_APPROVAL",
       "source_pen_tiles_compared":83,
       "max_MAE_rgb_255":round(max(scores),4),
       "avg_MAE_rgb_255":round(sum(scores)/len(scores),4),
       "review_candidate_approval":False,
       "source_original_1045_steps_unchanged":True,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--qa",type=Path,required=True)
    parser.add_argument("--verify-report",type=Path)
    args=parser.parse_args()
    render_build(args.output,args.qa)
    if args.verify_report:
        r=visual_verify(args.output,args.qa)
        args.verify_report.parent.mkdir(parents=True,exist_ok=True)
        args.verify_report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        print(json.dumps(r,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
