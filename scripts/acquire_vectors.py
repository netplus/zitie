#!/usr/bin/env python3
"""Acquire immutable, public stroke outlines. Acquisition is NOT content review."""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]
REV = '68d10a4b21150cae5e1ebbd223eed289cf32d90c'
BASE = 'https://raw.githubusercontent.com/chanind/hanzi-writer-data/' + REV

def main():
    entries = json.loads((ROOT/'data/B01.json').read_text(encoding='utf-8'))['entries']
    dest = ROOT/'build/vectors'
    dest.mkdir(parents=True,exist_ok=True)
    ledger=[]
    for e in entries:
        ch=e['character']; url=BASE+'/data/'+quote(ch)+'.json'
        with urlopen(Request(url,headers={'User-Agent':'zitie-reference-acquisition/0.1'}), timeout=45) as r:
            raw=r.read(1024*1024)
        obj=json.loads(raw)
        if len(obj.get('strokes',[])) != len(e['stroke_names']):
            raise ValueError(ch+': vector count differs from reviewed primary-source count')
        name=f'{ord(ch):04X}.json'
        (dest/name).write_bytes(raw)
        ledger.append({'character':ch,'file':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'status':'acquired_not_reviewed'})
    (dest/'manifest.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
    # A reference to the applicable upstream license, not a font-file download.
    (dest/'NOTICE.txt').write_text('Stroke outlines: Hanzi Writer / Make Me a Hanzi. Applicable Arphic Public License. No font files included.\nhttps://github.com/chanind/hanzi-writer-data\nhttps://github.com/skishore/makemeahanzi\n',encoding='utf-8')

if __name__=='__main__':main()
