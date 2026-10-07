#!/usr/bin/env python3
"""Render temporary P6 A4 layout previews. Never archives deliverables or grants release."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import ControlBoundsPen
from fontTools.svgLib.path import parse_path
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
PAGE_W, PAGE_H = A4
REV = "68d10a4b21150cae5e1ebbd223eed289cf32d90c"

INK = HexColor("#282B2D")
RED = HexColor("#BB3D42")
PREV = HexColor("#5F6264")
GRID = HexColor("#D9D9D9")
PALE = HexColor("#D4D6D7")
MID = HexColor("#A6A9AB")

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKSC-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]

class Pen(BasePen):
    def __init__(self, path):
        super().__init__(None)
        self.path = path
    def _moveTo(self, p): self.path.moveTo(*p)
    def _lineTo(self, p): self.path.lineTo(*p)
    def _curveToOne(self, a, b, c): self.path.curveTo(*a, *b, *c)
    def _closePath(self): self.path.close()
    def _endPath(self): pass

def register_font():
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont("CJK", path, subfontIndex=0))
            return path
    raise FileNotFoundError("No Noto CJK system font found")

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def stroke_info(entry):
    if isinstance(entry.get("stroke_names"), list):
        return len(entry["stroke_names"]), entry["stroke_names"]
    review = entry.get("fine_stroke_names_review") or {}
    if isinstance(review.get("adjudicated_names"), list):
        return len(review["adjudicated_names"]), review["adjudicated_names"]
    if isinstance(entry.get("stroke_names_candidate"), list):
        return len(entry["stroke_names_candidate"]), entry["stroke_names_candidate"]
    sr = entry.get("stroke_order_review") or {}
    if isinstance(sr.get("stroke_count"), int):
        return sr["stroke_count"], None
    if isinstance(entry.get("stroke_count"), int):
        return entry["stroke_count"], None
    code = order_code(entry)
    if code:
        return len(code), None
    raise ValueError(entry["character"] + ": no reviewed stroke count")

def order_code(entry):
    return (
        entry.get("order_code")
        or (entry.get("stroke_order_review") or {}).get("order_code")
        or entry.get("order_code_candidate")
        or ""
    )

def structure_label(entry):
    st = entry.get("structure") or {}
    klass = st.get("class")
    if klass == "undecomposable":
        return "独体"
    if klass == "decomposable":
        return "合体"
    ev = entry.get("structure_evidence") or {}
    if ev.get("result") == "listed":
        return "独体"
    return "按内容边界"

def pinyin_label(entry):
    value = entry.get("pinyin")
    return value if value else "本项不标"

def component_label(entry):
    value = entry.get("component_name")
    if not value:
        return "—"
    return str(value)

def wrap_cjk(text, font, size, max_width):
    text = str(text or "")
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if cur and pdfmetrics.stringWidth(trial, font, size) > max_width:
            lines.append(cur)
            cur = ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]

def vector_file(ch):
    return ROOT / "build" / "vectors" / f"{ord(ch):04X}.json"

def prepare_vector(ch, expected_count):
    raw = vector_file(ch).read_bytes()
    obj = json.loads(raw)
    strokes = obj.get("strokes", [])
    if len(strokes) != expected_count:
        raise ValueError(f"{ch}: vector count {len(strokes)} != reviewed count {expected_count}")
    bounds = []
    for stroke in strokes:
        pen = ControlBoundsPen(None)
        parse_path(stroke, pen)
        if not pen.bounds or not all(math.isfinite(x) for x in pen.bounds):
            raise ValueError(ch + ": invalid vector path")
        bounds.append(pen.bounds)
    box = (
        min(x[0] for x in bounds),
        min(x[1] for x in bounds),
        max(x[2] for x in bounds),
        max(x[3] for x in bounds),
    )
    return raw, strokes, box

def draw_grid(c, x, y, size, line=0.55):
    c.saveState()
    c.setStrokeColor(GRID)
    c.setLineWidth(line)
    c.rect(x, y, size, size)
    c.setDash(2, 2)
    c.line(x + size / 2, y, x + size / 2, y + size)
    c.line(x, y + size / 2, x + size, y + size / 2)
    c.restoreState()

def draw_vector(c, strokes, box, x, y, size, mode="full", step=None, color=None):
    a,b,d,e = box
    scale = 0.80 * size / max(d-a, e-b)
    c.saveState()
    c.translate(x + size/2 - (a+d)*scale/2, y + size/2 - (b+e)*scale/2)
    c.scale(scale, scale)
    upto = len(strokes) if step is None else step+1
    for i, stroke in enumerate(strokes[:upto]):
        if color is not None:
            fill = color
        elif mode == "step":
            fill = RED if i == step else PREV
        else:
            fill = INK
        c.setFillColor(fill)
        p = c.beginPath()
        parse_path(stroke, Pen(p))
        c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

def draw_exemplar(c, entry, strokes, box, page_no, subtitle=None):
    margin = 13*mm
    box_size = 38*mm
    x = margin
    y = PAGE_H - margin - box_size - 5*mm
    draw_grid(c, x, y, box_size)
    draw_vector(c, strokes, box, x, y, box_size)
    c.setFillColor(INK)
    c.setFont("CJK", 21)
    c.drawString(x + box_size + 8*mm, PAGE_H - 23*mm, entry["character"])
    c.setFont("CJK", 12)
    c.drawString(x + box_size + 8*mm, PAGE_H - 32*mm, f"拼音：{pinyin_label(entry)}")
    c.drawString(x + box_size + 8*mm, PAGE_H - 40*mm, f"结构：{structure_label(entry)}")
    c.drawString(x + box_size + 8*mm, PAGE_H - 48*mm, f"部件名：{component_label(entry)}")
    c.setFont("CJK", 7.5)
    c.setFillColor(PREV)
    c.drawRightString(PAGE_W-margin, PAGE_H-12*mm, f"main_id {entry.get('main_id')}  ·  {page_no}")
    if subtitle:
        c.drawRightString(PAGE_W-margin, PAGE_H-18*mm, subtitle)
    return y - 7*mm

def draw_tips(c, entry, top_y):
    margin = 13*mm
    width = PAGE_W - 2*margin
    c.setFillColor(INK)
    c.setFont("CJK", 9.5)
    y = top_y
    tips = entry.get("tips") or []
    for idx, tip in enumerate(tips[:2], 1):
        lines = wrap_cjk(f"{idx}. {tip}", "CJK", 9.5, width)
        for line in lines:
            c.drawString(margin, y, line)
            y -= 5.2*mm
    check = entry.get("check")
    if check:
        y -= 1*mm
        c.setFillColor(PREV)
        for line in wrap_cjk("自查：" + str(check), "CJK", 9, width):
            c.drawString(margin, y, line)
            y -= 4.8*mm
    return y

def draw_demo_panel(c, strokes, box, names, x, y, size, label, step):
    c.setFillColor(INK)
    c.setFont("CJK", 7.4)
    c.drawString(x, y + size + 2.2*mm, label)
    draw_grid(c, x, y, size, line=0.45)
    draw_vector(c, strokes, box, x, y, size, mode="full" if step is None else "step", step=step)

def demo_label(names, step):
    if step is None:
        return "完整字形"
    if names and step < len(names):
        return f"第{step+1}笔 · {names[step]}"
    return f"第{step+1}笔"

def draw_demo_simple(c, strokes, box, names, top_y):
    margin = 13*mm
    panels = [(None, "完整字形")] + [(i, demo_label(names, i)) for i in range(len(strokes))]
    cols = len(panels)
    gap = 3.2*mm
    size = min(25*mm, (PAGE_W - 2*margin - gap*(cols-1))/cols)
    y = top_y - size - 7*mm
    for col,(step,label) in enumerate(panels):
        x = margin + col*(size+gap)
        draw_demo_panel(c, strokes, box, names, x, y, size, label, step)
    return y - 8*mm

def draw_demo_complex(c, strokes, box, names, top_y):
    margin = 13*mm
    panels = [(None, "完整字形")] + [(i, demo_label(names, i)) for i in range(len(strokes))]
    cols = 4
    rows = math.ceil(len(panels)/cols)
    gap_x = 4*mm
    gap_y = 7*mm
    avail_w = PAGE_W - 2*margin - gap_x*(cols-1)
    avail_h = top_y - 18*mm
    size = min(36*mm, avail_w/cols, (avail_h-gap_y*(rows-1))/rows)
    for idx,(step,label) in enumerate(panels):
        row, col = divmod(idx, cols)
        x = margin + col*(size+gap_x)
        y = top_y - (row+1)*size - row*gap_y - 7*mm
        draw_demo_panel(c, strokes, box, names, x, y, size, label, step)

def practice_cell(c, strokes, box, x, y, size, glyph_color=None):
    draw_grid(c, x, y, size)
    if glyph_color is not None:
        draw_vector(c, strokes, box, x, y, size, color=glyph_color)

def draw_practice(c, strokes, box, top_y):
    margin = 13*mm
    cols, rows = 8, 4
    size = (PAGE_W - 2*margin) / cols
    total_h = rows*size
    bottom = max(16*mm, top_y-total_h)
    patterns = [
        [RED]*8,
        [PALE]*8,
        [MID if i%2==0 else None for i in range(8)],
        [MID if i in (0,4) else None for i in range(8)],
    ]
    labels = ["描红","淡写","临写","独写"]
    for r in range(rows):
        y = bottom + (rows-1-r)*size
        c.setFillColor(PREV)
        c.setFont("CJK", 7)
        c.drawRightString(margin-2*mm, y+size/2-2, labels[r])
        for col in range(cols):
            x = margin + col*size
            practice_cell(c, strokes, box, x, y, size, patterns[r][col])
    return bottom

def render_entry(c, batch_id, entry, output_pages):
    count,names = stroke_info(entry)
    raw,strokes,box = prepare_vector(entry["character"], count)
    if count <= 6:
        page_no = len(output_pages)+1
        top = draw_exemplar(c, entry, strokes, box, page_no, "单页：示范 + 分层练习")
        top = draw_demo_simple(c, strokes, box, names, top)
        draw_tips(c, entry, top)
        draw_practice(c, strokes, box, 92*mm)
        c.showPage()
        output_pages.append({"character":entry["character"],"kind":"single","page":page_no})
        return 1, hashlib.sha256(raw).hexdigest()
    # complex: demonstration page
    page_no = len(output_pages)+1
    top = draw_exemplar(c, entry, strokes, box, page_no, "复杂字：示范页（不缩小练习格）")
    draw_demo_complex(c, strokes, box, names, top)
    c.showPage()
    output_pages.append({"character":entry["character"],"kind":"demo","page":page_no})
    # practice page
    page_no = len(output_pages)+1
    top = draw_exemplar(c, entry, strokes, box, page_no, "复杂字：练习页")
    top = draw_tips(c, entry, top)
    draw_practice(c, strokes, box, min(top-8*mm, 108*mm))
    c.showPage()
    output_pages.append({"character":entry["character"],"kind":"practice","page":page_no})
    return 2, hashlib.sha256(raw).hexdigest()

def render_batch(batch_id, outdir):
    batch = load_json(f"data/{batch_id}.json")
    path = outdir / f"{batch_id}-layout-preview-A4.pdf"
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
    pages=[]
    entry_records=[]
    for e in batch["entries"]:
        num, vector_sha = render_entry(c, batch_id, e, pages)
        count,names = stroke_info(e)
        entry_records.append({
            "character":e["character"],
            "main_id":e.get("main_id"),
            "stroke_count":count,
            "stroke_name_labels_available":names is not None,
            "layout_mode":"single_page" if count<=6 else "demo_plus_practice_pages",
            "pages":num,
            "vector_sha256":vector_sha,
        })
    c.save()
    return {
        "batch_id":batch_id,
        "target_count":len(entry_records),
        "page_count":len(pages),
        "pdf":path.name,
        "pdf_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "pages":pages,
        "entries":entry_records,
    }

def main():
    register_font()
    p=argparse.ArgumentParser()
    p.add_argument("--batches",nargs="+",default=[f"B{i:02d}" for i in range(1,22)])
    p.add_argument("--output",default="build/layout-preview")
    args=p.parse_args()
    outdir=ROOT/args.output
    outdir.mkdir(parents=True,exist_ok=True)
    result={
        "schema_version":1,
        "record_kind":"P6_layout_preview_generation",
        "temporary_preview_only":True,
        "policy":"data/layout-policy.json",
        "vector_revision":REV,
        "batches":[render_batch(b,outdir) for b in args.batches],
    }
    result["target_count"]=sum(b["target_count"] for b in result["batches"])
    result["page_count"]=sum(b["page_count"] for b in result["batches"])
    (outdir/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"target_count":result["target_count"],"page_count":result["page_count"],"batches":args.batches},ensure_ascii=False))

if __name__=="__main__":
    main()
