#!/usr/bin/env python3
"""P3 art source safety, uniqueness and PDF vector placement.

The four handmade vector decorations are NOT teaching strokes, NOT a
publication approval, and may never replace any Page.show_pdf_page crop from
the released 299-page v0.5.1 PDF.
"""
from __future__ import annotations
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path

from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'data/cultural_edition/p3_artwork_draft_registry.json'
ALLOWED_ELEMENTS={'svg','title','g','path','ellipse','circle','rect','line'}
ALLOWED_ATTRIBUTES={'width','height','viewBox','role','aria-label','data-scene',
                    'opacity','fill','stroke','stroke-width','stroke-linejoin',
                    'stroke-linecap','d','cx','cy','rx','ry','r','x','y',
                    'x1','x2','y1','y2','transform'}

def git_blob_sha(binary:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(binary)).encode()+b'\0'+binary).hexdigest()

def read_registry(registry=REGISTRY,root=ROOT):
    entries=json.loads(Path(registry).read_text(encoding='utf8'))
    if entries.get('schema_version')!=1 or entries.get('review_state')!='all_artwork_unique_subject_drafts_not_publication':
        raise ValueError('Cannot treat P3 draft illustrations as approved sources')
    items=entries['entries']
    if len(items)!=4 or {x['main_character'] for x in items}!={'水','山','月','木'}:
        raise ValueError('Artwork sample must contain 4 distinct Hanzi themes')
    for attr in ('theme_key','asset_id','relative_path','expected_git_blob_sha','compositional_theme','alt_text'):
        values=[e[attr] for e in items]
        if len(set(values))!=4 or not all(isinstance(x,str) and x for x in values):
            raise ValueError('Art source identity not unique: '+attr)
    seen_motifs=set();seen_payloads=set();result={}
    for entry in items:
        if entry['editorial_status']!='draft_unapproved' or entry['illustrator_reviewed_at'] is not None:
            raise ValueError('No P3 illustration may claim prior human signoff')
        if entry['license_review']!='internal_authorship_review_pending':
            raise ValueError('Illustration license/source has not been reviewed')
        path=(Path(root)/entry['relative_path']).resolve()
        if not path.is_relative_to((Path(root)/'data/cultural_edition/artwork/drafts').resolve()):
            raise ValueError('P3 asset escapes designated draft art directory')
        raw=path.read_bytes()
        if len(raw)<1000 or len(raw)>120000:
            raise ValueError('Unusual vector draft content size')
        if git_blob_sha(raw)!=entry['expected_git_blob_sha']:
            raise ValueError('Artwork modified without updating signed-off source identifier')
        sha=hashlib.sha256(raw).hexdigest()
        if sha in seen_payloads:
            raise ValueError('Repeated artwork byte-for-byte')
        seen_payloads.add(sha)
        node=ET.fromstring(raw)
        if node.tag.rsplit('}',1)[-1]!='svg' or node.attrib.get('data-scene')!=entry['theme_key']:
            raise ValueError('SVG identity differs from registered character')
        if not entry.get('unique_motifs') or len(entry['unique_motifs'])<4:
            raise ValueError('Missing character-specific scene motifs')
        signatures=tuple(sorted(entry['unique_motifs']))
        if signatures in seen_motifs:
            raise ValueError('Two illustrations have identical motif sets')
        seen_motifs.add(signatures)
        paths=0
        for element in node.iter():
            tag=element.tag.rsplit('}',1)[-1]
            if tag not in ALLOWED_ELEMENTS:
                raise ValueError('Unsupported SVG element '+tag)
            if tag=='path':
                paths+=1
                if not re.match(r'^\s*[mM]',element.attrib.get('d','')):
                    raise ValueError('SVG paths require proper move-to grammar')
            if tag not in ('title','svg') and element.text and element.text.strip():
                raise ValueError('Text must not be drawn in pictorial art')
            for key,value in element.attrib.items():
                attr=key.rsplit('}',1)[-1]
                if attr not in ALLOWED_ATTRIBUTES:
                    raise ValueError('Disallowed SVG attribute '+attr)
                if 'url(' in value.lower() or '://' in value or '<' in value:
                    raise ValueError('External CSS/resource import not supported in art')
                if attr=='href' or attr.startswith('on'):
                    raise ValueError('Executable/remote SVG reference forbidden')
        if paths<10:
            raise ValueError('Scene is too trivial or empty')
        dimensions=(node.attrib.get('width'),node.attrib.get('height'),
                    node.attrib.get('viewBox'))
        if dimensions!=('820','630','0 0 820 630'):
            raise ValueError('Unexpected art viewBox cannot fit fixed P3 panel')
        result[entry['theme_key']]=dict(entry,
            actual_sha256=sha,source_size_bytes=len(raw),
            path_count=paths,final_editorial_status='draft_not_approved')
    return result

def paint_scene(canvas,theme_key,character,root=ROOT,assets=None):
    # The sole permitted art callable is placed in the upper-right region.
    # This function is never used to render any Chinese character or stroke.
    if assets is None:assets=read_registry(root=root)
    row=assets.get(theme_key)
    if not row or row['main_character']!=character:
        raise ValueError('Mismatched P3 theme or unregistered character')
    path=Path(root)/row['relative_path']
    drawing=svg2rlg(str(path))
    if drawing is None or drawing.width<=0 or drawing.height<=0:
        raise ValueError('Invalid renderer output for P3 SVG')
    mm=72/25.4
    x=111*mm;y=177*mm
    w=82*mm;h=75*mm
    canvas.saveState()
    canvas.translate(x,y)
    canvas.scale(w/drawing.width,h/drawing.height)
    renderPDF.draw(drawing,canvas,0,0)
    canvas.restoreState()

def report(registry=REGISTRY,root=ROOT):
    assets=read_registry(registry,root)
    return {'result':'SOURCE_VALIDATED_ART_DRAFT_NO_RELEASE',
            'number_of_distinct_assets':len(assets),
            'raster_assets':0,
            'external_resources':0,
            'handwriting_stroke_images_generated':0,
            'actual_files':[{'main_character':v['main_character'],
                             'asset_id':v['asset_id'],'theme_key':v['theme_key'],
                             'sha256':v['actual_sha256'],
                             'path_count':v['path_count'],
                             'status':v['final_editorial_status']} for v in assets.values()],
            'pending':['visual_expert_review','image_licensing_review',
                       '201_asset_global_uniqueness','final_style_approval']}
