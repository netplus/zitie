#!/usr/bin/env python3
"""P9.4 high-priority 40-glyph vector-stroke review atlas.

Includes 37 exceptional non-GF0023 components, 14 fine-name-unknown glyphs
(overlaps counted once), and 子 step-two classification dispute: exactly 40.
Original 1045 frozen-P9 full-book strokes are NEVER replaced; enlarged tiles
are clipped from the P9 manuscript's existing source vector Form XObjects.
Output is review-only and cannot authorize normative correctness or a release.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path

import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from build_cultural_sample import fonts
from build_cultural_fullbook import PageArtist, W, H, mm
from cultural_fullbook_model import ROOT, SHA

P9_SHA="8178a8d7bdf5258625efa0b74e7b82c0146c24da802f006f2135f17705e7fd89"
P9_SOURCE=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/zitie-201-P9-normative-stroke-review-UNREVIEWED.pdf"
ORIGINAL_SOURCE=ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
P9_PROOF=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/201-main-1045-stroke-full-page-provenance.json"
P9_REGISTRY=ROOT/"data/cultural_edition/p9_201_original_stroke_crosscheck.json"
P9_RISKS=ROOT/"data/cultural_edition/p9_normative_open_cases_37_83.json"
GF0023=ROOT/"data/cultural_edition/p9_GF0023_direct_primary_164.json"

CARD=39.0
X=(19.0,61.5,104.0,146.5)
Y=(93.0,151.0,209.0)

def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf8"))

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def index_records(root:Path=ROOT)->dict:
    if (sha(root/P9_SOURCE.relative_to(ROOT))!=P9_SHA
        or sha(root/ORIGINAL_SOURCE.relative_to(ROOT))!=SHA):
        raise ValueError("Original v0.5.1 or frozen P9 source PDF changed")
    review=load(root/P9_RISKS.relative_to(ROOT))
    p9=load(root/P9_REGISTRY.relative_to(ROOT))
    primary=load(root/GF0023.relative_to(ROOT))
    proof=load(root/P9_PROOF.relative_to(ROOT))
    if (review.get("source_v051_sha256")!=SHA or
        p9.get("frozen_source_pdf_sha256")!=SHA or
        primary.get("actual_official_GF0023_pdf_pages")!=581
        or proof.get("source_pdf_sha256")!=SHA or
        proof.get("output_pdf_sha256")!=P9_SHA
        or len(proof.get("page_map",[]))!=254
        or sum(len(r["source_steps"]) for r in proof["page_map"])!=1045):
        raise ValueError("Only the actual 201-glyph/1045-step original-source evidence can be illustrated")
    out_of_scope={x["main_id"] for x in review["out_of_scope_characters"]}
    missing={x["main_id"] for x in review["unknown_fine_name_steps"]}
    disputed={x["main_id"] for x in review["fine_name_vs_official_coarse_conflicts"]}
    risk_ids=sorted(out_of_scope|missing|disputed)
    if (len(out_of_scope),len(missing),len(disputed),len(risk_ids))!=(37,14,1,40):
        raise ValueError("The original 37+14+one disputed P9 review queue lost cases")
    source={x["main_id"]:x for x in p9["entries"]}
    official={x["main_id"]:x for x in primary["entries"]}
    if len(source)!=201 or len(official)!=164:
        raise ValueError("Original scope 201 / 164 changed")
    first={}; tiles=defaultdict(list)
    for rec in proof["page_map"]:
        mid=rec["main_id"]
        if rec["part"]==1:
            if mid in first: raise ValueError("Duplicate glyph cover page")
            first[mid]=rec
        for tile in rec["source_steps"]:
            tiles[mid].append(dict(tile,origin_p9_pdf_page=rec["preview_pdf_page"]))
    if len(first)!=201 or len(tiles)!=201:raise ValueError("Original source page coverage lost")
    rows=[]
    for mid in risk_ids:
        entry=source[mid]
        original=entry["source_step_records"]
        picture=sorted(tiles[mid],key=lambda x:x["index"])
        if len(picture)!=entry["stroke_count"] or entry["stroke_count"]>12:
            raise ValueError(f"ID{mid:03d} cannot fit safe A4 4x3 full-sized tiles")
        for a,b in zip(picture,original):
            if (a["index"]!=b["index"] or a["name"]!=b["name"]
                or a["origin_p9_pdf_page"]<7 or a["origin_p9_pdf_page"]>260
                or len(a["preview_rect_pt"])!=4):
                raise ValueError("A reviewer step does not match frozen original source identity")
        if mid not in out_of_scope and mid not in official:
            raise ValueError("Risk atlas mistakenly called a glyph GF0023 primary verified")
        risk=[]
        if mid in out_of_scope:risk.append("超出GF0023适用范围")
        if mid in missing:risk.append("具体笔画名称缺失")
        if mid in disputed:risk.append("子第二笔名称与五类码有争议")
        rows.append({
            "main_id":mid,"character":entry["character"],
            "batch_id":entry["batch_id"],"stroke_count":entry["stroke_count"],
            "risk_reasons":risk,
            "GF0023_numeric_five_type_code":(
                official[mid]["GF0023_official_five_type_code"] if mid in official else None),
            "GF0023_original_physical_page":(
                official[mid]["GF0023_original_pdf_page_1based"] if mid in official else None),
            "secondary_five_type_code_NOT_authority":entry["secondary_reference_five_type_code"],
            "generic_fine_name_step_count":entry["generic_numbered_stroke_names"],
            "human_first_reviewer":None,"independent_second_reviewer":None,
            "source_vector_steps":[dict(v) for v in picture],
            "art_review_pdf_page":1+len(rows)+1,
            "publication_eligible":False,
        })
    return {
        "schema_version":1,
        "review_status":"40_P9_EXCEPTION_GLYPHS_SOURCE_TILES_ENLARGED_PENDING_AUTHORITY_AND_TWO_HUMANS",
        "original_release_sha256":SHA,
        "original_P9_pdf_sha256":P9_SHA,
        "main_glyphs":201,
        "original_vector_stroke_steps_total":1045,
        "GF0023_original_numeric_evidence_glyphs":164,
        "GF0023_outside_scope_glyphs":37,
        "individual_unreviewed_fine_pen_name_steps":83,
        "disputed_zi_fine_label_glyphs":1,
        "priority_unique_main_glyphs":40,
        "release_eligible":False,
        "entries":rows,
    }

def build(pdf_path:Path,qa_path:Path,root:Path=ROOT):
    plan=index_records(root)
    fonts()
    fallback=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
    if not fallback.is_file():
        raise ValueError("Missing embeddable rare CJK font")
    if "CultureRare" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CultureRare",str(fallback),subfontIndex=0))
    buf=io.BytesIO()
    c=canvas.Canvas(buf,pagesize=(W,H),pageCompression=1,invariant=1)
    c.setTitle("P9 40字异常笔画原PDF源矢量逐笔核对图册 · 未审定")
    p=PageArtist(c)
    p.page_border(1,"P9 风险逐笔高清校对图册 · 只作专家审稿")
    p.label(19,34,"40个字形 · 逐笔原图复核",23,"Kai","#943E48")
    p.label(19,49,"源图保真 · 不补写任何未经权威审核的笔画名称",12,"Kai")
    p.label(19,76,"GF0023外 37 字 / 缺具体笔名 14 字83笔 / 子字名称争议 1 项",10,"Kai")
    p.label(19,95,"交叉去重后40字形，每个字形独立一页，原笔顺图直接放大显示。",10,"Kai")
    p.label(19,111,"图中只证明旧PDF来源一致；不代表旧书笔顺必然符合现行规范。",10,"Kai","#943E48")
    p.label(19,129,"审核要求：规范原表页码、实际折勾形态、一审/独立二审、教材一致性。",10,"Kai")
    p.label(19,159,"本图册所有笔名、五类编码和教学提示均处于待核状态。",11,"Kai","#943E48")
    p.label(19,190,"正式出版审核通过：0 / 40字；旧v0.5.1及P9/P10 PDF不修改。",10,"Kai")
    p.label(19,248,"读取者：请据来源ID查到源书页，逐笔验其形体与连贯笔势。",10,"Kai")
    c.showPage()
    tiles=[]
    for row in plan["entries"]:
        pageno=row["art_review_pdf_page"]
        p.page_border(pageno,f"P9 · ID{row['main_id']:03d} {row['character']} · 专家逐笔审校 · 未批准")
        p.label(19,23,f"ID{row['main_id']:03d}  {row['character']} · {row['batch_id']}",23,"Kai","#943E48")
        p.label(19,35,f"原PDF共{row['stroke_count']}笔；规范五类参考：{row['secondary_five_type_code_NOT_authority']}",10,"Kai")
        reason="／".join(row["risk_reasons"])
        for i,text in enumerate(p.rows("风险："+reason,166,10,max_lines=2)):
            p.label(19,46+i*6,text,10,"Kai","#943E48")
        if row["GF0023_numeric_five_type_code"]:
            p.label(19,69,f"GF0023原表第{row['GF0023_original_physical_page']}页 · 五类码{row['GF0023_numeric_five_type_code']}（具体笔形仍待核）",8.6,"Kai")
        else:
            p.label(19,69,"本形体不在GF0023的8105字范围；GF3002等适用原表仍待找到。",8.6,"Kai")
        p.label(19,77,"下方每幅均取冻结P9中真实旧PDF累计笔顺矢量：灰为以前，红为本笔。",9,"Kai")
        for i,step in enumerate(row["source_vector_steps"]):
            x=X[i%4];y=Y[i//4];caption=step["name"]
            if caption.startswith("第") and caption.endswith("笔"):caption="具体笔名待核"
            if row["main_id"]==54 and step["index"]==2:caption="第二笔名称有争议"
            p.label(x,y-5.4,f"第{step['index']}笔 · {caption}",8.4,"Kai","#943E48")
            dest=[x,y,x+CARD,y+CARD]
            tiles.append({
               "main_id":row["main_id"],"character":row["character"],
               "index":step["index"],"review_page":pageno,
               "P9_source_pdf_page":step["origin_p9_pdf_page"],
               "original_P9_clip_pt":step["preview_rect_pt"],
               "atlas_tile_rect_pt":[round(mm(v),5) for v in dest],
               "source_pen_name_unapproved":step["name"],
               "source_vector_copied_not_redrawn":True,
            })
        p.label(19,264,"不以此稿直接教学：细笔名、落笔轨迹、折钩合笔、笔序和提示待原规范双审。",8.8,"Kai","#943E48")
        p.label(19,275,"第一审核：_________  独立复核：_________   权威来源/页：________________",8.4,"Kai")
        c.showPage()
    c.save()
    pdf_path.parent.mkdir(parents=True,exist_ok=True)
    with fitz.open(stream=buf.getvalue(),filetype="pdf") as result,fitz.open(root/P9_SOURCE.relative_to(ROOT)) as original:
        if len(result)!=41 or len(original)!=260:raise ValueError("Expected 40 glyph reviews and unchanged 260-page source")
        for rec in tiles:
            result[rec["review_page"]-1].show_pdf_page(
                fitz.Rect(rec["atlas_tile_rect_pt"]),
                original,rec["P9_source_pdf_page"]-1,
                clip=fitz.Rect(rec["original_P9_clip_pt"]),
                keep_proportion=False,overlay=True)
        result.set_toc([[1,"风险图册说明",1]]+
            [[1,f"ID{x['main_id']:03d} {x['character']} · 待审",x["art_review_pdf_page"]]
             for x in plan["entries"]])
        result.save(pdf_path,garbage=4,deflate=True,no_new_id=True)
    qa={
      "schema_version":1,
      "result":"P9_40_PRIORITY_GLYPHS_ORIGINAL_VECTOR_STEPS_ENLARGED_FOR_REVIEW_ONLY",
      "art_review_pdf_sha256":sha(pdf_path),
      "art_review_pdf_bytes":pdf_path.stat().st_size,
      "art_review_pdf_pages":41,
      "original_P9_260_page_pdf_sha256":P9_SHA,
      "original_released_v051_pdf_sha256":SHA,
      "priority_glyphs":40,
      "GF0023_outside_8105":37,
      "missing_specific_fine_pen_name_steps_in_201_book":83,
      "zi_second_stroke_legacy_classification_risk":1,
      "risk_atlas_copied_source_cumulative_steps":len(tiles),
      "original_1045_stroke_source_modified":False,
      "human_approved_risk_glyphs":0,
      "publication_eligible":False,
      "page_mapping":plan["entries"],
      "individual_copied_steps":tiles,
    }
    qa_path.parent.mkdir(parents=True,exist_ok=True)
    qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in qa.items() if k not in ("page_mapping","individual_copied_steps")},ensure_ascii=False,indent=2))
    return qa

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--qa",type=Path,required=True)
    args=ap.parse_args()
    build(args.output,args.qa)

if __name__=="__main__":
    main()
