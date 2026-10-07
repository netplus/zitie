#!/usr/bin/env python3
"""Verify M1 candidate bytes/labels/font embedding; not visual approval."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from pypdf import PdfReader
from patch_edition import PatchEdition

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(directory):
    directory = Path(directory)
    meta = json.loads((directory / 'generation.json').read_text(encoding='utf-8'))
    edition = PatchEdition(meta['version'].split('-rc')[0])
    require(meta['version'] == edition.identifier, 'Candidate version mismatch')
    require(Path(meta['pdf']).name == meta['pdf'], 'Expected a flat candidate filename')
    require(re.fullmatch(r'[0-9a-f]{40}', meta['source_commit']), 'Exact source commit required')
    require(meta['mode'] == 'candidate' and meta['release_eligible'] is False, 'Premature release')
    require(meta['variant_font']['checked_form_count'] == 32, 'Variant font coverage incomplete')
    require(meta['variant_font']['missing_glyphs'] == [], 'Missing variant font glyphs')
    raw = (directory / meta['pdf']).read_bytes()
    require(len(raw) == meta['bytes'], 'Candidate size mismatch')
    require(hashlib.sha256(raw).hexdigest() == meta['sha256'], 'Candidate hash mismatch')
    reader = PdfReader(directory / meta['pdf'])
    texts = [p.extract_text() or '' for p in reader.pages]
    require(len(texts) == meta['pages'] == 276, 'Unexpected candidate page count')
    for page in reader.pages:
        require(abs(float(page.mediabox.width) - 595.2756) < .1
                and abs(float(page.mediabox.height) - 841.8898) < .1, 'Not portrait A4')
    require(meta['mode'] == 'candidate' and meta['release_eligible'] is False, 'Premature release')
    require(meta['main_count'] == len(meta['entries']) == 201, 'Main count mismatch')
    require(sorted(x['main_id'] for x in meta['entries']) == list(range(1, 202)), 'Main IDs mismatch')
    require(meta['practice_pages'] == sum(x['pages'] for x in meta['entries']) == 258, 'Practice count mismatch')
    for i in range(3):
        require(edition.label in texts[i], 'Wrong preface edition')
    for i in (3, 4):
        require(edition.label in texts[i], 'Wrong TOC edition')
    for i in range(5, 263):
        require(edition.practice_label in texts[i], 'Wrong practice edition on page ' + str(i+1))
        require('正式发布版 v0.4.0' not in texts[i], 'Stale practice edition')
    for i in (269, 271):
        require('V007' in texts[i] and '龵' in texts[i], 'V007 content missing')
        fonts = reader.pages[i]['/Resources']['/Font'].get_object().values()
        embedded = [f.get_object() for f in fonts if re.fullmatch(re.escape(meta['variant_font']['font_name']) + r'(?:-\d+)?', str(f.get_object().get('/BaseFont', '')).split('+')[-1].lstrip('/'))]
        require(embedded, 'V007 embedded font missing')
        require(all('/FontFile2' in f['/FontDescriptor'].get_object() for f in embedded), 'Font not embedded')
    require('P2统计范围：B04—B21，共171项' in texts[273], 'P2 scope note missing')
    require('上述157+14不是全书201项合计' in texts[273], 'P2 denominator disclosure missing')
    require('201 source_blocked_fail_closed' in texts[273], 'Source boundary missing')
    require(edition.identifier in texts[275] and 'E001' in texts[275] and 'E002' in texts[275], 'Errata/version record missing')
    require(meta['variant_font']['checked_form_count'] == 32, 'Variant font coverage incomplete')
    require(meta['variant_font']['missing_glyphs'] == [], 'Missing variant font glyphs')
    return {'version': edition.identifier, 'pages': 276, 'sha256': meta['sha256'],
            'structural_checks': 'passed', 'visual_approval': False,
            'release_eligible': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory', type=Path, default=ROOT/'build/v0.4.1-rc1')
    print(json.dumps(verify(p.parse_args().directory), ensure_ascii=False, indent=2))
