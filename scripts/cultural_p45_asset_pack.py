#!/usr/bin/env python3
"""Read/check all 201 drafted cultural SVGs, paint them outside teaching ink.

The four existing P3 scenes are retained unchanged; the 197 individually
generated images have byte hashes, source briefs, and never embed Unicode
glyphs, external CSS, raster images, HTML, remote data or scripted elements.
"""
from __future__ import annotations
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from cultural_fullbook_model import ROOT,SHA,checked_drafts
from cultural_p3_artwork import read_registry,paint_scene

ALLOWED={"svg","title","style","g","rect","circle","ellipse","line","path"}
PANEL=(111,43,82,70)

def checked_assets(registry_path:Path,assets_dir:Path,root:Path=ROOT):
    content=json.loads(Path(registry_path).read_text(encoding="utf-8"))
    if (content.get("schema_version")!=1 or content.get("source_pdf_sha256")!=SHA
            or content.get("generated_unique_svg_scenes")!=197
            or content.get("existing_svg_artwork_not_replaced")!=4
            or content.get("editorial_approved")!=0):
        raise ValueError("All 197 unreviewed cultural scenes are required")
    drafts=checked_drafts(root)
    old=read_registry(root=root)
    if len(old)!=4:raise ValueError("Original four SVGs were replaced")
    rows=content["entries"]
    if len(rows)!=197:raise ValueError("197 actual art records required")
    found={};hashes=set()
    for row in rows:
        mid=row["main_id"]
        if (mid in found or mid not in drafts or
            drafts[mid]["artwork_stage"]=="four_unique_svg_drafts_not_approved"
            or row["theme_key"]!=drafts[mid]["theme_key"]
            or row["character"]!=drafts[mid]["character"]
            or row["source_illustration_brief"]!=drafts[mid]["art_brief"]):
            raise ValueError("Art ID/themed brief does not match original cultural text")
        if not (row["filename"].startswith(f"ID{mid:03d}-") and
                re.fullmatch(r"[a-zA-Z0-9_.-]+\.svg",row["filename"])):
            raise ValueError("Art filename is not a safe one-to-one main ID")
        raw=(assets_dir/row["filename"]).read_bytes()
        if len(raw)<650 or len(raw)>90000:
            raise ValueError("Artwork scene too small or unexpectedly large")
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=row["sha256"] or len(raw)!=row["bytes"] or digest in hashes:
            raise ValueError("Scene SHA, size, or uniqueness changed")
        hashes.add(digest)
        node=ET.fromstring(raw)
        if node.tag.rsplit("}",1)[-1]!="svg" or node.attrib.get("data-scene")!=row["theme_key"]:
            raise ValueError("An artwork has an incorrect scene identity")
        motif=[el.attrib.get("data-motif") for el in node.iter() if "data-motif" in el.attrib]
        if len(set(motif))<2 or motif!=row["motifs"]:
            raise ValueError("A scene needs two source-linked physical motifs")
        for el in node.iter():
            tag=el.tag.rsplit("}",1)[-1]
            if tag not in ALLOWED:
                raise ValueError("Unsafe SVG visual tag: "+tag)
            for k,v in el.attrib.items():
                key=k.rsplit("}",1)[-1]
                if (key.lower().startswith("on") or key in ("href","style") or
                    re.search(r"https?://|url\s*\(|data:",v,re.I)):
                    raise ValueError("SVG artwork cannot load remote or executable assets")
            if tag=="style" and (el.text is None or len(el.text)>300):
                raise ValueError("Unexpected SVG stylesheet")
        if row["editorial_state"]!="vector_draft_unreviewed" or row["human_visual_signoff"] is not False:
            raise ValueError("Automated art must never claim professional signoff")
        found[mid]=dict(row,absolute_path=str(assets_dir/row["filename"]))
    expected=set(drafts)-{39,64,77,88}
    if set(found)!=expected or set(found)&{39,64,77,88}:
        raise ValueError("Art records do not cover the remaining 197 main glyphs")
    if len({r["theme_key"] for r in found.values()})!=197:
        raise ValueError("Two pictures share an unrelated theme")
    return found,old

def paint(canvas,row,generated,old,root=ROOT):
    mid=row["main_id"]
    manuscript=row["manuscript"]
    if mid in (39,64,77,88):
        theme=manuscript["theme_key"]
        paint_scene(canvas,theme,row["character"],root=root,assets=old)
        return {"art_state":"existing_p3_svg_draft_unreviewed",
                "main_id":mid,"theme_key":theme,
                "asset_sha256":old[theme]["actual_sha256"]}
    entry=generated.get(mid)
    if not entry:raise ValueError(f"Missing art: ID{mid:03d}")
    drawing=svg2rlg(entry["absolute_path"])
    if drawing is None or drawing.width<=0 or drawing.height<=0:
        raise ValueError("Generated SVG could not be rendered as vector content")
    mm=72/25.4
    x,y,w,h=PANEL
    # PDF user space has upward y. Painting here must not touch the left
    # 1045 original stroke positions; upper-right culture art panel only.
    canvas.saveState()
    canvas.translate(x*mm,(297-y-h)*mm)
    canvas.scale(w*mm/drawing.width,h*mm/drawing.height)
    renderPDF.draw(drawing,canvas,0,0)
    canvas.restoreState()
    return {"art_state":"new_source_linked_svg_draft_unreviewed",
            "main_id":mid,"theme_key":entry["theme_key"],
            "asset_sha256":entry["sha256"],
            "source_brief":entry["source_illustration_brief"],
            "motifs":entry["motifs"]}
