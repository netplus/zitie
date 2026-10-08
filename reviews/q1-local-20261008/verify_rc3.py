#!/usr/bin/env python3
"""Verify a reviewed RC3 PDF without granting publication approval.

Requires PyMuPDF. RGB hashes are renderer-specific; use the version recorded
in the embedded review. This utility does not export font files or images.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import fitz

REVIEW_NAME = 'Q1-page-review-rc3.json'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normal(value: Any) -> Any:
    if isinstance(value, (fitz.Point, fitz.Rect, fitz.Quad)):
        return [normal(v) for v in value]
    if isinstance(value, dict):
        return {k: normal(v) for k, v in value.items() if k not in ('seqno', 'xref', 'id')}
    if isinstance(value, (list, tuple)):
        return [normal(v) for v in value]
    return value


def object_sha(value: Any) -> str:
    return sha(json.dumps(normal(value), sort_keys=True, separators=(',', ':')).encode())


def load_review(doc: fitz.Document) -> dict[str, Any]:
    if REVIEW_NAME not in doc.embfile_names():
        raise ValueError('The PDF lacks its original page-by-page review')
    review = json.loads(doc.embfile_get(REVIEW_NAME))
    records = review.get('page_results', [])
    if [r['page'] for r in records] != list(range(1, len(doc) + 1)):
        raise ValueError('Missing, duplicate, or out-of-order reviewed page')
    if not all(r['source_full_page_visually_read'] for r in records):
        raise ValueError('Historical visual coverage is incomplete')
    if review['renderers']['MuPDF'] != fitz.VersionBind:
        raise ValueError('Render hash comparison requires recorded PyMuPDF ' + review['renderers']['MuPDF'])
    return review


def inspect(pdf: Path, start: int, end: int, source: Path | None = None,
            original: Path | None = None) -> dict[str, Any]:
    """Perform current machine checks; never claim a new visual review."""
    doc = fitz.open(pdf)
    review = load_review(doc)
    # The final-check delivery is an incremental PDF update. Its initial bytes
    # are the original reviewed RC3, so evidence does not rely on a circular hash.
    packet = None
    if 'Q1-final-integrity.json' in doc.embfile_names():
        packet = json.loads(doc.embfile_get('Q1-final-integrity.json'))
        base = packet['base_pdf']
        if sha(pdf.read_bytes()[:base['bytes']]) != base['sha256']:
            raise ValueError('Original reviewed RC3 prefix is not intact')
        if sha(doc.embfile_get(REVIEW_NAME)) != packet['original_review_attachment_sha256']:
            raise ValueError('Original review attachment was changed')
        if doc.get_toc() != packet['bookmarks']:
            raise ValueError('Final delivery bookmarks were changed')
    if len(doc) != 299 or start < 1 or end > len(doc) or end < start:
        raise ValueError('Invalid page range or unexpected page count')
    baseline = fitz.open(source) if source else None
    original_doc = fitz.open(original) if original else None
    if source and sha(source.read_bytes()) != review['source']['sha256']:
        raise ValueError('RC2 source file does not match the historical review')
    if original_doc and original_doc.get_toc() != doc.get_toc():
        raise ValueError('Bookmarks differ from original frozen candidate')
    if len(doc.get_toc()) != 238:
        raise ValueError('Unexpected bookmark count')
    rows = []
    for page_no in range(start, end + 1):
        page = doc[page_no-1]
        prior = review['page_results'][page_no-1]
        failures: list[str] = []
        rgb = page.get_pixmap(matrix=fitz.Matrix(96/72, 96/72), alpha=False,
                              colorspace=fitz.csRGB)
        rendered = sha(rgb.samples)
        if rendered != prior['rc3_rgb96_sha256']:
            failures.append('render_differs_from_reviewed_RC3')
        if abs(page.rect.width - 595.2756) > .15 or abs(page.rect.height - 841.8898) > .15 or page.rotation:
            failures.append('not_portrait_A4')
        text = page.get_text('text')
        if not text.strip():
            failures.append('empty_text')
        footer = page.get_text('text', clip=fitz.Rect(0, page.rect.height-75, page.rect.width, page.rect.height))
        if 'v0.5.0-rc3' not in footer or f'{page_no}/299' not in footer:
            failures.append('incorrect_version_or_page_footer')
        missing, outside = [], []
        glyphs = 0
        for span in page.get_texttrace():
            for codepoint, glyph_id, origin, bounds in span['chars']:
                char = chr(codepoint)
                if char.isspace():
                    continue
                glyphs += 1
                if glyph_id == 0 or char in ('\ufffd', '\x00'):
                    missing.append({'character': char, 'font': span['font']})
                rect = fitz.Rect(bounds)
                if not (page.rect + (-.5,-.5,.5,.5)).contains(rect):
                    outside.append({'character': char, 'bbox': list(rect)})
        if missing:
            failures.append('unmapped_glyph')
        if outside:
            failures.append('text_outside_page')
        drawings_sha = object_sha(page.get_drawings())
        links = normal(page.get_links())
        if packet is not None:
            recorded = packet['page_results'][page_no-1]
            if links != recorded['links']:
                failures.append('link_changed_from_final_check')
            if drawings_sha != recorded['nontext_drawing_sha256']:
                failures.append('drawing_changed_from_final_check')
        if original_doc:
            if drawings_sha != object_sha(original_doc[page_no-1].get_drawings()):
                failures.append('nontext_drawing_changed_from_RC1')
            if links != normal(original_doc[page_no-1].get_links()):
                failures.append('link_changed_from_RC1')
        source_hash = None
        if baseline:
            p = baseline[page_no-1].get_pixmap(matrix=fitz.Matrix(96/72,96/72), alpha=False, colorspace=fitz.csRGB)
            source_hash = sha(p.samples)
            if source_hash != prior['source_rc2_rgb96_sha256']:
                failures.append('source_render_differs_from_reviewed_RC2')
            if drawings_sha != object_sha(baseline[page_no-1].get_drawings()):
                failures.append('nontext_drawing_changed_from_RC2')
        rows.append({'page': page_no, 'rgb96_sha256': rendered,
                     'source_rc2_rgb96_sha256': source_hash,
                     'nontext_drawing_sha256': drawings_sha,
                     'glyphs_checked': glyphs, 'glyph_findings': missing,
                     'out_of_bounds': outside, 'links': links,
                     'failures': failures, 'passed': not failures})
    return {'kind':'machine_revalidation_of_existing_visual_review_not_new_visual_approval',
            'file':pdf.name, 'sha256':sha(pdf.read_bytes()), 'bytes':pdf.stat().st_size,
            'pages':len(doc), 'renderer':fitz.VersionBind, 'start':start, 'end':end,
            'historical_review_attachment_sha256':sha(doc.embfile_get(REVIEW_NAME)),
            'page_results':rows, 'failures':[r for r in rows if r['failures']],
            'repository_archival_completed':False, 'new_remote_CI_executed':False,
            'formal_publication_completed':False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int, default=299)
    parser.add_argument('--rc2', type=Path)
    parser.add_argument('--rc1', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.pdf, args.start, args.end, args.rc2, args.rc1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pages_checked':len(report['page_results']),
                      'failed_pages':[r['page'] for r in report['failures']],
                      'report':str(args.output)}, ensure_ascii=False))
    raise SystemExit(1 if report['failures'] else 0)

if __name__ == '__main__':
    main()
