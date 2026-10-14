#!/usr/bin/env python3
"""Independent checks for the 15-mm print candidate, including real PDF rendering."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
DIR = ROOT / "deliverables/candidates/v0.5.2-15mm"
NEW = DIR / "zitie-v0.5.2-A4-15mm-candidate.pdf"
REPORT = DIR / "geometry.json"
TARGET_PT = 15 * 72 / 25.4


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def link_shapes(page):
    return sorted((x.get("kind"), tuple(round(v, 3) for v in x.get("from", ())),
                   x.get("page"), str(x.get("to")), x.get("uri")) for x in page.get_links())


def count_new_squares(page):
    found = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "re":
                r = fitz.Rect(item[1])
                if abs(r.width - TARGET_PT) < 0.3 and abs(r.height - TARGET_PT) < 0.3:
                    found.append(r)
    return found


def render_unchanged_outside(old, new, bounds=None):
    a = old.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    b = new.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    assert (a.width, a.height, a.n, a.stride) == (b.width, b.height, b.n, b.stride)
    if bounds is None:
        assert a.samples == b.samples, f"Unexpected raster change on page {old.number+1}"
        return
    # Outside the exercise region all vectors, text, navigation labels and page
    # furniture must render pixel-for-pixel as before.
    x0, y0, x1, y1 = bounds
    for y in range(0, a.height, 3):
        for x in range(0, a.width, 3):
            if x0 - 3 <= x <= x1 + 3 and y0 - 3 <= y <= y1 + 3:
                continue
            i = y * a.stride + x * a.n
            assert a.samples[i:i+3] == b.samples[i:i+3], (
                f"Page {old.number+1} changed outside exercise at {(x, y)}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=SOURCE)
    p.add_argument("--candidate", type=Path, default=NEW)
    p.add_argument("--report", type=Path, default=REPORT)
    args = p.parse_args()
    info = json.loads(args.report.read_text(encoding="utf8"))
    assert sha(args.source) == info["source_sha256"]
    assert sha(args.candidate) == info["output_sha256"]
    assert info["status"] == "candidate_not_released"
    assert (info["guided_pages"], info["recall_pages"], info["untouched_pages"]) == (268, 6, 25)
    assert info["old_cells_per_practice_page"] == 32
    assert info["new_cells_per_practice_page"] == 40
    assert info["new_grid_mm"] == 15
    altered = {x["page"]: x for x in info["rows"]}
    assert len(altered) == 274
    with fitz.open(args.source) as source, fitz.open(args.candidate) as candidate:
        assert len(source) == len(candidate) == 299
        assert source.get_toc() == candidate.get_toc()
        assert len(source.get_toc()) == 238
        for pno in range(299):
            assert link_shapes(source[pno]) == link_shapes(candidate[pno]), (
                f"Page {pno+1}: hyperlink changed")
        # All untouched content pages must remain pixel-identical.
        for pno in range(299):
            if pno + 1 not in altered:
                render_unchanged_outside(source[pno], candidate[pno])
        # Guided, independent recall, and end-of-book migration examples.
        samples = [6, 7, 34, 263, 265, 284, 285]
        for n in samples:
            assert n in altered, n
            rec = altered[n]
            squares = count_new_squares(candidate[n-1])
            assert len(squares) >= 40, (n, len(squares))
            left = min(x.x0 for x in squares)
            right = max(x.x1 for x in squares)
            top = min(x.y0 for x in squares)
            bottom = max(x.y1 for x in squares)
            assert left >= 35 and right <= 560 and top >= 150 and bottom <= 745, (
                n, left, right, top, bottom)
            render_unchanged_outside(source[n-1], candidate[n-1],
                (35, rec["practice_top_pt"], 560, rec["practice_bottom_pt"]))
    print(json.dumps({
        "result": "PASS", "A4_pages": 299, "sized_pages": len(altered),
        "unchanged_pages_pixel_identical": 25, "sample_reflow_pages_pixel_safe": 7,
        "grid_mm": 15, "columns": 10, "rows": 4,
        "source_sha256": info["source_sha256"],
        "candidate_sha256": info["output_sha256"],
        "physical_print_test": "not performed"
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
