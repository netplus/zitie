#!/usr/bin/env python3
"""Acquire immutable public stroke outlines, not font files or review approvals."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen, Request
ROOT=Path(__file__).resolve().parents[1]
REV='68d10a4b21150cae5e1ebbd223eed289cf32d90c'
BASE='https://raw.githubusercontent.com/chanind/hanzi-writer-data/'+REV

def retrieve(url):
    with urlopen(Request(url,headers={'User-Agent':'zitie-reference-acquisition/0.1'}),timeout=45) as r:
        return r.read(1024*1024)

def main():
    p=argparse.ArgumentParser();p.add_argument('--batches',nargs='+',choices=['B01','B02'],default=['B01']);args=p.parse_args()
    entries=[]
    for bid in args.batches: entries.extend(json.loads((ROOT/f'data/{bid}.json').read_text(encoding='utf-8'))['entries'])
    dest=ROOT/'build/vectors';dest.mkdir(parents=True,exist_ok=True)
    # Preserve the complete upstream license alongside downloaded outlines.
    license_bytes=retrieve(BASE+'/ARPHICPL.TXT')
    if b'ARPHIC PUBLIC LICENSE' not in license_bytes: raise ValueError('Unexpected license response')
    (dest/'ARPHICPL.TXT').write_bytes(license_bytes)
    ledger=[]
    for e in entries:
        ch=e['character'];url=BASE+'/data/'+quote(ch)+'.json';raw=retrieve(url);obj=json.loads(raw)
        if len(obj.get('strokes',[]))!=len(e['stroke_names']): raise ValueError(ch+': vector count mismatch')
        name=f'{ord(ch):04X}.json';(dest/name).write_bytes(raw)
        ledger.append({'character':ch,'file':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'status':'acquired_not_reviewed_by_script'})
    (dest/'manifest.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'NOTICE.txt').write_text('Outlines: Hanzi Writer / Make Me a Hanzi, from immutable revision '+REV+'.\nOutline files are unmodified. See ARPHICPL.TXT. No font files included.\nhttps://github.com/chanind/hanzi-writer-data\n',encoding='utf-8')

if __name__=='__main__':main()
