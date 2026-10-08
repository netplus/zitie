#!/usr/bin/env python3
"""Reproduce the v0.5.1 punctuation erratum edition from the reviewed RC3 PDF bytes.

This is a PDF-level derivative, not a regeneration from the earlier M3 RC1
source checkout. Keep that provenance distinction visible in release metadata.
The builder does not modify any archived candidate, normative dataset, or font.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import fitz
from fix_uming_cjk_punctuation import apply_to_doc

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3-finalcheck.pdf'
DEFAULT_OUTPUT = 'build/v0.5.1/zitie-v0.5.1-A4.pdf'
SOURCE_SHA = 'd54184705c6849d6617c7ea201a659d77796cad9b05792782032b320127bbb27'
FORMAL_SHA = '7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90'
FORMAL_BYTES = 7478502
FONT = Path('/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf')
FONT_SHA = '61519fb9bdda4a1a3aa02a12cbb76c2ef897ce879775d7ea2265d0a65fe54d16'
EDITS = 1121
PAGES = 299

# Exact span replacement: location-specific long editorial sentences are kept
# alongside the global page-version labels to prevent accidental substitutions.
REPLACEMENTS = {
    ('发布候选 ', 'always'): '正式版本 ',
    ('v0.5.0-rc3', 'always'): 'v0.5.1',
    ('区分发布候选与正式交付', 2): '本版验收与正式交付',
    ('本候选的299页已逐页复核，修订页也已复看。仓库归档、最终自动检查和正式发布尚未', 2):
        '本版299页已完成逐页复核，全部修订区域均已复看。正式版须经本版校验后归档。',
    ('完成，当前仍为修订候选。', 2): '本页保留原有教学提示及来源限制。',
    ('这是本次候选的数据，不反向改写旧PDF的发布快照。', 297):
        '这是本版审读数据，不反向改写旧PDF的发布快照。',
    ('发布候选 v0.5.0-rc3；本地逐页复核完成，尚未正式发布。', 299):
        '正式版本 v0.5.1；本书299页逐页复核完成，保留全部历史证据。',
    ('本文件是基于RC2制作的本地修订候选。仓库归档、最终自动检查和正式发布仍待完成，', 299):
        '本正式版从已归档的RC3终检候选派生，保留原教学内容和逐页审读来源，不冒充',
    ('不能仅靠改名升级为正式版。', 299): '从RC1源码重新生成；历史候选均可追溯。',
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(root: Path = ROOT, dest: Path | None = None, *, require_output_sha: bool = True, edit_log: Path | None = None):
    root = Path(root)
    source = root / SOURCE
    if dest is None:
        dest = root / DEFAULT_OUTPUT
    dest = Path(dest)
    assert sha(source.read_bytes()) == SOURCE_SHA, 'Reviewed RC3 input mismatch'
    assert FONT.is_file() and sha(FONT.read_bytes()) == FONT_SHA, 'Unexpected font input'
    assert fitz.VersionBind == '1.26.7', 'Unexpected PDF engine version'
    assert source.resolve() != dest.resolve(), 'Cannot overwrite reviewed RC3'
    doc = fitz.open(source)
    changes = []
    try:
        assert len(doc) == PAGES
        assert len(doc.get_toc()) == 238
        assert sum(len(p.get_links()) for p in doc) == 50
        for page_number, page in enumerate(doc, 1):
            replacements = []
            links = page.get_links()
            original_annots = doc.xref_get_key(page.xref, 'Annots')
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    for span in line['spans']:
                        key = (span['text'], page_number)
                        if key in REPLACEMENTS:
                            new = REPLACEMENTS[key]
                        elif (span['text'], 'always') in REPLACEMENTS and span['bbox'][1] > 740:
                            new = REPLACEMENTS[(span['text'], 'always')]
                        else:
                            continue
                        replacements.append((span, new))
            assert replacements, f'Missing expected version span on page {page_number}'
            for span, _ in replacements:
                r = fitz.Rect(span['bbox']); r += (-.25, -.25, .25, .25)
                page.add_redact_annot(r, fill=(1, 1, 1))
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                  graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                  text=fitz.PDF_REDACT_TEXT_REMOVE)
            if original_annots[0] == 'array' and original_annots != doc.xref_get_key(page.xref, 'Annots'):
                doc.xref_set_key(page.xref, 'Annots', original_annots[1])
            page.insert_font(fontname='GKAI', fontfile=str(FONT))
            for span, new in replacements:
                color_num = span['color']
                color = ((color_num >> 16 & 255)/255, (color_num >> 8 & 255)/255, (color_num & 255)/255)
                page.insert_text(fitz.Point(*span['origin']), new, fontname='GKAI',
                                 fontsize=span['size'], color=color, overlay=True)
                changes.append({'page': page_number, 'old': span['text'], 'new': new,
                                'rect': list(span['bbox']), 'size': span['size']})
            assert page.get_links() == links, f'Internal link annotations changed on page {page_number}'
        assert len(changes) == EDITS, f'Expected {EDITS} bounded edits, got {len(changes)}'
        punctuation_glyphs = apply_to_doc(doc)
        assert len(punctuation_glyphs) == 33
        metadata = doc.metadata
        metadata.update(title='循序渐进汉字部首字帖｜v0.5.1 标点位置勘误版',
                        subject='依据RC3终检候选重建，并仅对中文横排句号和顿号的内嵌字形进行左下定位修正；保留全书原有教学内容。',
                        keywords='字帖;299页;标点勘误;句号;顿号;v0.5.1;既有2022来源限制保留',
                        producer='PyMuPDF')
        doc.set_metadata(metadata)
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Explicitly preserve the original PDF ID so two builds generate
        # byte-identical content from identical PDF/font/engine inputs.
        doc.save(dest, garbage=4, deflate=True, clean=False, no_new_id=True)
    finally:
        doc.close()
    if edit_log is not None:
        edit_log = Path(edit_log); edit_log.parent.mkdir(parents=True, exist_ok=True)
        edit_log.write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    actual_sha = sha(dest.read_bytes())
    if require_output_sha:
        assert (dest.stat().st_size, actual_sha) == (FORMAL_BYTES, FORMAL_SHA), 'Non-reproducible formal output'
    return {'source_sha256': SOURCE_SHA, 'file': str(dest), 'sha256': actual_sha,
            'bytes': dest.stat().st_size, 'pages': PAGES, 'edits': len(changes), 'font_sha256': FONT_SHA, 'punctuation_glyphs':len(punctuation_glyphs)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--edit-log', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(dest=args.output, edit_log=args.edit_log), ensure_ascii=False, indent=2))
