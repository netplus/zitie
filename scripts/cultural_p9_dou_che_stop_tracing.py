#!/usr/bin/env python3
"""P9.7: suppress misleading imitation instructions on 鬥 and 屮 risk pages.

Their source sequence cannot be certified from a repeated five-type code or
copied old ink. This keeps all 1045 original cumulative source vector tiles
pixel IDENTICAL for a later qualified reviewer and removes precisely five
"keep writing this source stroke order" cues on the affected three A4 pages.
The PDF remains a review-only document, not a repaired normative stroke order.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FORMAL="deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
FORMAL_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
P9_PROOF="deliverables/drafts/cultural-v0.9-stroke-review/201-main-1045-stroke-full-page-provenance.json"
SOURCE="deliverables/drafts/cultural-v0.11.2-zi-wangou-MOE-UNREVIEWED/zitie-201-P9-zi-wangou-260-UNREVIEWED.pdf"
SOURCE_SHA="c37ca8aa82de52e5792eb03c3bdde158060698b676af3d21d0dca2d3419e3455"
P9_83="data/cultural_edition/p9_83_fine_pen_research_candidates_20261029.json"
EMBEDDED_FONT=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
FONT_NAME="P9BlockedRiskCJK"
TARGETS={
  117:{"mid":55,"character":"屮","old":(
        "看清这一步新出现的红色笔画，再接着写。",
        "先按序号练习，不把待核实的笔画名称当作答案。"),
       "new":("“屮”原笔名与数码出处冲突，暂停临摹。",
              "原图仅供规范审校，待逐笔原始证据核实。"),
       "clip":[48,457,297,485]},
  237:{"mid":190,"character":"鬥","old":(
        "看清这一步新出现的红色笔画，再接着写。",
        "先按序号练习，不把待核实的笔画名称当作答案。"),
       "new":("“鬥”原书起笔竖，多个字典记横，须核笔序。",
              "此页旧序暂勿临摹；原图仅供专家对照。"),
       "clip":[48,457,301,485]},
  238:{"mid":190,"character":"鬥","old":(
        "看清这一步新出现的红色笔画，再接着写。",
        "先按序号练习，不把待核实的笔画名称当作答案。",
        "提示：依原书序号逐步完成，灰色为先前笔画，红色为当前笔画。"),
       "new":("“鬥”旧笔顺与多本字典冲突，暂勿临摹。",
              "灰红原图仅供核对，待适用原规范与双审。",
              "提示：原书“鬥”笔序存在争议，暂停按图书写。"),
       "clip":[48,210,296,240],"tip_clip":[48,159,364,174]}
}
def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(root:Path,name:str):
    return json.loads((root/name).read_text(encoding="utf8"))

def evidence(root:Path=ROOT):
    root=Path(root)
    if (sha(root/FORMAL)!=FORMAL_SHA or sha(root/SOURCE)!=SOURCE_SHA
        or not EMBEDDED_FONT.is_file()):
        raise ValueError("Frozen formal/original review PDF or full portable CJK font missing")
    e=load(root,P9_83);proof=load(root,P9_PROOF)
    if (e.get("source_v051_sha256")!=FORMAL_SHA
        or e.get("safety",{}).get("release_eligible") is not False
        or e.get("expected_missing_specific_names")!=83
        or proof.get("source_pdf_sha256")!=FORMAL_SHA
        or proof.get("output_pdf_pages")!=260
        or sum(len(x["source_steps"]) for x in proof["page_map"])!=1045):
        raise ValueError("The P9.6 source sequence and all 1045 frozen old source ink tiles must remain traceable")
    critical={x["main_id"]:x for x in e["high_priority_sequence_discrepancies"]}
    if (set(critical)!={55,190}
        or critical[190]["original_old_PDF_visual_and_registry_code"]!="2112111212"
        or critical[190]["independent_lexicon_repeated_code"]!="1121211212"
        or critical[190]["mismatch_step_indexes"]!=[1,3,4,5]
        or critical[190]["status"]!="blocked_normative_primary_GF3002_exact_UCS_row_and_geometry_required"
        or critical[55]["original_old_PDF_visual_and_registry_code"]!="522"
        or critical[55]["coarse_code_from_secondary_written_labels"]!="252"
        or critical[55]["status"]!="blocked_GF3002_exact_row_and_original_pen_geometry_required"):
        raise ValueError("Source-sequence discrepancies must be real and still blocked")
    mapping={r["preview_pdf_page"]:r for r in proof["page_map"]}
    if (len(mapping)!=254 or mapping[117]["main_id"]!=55
        or mapping[237]["main_id"]!=190 or mapping[238]["main_id"]!=190
        or mapping[238]["part"]!=2):
        raise ValueError("The original B12/B19 PDF risk page identities moved")
    for num,rule in TARGETS.items():
        card=mapping[num]
        if card["character"]!=rule["character"] or card["main_id"]!=rule["mid"]:
            raise ValueError("P9.7 source glyph identity changed")
        rects=[fitz.Rect(rule["clip"])]
        if num==238:rects.append(fitz.Rect(rule["tip_clip"]))
        for s in card["source_steps"]:
            ink=fitz.Rect(s["preview_rect_pt"])
            if any(r.intersects(ink) for r in rects):
                raise ValueError(f"One true original ink step overlaps an editorial safety-warning rectangle p{num}")
    return mapping

def redact_and_replace(page:fitz.Page,number:int):
    rule=TARGETS[number]
    source=page.get_text()
    if any(source.count(s)!=1 for s in rule["old"]):
        raise ValueError(f"Expected unique original risky imitation hint missing on p{number}")
    if "禁止作为正式教材发行" not in source or "原PDF笔顺提示·未获规范批准" not in source:
        raise ValueError(f"Must retain visible release & source-review warnings on p{number}")
    spans=[page.search_for(s) for s in rule["old"]]
    if any(len(s)!=1 for s in spans):
        raise ValueError("A suspected unsafe label cannot be redacted without a unique physical text location")
    rect=fitz.Rect(rule["clip"])
    if not all(rect.contains(spans[i][0]) for i in range(2)):
        raise ValueError("The prose panel moved and cannot be safely modified")
    page.add_redact_annot(rect,fill=(1,1,1))
    if number==238:
        extra=fitz.Rect(rule["tip_clip"])
        if not extra.contains(spans[2][0]):
            raise ValueError("The old source-stroke continuation line moved")
        page.add_redact_annot(extra,fill=(1,1,1))
    page.apply_redactions(images=0,graphics=0,text=0)
    page.insert_font(fontname=FONT_NAME,fontfile=str(EMBEDDED_FONT))
    y=465 if number!=238 else 218
    for line in rule["new"][:2]:
        page.insert_text((51.5,y),line,fontname=FONT_NAME,
                         fontsize=8.6,color=(.56,.22,.29))
        y+=13.15 if number!=238 else 14.18
    if number==238:
        page.insert_text((51.5,169),rule["new"][2],
                         fontname=FONT_NAME,fontsize=8.5,color=(.61,.24,.28))
    final=page.get_text()
    if any(x in final for x in rule["old"]) or any(final.count(s)!=1 for s in rule["new"]):
        raise ValueError(f"Unsafe old encouragement survived or new stop-learning warning missing p{number}")

def pixel_diff_scope(before:fitz.Page,after:fitz.Page,allowed:list[fitz.Rect]):
    scale=.80;matrix=fitz.Matrix(scale,scale)
    a=before.get_pixmap(matrix=matrix,alpha=False)
    b=after.get_pixmap(matrix=matrix,alpha=False)
    if (a.width,a.height)!=(b.width,b.height):
        raise ValueError("Physical A4 size changed")
    x=np.frombuffer(a.samples,dtype=np.uint8).reshape(a.height,a.width,3)
    y=np.frombuffer(b.samples,dtype=np.uint8).reshape(b.height,b.width,3)
    yy,xx=np.nonzero(np.any(x!=y,axis=2))
    if xx.size<60:raise ValueError("Claimed safety correction was not visibly written")
    for ix,iy in zip(xx,yy):
        pt=fitz.Point((int(ix)+.5)/scale,(int(iy)+.5)/scale)
        if not any((r+(-3,-3,3,3)).contains(pt) for r in allowed):
            raise ValueError(f"Pass1 redaction changed ink outside its safe region {pt}")
    return {"changed_rgb_pixels":int(xx.size),
            "changed_bbox_pt":[round(float(xx.min())/scale,2),round(float(yy.min())/scale,2),
                               round(float(xx.max()+1)/scale,2),round(float(yy.max()+1)/scale,2)]}

def build(out:Path,report:Path,root:Path=ROOT):
    root=Path(root)
    mapping=evidence(root)
    source=root/SOURCE
    out.parent.mkdir(parents=True,exist_ok=True)
    with fitz.open(source) as book:
        if len(book)!=260:raise ValueError("Old full A4 cultural review must have exactly 260 pages")
        for number in TARGETS:redact_and_replace(book[number-1],number)
        book.set_metadata({
          "title":"260页文化识字校对稿 · 鬥屮有实际笔序疑点暂停临摹",
          "author":"netplus/zitie",
          "subject":"原1045幅墨迹不改；高风险两字暂停临摹；GF3002完整适用原表待审；正式发行阻断",
          "keywords":"P9,stop-tracing,dou,che,source-order-conflict,review-only,260",
        })
        book.save(out,garbage=4,deflate=True,no_new_id=True)
    trace=[];strokes=0;preserved=0
    with fitz.open(source) as old,fitz.open(out) as new:
        if len(old)!=260 or len(new)!=260 or old.get_toc()!=new.get_toc():
            raise ValueError("All 260 pages and all original 201-character bookmark links must remain")
        for i in range(1,261):
            before=old[i-1];after=new[i-1]
            if before.rect!=after.rect:raise ValueError(f"A4 physical size changed p{i}")
            if i in TARGETS:
                regions=[fitz.Rect(TARGETS[i]["clip"])]
                if i==238:regions.append(fitz.Rect(TARGETS[i]["tip_clip"]))
                difference=pixel_diff_scope(before,after,regions)
                trace.append({
                    "main_id":TARGETS[i]["mid"],"character":TARGETS[i]["character"],
                    "PDF_page":i,"new_stop_tracing_warnings":list(TARGETS[i]["new"]),
                    "original_old_source_ink_modified":False,
                    **difference
                })
                if not any("暂停" in s or "暂勿" in s for s in TARGETS[i]["new"]):
                    raise ValueError("A conflicting original order was not explicitly blocked")
            else:
                matrix=fitz.Matrix(.64,.64)
                a=before.get_pixmap(matrix=matrix,alpha=False)
                b=after.get_pixmap(matrix=matrix,alpha=False)
                if (a.width,a.height,a.samples)!=(b.width,b.height,b.samples):
                    raise ValueError(f"An unrelated A4 page {i} visually changed")
                preserved+=1
        for row in mapping.values():
            p=row["preview_pdf_page"]
            for step in row["source_steps"]:
                clip=fitz.Rect(step["preview_rect_pt"])
                m=fitz.Matrix(1.35,1.35)
                a=old[p-1].get_pixmap(matrix=m,clip=clip,alpha=False)
                b=new[p-1].get_pixmap(matrix=m,clip=clip,alpha=False)
                if (a.width,a.height,a.samples)!=(b.width,b.height,b.samples):
                    raise ValueError(f"One of 1045 genuine red/gray source pen ink tiles changed ID{row['main_id']:03d} step{step['index']}")
                strokes+=1
        if (preserved,strokes,len(trace))!=(257,1045,3):
            raise ValueError("Source-lock and targeted A4 modifications did not reconcile")
    result={
      "schema_version":1,
      "result":"P9_7_TWICE_VERIFIED_REAL_ORDER_DISAGREEMENTS_WARNED_AND_ORIGINAL_1045_SOURCE_PEN_TILES_IDENTICAL",
      "original_formal_299page_pdf_sha256":FORMAL_SHA,
      "parent_260page_v0112_pdf_sha256":SOURCE_SHA,
      "candidate_260page_pdf_sha256":sha(out),
      "candidate_pdf_bytes":out.stat().st_size,
      "candidate_pdf_A4_pages":260,
      "P9_83_candidate_source_records_retained":83,
      "original_1045_source_stroke_tiles_pixel_identical":1045,
      "warning_pages_and_no_ink_touch":trace,
      "untouched_full_A4_pages_pixel_identical":257,
      "current_source_sequence_discrepancies":[
          {"id":55,"character":"屮","old_source_five_type":"522",
           "lexicon_fine_written_coarse_equivalent":"252"},
          {"id":190,"character":"鬥","old_source_five_type":"2112111212",
           "other_repeated_dictionary_five_type":"1121211212"}
      ],
      "two_conflicting_source_orders_allowed_in_approved_child_learning_material":False,
      "P9_original_normative_full_source_human_double_reviewed":False,
      "P8_1013_children_pronunciations_approved":0,
      "P10_all_201_professional_illustrations_approved":0,
      "P5_paper_print_reviewed":False,
      "P6_user_publication_approved":False,
      "release_eligible":False,
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k!="warning_pages_and_no_ink_touch"},ensure_ascii=False,indent=2))
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--qa",type=Path,required=True)
    args=ap.parse_args()
    build(args.output,args.qa)

if __name__=="__main__":main()
