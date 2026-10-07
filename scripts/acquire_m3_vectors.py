#!/usr/bin/env python3
"""Acquire six fixed, hash-checked drawing JSONs; never grant source approval."""
import argparse
from pathlib import Path
from urllib.parse import quote
from acquire_vectors import retrieve, REV, BASE
from m3_model import ROOT, digest
from m3_migration import RECORD, CACHE, verify_outline
from verify_m2_closeout import load, require


def acquire(offline=False):
    manifest=load(ROOT, RECORD);out=ROOT/CACHE;out.mkdir(parents=True,exist_ok=True)
    require(manifest['upstream_revision']==REV, 'Unknown artwork revision')
    for r in manifest['cases']:
        expected=BASE+'/data/'+quote(r['whole_character'])+'.json'
        require(r['vector_url']==expected, 'Unexpected artwork URL')
        path=out/f'{ord(r["whole_character"]):04X}.json'
        if not path.is_file():
            require(not offline, 'Missing offline outline: '+str(path))
            raw=retrieve(expected);verify_outline(raw,r);path.write_bytes(raw)
        verify_outline(path.read_bytes(),r)
    license_path=ROOT/'build/vectors/ARPHICPL.TXT'
    if license_path.is_file(): raw=license_path.read_bytes()
    else:
        require(not offline, 'Missing offline outline license')
        raw=retrieve(BASE+'/ARPHICPL.TXT')
    require(b'ARPHIC PUBLIC LICENSE' in raw, 'Wrong outline license')
    (out/'ARPHICPL.TXT').write_bytes(raw)
    (out/'NOTICE.txt').write_text('Six unmodified Hanzi Writer drawing JSONs from '+REV+'.\n'
        'Drawing only, not normative authority. See ARPHICPL.TXT. No font file included.\n',encoding='utf-8')
    print('Six complete outlines and original license verified; no source approval granted.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--offline',action='store_true')
    acquire(p.parse_args().offline)
