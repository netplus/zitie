#!/usr/bin/env python3
"""Probe unmodified GF0023 PDF text and rendered original page, never approve."""
from pathlib import Path
import argparse, hashlib, json
import fitz

def probe(path,output,render):
    data=path.read_bytes()
    doc=fitz.open(stream=data,filetype="pdf")
    if len(doc)<100:
        raise ValueError("Missing complete GF0023 standard")
    interesting=["一","十","人","子","水","牙","龺","鬥"]
    samples={}
    target_page=None
    for page in doc:
        t=page.get_text(sort=True)
        for ch in interesting:
            if ch not in samples and ch in t:
                start=t.find(ch)
                samples[ch]={"page":page.number+1,"raw_around":t[max(0,start-180):start+380]}
                if ch=="子":target_page=page.number
    render.mkdir(parents=True,exist_ok=True)
    if target_page is not None:
        doc[target_page].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(render/"GF0023_zi_reference_page.png")
    result={"status":"GF0023_FULL_PRIMARY_PDF_ACQUIRED_TEXT_PROBE_NOT_PER_CHARACTER_APPROVAL",
      "sha256":hashlib.sha256(data).hexdigest(),"pdf_pages":len(doc),"bytes":len(data),
      "sample_rows":samples,"display_page_for_zi":None if target_page is None else target_page+1}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    doc.close()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--render-dir",type=Path,required=True)
    a=p.parse_args()
    probe(a.input,a.output,a.render_dir)
