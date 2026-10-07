#!/usr/bin/env python3
"""Build a versioned M1 patch candidate without overwriting legacy outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
from apply_artwork import apply_artwork
from build_batch import setup_fonts, prepare, make_entry_pages, frontmatter
from build_book_matter import register_font, build_toc, build_backmatter, build_navigation, stroke_count
from patch_edition import PatchEdition, register_variant_font
from validate_project import validate

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def build(args):
    edition = PatchEdition(args.version)
    out = ROOT / 'build' / ('v' + edition.identifier)
    out.mkdir(parents=True, exist_ok=True)
    coverage = load('data/coverage.json')
    batches = load('data/batches.json')
    variants = load('data/variants.json')
    expected_batches = [f'B{i:02d}' for i in range(1, 22)]
    if [b['id'] for b in batches['frozen_batches']] != expected_batches:
        raise ValueError('Expected full B01-B21 coverage')
    setup_fonts(args.font, args.latin_font)
    font = register_font()
    form_font, font_audit = register_variant_font(
        args.variant_font, [v['form'] for v in variants['items']], args.variant_subfont)
    files = []
    preface = out / 'preface.pdf'
    frontmatter(preface, 'candidate', edition=edition)
    files.append(preface)
    toc = out / 'toc.pdf'
    build_toc(toc, font, edition=edition)
    files.append(toc)
    checks = []
    for bid in expected_batches:
        batch = load(f'data/{bid}.json')
        validate(coverage, batches, variants, batch)
        pdf = out / (bid + '_candidate_A4.pdf')
        c = canvas.Canvas(str(pdf), pagesize=A4, pageCompression=1, invariant=1)
        c.setTitle(bid + '笔顺练字帖｜' + edition.label)
        page_number = 1
        for entry in batch['entries']:
            char = entry['character']
            raw = (ROOT / 'build/vectors' / f'{ord(char):04X}.json').read_bytes()
            art, audit = apply_artwork(char, raw)
            data = prepare(art, stroke_count(entry))
            pages = make_entry_pages(c, entry, data, page_number, 'candidate', batch, edition=edition)
            checks.append({'main_id': entry['main_id'], 'character': char, 'batch': bid,
                           'pages': pages, 'vector_sha256': hashlib.sha256(raw).hexdigest(),
                           'artwork_audit': audit})
            page_number += pages
        c.save()
        files.append(pdf)
    back = out / 'backmatter.pdf'
    build_backmatter(back, font, edition=edition, variant_font=form_font)
    files.append(back)
    writer = PdfWriter()
    for pdf in files:
        writer.append(str(pdf))
    writer.add_metadata({'/Title': '循序渐进汉字部首字帖｜' + edition.label})
    full = out / f'B01-B21_v{edition.identifier}_A4.pdf'
    with full.open('wb') as stream:
        writer.write(stream)
    raw = full.read_bytes()
    pages = len(PdfReader(full).pages)
    _, _, nav, _ = build_navigation()
    p2 = coverage['phase1_content_progress']['p2_fine_stroke_names']
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    meta = {'schema_version': 1, 'version': edition.identifier, 'mode': 'candidate',
            'pdf': full.name, 'pages': pages, 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(), 'source_commit': source,
            'variant_font': font_audit,
            'body_fonts': [{'file_name': Path(p).name, 'sha256': hashlib.sha256(Path(p).read_bytes()).hexdigest()}
                           for p in (args.font, args.latin_font)],
            'main_count': len(checks), 'practice_pages': sum(x['pages'] for x in checks),
            'entries': checks, 'navigation': nav,
            'p2_summary_scope': {'scope': p2['scope'], 'target_count': p2['target_count']},
            'corrected_errata': ['E001', 'E002'], 'visual_review': 'pending',
            'status': 'candidate_generated_not_archived', 'release_eligible': False}
    (out / 'generation.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: meta[k] for k in ('version', 'pdf', 'pages', 'bytes', 'sha256', 'source_commit', 'status')}, ensure_ascii=False, indent=2))
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version', default='0.4.1')
    p.add_argument('--font', default='/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf')
    p.add_argument('--latin-font', default='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    p.add_argument('--variant-font', default='/usr/share/fonts/truetype/arphic/uming.ttc')
    p.add_argument('--variant-subfont', type=int, default=0)
    build(p.parse_args())


if __name__ == '__main__':
    main()
