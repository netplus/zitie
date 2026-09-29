#!/usr/bin/env python3
"""Apply reviewed, source-hash-pinned stroke edits without altering vendor data."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OVERRIDES = ROOT / 'data/artwork/terminal-overrides-v1.json'


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def apply_artwork(character: str, raw: bytes, override_file: Path = OVERRIDES) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fail on a changed source; never infer edits from a glyph or stroke name."""
    if len(character) != 1:
        raise ValueError('Expected exactly one character')
    original = json.loads(raw)
    data = copy.deepcopy(original)
    manifest = json.loads(override_file.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported artwork override schema')
    applied: list[int] = []
    for entry in manifest['entries']:
        if entry['character'] != character:
            continue
        if digest(raw) != entry['source_sha256']:
            raise ValueError(character + ': vector source hash mismatch')
        index = entry['stroke_index']
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(data['strokes']):
            raise ValueError(character + ': invalid stroke index')
        if index in applied:
            raise ValueError(character + ': duplicate stroke override')
        old = original['strokes'][index]
        if digest(old.encode('utf-8')) != entry['source_stroke_sha256']:
            raise ValueError(character + ': original stroke hash mismatch')
        new = entry['replacement_path']
        if not isinstance(new, str) or not new.strip().startswith('M ') or not new.strip().endswith('Z'):
            raise ValueError(character + ': replacement must be a closed SVG path')
        data['strokes'][index] = new
        if 'medians' in data:
            data['medians'][index] = entry['replacement_median']
        applied.append(index)
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return data, {
        'source_sha256': digest(raw),
        'applied_artwork_sha256': digest(encoded),
        'override_sha256': digest(override_file.read_bytes()) if applied else None,
        'modified_stroke_indices': applied,
        'notice': 'Source-pinned teaching artwork edit, not an official normative glyph.' if applied else 'Unmodified vendor artwork.',
    }
