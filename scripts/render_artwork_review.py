#!/usr/bin/env python3
"""Generate temporary P6 cumulative-stroke review sheets; never grants artwork approval."""
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
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
W, H = landscape(A4)
COLORS = {
    "red": HexColor("#BB3D42"),
    "previous": HexColor("#5F6264"),
    "ink": HexColor("#282B2D"),
    "guide": HexColor("#D9D9D9"),
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

def expected_stroke_count(entry: dict) -> tuple[int, list[str] | None]:
    """Return a reviewed drawing-step count without inventing fail-closed stroke names."""
    if isinstance(entry.get("stroke_names"), list):
        return len(entry["stroke_names"]), entry["stroke_names"]
    review = entry.get("fine_stroke_names_review") or {}
    if isinstance(review.get("adjudicated_names"), list):
        return len(review["adjudicated_names"]), review["adjudicated_names"]
    if isinstance(entry.get("stroke_names_candidate"), list):
        return len(entry["stroke_names_candidate"]), entry["stroke_names_candidate"]
    stroke_review = entry.get("stroke_order_review") or {}
    if isinstance(stroke_review.get("stroke_count"), int):
        return stroke_review["stroke_count"], None
    if isinstance(entry.get("stroke_count"), int):
        return entry["stroke_count"], None
    code = order_code(entry)
    if code:
        return len(code), None
    raise ValueError(entry["character"] + ": no reviewed stroke-count source")

def order_code(entry: dict) -> str:
    return (
        entry.get("order_code")
        or (entry.get("stroke_order_review") or {}).get("order_code")
        or entry.get("order_code_candidate")
        or ""
    )

def vector_path(ch: str) -> Path:
    return ROOT / "build" / "vectors" / f"{ord(ch):04X}.json"

def prepare(raw: bytes, expected_count: int):
    obj = json.loads(raw)
    strokes = obj.get("strokes", [])
    if len(strokes) != expected_count:
        raise ValueError(f"{obj.get('character', '?')}: vector count mismatch")
    bounds = []
    for stroke in strokes:
        pen = ControlBoundsPen(None)
        parse_path(stroke, pen)
        if not pen.bounds or not all(math.isfinite(x) for x in pen.bounds):
            raise ValueError("invalid vector path")
        bounds.append(pen.bounds)
    box = (
        min(b[0] for b in bounds),
        min(b[1] for b in bounds),
        max(b[2] for b in bounds),
        max(b[3] for b in bounds),
    )
    return obj, strokes, box

def draw_grid(c, x, y, size):
    c.saveState()
    c.setStrokeColor(COLORS["guide"])
    c.setLineWidth(0.5)
    c.rect(x, y, size, size)
    c.setDash(2, 2)
    c.line(x + size / 2, y, x + size / 2, y + size)
    c.line(x, y + size / 2, x + size, y + size / 2)
    c.restoreState()

def draw_glyph(c, strokes, box, x, y, size, step=None):
    a, b, d, e = box
    scale = 0.82 * size / max(d - a, e - b)
    c.saveState()
    c.translate(x + size / 2 - (a + d) * scale / 2,
                y + size / 2 - (b + e) * scale / 2)
    c.scale(scale, scale)
    upto = len(strokes) if step is None else step + 1
    for i, stroke in enumerate(strokes[:upto]):
        if step is None:
            color = COLORS["ink"]
        else:
            color = COLORS["red"] if i == step else COLORS["previous"]
        c.setFillColor(color)
        path = c.beginPath()
        parse_path(stroke, Pen(path))
        c.drawPath(path, stroke=0, fill=1)
    c.restoreState()

def render_batch(batch_id: str, outdir: Path) -> dict:
    batch = json.loads((ROOT / f"data/{batch_id}.json").read_text(encoding="utf-8"))
    pdf_path = outdir / f"{batch_id}-artwork-review.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=landscape(A4), pageCompression=1, invariant=1)
    records = []
    cols, rows = 5, 4
    margin_x, margin_y = 24, 24
    header_h = 54
    gap = 8
    cell_w = (W - 2 * margin_x - (cols - 1) * gap) / cols
    cell_h = (H - header_h - 2 * margin_y - (rows - 1) * gap) / rows
    glyph_size = min(cell_w - 8, cell_h - 22)

    for entry_index, entry in enumerate(batch["entries"], 1):
        ch = entry["character"]
        expected_count, names = expected_stroke_count(entry)
        raw = vector_path(ch).read_bytes()
        obj, strokes, box = prepare(raw, expected_count)
        code = order_code(entry)
        c.setFillColor(COLORS["ink"])
        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin_x, H - 24, f"{batch_id}  item={entry_index:02d}  main_id={entry.get('main_id')}  U+{ord(ch):04X}")
        c.setFont("Helvetica", 9)
        c.drawString(margin_x, H - 39, f"strokes={len(names)}  order_code={code}  vector_sha256={hashlib.sha256(raw).hexdigest()[:16]}...")
        c.setFont("Helvetica", 8)
        c.drawRightString(W - margin_x, H - 39, "FULL + cumulative steps; current=red previous=gray")

        panels = [("FULL", None)] + [(f"STEP {i+1}", i) for i in range(len(strokes))]
        for pidx, (label, step) in enumerate(panels):
            r, col = divmod(pidx, cols)
            if r >= rows:
                raise ValueError(f"{ch}: {len(strokes)} strokes exceed review-sheet capacity")
            x = margin_x + col * (cell_w + gap)
            y = H - header_h - margin_y - (r + 1) * cell_h - r * gap
            c.setFillColor(COLORS["ink"])
            c.setFont("Helvetica", 8)
            c.drawString(x + 2, y + cell_h - 10, label)
            gx = x + (cell_w - glyph_size) / 2
            gy = y + 2
            draw_grid(c, gx, gy, glyph_size)
            draw_glyph(c, strokes, box, gx, gy, glyph_size, step=step)
        c.showPage()

        records.append({
            "batch_id": batch_id,
            "character": ch,
            "main_id": entry.get("main_id"),
            "order_code": code,
            "stroke_names": names,
            "stroke_name_labels_available": names is not None,
            "vector_file": vector_path(ch).name,
            "vector_sha256": hashlib.sha256(raw).hexdigest(),
            "vector_stroke_count": len(strokes),
            "status": "generated_for_manual_visual_review_not_approved",
        })
    c.save()
    return {
        "batch_id": batch_id,
        "target_count": len(records),
        "pdf": pdf_path.name,
        "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "entries": records,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--batches", nargs="+", default=["B04","B05","B06","B07","B08","B09","B10","B11"])
    p.add_argument("--output", default="build/artwork-review")
    args = p.parse_args()
    outdir = ROOT / args.output
    outdir.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": 1,
        "record_kind": "P6_artwork_review_sheet_generation",
        "drawing_material_only": True,
        "manual_visual_review_required": True,
        "batches": [render_batch(b, outdir) for b in args.batches],
    }
    result["target_count"] = sum(b["target_count"] for b in result["batches"])
    (outdir / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"target_count": result["target_count"], "batches": args.batches}, ensure_ascii=False))

if __name__ == "__main__":
    main()
