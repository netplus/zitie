#!/usr/bin/env python3
"""Versioned patch rendering. Legacy v0.4.0 rendering stays separate."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@dataclass(frozen=True)
class PatchEdition:
    version: str = '0.4.1'
    mode: str = 'candidate'
    rc: int = 1

    def __post_init__(self):
        if not re.fullmatch(r'0\.4\.[1-9][0-9]*', self.version):
            raise ValueError('M1 only supports new 0.4.x patch versions')
        if self.mode not in ('candidate', 'formal'):
            raise ValueError('Unknown patch mode')
        if type(self.rc) is not int or self.rc < 1:
            raise ValueError('Positive RC number required')

    @property
    def identifier(self):
        return self.version + (f'-rc{self.rc}' if self.mode == 'candidate' else '')

    @property
    def label(self):
        return ('发布候选稿 v' if self.mode == 'candidate' else '勘误修订版 v') + self.identifier

    @property
    def practice_label(self):
        return self.label + '｜保留卷末 fail-closed/source-blocked 边界。'


def register_variant_font(path, forms, subfont=0, name='VariantFallback'):
    """Require a real TrueType embedded font with non-.notdef form glyphs.

    No font bytes are exported. The SHA and face index identify the local font.
    Cmap validation is only a structural check, not visual approval.
    """
    if type(subfont) is not int or subfont < 0:
        raise ValueError('Non-negative font face index required')
    path = Path(path)
    if not path.is_file():
        raise ValueError('Install/provide a TrueType variant font: ' + str(path))
    font = TTFont(name, str(path), subfontIndex=subfont)
    missing = sorted({ch for form in forms for ch in form
                      if not ch.isspace() and not font.face.charToGlyph.get(ord(ch), 0)})
    if missing:
        raise ValueError('Variant font lacks glyphs: ' + ''.join(missing))
    pdfmetrics.registerFont(font)
    return name, {
        'file_name': path.name, 'subfont_index': subfont,
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'font_name': font.face.name.decode('ascii', errors='replace') if isinstance(font.face.name, bytes) else str(font.face.name),
        'checked_form_count': len(forms), 'missing_glyphs': [],
        'rendering_scope': 'V007/V026/V029/V031/V032 form tokens only; other typography unchanged',
        'embedded_forms': ['龵', '⻊', '⺮', '⺌', '⺶'],
        'embedding': 'TrueType subset in PDF only; no font file exported',
        'visual_approval': False,
    }
