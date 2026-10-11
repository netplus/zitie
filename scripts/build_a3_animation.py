#!/usr/bin/env python3
"""A3: derive a read-only 201-glyph brush animation pack from the RELEASED PDF inputs.

The 299-page v0.5.1 PDF is the immutable publication reference. It contains
the section and individual ID bookmarks, but does NOT contain measured pen
trajectories. Reuse its exact B01-B21 pedagogical adapter, immutable pinned
Hanzi Writer artwork and hash-guarded edits; never infer stroke order by OCR.
No teaching-review or 2022 identity status is upgraded here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from pypdf import PdfReader

from acquire_vectors import REV
from apply_artwork import apply_artwork
from a1_audit import order_code
from build_batch import reviewed_stroke_names
from build_book_matter import stroke_count
from m3_model import display_entry, read_model

ROOT = Path(__file__).resolve().parents[1]
REL_PDF = 'deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf'
EXPECTED_PAGES = 299
ID_LABEL = re.compile(r'^ID(\d{3})\s+(.+)$')


def require(ok: bool, message: str):
    if not ok:
        raise ValueError('A3 PDF/animation mismatch: ' + message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pdf_bookmarks(path: Path) -> tuple[int, dict[int, tuple[str, int]]]:
    reader = PdfReader(str(path))
    pages = len(reader.pages)
    require(pages == EXPECTED_PAGES, 'released book must have 299 pages')
    mapping: dict[int, tuple[str, int]] = {}

    def walk(outlines):
        for item in outlines:
            if isinstance(item, list):
                walk(item)
                continue
            title = str(getattr(item, 'title', ''))
            match = ID_LABEL.fullmatch(title)
            if not match:
                continue
            number = int(match.group(1))
            page = reader.get_destination_page_number(item) + 1
            require(1 <= number <= 201, 'bookmark ID outside canonical set')
            require(1 <= page <= pages, 'bookmark page outside released PDF')
            require(number not in mapping, 'duplicate bookmark ID ' + str(number))
            mapping[number] = (match.group(2), page)

    walk(reader.outline)
    require(sorted(mapping) == list(range(1, 202)),
            'released PDF does not provide 201 unique ID bookmarks')
    return pages, mapping


def clean_geometry(art, count, ch):
    outlines = art.get('strokes')
    medians = art.get('medians')
    require(isinstance(outlines, list) and len(outlines) == count,
            ch + ': missing SVG outlines')
    require(isinstance(medians, list) and len(medians) == count,
            ch + ': missing per-stroke medians')
    result = []
    for i, (outline, median) in enumerate(zip(outlines, medians), 1):
        require(isinstance(outline, str) and
                re.match(r'^\s*M\s', outline, flags=re.I) is not None and
                re.search(r'[zZ]\s*$', outline) is not None,
                ch + ': invalid outline at stroke ' + str(i))
        require(isinstance(median, list) and len(median) >= 2 and all(
            isinstance(p, list) and len(p) == 2 and
            all(type(v) in (int, float) and math.isfinite(v) for v in p)
            for p in median), ch + ': invalid median at stroke ' + str(i))
        require(any(math.dist(median[k-1], median[k]) > .01
                    for k in range(1, len(median))),
                ch + ': zero-length median at stroke ' + str(i))
        result.append((outline, median))
    return result


def make_pack(root: Path, vectors: Path) -> dict:
    pdf = root / REL_PDF
    pdf_bytes = pdf.read_bytes()
    pdf_sha = digest(pdf_bytes)
    manifest = json.loads((root/'deliverables/manifest.json').read_text(encoding='utf-8'))
    matching = [a for a in manifest['artifacts'] if a.get('path') == REL_PDF]
    require(len(matching) == 1, 'exactly one released v0.5.1 manifest record required')
    release = matching[0]
    require(release.get('status') == 'released' and
            release.get('version') == '0.5.1' and
            release.get('pages') == EXPECTED_PAGES and
            release.get('sha256') == pdf_sha and
            release.get('bytes') == len(pdf_bytes),
            'PDF bytes must equal the frozen formal v0.5.1 manifest')
    pages, bookmarks = pdf_bookmarks(pdf)

    config, scope, policy, batches, by_id = read_model(root)
    require(len(by_id) == 201, 'canonical teaching model must contain 201 entries')
    glyphs = []
    total_strokes = 0
    overrides = 0
    blocked_names = 0
    missing_pinyin = 0
    for mid in range(1, 202):
        batch, entry = by_id[mid]
        ch = entry['character']
        require(len(ch) == 1, 'one-character main-id lookup required')
        book_char, first_page = bookmarks[mid]
        require(book_char == ch, 'PDF bookmark disagrees with B01-B21: ' + str(mid))
        count = stroke_count(entry)
        order = order_code(entry)
        require(isinstance(order, str) and
                len(order) == count and
                re.fullmatch(r'[1-5]+', order) is not None,
                ch + ': invalid reviewed stroke order code')
        raw = (vectors / f'{ord(ch):04X}.json').read_bytes()
        art, audit = apply_artwork(ch, raw)
        geometry = clean_geometry(art, count, ch)
        shown, decision = display_entry(root, policy, batch, entry)
        names = reviewed_stroke_names(shown, count)
        if names is not None:
            require(len(names) == count and all(
                isinstance(n, str) and n.strip() for n in names),
                ch + ': partial reviewed stroke names')
        else:
            blocked_names += 1
        if shown.get('pinyin') is None:
            missing_pinyin += 1
        strokes = []
        for k, (outline, median) in enumerate(geometry):
            strokes.append({
                'index': k + 1,
                'outline': outline,
                'median': median,
                'name': names[k] if names else None,
                'name_status': 'reviewed' if names else 'ordinal_only',
            })
        length_pages = math.ceil(count / 6)
        require(first_page + length_pages - 1 <= pages,
                ch + ': PDF teaching steps beyond released page range')
        overrides += bool(audit['modified_stroke_indices'])
        glyphs.append({
            'main_id': mid,
            'character': ch,
            'batch_id': batch['batch_id'],
            'normative_ref': f'{batch["batch_id"]}/{mid}',
            'expected_stroke_count': count,
            'order_code': order,
            'pinyin': shown.get('pinyin'),
            'reading_note': shown.get('reading_note'),
            'tips': shown['tips'],
            'check': shown['check'],
            'pdf_page_start': first_page,
            'pdf_page_end': first_page + length_pages - 1,
            'pdf_step_pages': length_pages,
            'fine_name_policy': decision['fine_names'],
            'pronunciation_policy': decision['pronunciation'],
            'source_sha256': audit['source_sha256'],
            'artwork_override_indices': [i+1 for i in audit['modified_stroke_indices']],
            'outline_review_status': 'released_pdf_derived_licensed_artwork',
            'trajectory_review_status': 'engineering_preview_unreviewed',
            'strokes': strokes,
        })
        total_strokes += count

    require(len(glyphs) == 201 and
            len({g['character'] for g in glyphs}) == 201,
            'duplicate/missing canonical characters')
    for g in glyphs:
        require(g['pdf_page_end'] < EXPECTED_PAGES,
                'practice page overlaps nonexistent closing page')
    return {
        'schema_version': 1,
        'version': 'A3.1-pdf-backed-brush-preview',
        'review_state': 'stroke_order_source_reviewed_motion_unreviewed',
        'publication': {
            'version': '0.5.1', 'title': '循序渐进汉字部首字帖',
            'pages': pages, 'sha256': pdf_sha, 'path': REL_PDF,
            'site_url': '../book/zitie-v0.5.1-A4.pdf',
            'step_limit_per_pdf_page': 6,
        },
        'source_revision': REV,
        'artwork_license': 'data/artwork/ARPHICPL.TXT',
        'source_kind': 'same approved PDF input outlines/medians, NOT captured handwriting',
        'summary': {
            'characters': len(glyphs), 'strokes': total_strokes,
            'batches': 21, 'artwork_override_characters': overrides,
            'ordinal_only_characters': blocked_names,
            'no_adopted_pinyin_characters': missing_pinyin,
        },
        'glyphs': glyphs,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--vectors', type=Path, default=Path('build/vectors'))
    parser.add_argument('--output', type=Path, default=Path('build/a3/book-pack.js'))
    args = parser.parse_args()
    root = args.root.resolve()
    vectors = args.vectors if args.vectors.is_absolute() else root / args.vectors
    path = args.output if args.output.is_absolute() else root / args.output
    pack = make_pack(root, vectors)
    # Static script, offline: neither the learner's browser nor the published
    # site downloads handwriting vectors, fonts or a remote JSON API.
    payload = json.dumps(pack, ensure_ascii=False, separators=(',', ':'),
                         sort_keys=False, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('window.ZITIE_BOOK_PACK = ' + payload + ';\n',
                    encoding='utf-8')
    print(json.dumps({'output': str(path), 'bytes': path.stat().st_size,
        **pack['summary'], 'pdf_sha256': pack['publication']['sha256']},
        ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
