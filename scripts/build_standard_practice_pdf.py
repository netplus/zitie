#!/usr/bin/env python3
"""Derive a compact 15-mm practice edition from the *released* v0.5.1 PDF.

This does NOT regenerate any glyph or alter the reviewed source, stroke-order
demonstrations, page links, bookmarks or the immutable v0.5.1 release.
The exact existing vector practice cells are copied into smaller cells using
PyMuPDF page-form clipping. No fonts or copyrighted assets are introduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
SOURCE_SHA256 = "7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
DEFAULT_DIR = ROOT / "deliverables/drafts/v0.6.0-15mm-rc1"
OUTPUT = DEFAULT_DIR / "zitie-v0.6.0-A4-15mm-candidate.pdf"
REPORT = DEFAULT_DIR / "geometry.json"
A4_PT = (595.2756, 841.8898)
MM_PT = 72.0 / 25.4
TARGET_MM = 15.0
TARGET_PT = TARGET_MM * MM_PT
SOURCE_PT = (A4_PT[0] - 72.0 - 7 * 6.0) / 8.0
NEW_COLS = 10
NEW_ROWS = 4
GAP_X = 6.0
GAP_Y = 16.0
TOLERANCE = 0.6


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def close(a: float, b: float, tol: float = TOLERANCE) -> bool:
    return abs(a - b) < tol


def old_grids(page: fitz.Page) -> list[list[fitz.Rect]]:
    """Identify only exactly the old 8 x 4 practice block; fail closed."""
    squares = []
    for path in page.get_drawings():
        for item in path["items"]:
            if item[0] != "re":
                continue
            rect = fitz.Rect(item[1])
            if close(rect.width, SOURCE_PT) and close(rect.height, SOURCE_PT):
                squares.append(rect)
    if not squares:
        return []
    if len(squares) != 32:
        raise ValueError(f"Page {page.number+1}: {len(squares)} old-sized squares, expected 32")
    squares.sort(key=lambda box: (box.y0, box.x0))
    rows = [sorted(squares[i:i + 8], key=lambda box: box.x0) for i in range(0, 32, 8)]
    for ri, row in enumerate(rows):
        if not all(close(r.y0, row[0].y0, 0.08) and close(r.y1, row[0].y1, 0.08) for r in row):
            raise ValueError(f"Page {page.number+1}: source row {ri} not horizontal")
        if not close(row[0].x0, 36.0):
            raise ValueError(f"Page {page.number+1}: unexpected left origin")
        for j, rect in enumerate(row):
            if not close(rect.x0, 36.0 + j * (SOURCE_PT + 6.0)):
                raise ValueError(f"Page {page.number+1}: source grid x={rect.x0}")
    pitch = rows[1][0].y0 - rows[0][0].y0
    if not all(close(rows[i+1][0].y0 - rows[i][0].y0, pitch) for i in range(3)):
        raise ValueError(f"Page {page.number+1}: inconsistent source row pitch")
    if not (close(pitch, SOURCE_PT + 13) or close(pitch, SOURCE_PT + 40)):
        raise ValueError(f"Page {page.number+1}: unexpected row pitch {pitch:.2f}pt")
    return rows


def clone_cell(page: fitz.Page, original: fitz.Document, pno: int,
               source: fitz.Rect, target: fitz.Rect) -> None:
    # A PDF form references the actual old vector cell, retaining its red/grey
    # ink, solid border and dashed alignment guides without rasterizing.
    page.show_pdf_page(target, original, pno, clip=source,
                       keep_proportion=False, overlay=True)


def reflow(page: fitz.Page, original: fitz.Document, pno: int,
           rows: list[list[fitz.Rect]]) -> dict:
    old_pitch = rows[1][0].y0 - rows[0][0].y0
    kind = "recall" if old_pitch > SOURCE_PT + 25 else "guided"
    orig_left = min(r[0].x0 for r in rows)
    orig_right = max(r[-1].x1 for r in rows)
    orig_top = rows[0][0].y0
    orig_bottom = rows[-1][0].y1
    block_width = NEW_COLS * TARGET_PT + (NEW_COLS - 1) * GAP_X
    x0 = (page.rect.width - block_width) / 2
    if x0 < orig_left + 5 or x0 + block_width > orig_right - 5:
        raise ValueError(f"Page {pno+1}: compact block would clip")
    if kind == "guided":
        total_height = NEW_ROWS * TARGET_PT + (NEW_ROWS - 1) * GAP_Y
        if total_height > orig_bottom - orig_top - 8:
            raise ValueError(f"Page {pno+1}: insufficient practice height")
        y0 = orig_top + (orig_bottom - orig_top - total_height) / 2
        # Blank only the exercise area, never the captions, footnotes or strokes.
        page.draw_rect(fitz.Rect(orig_left - 1, orig_top - 1,
                                 orig_right + 1, orig_bottom + 1),
                       color=None, fill=(1, 1, 1), overlay=True)
        new_ys = [y0 + k * (TARGET_PT + GAP_Y) for k in range(NEW_ROWS)]
    else:
        # Independent-recall pages have row labels *between* their four rows;
        # blank/reposition each row separately to retain those teaching labels.
        new_ys = []
        for old in rows:
            box = fitz.Rect(orig_left - 1, old[0].y0 - 1,
                            orig_right + 1, old[0].y1 + 1)
            page.draw_rect(box, color=None, fill=(1, 1, 1), overlay=True)
            new_ys.append((old[0].y0 + old[0].y1 - TARGET_PT) / 2)

    # Exercise semantics are immutable: row 1 trace (10), row 2 grey (10),
    # rows 3-4 sample first then write independently. Recall rows blank.
    for row_index, top in enumerate(new_ys):
        for col_index in range(NEW_COLS):
            if kind == "recall":
                source_cell = rows[row_index][1]
            elif row_index < 2:
                source_cell = rows[row_index][0]
            elif col_index == 0:
                source_cell = rows[row_index][0]
            else:
                source_cell = rows[row_index][1]
            x = x0 + col_index * (TARGET_PT + GAP_X)
            dst = fitz.Rect(x, top, x + TARGET_PT, top + TARGET_PT)
            clone_cell(page, original, pno, source_cell, dst)
    return {
        "page": pno + 1, "type": kind,
        "source_mm": round(SOURCE_PT / MM_PT, 4),
        "new_mm": TARGET_MM, "source_cells": 32, "new_cells": NEW_COLS * NEW_ROWS,
        "practice_top_pt": round(orig_top, 3),
        "practice_bottom_pt": round(orig_bottom, 3),
        "new_x_pt": round(x0, 3), "new_y_pt": [round(y, 3) for y in new_ys],
    }


def build(source: Path, output: Path, report: Path, previews: Path | None = None) -> dict:
    if digest(source) != SOURCE_SHA256:
        raise ValueError("Refusing to derive from a changed/unreviewed v0.5.1 source PDF")
    original = fitz.open(source)
    target = fitz.open(source)
    try:
        if len(original) != 299 or len(target) != 299:
            raise ValueError("Expected precisely 299 A4 source pages")
        old_toc = target.get_toc(simple=False)
        old_links = [p.get_links() for p in target]
        audit = []
        skipped = []
        sample_pages = []
        for pno, page in enumerate(target):
            if not close(page.rect.width, A4_PT[0]) or not close(page.rect.height, A4_PT[1]):
                raise ValueError(f"Not A4: page {pno+1}")
            rows = old_grids(original[pno])
            if not rows:
                skipped.append(pno+1)
                continue
            audit.append(reflow(page, original, pno, rows))
            if len(sample_pages) < 2 or (audit[-1]["type"] == "recall" and not any(
                    z["type"] == "recall" for z in sample_pages)):
                sample_pages.append(audit[-1])
            if page.get_links() != old_links[pno]:
                raise ValueError(f"Page {pno+1}: navigation links changed")

        guided = sum(x["type"] == "guided" for x in audit)
        recall = sum(x["type"] == "recall" for x in audit)
        # There are 258 original body pages + 10 full-character transfer
        # pages; newer material contains additional independent recall pages.
        if not (258 <= guided <= 280 and 2 <= recall <= 12):
            raise ValueError(f"Unexpected page coverage: guided={guided}, recall={recall}")
        if target.get_toc(simple=False) != old_toc:
            raise ValueError("Bookmarks changed")
        if any(target[pno].get_links() != old_links[pno] for pno in range(299)):
            raise ValueError("Link annotations changed")
        if any(close(item["new_mm"], item["source_mm"]) for item in audit):
            raise ValueError("No actual practice cell resizing")
        info = dict(target.metadata)
        info["title"] = "循序渐进汉字部首字帖 · 15 mm 中号田字格（独立候选）"
        info["subject"] = "Based on fixed v0.5.1; practice grids only; 15 mm; not an approved release"
        target.set_metadata(info)
        output.parent.mkdir(parents=True, exist_ok=True)
        target.save(output, garbage=4, deflate=True, no_new_id=True)
        result = {
            "status": "candidate_not_released",
            "source": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
            "source_sha256": SOURCE_SHA256,
            "output": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
            "output_sha256": digest(output),
            "bytes": output.stat().st_size,
            "a4_pages": 299, "bookmarks": len(old_toc),
            "transformed_pages": len(audit), "guided_pages": guided,
            "recall_pages": recall, "untouched_pages": len(skipped),
            "old_grid_mm": round(SOURCE_PT / MM_PT, 4),
            "new_grid_mm": TARGET_MM,
            "old_cells_per_practice_page": 32, "new_cells_per_practice_page": 40,
            "preserved_original_v051": True,
            "physical_print_test": "not performed; use 100 percent print scale",
            "rows": audit,
        }
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if previews:
            previews.mkdir(parents=True, exist_ok=True)
            for item in sample_pages:
                pno = item["page"] - 1
                target[pno].get_pixmap(matrix=fitz.Matrix(1.15, 1.15), alpha=False).save(
                    previews / f"page-{pno+1:03d}-15mm.png")
        return result
    finally:
        target.close()
        original.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--previews", type=Path, default=None)
    args = parser.parse_args()
    result = build(args.source, args.output, args.report, args.previews)
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
