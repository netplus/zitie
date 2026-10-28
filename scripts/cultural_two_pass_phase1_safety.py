#!/usr/bin/env python3
"""Two-pass cultural book: pass ONE safe wording, 114 exact pages, all 1045 inks.

Read the immutable 260-page P10.2 draft. Correct the false assertion that
stroke orders were already nationally reviewed; don't touch a single original
cumulative pen tile, glyph, pronunciation, or established historical PDF.
No professional, lexicographic, art or release approval is implied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import fitz
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"deliverables/drafts/cultural-v0.10-eight-art-p9-risk-UNREVIEWED/zitie-201-P10-art-integrated-source-UNREVIEWED.pdf"
BASE_SHA="fb2388fe0d5642b35fe3560ff5733c653335074cba9460003d5388d4f42a361f"
P9=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/201-main-1045-stroke-full-page-provenance.json"
P8=ROOT/"data/cultural_edition/p8_all_1013_pinyin_review_queue.json"
SOURCE=ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
SOURCE_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
OLD="按已核规范笔顺逐笔书写"
NEW="原版笔顺待权威核验"
REQUIRED_PAGES=114

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verified_proof(root:Path):
    doc=json.loads((root/P9.relative_to(ROOT)).read_text(encoding="utf8"))
    p8=json.loads((root/P8.relative_to(ROOT)).read_text(encoding="utf8"))
    if (doc.get("output_pdf_pages")!=260
        or doc.get("source_pdf_sha256")!=SOURCE_SHA
        or doc.get("strict_pinyin_review_mode") is not True
        or doc.get("strict_P9_normative_stroke_review_mode") is not True
        or len(doc.get("page_map",[]))!=254
        or sum(len(r["source_steps"]) for r in doc["page_map"])!=1045
        or p8.get("frozen_source_pdf_sha256")!=SOURCE_SHA
        or len(p8.get("entries",[]))!=1013
        or any(r.get("print_eligible") is not False or
               r.get("publication_approved") is not False for r in p8["entries"])):
        raise ValueError("Frozen 201/1045/1013 original-source provenance was changed")
    by_page={r["preview_pdf_page"]:r for r in doc["page_map"]}
    if len(by_page)!=254 or set(by_page)!=set(range(7,261)):
        raise ValueError("All 254 B01-B21 content/continuation pages must be identified")
    return doc,by_page

def render_equal(a:fitz.Page,b:fitz.Page,scale:float=.60)->bool:
    matrix=fitz.Matrix(scale,scale)
    p=a.get_pixmap(matrix=matrix,alpha=False)
    q=b.get_pixmap(matrix=matrix,alpha=False)
    return (p.width,p.height,p.samples)==(q.width,q.height,q.samples)

def assert_localized_difference(a:fitz.Page,b:fitz.Page,rect:fitz.Rect,scale:float=.75):
    m=fitz.Matrix(scale,scale)
    before=a.get_pixmap(matrix=m,alpha=False)
    after=b.get_pixmap(matrix=m,alpha=False)
    if (before.width,before.height)!=(after.width,after.height):
        raise ValueError("A4 geometry drifted")
    p=np.frombuffer(before.samples,dtype=np.uint8).reshape(before.height,before.width,3)
    q=np.frombuffer(after.samples,dtype=np.uint8).reshape(after.height,after.width,3)
    changed=np.any(p!=q,axis=2)
    ys,xs=np.nonzero(changed)
    if xs.size<10:
        raise ValueError("Editorial overclaim was not actually visually corrected")
    # Redaction only affects one 8.6pt text line; extra padding accounts for
    # glyph antialiasing and newly inserted CJK glyph shadows.
    xmin=float(xs.min()/scale);xmax=float((xs.max()+1)/scale)
    ymin=float(ys.min()/scale);ymax=float((ys.max()+1)/scale)
    protected=rect+(-3,-3,3,3)
    if not (protected.x0<=xmin and xmax<=protected.x1 and
            protected.y0<=ymin and ymax<=protected.y1):
        raise ValueError(f"Pass 1 changed unrelated page ink near {(xmin,ymin,xmax,ymax)}")
    return [round(v,2) for v in (xmin,ymin,xmax,ymax)]

def build(output:Path,qa:Path,root:Path=ROOT):
    root=Path(root)
    base=root/BASE.relative_to(ROOT)
    if digest(base)!=BASE_SHA or digest(root/SOURCE.relative_to(ROOT))!=SOURCE_SHA:
        raise ValueError("Immutable previous cultural draft or formal old book was modified")
    proof,by_page=verified_proof(root)
    report=[]
    output.parent.mkdir(parents=True,exist_ok=True)
    with fitz.open(base) as book:
        if len(book)!=260:
            raise ValueError("Original 260-page cultural review draft missing pages")
        expected=[];regions={}
        for page in book:
            number=page.number+1
            old_count=page.get_text().count(OLD)
            if old_count:
                found=page.search_for(OLD)
                if old_count!=1 or len(found)!=1 or number not in by_page:
                    raise ValueError(f"Ambiguous unverified-standard wording on A4 p{number}")
                rect=found[0]
                if not (49<rect.x0<54 and 143<rect.x1<148 and
                        (458<rect.y0<462 or 211<rect.y0<215)):
                    raise ValueError(f"Editorial source layout moved on p{number}: {rect}")
                if any(rect.intersects(fitz.Rect(s["preview_rect_pt"]))
                       for s in by_page[number]["source_steps"]):
                    raise ValueError("A source ink stroke intersects the editorial label redaction")
                expected.append(number);regions[number]=rect
        if len(expected)!=REQUIRED_PAGES:
            raise ValueError(f"Expected 114 false 'already normative reviewed' assertions, found {len(expected)}")
        for number in expected:
            page=book[number-1]
            rect=regions[number]
            page.add_redact_annot(rect,fill=(1,1,1))
            page.apply_redactions(images=0,graphics=0,text=0)
            page.insert_text((rect.x0,rect.y1-1.2),NEW,
                             fontname="china-s",fontsize=8.1,color=(.51,.25,.30))
            text=page.get_text()
            if OLD in text or NEW not in text or "未获规范批准" not in text:
                raise ValueError(f"Unreviewed source teaching statement still printed on p{number}")
            ref=by_page[number]
            report.append({
                "physical_pdf_page":number,"source_main_id":ref["main_id"],
                "character":ref["character"],"batch_id":ref["batch_id"],
                "page_part":ref["part"],"old_disallowed_claim":OLD,
                "new_unapproved_statement":NEW,
                "clip_pt":[round(v,4) for v in rect],
                "old_source_step_ink_changed":False,
                "new_approval_granted":False
            })
        old=book.metadata
        meta=dict(old or {})
        meta["title"]="文化识字201字 · 第一次整书教学校对 · 260页未审稿"
        meta["subject"]="114处笔顺已核误述隔离；原书1045幅累计笔画未改；1013音未审；禁止正式发行"
        meta["keywords"]="201,1045,1013,P8,P9,P10,pass1,review-only,NO-RELEASE"
        book.set_metadata(meta)
        book.save(output,garbage=4,deflate=True,no_new_id=True)

    with fitz.open(base) as original,fitz.open(output) as candidate:
        if len(original)!=260 or len(candidate)!=260:
            raise ValueError("Pass 1 lost or inserted A4 pages")
        changed=set(expected);strokes=0;unchanged=0
        for i in range(260):
            number=i+1;a=original[i];b=candidate[i]
            if number not in changed:
                if not render_equal(a,b):
                    raise ValueError(f"Unexpected changes on complete unchanged PDF page {number}")
                unchanged+=1
            else:
                if OLD in b.get_text() or NEW not in b.get_text():
                    raise ValueError(f"Unreplaced old normative claim p{number}")
                bbox=assert_localized_difference(a,b,regions[number])
                report[expected.index(number)]["actual_visual_difference_pt"]=bbox
        for rec in proof["page_map"]:
            num=rec["preview_pdf_page"]
            for step in rec["source_steps"]:
                rect=fitz.Rect(step["preview_rect_pt"])
                m=fitz.Matrix(1.35,1.35)
                p=original[num-1].get_pixmap(matrix=m,clip=rect,alpha=False)
                q=candidate[num-1].get_pixmap(matrix=m,clip=rect,alpha=False)
                if (p.width,p.height,p.samples)!=(q.width,q.height,q.samples):
                    raise ValueError(f"One of 1045 original pen tiles changed on ID{rec['main_id']} index{step['index']}")
                strokes+=1
    if strokes!=1045 or unchanged!=146:
        raise ValueError("Pass-1 page/pen provenance coverage is incomplete")
    result={
        "schema_version":1,
        "result":"PASS1_114_UNVERIFIED_NORMATIVE_PEDAGOGICAL_CLAIMS_QUARANTINED_AND_ALL_1045_ORIGINAL_PEN_INK_IDENTICAL",
        "source_cultural_v010_draft_sha256":BASE_SHA,
        "output_draft_sha256":digest(output),
        "output_pdf_pages":260,
        "canonical_glyphs":201,
        "original_cumulative_pen_tiles_exactly_unchanged":1045,
        "misleading_already_normative_verified_claims_removed":114,
        "entire_unedited_pages_pixel_identical":146,
        "unapproved_P8_glyph_and_word_readings_printed":0,
        "untouched_zi_second_pen_quarantine":True,
        "unapproved_illustrations_formally_signed":0,
        "human_editorial_signoff":False,
        "release_eligible":False,
        "page_corrections":report,
    }
    qa.parent.mkdir(parents=True,exist_ok=True)
    qa.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k!="page_corrections"},ensure_ascii=False,indent=2))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--qa",type=Path,required=True)
    opts=p.parse_args()
    build(opts.output,opts.qa)

if __name__=="__main__":main()
