#!/usr/bin/env python3
"""Probe Education Ministry GF3002-1999 original PDF without claiming norm approval.

Report exact PDF bytes hash, page/text structure, candidate UCS anchor words,
and 5 rasterized page samples. No OCR, no character approvals, no release.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from collections import Counter
from pathlib import Path
import fitz

OFFICIAL_URL="https://www.moe.gov.cn/jyb_sjzl/ziliao/A19/201001/W020150902457900316281.pdf"
SRC_SHA="7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"

def probe(source:Path,registry:Path,out:Path):
    r=json.loads(registry.read_text(encoding="utf8"))
    if (r.get("source_v051_sha256")!=SRC_SHA or
        len(r.get("out_of_scope_characters",[]))!=37 or r["release_eligible"] is not False):
        raise ValueError("P9 baseline 37 rare radicals changed")
    target={f"{ord(x['character']):04X}":x for x in r["out_of_scope_characters"]}
    targets=set(target)
    raw=source.read_bytes()
    if not raw.startswith(b"%PDF-") or len(raw)<20000:
        raise ValueError("Not a real Ministry GF3002 PDF")
    out.mkdir(parents=True,exist_ok=True)
    original_sha=hashlib.sha256(raw).hexdigest()
    found={k:[] for k in targets}
    stats=[]; most=Counter();samples={}
    with fitz.open(stream=raw,filetype="pdf") as book:
        n=len(book)
        for index,page in enumerate(book):
            text=page.get_text()
            words=page.get_text("words")
            hex_anchors={}
            for w in words:
                token=str(w[4]).strip().upper().removeprefix("U+")
                if token in targets:
                    hex_anchors.setdefault(token,[]).append({
                        "word":str(w[4]),"rect":[round(v,3) for v in w[:4]]})
            # Some PDF producers split a U+ code into spaces or glyph columns;
            # samples reveal whether exact native text extraction is possible.
            for hexkey,anchors in hex_anchors.items():
                found[hexkey].append({"physical_pdf_page":index+1,
                                      "word_anchors":anchors[:6]})
            if index<8 or index%50==0 or index>=n-3:
                stats.append({"page":index+1,"text_characters":len(text),
                              "word_count":len(words),
                              "sample":text[:190].replace("\n"," ")})
            most["pages_with_native_text"]+=int(len(text.strip())>0)
            if index in (0,2,6,10,15,n//2,n-1):
                samples[index]=page
        matched_pages=sorted({r["physical_pdf_page"] for seq in found.values() for r in seq})
        selected=[0,2,6,n//2,n-1]+[p-1 for p in matched_pages[:4]]
        sampled=[]
        for i in dict.fromkeys(index for index in selected if 0<=index<n):
            pix=book[i].get_pixmap(matrix=fitz.Matrix(1.05,1.05),alpha=False)
            dest=out/f"GF3002-original-page-{i+1:04d}.png"
            pix.save(str(dest))
            sampled.append({"physical_page":i+1,"file":dest.name})
        report={
           "schema_version":1,
           "result":"GF3002_OFFICIAL_ORIGINAL_PDF_PROBE_NOT_A_NORMATIVE_CHARACTER_APPROVAL",
           "source_url":OFFICIAL_URL,
           "official_pdf_sha256":original_sha,
           "official_pdf_bytes":len(raw),"official_pdf_pages":n,
           "original_201_v051_sha256":SRC_SHA,
           "rare_radical_targets":37,
           "targets_with_word_level_UCS_anchors":sum(bool(x) for x in found.values()),
           "pages_with_nonempty_native_text":most["pages_with_native_text"],
           "target_anchors":[{"main_id":v["main_id"],"character":v["character"],
                              "ucs_hex":k,"matches":found[k][:8]} for k,v in sorted(target.items(),key=lambda i:i[1]["main_id"])],
           "sample_native_page_text":stats,
           "rendered_primary_source_pages":sampled,
           "limitation":"Do not treat matching characters or UCS anchors as verified original stroke sequences: coordinate-isolate row digits and have humans confirm drawn geometry/pen names.",
           "human_reviewers":[],"approved_normative_stroke_shapes":0,
           "release_eligible":False,
        }
    p=out/"GF3002-original-PDF-source-structure-probe.json"
    p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("target_anchors","sample_native_page_text")},
                     ensure_ascii=False,indent=2))
    print("First original native table text probes: "+str(stats[:7]))
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--registry",type=Path,default=Path("data/cultural_edition/p9_normative_open_cases_37_83.json"))
    a.add_argument("--out",type=Path,required=True)
    s=a.parse_args()
    probe(s.source,s.registry,s.out)
