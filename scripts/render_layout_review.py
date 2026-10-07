#!/usr/bin/env python3
"""Render P6 A4 layout-review candidates for artwork-ready batches.

This renderer is deliberately separate from publication/deliverables. It consumes the
reviewed canonical content and pinned vector material, supports every frozen B01-B21
batch, preserves fail-closed semantic fields, and paginates complex targets in chunks
of at most six cumulative strokes without shrinking the practice grid.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import ControlBoundsPen
from fontTools.svgLib.path import parse_path
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
W, H = A4
LEFT, RIGHT = 36, W - 36
COL = {
    "red": "#BB3D42",
    "previous": "#5F6264",
    "ink": "#282B2D",
    "trace": "#D47275",
    "pale": "#B9BBBC",
    "border": "#C99A9D",
    "guide": "#E0C5C7",
    "muted": "#74777A",
}


class Pen(BasePen):
    def __init__(self, path):
        super().__init__(None)
        self.path = path

    def _moveTo(self, p): self.path.moveTo(*p)
    def _lineTo(self, p): self.path.lineTo(*p)
    def _curveToOne(self, a, b, c): self.path.curveTo(*a, *b, *c)
    def _closePath(self): self.path.close()
    def _endPath(self): pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def setup_fonts(cjk: str, latin: str, fallback: str) -> None:
    for path in (cjk, latin, fallback):
        if not Path(path).is_file():
            raise ValueError(f"Provide an installed font: {path}")
    pdfmetrics.registerFont(TTFont("CJK", cjk))
    pdfmetrics.registerFont(TTFont("Latin", latin))
    pdfmetrics.registerFont(TTFont("CJKFallback", fallback, subfontIndex=0))


def resolve_font(value: str, font: str) -> str:
    if font != "CJK":
        return font
    face = pdfmetrics.getFont("CJK").face
    missing = {ch for ch in value if not ch.isspace() and ord(ch) not in face.charToGlyph}
    if not missing:
        return "CJK"
    fallback = pdfmetrics.getFont("CJKFallback").face
    fallback_missing = {ch for ch in value if not ch.isspace() and ord(ch) not in fallback.charToGlyph}
    if fallback_missing:
        raise ValueError("Missing font glyphs: " + "".join(sorted(fallback_missing)))
    return "CJKFallback"


def draw_text(c, x, y, value, size=11, color="ink", font="CJK", center=False):
    if value is None:
        return
    value = str(value)
    font = resolve_font(value, font)
    face = pdfmetrics.getFont(font).face
    missing = {ch for ch in value if not ch.isspace() and ord(ch) not in face.charToGlyph}
    if missing:
        raise ValueError("Missing font glyphs: " + "".join(sorted(missing)))
    c.setFont(font, size)
    c.setFillColor(HexColor(COL[color]))
    if center:
        c.drawCentredString(x, y, value)
    else:
        c.drawString(x, y, value)


def wrap_text(value: str, font: str, size: float, width: float) -> tuple[list[str], str]:
    value = str(value or "")
    if not value:
        return [], font
    font = resolve_font(value, font)
    lines, current = [], ""
    for ch in value:
        candidate = current + ch
        if current and pdfmetrics.stringWidth(candidate, font, size) > width:
            lines.append(current)
            current = ch
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines, font


def draw_wrapped(c, x, y, value, width, size=10.5, leading=15, color="ink", max_lines=2):
    lines, wrap_font = wrap_text(value, "CJK", size, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and pdfmetrics.stringWidth(last + "…", wrap_font, size) > width:
            last = last[:-1]
        lines[-1] = last + "…"
    for idx, line in enumerate(lines):
        draw_text(c, x, y - idx * leading, line, size=size, color=color, font=wrap_font)
    return len(lines)


def grid(c, x, y, size):
    c.saveState()
    c.setStrokeColor(HexColor(COL["border"]))
    c.setLineWidth(0.65)
    c.rect(x, y, size, size)
    c.setStrokeColor(HexColor(COL["guide"]))
    c.setLineWidth(0.4)
    c.setDash(2, 2)
    c.line(x + size / 2, y, x + size / 2, y + size)
    c.line(x, y + size / 2, x + size, y + size / 2)
    c.restoreState()


def vector_file(ch: str) -> Path:
    return ROOT / "build" / "vectors" / f"{ord(ch):04X}.json"


def order_code(entry: dict) -> str:
    review = entry.get("stroke_order_review") or {}
    return (
        entry.get("order_code")
        or review.get("order_code")
        or entry.get("order_code_candidate")
        or ""
    )


def stroke_count(entry: dict) -> int:
    if isinstance(entry.get("stroke_count"), int):
        return entry["stroke_count"]
    code = order_code(entry)
    if code:
        return len(code)
    for key in ("stroke_names", "stroke_names_candidate"):
        if isinstance(entry.get(key), list):
            return len(entry[key])
    review = entry.get("fine_stroke_names_review") or {}
    if isinstance(review.get("adjudicated_names"), list):
        return len(review["adjudicated_names"])
    raise ValueError(entry["character"] + ": no reviewed stroke count")


def reviewed_stroke_names(entry: dict) -> list[str] | None:
    status = (entry.get("field_status") or {}).get("fine_stroke_names", "")
    if status.startswith("conflict_fail_closed") or status.startswith("source_blocked_fail_closed"):
        return None
    if isinstance(entry.get("stroke_names"), list):
        return entry["stroke_names"]
    review = entry.get("fine_stroke_names_review") or {}
    if isinstance(review.get("adjudicated_names"), list):
        return review["adjudicated_names"]
    if status.startswith("reviewed_") and isinstance(entry.get("stroke_names_candidate"), list):
        return entry["stroke_names_candidate"]
    if not entry.get("field_status") and isinstance(entry.get("stroke_names_candidate"), list):
        return entry["stroke_names_candidate"]
    return None


def prepare_vector(raw: bytes, expected_count: int):
    obj = json.loads(raw)
    strokes = obj.get("strokes", [])
    if len(strokes) != expected_count:
        raise ValueError(f"{obj.get('character', '?')}: vector count mismatch")
    bounds = []
    for stroke in strokes:
        pen = ControlBoundsPen(None)
        parse_path(stroke, pen)
        if not pen.bounds or not all(math.isfinite(n) for n in pen.bounds):
            raise ValueError("Invalid vector path")
        bounds.append(pen.bounds)
    box = (
        min(b[0] for b in bounds),
        min(b[1] for b in bounds),
        max(b[2] for b in bounds),
        max(b[3] for b in bounds),
    )
    if max(box[2] - box[0], box[3] - box[1]) <= 0:
        raise ValueError("Empty glyph")
    return strokes, box


def glyph(c, data, x, y, size, color="red", step=None):
    strokes, (a, b, d, e) = data
    scale = 0.81 * size / max(d - a, e - b)
    c.saveState()
    c.translate(x + size / 2 - (a + d) * scale / 2,
                y + size / 2 - (b + e) * scale / 2)
    c.scale(scale, scale)
    upto = len(strokes) if step is None else step + 1
    for i, stroke in enumerate(strokes[:upto]):
        paint = color if step is None else ("red" if i == step else "previous")
        c.setFillColor(HexColor(COL[paint]))
        path = c.beginPath()
        parse_path(stroke, Pen(path))
        c.drawPath(path, stroke=0, fill=1)
    c.restoreState()


def structure_label(entry: dict) -> str:
    legacy = entry.get("structure_evidence") or {}
    if legacy.get("result") == "listed":
        return "结构：独体"
    cls = (entry.get("structure") or {}).get("class")
    if cls is None:
        cls = (entry.get("structure_review") or {}).get("structure_class")
    if cls == "undecomposable":
        return "结构：独体"
    if cls == "decomposable":
        return "结构：可分解"
    status = (entry.get("field_status") or {}).get("structure", "")
    if "fail_closed" in status or "source_blocked" in status:
        return "结构：精确身份边界保留"
    return "结构：—"


def pinyin_label(entry: dict) -> tuple[str, str]:
    pinyin = entry.get("pinyin")
    if isinstance(pinyin, str) and pinyin.strip():
        return pinyin.strip(), "Latin"
    status = (entry.get("field_status") or {}).get("pronunciation") or entry.get("pinyin_status") or ""
    if status.startswith("not_applicable"):
        return "读音：不单列", "CJK"
    if "fail_closed" in status or "source_blocked" in status:
        return "读音：证据边界保留", "CJK"
    return "读音：—", "CJK"


def source_label(entry: dict) -> str:
    review = entry.get("stroke_order_review") or {}
    publication = review.get("publication_id")
    printed = review.get("printed_page")
    if not publication and entry.get("primary_printed_page"):
        publication = "GF0023—2020"
        printed = entry.get("primary_printed_page")
    if publication and printed:
        return f"笔顺依据：{publication} 原印第{printed}页；矢量仅作绘图材料。"
    if publication:
        return f"笔顺依据：{publication} 原页证据已入库；矢量仅作绘图材料。"
    return "笔顺依据：字段级原页证据已入库；矢量仅作绘图材料。"


def draw_header(c, entry: dict, batch_id: str, item_no: int, page_idx: int, page_total: int):
    ch = entry["character"]
    suffix = "" if page_total == 1 else f" · {page_idx}/{page_total}"
    draw_text(c, LEFT, H - 49, ch + "｜笔顺练字帖" + suffix, 24)
    draw_text(c, RIGHT - 160, H - 46, f"{batch_id} / 主项{item_no:02d} / A4", 9, color="muted")
    c.setStrokeColor(HexColor(COL["red"]))
    c.setLineWidth(1.1)
    c.line(LEFT, H - 62, RIGHT, H - 62)


def draw_overview(c, entry: dict, data):
    grid(c, LEFT, 642, 94)
    glyph(c, data, LEFT, 642, 94, color="ink")
    py, py_font = pinyin_label(entry)
    draw_text(c, 155, 711, py, 20 if py_font == "Latin" else 11, font=py_font, color="ink" if py_font == "Latin" else "muted")
    draw_text(c, 155, 686, f"{stroke_count(entry)}画 · {structure_label(entry)}", 12)
    name = entry.get("component_name")
    if isinstance(name, str) and name.strip() and name.strip() != entry["character"]:
        draw_wrapped(c, 155, 666, "规范名称记录：" + name.strip(), RIGHT - 155, size=9.5, leading=13, color="muted", max_lines=1)
    tips = entry.get("tips") or []
    if tips:
        draw_wrapped(c, 155, 646, tips[0], RIGHT - 155, size=10.3, leading=14, max_lines=2)
    if len(tips) > 1:
        draw_wrapped(c, 155, 616, tips[1], RIGHT - 155, size=10.3, leading=14, color="red", max_lines=2)


def draw_steps(c, entry: dict, data, start: int, stop: int, top_y: float, size=78):
    names = reviewed_stroke_names(entry)
    count = stop - start
    span = RIGHT - LEFT - size
    xs = [(LEFT + RIGHT - size) / 2] if count == 1 else [LEFT + i * span / (count - 1) for i in range(count)]
    for local, step in enumerate(range(start, stop)):
        x = xs[local]
        label = f"第{step + 1}笔"
        if names and step < len(names):
            label += " · " + names[step]
        draw_text(c, x + size / 2, top_y + size + 11, label, 10.3, center=True)
        grid(c, x, top_y, size)
        glyph(c, data, x, top_y, size, step=step)
        if local < count - 1:
            x1, x2 = x + size + 8, xs[local + 1] - 8
            if x2 > x1 + 4:
                c.setStrokeColor(HexColor(COL["border"]))
                c.setLineWidth(0.7)
                mid = top_y + size / 2
                c.line(x1, mid, x2, mid)
                c.line(x2 - 3, mid + 3, x2, mid)
                c.line(x2 - 3, mid - 3, x2, mid)


def draw_practice(c, entry: dict, data, heading_y=430, first_row_y=326):
    draw_text(c, LEFT, heading_y, "02  描红、描淡字、独立写", 14, color="red")
    draw_text(c, LEFT, heading_y - 20, "第1行描红，第2行描淡字；后两行看范字，再在空格中练写。", 9.5, color="muted")
    cell = (RIGHT - LEFT - 7 * 6) / 8
    for row in range(4):
        y = first_row_y - row * (cell + 13)
        for col in range(8):
            x = LEFT + col * (cell + 6)
            grid(c, x, y, cell)
            if row < 2 or col == 0:
                glyph(c, data, x, y, cell, ["trace", "pale", "ink", "ink"][row])
    check = entry.get("check") or "按已审笔顺逐笔检查。"
    draw_wrapped(c, LEFT, 87, "写完检查：" + check, RIGHT - LEFT, size=9.5, leading=12, color="muted", max_lines=2)


def footer(c, entry: dict, batch_id: str, item_no: int, page_idx: int, page_total: int):
    c.setStrokeColor(HexColor(COL["guide"]))
    c.line(LEFT, 67, RIGHT, 67)
    draw_text(c, LEFT, 51, "P6版式候选｜仅供layout review，未归档为交付PDF。", 8, color="red")
    draw_wrapped(c, LEFT, 37, source_label(entry), RIGHT - LEFT - 82, size=7.4, leading=9, color="muted", max_lines=1)
    draw_text(c, RIGHT - 72, 29, f"{batch_id}-{item_no:02d} / {page_idx}-{page_total}", 7.5, color="muted", font="Latin")


def render_entry(c, entry: dict, data, batch_id: str, item_no: int) -> dict:
    n = stroke_count(entry)
    page_total = math.ceil(n / 6)
    for page_idx in range(1, page_total + 1):
        start = (page_idx - 1) * 6
        stop = min(start + 6, n)
        is_first = page_idx == 1
        is_last = page_idx == page_total
        draw_header(c, entry, batch_id, item_no, page_idx, page_total)
        if is_first:
            draw_overview(c, entry, data)
            draw_text(c, LEFT, 586, "01  看笔顺", 14, color="red")
            draw_text(c, RIGHT - 205, 587, "红色：当前笔　深灰：此前笔画", 9, color="muted")
            draw_steps(c, entry, data, start, stop, 477, size=78)
            if is_last:
                draw_practice(c, entry, data, heading_y=425, first_row_y=326)
            else:
                draw_text(c, LEFT, 444, f"本页展示第{start + 1}—{stop}笔；后续笔顺与练习继续下一页。", 10, color="muted")
                draw_text(c, LEFT, 405, "复杂字按页展开，不缩小田字格与累计笔画示范。", 11, color="red")
        else:
            draw_text(c, LEFT, 748, f"01  看笔顺（续：第{start + 1}—{stop}笔）", 14, color="red")
            draw_text(c, RIGHT - 205, 749, "红色：当前笔　深灰：此前笔画", 9, color="muted")
            draw_steps(c, entry, data, start, stop, 620, size=78)
            if is_last:
                draw_practice(c, entry, data, heading_y=500, first_row_y=395)
            else:
                draw_text(c, LEFT, 560, f"本页展示第{start + 1}—{stop}笔；下一页继续。", 10, color="muted")
                draw_text(c, LEFT, 515, "保持同一字号与田字格尺寸，避免复杂字因笔画多而缩小。", 11, color="red")
        footer(c, entry, batch_id, item_no, page_idx, page_total)
        c.showPage()
    return {
        "character": entry["character"],
        "main_id": entry.get("main_id"),
        "stroke_count": n,
        "layout_pages": page_total,
        "stroke_name_labels": reviewed_stroke_names(entry) is not None,
        "pinyin_display": pinyin_label(entry)[0],
        "structure_display": structure_label(entry),
        "practice_cells": 32,
    }


def available_batches() -> list[str]:
    plan = load_json(ROOT / "data/batches.json")
    return [b["id"] for b in plan["frozen_batches"]]


def render_batch(batch_id: str, outdir: Path) -> dict:
    batch = load_json(ROOT / f"data/{batch_id}.json")
    plan = load_json(ROOT / "data/batches.json")
    declared = next(b for b in plan["frozen_batches"] if b["id"] == batch_id)
    if declared.get("artwork_status") != "artwork_ready":
        raise ValueError(f"{batch_id}: declared artwork_status is not artwork_ready")
    pdf_path = outdir / f"{batch_id}-layout-review-A4.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4, pageCompression=1, invariant=1)
    c.setTitle(batch_id + " P6 layout review")
    entries = []
    for item_no, entry in enumerate(batch["entries"], 1):
        raw = vector_file(entry["character"]).read_bytes()
        data = prepare_vector(raw, stroke_count(entry))
        record = render_entry(c, entry, data, batch_id, item_no)
        record["vector_sha256"] = hashlib.sha256(raw).hexdigest()
        entries.append(record)
    c.save()
    page_count = len(PdfReader(str(pdf_path)).pages)
    expected_pages = sum(e["layout_pages"] for e in entries)
    if page_count != expected_pages:
        raise ValueError(f"{batch_id}: PDF pages {page_count} != expected {expected_pages}")
    return {
        "batch_id": batch_id,
        "target_count": len(entries),
        "pages": page_count,
        "pdf": pdf_path.name,
        "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "entries": entries,
    }


def main():
    choices = available_batches()
    p = argparse.ArgumentParser()
    p.add_argument("--batches", nargs="+", choices=choices)
    p.add_argument("--all", action="store_true")
    p.add_argument("--output", default="build/layout-review")
    p.add_argument("--font", default="/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf")
    p.add_argument("--latin-font", default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    p.add_argument("--fallback-font", default="/usr/share/fonts/truetype/arphic/uming.ttc")
    args = p.parse_args()
    if args.all and args.batches:
        p.error("use either --all or --batches")
    batch_ids = choices if args.all else (args.batches or ["B01"])
    setup_fonts(args.font, args.latin_font, args.fallback_font)
    outdir = ROOT / args.output
    outdir.mkdir(parents=True, exist_ok=True)
    batches = [render_batch(b, outdir) for b in batch_ids]
    writer = PdfWriter()
    for b in batches:
        writer.append(str(outdir / b["pdf"]))
    combined = outdir / "P6-layout-review-A4.pdf"
    with combined.open("wb") as stream:
        writer.write(stream)
    report = {
        "schema_version": 1,
        "record_kind": "P6_layout_review_candidate_generation",
        "publication_output": False,
        "manual_visual_review_required": True,
        "complex_pagination_rule": "at_most_6_cumulative_steps_per_A4_page; practice_grid_not_shrunk",
        "batch_ids": batch_ids,
        "target_count": sum(b["target_count"] for b in batches),
        "page_count": sum(b["pages"] for b in batches),
        "complex_target_count": sum(1 for b in batches for e in b["entries"] if e["stroke_count"] > 6),
        "batches": batches,
        "combined_pdf": combined.name,
        "combined_pdf_sha256": hashlib.sha256(combined.read_bytes()).hexdigest(),
        "status": "generated_for_manual_layout_review_not_approved",
    }
    (outdir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["target_count", "page_count", "complex_target_count", "combined_pdf_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
