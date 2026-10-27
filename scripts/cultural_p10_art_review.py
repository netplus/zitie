#!/usr/bin/env python3
"""P10: fail-closed 201-scene artwork ledger and four *unapproved* A4 art studies.

Art is separate from source ink: no SVG produced here is a Chinese glyph,
stroke step, P8 pronunciation proof, or P9 normative certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageOps, ImageStat
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from svglib.svglib import svg2rlg

from build_cultural_fullbook import PageArtist, W, H, MM, mm
from build_cultural_sample import fonts
from cultural_fullbook_model import ROOT, SHA, checked_drafts
from cultural_p3_artwork import read_registry

SOURCE_PDF=ROOT/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
P9_PDF=ROOT/"deliverables/drafts/cultural-v0.9-stroke-review/zitie-201-P9-normative-stroke-review-UNREVIEWED.pdf"
P9_SHA="8178a8d7bdf5258625efa0b74e7b82c0146c24da802f006f2135f17705e7fd89"
ART_DIR=ROOT/"data/cultural_edition/artwork/p10_studies"
INVENTORY=ROOT/"data/cultural_edition/p10_study_inventory.json"

def load_studies_inventory(registry:Path=INVENTORY)->dict:
    payload=json.loads(Path(registry).read_text(encoding="utf8"))
    if (payload.get("schema_version")!=1
        or payload.get("source_pdf_sha256")!=SHA
        or payload.get("release_eligible") is not False
        or payload.get("root_dir")!="data/cultural_edition/artwork/p10_studies"):
        raise ValueError("P10 artwork study inventory cannot silently change its source or release status")
    expected=("art_direction_status","semantic_review_status",
              "visual_human_first_review","visual_human_second_review","publication_eligible")
    out={}; filenames=set();scenes=set()
    for item in payload.get("entries",[]):
        mid=item.get("main_id")
        if (not isinstance(mid,int) or not 1<=mid<=201 or mid in out
            or not isinstance(item.get("character"),str) or len(item["character"])!=1):
            raise ValueError("Duplicate or invalid frozen P10 main ID")
        scene=item.get("scene");filename=item.get("filename")
        if (not isinstance(scene,str) or not re.fullmatch(r"[a-z0-9-]{8,90}",scene)
            or not isinstance(filename,str)
            or not re.fullmatch(rf"ID{mid:03d}-[a-z0-9-]+\.svg",filename)
            or scene in scenes or filename in filenames):
            raise ValueError("Each P10 study must have a safe unique scene and filename")
        if (item.get("art_direction_status")!="unreviewed"
            or item.get("semantic_review_status")!="pending"
            or item.get("license_origin")!="repo_composed_vectors_requires_human_rights_check"
            or item.get("visual_human_first_review") is not None
            or item.get("visual_human_second_review") is not None
            or item.get("publication_eligible") is not False):
            raise ValueError("No automatically approved artwork registry record is accepted")
        motifs=item.get("motifs")
        if (not isinstance(motifs,list) or len(motifs)<5
            or any(not isinstance(x,str) or not re.fullmatch(r"[a-z0-9-]{3,80}",x) for x in motifs)
            or len(set(motifs))!=len(motifs)
            or not isinstance(item.get("description"),str) or len(item["description"])<8):
            raise ValueError("P10 semantic scene needs five individually named physical motifs")
        out[mid]=(item["character"],scene,filename,item["description"],set(motifs))
        scenes.add(scene);filenames.add(filename)
    if not {39,64,77,88}.issubset(out) or len(out)>201:
        raise ValueError("P10 four authored baseline scenes must remain until superseded by reviewed replacements")
    return out

STUDIES=load_studies_inventory()

SAFE_TAGS={"svg","title","rect","path","circle","ellipse","line","g"}
SAFE_ATTRIBUTES={
    "width","height","viewBox","role","aria-label","data-scene","data-motif",
    "x","y","rx","ry","cx","cy","r","x1","x2","y1","y2","d",
    "stroke","stroke-width","stroke-linejoin","stroke-linecap","stroke-dasharray",
    "fill","opacity","transform",
}

PUBLISHED_SAFETY_FIELDS={
    "art_director_approval":None,
    "semantic_review":None,
    "licensing_proof":None,
    "accessibility_review":None,
    "gray_and_color_print_signoff":None,
    "editorial_first_review":None,
    "editorial_second_review":None,
    "publication_eligible":False,
}

def hash_file(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_svg(raw:bytes,scene:str,motifs:set[str])->dict:
    if not 2200<=len(raw)<=100000 or b"<!DOCTYPE" in raw or b"<!ENTITY" in raw:
        raise ValueError("P10 scene payload too small, huge or unsafe")
    try:
        svg=ET.fromstring(raw)
    except ET.ParseError as ex:
        raise ValueError("Invalid SVG") from ex
    if (svg.tag.rsplit("}",1)[-1]!="svg"
        or svg.attrib.get("data-scene")!=scene
        or svg.attrib.get("viewBox")!="0 0 820 630"
        or svg.attrib.get("width")!="820"
        or svg.attrib.get("height")!="630"):
        raise ValueError("An illustration was swapped, stretched or misidentified")
    found=[];paths=0
    for tag in svg.iter():
        kind=tag.tag.rsplit("}",1)[-1]
        if kind not in SAFE_TAGS:
            raise ValueError("Art SVG must not contain script, text, foreign objects or external media")
        if kind=="path":
            paths+=1
            if not re.match(r"^\s*[mM]",tag.attrib.get("d","")):
                raise ValueError("Illustration path must start with a move")
        if kind not in {"title","svg"} and tag.text and tag.text.strip():
            raise ValueError("Unreviewed SVG is not a place for Chinese teaching text")
        if "data-motif" in tag.attrib:found.append(tag.attrib["data-motif"])
        for k,v in tag.attrib.items():
            name=k.rsplit("}",1)[-1]
            if (name not in SAFE_ATTRIBUTES or name.startswith("on")
                or re.search(r"url\s*\(|https?:|data:|javascript:|<",v,re.I)):
                raise ValueError("Executable, foreign or unreviewed SVG resource")
    if paths<18 or not motifs.issubset(set(found)) or len(set(found))<5:
        raise ValueError("Too little physical story detail for a cultural art study")
    return {"paths":paths,"motifs":sorted(set(found)),"bytes":len(raw)}

def make_ledger(root:Path=ROOT,art_dir:Path|None=None)->dict:
    root=Path(root)
    art_dir=Path(art_dir) if art_dir else root/"data/cultural_edition/artwork/p10_studies"
    drafts=checked_drafts(root)
    old=read_registry(root=root)
    if len(old)!=4 or set(drafts)!=set(range(1,202)):
        raise ValueError("Original 201 glyphs and four P3 art drafts must remain unchanged")
    records=[];shas=set()
    for mid in range(1,202):
        row=drafts[mid];record={
            "main_id":mid,"character":row["character"],
            "theme_key":row["theme_key"],
            "canonical_storyboard":row.get("art_brief"),
            "source_culture_status":"unreviewed_201_editorial_drafts",
            "previous_P45_algorithmic_scene_role":"blocked_legacy_reference_only",
            "previous_P3_svg_role":"blocked_legacy_reference_only",
            "p10_art_asset":None,
            "p10_asset_sha256":None,
            "p10_asset_type":None,
            "review_state":"not_drawn",
            "reviewer_notes":None,
            **PUBLISHED_SAFETY_FIELDS,
        }
        if mid in STUDIES:
            char,scene,filename,meaning,motifs=STUDIES[mid]
            if char!=row["character"]:
                raise ValueError("Study does not match the frozen main ID")
            raw=(art_dir/filename).read_bytes()
            detail=validate_svg(raw,scene,motifs)
            sha=hashlib.sha256(raw).hexdigest()
            if sha in shas:
                raise ValueError("Duplicate P10 art payload")
            shas.add(sha)
            record.update({
                "p10_art_asset":f"data/cultural_edition/artwork/p10_studies/{filename}",
                "p10_asset_sha256":sha,
                "p10_asset_type":"hand_composed_svg_art_direction_study",
                "p10_visual_subject":meaning,
                "p10_detail":detail,
                "review_state":"art_direction_study_not_approved",
                "art_origin":"new_repo_composition_license_check_pending",
            })
        elif mid not in STUDIES:
            record["missing_visual_illustration"]=True
        records.append(record)
    assert len(records)==201 and len(shas)==len(STUDIES)
    return {
        "schema_version":1,
        "document_kind":"P10_ART_DIRECTION_REVIEW_REGISTRY_NOT_A_BOOK_RELEASE",
        "immutable_v051_source_sha256":SHA,
        "unchanged_P9_draft_sha256":P9_SHA,
        "original_main_ids":201,
        "original_strokes_untouched":1045,
        "professional_illustrations_approved":0,
        "art_direction_studies":len(STUDIES),
        "high_quality_illustrations_still_missing_or_not_approved":201,
        "not_yet_redrawn":201-len(STUDIES),
        "manual_art_and_print_signoffs":0,
        "release_eligible":False,
        "safety_note":"Old SVGs are never used as final paintings. Individually authored scene studies require artist, license, age, semantics, grayscale, paper and P8/P9 first/second reviews.",
        "entries":records,
    }

def audit_ledger(ledger:dict)->dict:
    """Hard-block promotions while any illustration, copy or real print is unsigned."""
    entries=ledger.get("entries",[])
    if (ledger.get("immutable_v051_source_sha256")!=SHA
        or ledger.get("unchanged_P9_draft_sha256")!=P9_SHA
        or ledger.get("release_eligible") is not False
        or ledger.get("professional_illustrations_approved")!=0
        or len(entries)!=201
        or [r.get("main_id") for r in entries]!=list(range(1,202))):
        raise ValueError("P10 art audit cannot approve a modified or partial full book")
    n=0;missing=0;digests=set();themes=set()
    for row in entries:
        if row["theme_key"] in themes or not row["character"]:
            raise ValueError("Missing or duplicated character-specific artwork brief")
        themes.add(row["theme_key"])
        for key,value in PUBLISHED_SAFETY_FIELDS.items():
            if row.get(key)!=value:
                raise ValueError("Unauthorized human or publication signoff in P10")
        if row["main_id"] in STUDIES:
            n+=1
            if (row["review_state"]!="art_direction_study_not_approved"
                or row["p10_asset_type"]!="hand_composed_svg_art_direction_study"
                or not row["p10_asset_sha256"]):
                raise ValueError("Artwork study is not verified against its provenance")
            if row["p10_asset_sha256"] in digests:
                raise ValueError("Two P10 scenes have identical bytes")
            digests.add(row["p10_asset_sha256"])
        else:
            missing+=1
            if (row["review_state"]!="not_drawn"
                or row["p10_art_asset"] is not None
                or row["p10_asset_sha256"] is not None):
                raise ValueError("Undrawn work must not be presented as an approved image")
    if (n,missing)!=(len(STUDIES),201-len(STUDIES)):
        raise ValueError("P10 cannot claim 201 art pieces were redrawn")
    return {"source_main_id_count":201,"reviewable_scene_studies":n,
            "undrawn_remaining":missing,"publication_eligible":False}

def raster_scene(path:Path)->Image.Image:
    drawing=svg2rlg(str(path))
    if drawing is None or drawing.width<=0 or drawing.height<=0:
        raise ValueError("P10 SVG did not produce visible vector artwork")
    pdf_bytes=renderPDF.drawToString(drawing)
    with fitz.open(stream=pdf_bytes,filetype="pdf") as doc:
        pix=doc[0].get_pixmap(matrix=fitz.Matrix(1.0,1.0),alpha=False)
        image=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
    if image.width<200 or image.height<150:
        raise ValueError("P10 artwork raster is unexpectedly tiny")
    return image

def check_print_scene(img:Image.Image)->dict:
    # Simulate grayscale output at actual A4 panel footprint, not at the
    # enlarged illustration full-view or a monitor-only zoom level.
    gray=ImageOps.grayscale(img.resize((969,827),Image.Resampling.LANCZOS))
    std=ImageStat.Stat(gray).stddev[0]
    dark=sum(1 for p in gray.resize((120,100)).getdata() if p<185)/12000
    if std<14 or dark<.012 or dark>.78:
        raise ValueError("Art study has insufficient contrast or lost its readable gray figure")
    return {"gray_stddev":round(std,2),"gray_dark_pixel_fraction":round(dark,4),
            "assessment":"machine_gray_preview_only_paper_test_missing"}

def paint_svg(canvas_obj,path:Path,x:float,y:float,w:float,h:float):
    drawing=svg2rlg(str(path))
    if drawing is None:raise ValueError("Missing renderable SVG")
    scale=min(mm(w)/drawing.width,mm(h)/drawing.height)
    canvas_obj.saveState()
    canvas_obj.translate(mm(x)+(mm(w)-scale*drawing.width)/2,
                         H-mm(y+h)+(mm(h)-scale*drawing.height)/2)
    canvas_obj.scale(scale,scale)
    renderPDF.draw(drawing,canvas_obj,0,0)
    canvas_obj.restoreState()

def create_review_pdf(pdf_path:Path,ledger:dict,root:Path=ROOT):
    fonts()
    rare=Path("/usr/share/fonts/truetype/arphic/uming.ttc")
    if not rare.is_file():raise ValueError("Missing rare-glyph CJK font for print proof")
    if "CultureRare" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CultureRare",str(rare),subfontIndex=0))
    pdf_path.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(pdf_path),pagesize=(W,H),pageCompression=1,invariant=1)
    c.setTitle("P10 文化插画审美方向 · 四幅样稿 · 未批准")
    p=PageArtist(c)
    p.page_border(1,"P10 · 四幅原创新场景审美母稿")
    p.label(22,38,"文化识字 · 插画方向审稿",25,"Kai","#943E48")
    p.label(22,58,"第三次交付 / P10 · P5 美术与纸质质量检查",11,"Kai")
    p.line(22,68,188,68)
    p.label(22,88,"201个主字全部建档，旧197张程序草稿禁止入书。",12,"Kai")
    p.label(22,103,f"当前{len(STUDIES)}张新图仅为绘画方向探索；201张均未获终审。",12,"Kai","#943E48")
    p.label(22,130,"审核重点：场景与字义相符、不是通用装饰、灰度可辨。",11,"Kai")
    p.label(22,144,"每张应检查：线条层次 / 适龄表达 / 源版权 / 印刷色差。",11,"Kai")
    p.label(22,169,"重要：本样本不是笔顺教学，也不批准任何拼音。",11,"Kai")
    p.label(22,189,"1045幅原PDF笔顺、P8/P9待审状态与旧版均不变。",11,"Kai")
    p.label(22,222,f"后续{201-len(STUDIES)}字仍需逐幅专门创作，禁止模板批量补位。",10,"Kai","#943E48")
    c.showPage()
    imgs=[]
    for number,mid in enumerate(sorted(STUDIES),2):
        row=ledger["entries"][mid-1]
        char,theme,filename,description,motifs=STUDIES[mid]
        art=root/"data/cultural_edition/artwork/p10_studies"/filename
        img=raster_scene(art)
        gray=ImageOps.grayscale(img).convert("RGB")
        p.page_border(number,f"P10 · ID{mid:03d} {char} · 新美术方向 / 未审")
        p.label(20,29,f"ID{mid:03d}  {char} · 文化场景原创新稿",20,"Kai","#943E48")
        p.label(20,42,description,10,"Kai")
        p.section(20,52,"构图放大审读",190)
        paint_svg(c,art,23,59,165,114)
        p.section(20,181,"成书版面大小",108)
        paint_svg(c,art,20,189,82,65)
        p.section(114,181,"黑白复印模拟",191)
        buf=io.BytesIO();gray.save(buf,format="PNG");buf.seek(0)
        c.drawImage(ImageReader(buf),mm(114),H-mm(254),width=mm(77),height=mm(65))
        p.label(20,268,"美术 / 语义 / 版权 / 灰度打印 / 原纸双审：均待签",8.4,"Kai","#943E48")
        c.showPage()
        imgs.append(img)
    c.save()
    return imgs

def run(output:Path,ledger_path:Path,qa_path:Path,root:Path=ROOT):
    root=Path(root)
    ledger=make_ledger(root)
    audit_ledger(ledger)
    if hash_file(root/"deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf")!=SHA:
        raise ValueError("Historical released PDF was modified")
    if hash_file(root/"deliverables/drafts/cultural-v0.9-stroke-review/zitie-201-P9-normative-stroke-review-UNREVIEWED.pdf")!=P9_SHA:
        raise ValueError("P9 master was modified during art generation")
    imgs=create_review_pdf(output,ledger,root)
    checks=[check_print_scene(i) for i in imgs]
    similarities=[]
    for i in range(len(imgs)):
        for j in range(i+1,len(imgs)):
            x=ImageOps.grayscale(imgs[i].resize((200,150)))
            y=ImageOps.grayscale(imgs[j].resize((200,150)))
            diff=ImageChops.difference(x,y)
            rms=math.sqrt(sum(v*v*n for v,n in enumerate(diff.histogram()))/(200*150))
            if rms<22:
                raise ValueError("P10 semantic scenes are too visually similar")
            similarities.append(round(rms,2))
    with fitz.open(output) as proof:
        if len(proof)!=1+len(STUDIES) or any(len(p.get_pixmap(matrix=fitz.Matrix(1,1)).samples)<10000 for p in proof):
            raise ValueError("P10 art proof failed page rendering")
    ledger_path.parent.mkdir(parents=True,exist_ok=True)
    qa_path.parent.mkdir(parents=True,exist_ok=True)
    ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    qa={
        "result":"PASS_P10_SOURCE_LOCKED_INDIVIDUALLY_AUTHORED_ART_STUDIES_AND_201_FAIL_CLOSED_LEDGERS",
        "glyphs_in_art_queue":201,"old_programmatic_P45_svg_blocked":197,
        "old_P3_svg_blocked":4,"new_studies":len(STUDIES),"still_undrawn":201-len(STUDIES),
        "professional_picture_approvals":0,"editorial_double_signoffs":0,
        "publication_eligible":False,"original_stroke_steps_unmodified":1045,
        "gray_machine_check":checks,"pairwise_rms_differences":similarities,
        "print_hardware_checked":False,"p8_p9_child_release_allowed":False,
        "pdf_pages":1+len(STUDIES),"pdf_sha256":hash_file(output)
    }
    qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(qa,ensure_ascii=False,indent=2))
    return qa

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--ledger",type=Path,required=True)
    parser.add_argument("--qa",type=Path,required=True)
    args=parser.parse_args()
    run(args.output,args.ledger,args.qa)

if __name__=="__main__":
    main()
