#!/usr/bin/env python3
"""Audit Chinese horizontal comma, semicolon and colon in immutable v0.5.1.

Diagnostic/quality gate, not a typography validator for other font families.
Checks all 299 pages, glyph usage, embedded UMing TrueType subset outlines,
advances, source PDF SHA, and PDF structure. Never writes/changes any PDF.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import io
import json
from pathlib import Path
import re

import fitz
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
REL = "deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf"
PDF_SHA256 = "7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
PDF_BYTES = 7_478_502
PAGE_COUNT = 299
EXPECTED = {
    "，": {"unicode": "FF0C", "uming_uses": 173, "uming_subsets": 16, "bbox": (171, -109, 277, 108)},
    "；": {"unicode": "FF1B", "uming_uses": 83, "uming_subsets": 17, "bbox": (138, -109, 251, 362)},
    "：": {"unicode": "FF1A", "uming_uses": 202, "uming_subsets": 16, "bbox": (130, 15, 230, 362)},
}
OTHER_FONT = "GBZenKai-Medium"
UMING_FONT = "UMingCN-0"


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def left_lower(bbox: tuple[int,int,int,int], advance: int, units: int) -> bool:
    """Conservative geometric alarm for this known font, not a normative ruling."""
    x0, y0, x1, y1 = bbox
    return (x0 < x1 <= 0.45 * units and y0 < y1 <= 0.40 * units
            and 0 <= x0 < 0.36 * units and advance == units)


def get_subset_metrics(doc: fitz.Document) -> dict[str, list[dict]]:
    allrefs = {f[0] for page in doc for f in page.get_fonts(full=True)}
    out: dict[str, list[dict]] = {k: [] for k in EXPECTED}
    font_count = 0
    for fx in sorted(allrefs):
        font_obj = doc.xref_object(fx)
        if UMING_FONT not in font_obj:
            continue
        match = re.search(r"/ToUnicode\s+(\d+)\s+0\s+R", font_obj)
        if not match:
            continue
        covered = False
        cmap = doc.xref_stream(int(match.group(1))).decode("latin1")
        font = TTFont(io.BytesIO(doc.extract_font(fx)[3]))
        check(font["head"].unitsPerEm == 1024, f"Unexpected units-per-em in xref {fx}")
        for char, rule in EXPECTED.items():
            found = re.findall(r"<([0-9A-Fa-f]{2,4})>\s+<" + rule["unicode"] + r">", cmap, re.I)
            if not found:
                continue
            covered = True
            check(len(found) == 1, f"Ambiguous ToUnicode for {char!r} at font xref {fx}")
            code = int(found[0], 16)
            glyphs = {t.cmap[code] for t in font["cmap"].tables if code in t.cmap}
            check(len(glyphs) == 1, f"Ambiguous embedded glyph for {char!r} at font xref {fx}")
            glyph_name = next(iter(glyphs))
            glyph = font["glyf"][glyph_name]
            bbox = (glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax)
            advance, _ = font["hmtx"][glyph_name]
            check(bbox == rule["bbox"], f"Unexpected {char} bbox {bbox} in xref {fx}")
            check(left_lower(bbox, advance, 1024), f"Off-center {char} bbox in xref {fx}")
            out[char].append({"font_xref": fx, "bbox_1024_em": list(bbox), "advance": advance})
        if covered:
            font_count += 1
    check(font_count == 20, f"Unexpected UMing subset count {font_count}")
    for ch, rule in EXPECTED.items():
        check(len(out[ch]) == rule["uming_subsets"],
              f"Unexpected {ch} glyph subset count {len(out[ch])}")
    return out


def audit(pdf: Path) -> dict:
    raw = pdf.read_bytes()
    check(len(raw) == PDF_BYTES and sha256(raw).hexdigest() == PDF_SHA256,
          "Input PDF is not the exact released v0.5.1 bytes")
    counts: dict[str, Counter] = {ch: Counter() for ch in EXPECTED}
    pages: dict[str, set[int]] = {ch: set() for ch in EXPECTED}
    with fitz.open(pdf) as doc:
        check(len(doc) == PAGE_COUNT, "Page count changed")
        check(len(doc.get_toc()) == 238, "Bookmark count changed")
        check(sum(len(p.get_links()) for p in doc) == 50, "Internal link count changed")
        for n, page in enumerate(doc, start=1):
            check(abs(page.rect.width - 595.2756) < 1.0 and
                  abs(page.rect.height - 841.8898) < 1.0, "Not portrait A4 on page " + str(n))
            for block in page.get_text("rawdict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        for ch in span["chars"]:
                            if ch["c"] in EXPECTED:
                                counts[ch["c"]][span["font"]] += 1
                                pages[ch["c"]].add(n)
        outlines = get_subset_metrics(doc)
    for ch, rule in EXPECTED.items():
        check(counts[ch][UMING_FONT] == rule["uming_uses"],
              f"Unexpected UMing {ch} occurrences: {counts[ch][UMING_FONT]}")
        check(set(counts[ch]).issubset({UMING_FONT, OTHER_FONT}),
              f"Unknown font used for {ch}: {dict(counts[ch])}")
    return {
        "schema_version": 1,
        "kind": "v051_remaining_cjk_punctuation_preventive_audit",
        "release_path": REL,
        "release_sha256": PDF_SHA256,
        "release_bytes": PDF_BYTES,
        "pages": PAGE_COUNT,
        "read_only_audit": True,
        "scope": "Full PDF text occurrence scan; strict UMingCN embedded-glyph audit of U+FF0C, U+FF1B, U+FF1A. Other font families retained from previous review, not freshly shape-certified.",
        "characters": {ch: {
            "code_point": "U+" + rule["unicode"],
            "total_occurrences": sum(counts[ch].values()),
            "fonts": dict(sorted(counts[ch].items())),
            "distinct_pages": len(pages[ch]),
            "uming_subset_count": len(outlines[ch]),
            "uming_bbox_1024_em": list(rule["bbox"]),
            "uming_advance": 1024,
            "off_center_glyphs_found": 0,
        } for ch, rule in EXPECTED.items()},
        "finding": "No analogous UMingCN centering defect for the audited comma, semicolon or colon; retain published v0.5.1 bytes.",
        "remaining_limitations": [
            "A virtual/PDF outline audit does not replace a physical paper print test.",
            "This audit does not certify all typography in all font families or all punctuation characters.",
        ],
        "physical_print_test_performed": False,
        "reissue_required_by_this_audit": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, default=ROOT / REL)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    report = audit(args.pdf)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sha256": report["release_sha256"], "pages": report["pages"],
                     "chars": report["characters"], "reissue_required": report["reissue_required_by_this_audit"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
