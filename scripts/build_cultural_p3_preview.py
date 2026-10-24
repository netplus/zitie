#!/usr/bin/env python3
"""Four-character P3 visual proof: unique vector decorations, original PDF ink.

The output is a DRAFT. Every teaching stroke and specimen glyph remains
identical to the actual released v0.5.1 source. No new pronunciation/quote
claims are approved by this artwork change.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from build_cultural_sample import create
from cultural_source_audit import audit
from cultural_p3_artwork import read_registry,paint_scene,report as artwork_report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--content',type=Path,required=True)
    p.add_argument('--artwork-registry',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--proof',type=Path,required=True)
    args=p.parse_args()
    assets=read_registry(registry=args.artwork_registry)
    content=json.loads(args.content.read_text(encoding='utf8'))
    if {e['theme_key'] for e in content['entries']}!=set(assets):
        raise ValueError('Every content theme requires exactly one unique registered art source')
    for entry in content['entries']:
        item=assets[entry['theme_key']]
        if entry['character']!=item['main_character']:
            raise ValueError('Artwork and teaching character do not match')
    result=create(args.source,audit(args.source,args.manifest),content,
        args.output,args.proof,
        theme_painter=lambda c,key,ch:paint_scene(c,key,ch,assets=assets))
    result['p3_artwork']=artwork_report(args.artwork_registry)
    result['editorial_release_eligible']=False
    result['artwork_is_teaching_ink']=False
    result['artwork_review_state']='source_vetted_distinct_vector_draft_editorial_pending'
    args.proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'pages':result['pages'],
       'source_steps':result['source_step_total'],
       'artworks':result['p3_artwork']['number_of_distinct_assets'],
       'publication_eligible':False},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
