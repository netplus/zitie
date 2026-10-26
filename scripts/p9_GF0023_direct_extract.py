#!/usr/bin/env python3
"""Exact GF0023-2020 official 581-page PDF table extraction (164/201 IDs).

Read the actual UCS column and the original printed five-type digit sequence
in each two-column table cell; NEVER substitute crowd TSV when parsing fails.
This certifies exact primary table code and source PDF page, NOT full pen
geometry or human editorial approval. The remaining 37 rare component shapes
are outside GF0023's 8105-character scope.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re
from pathlib import Path

import fitz
from cultural_p9_stroke_audit import REGISTRY,load,SOURCE_SHA

OFFICIAL_PDF_SHA="0ff0890afc34c5e486edeebafb05350dec69a7bf0d1d75044d7d3f7b722ec3d0"
SCOPE=164
SIDE_GRID=((260,291,116,224),(475,508,331,445))

def extract(input_pdf:Path,reference_registry:Path=REGISTRY):
    raw=input_pdf.read_bytes()
    source_sha=hashlib.sha256(raw).hexdigest()
    if source_sha!=OFFICIAL_PDF_SHA:
        raise ValueError("GF0023 primary PDF changed: official document source checksum mismatch")
    snapshot=load(reference_registry)
    if snapshot.get("frozen_source_pdf_sha256")!=SOURCE_SHA:
        raise ValueError("Frozen released stroke source changed")
    mains={r["main_id"]:r for r in snapshot["entries"]}
    if set(mains)!=set(range(1,202)):
        raise ValueError("P9 must retain 201 source main IDs")
    targets={f"{ord(row['character']):05X}":row for row in mains.values()}
    direct={};duplicates=set()
    with fitz.open(input_pdf) as official:
        if len(official)!=581:
            raise ValueError("Require complete 581-page original GF0023 standard PDF")
        for page in official:
            if abs(page.rect.width-595.275)>1:
                raise ValueError("Official PDF table page width changed")
            words=page.get_text("words")
            for xlow,xhigh,stroke_x_min,stroke_x_max in SIDE_GRID:
                anchors=sorted((w for w in words if xlow<=w[0]<xhigh and
                                re.fullmatch(r"[0-9A-F]{5}",str(w[4]))),
                               key=lambda w:w[1])
                for i,anchor in enumerate(anchors):
                    codepoint=str(anchor[4])
                    if codepoint not in targets:continue
                    target=targets[codepoint];mid=target["main_id"]
                    if mid in direct:
                        duplicates.add(mid)
                        continue
                    prev=anchors[i-1][1] if i else 0
                    nxt=anchors[i+1][1] if i+1<len(anchors) else 0
                    # The UCS codepoint is centered vertically inside its
                    # table row. For >7 strokes the number strip spans up to
                    # THREE horizontal lines; delimit by adjacent UCS anchors.
                    top=(prev+anchor[1])/2 if i else 129.0
                    bottom=(anchor[1]+nxt)/2 if i+1<len(anchors) else max(745,anchor[1]+100)
                    digits=[w for w in words if
                        stroke_x_min<=w[0]<=stroke_x_max and
                        top<=w[1]<=bottom and
                        re.fullmatch(r"[1-5]",str(w[4]))]
                    digits.sort(key=lambda w:(round(w[1]/5)*5,w[0]))
                    sequence="".join(str(d[4]) for d in digits)
                    if len(sequence)!=target["stroke_count"]:
                        raise ValueError(
                            f"GF0023 official row ambiguous for ID{mid:03d} "
                            f"{target['character']}: {sequence!r} count={target['stroke_count']} "
                            f"on official PDF page {page.number+1}")
                    direct[mid]={
                        "main_id":mid,"character":target["character"],
                        "unicode":codepoint,
                        "source_stroke_count":target["stroke_count"],
                        "GF0023_official_five_type_code":sequence,
                        "GF0023_original_pdf_page_1based":page.number+1,
                        "GF0023_original_UCS_cell_pt":[round(v,4) for v in anchor[:4]],
                        "GF0023_original_sequence_digit_positions_pt":[
                            [round(d[0],3),round(d[1],3)] for d in digits],
                        "secondary_reference_code":target["secondary_reference_five_type_code"],
                        "second_source_agreement":sequence==target["secondary_reference_five_type_code"],
                        "old_source_label_derived_coarse_code":target["source_five_type_code_candidate"],
                        "original_named_strokes_missing":target["generic_numbered_stroke_names"],
                        "printed_original_stroke_name_conflict_requires_review":(
                            "?" not in target["source_five_type_code_candidate"] and
                            sequence!=target["source_five_type_code_candidate"]),
                        "mainland_normative_reference_scope":"GF0023_8105_exact_UCS_row",
                        "fine_stroke_name_standard_not_yet_double_reviewed":True,
                        "actual_source_ink_geometry_not_yet_double_reviewed":True,
                        "first_editorial_reviewer":None,
                        "second_editorial_reviewer":None,
                        "publication_eligible":False,
                    }
    if duplicates or len(direct)!=SCOPE:
        raise ValueError(f"GF0023 primary extracted {len(direct)}/164 IDs duplicates={duplicates}")
    outside=[r for r in mains.values() if r["main_id"] not in direct]
    if len(outside)!=37 or any(r["in_secondary_8105_character_list"] for r in outside):
        raise ValueError("37 uncommon radical components have no GF0023 primary code")
    if any(not mains[mid]["in_secondary_8105_character_list"] for mid in direct):
        raise ValueError("Unofficial 8105 proxy disagrees with original GF0023 character coverage")
    mismatches=[x for x in direct.values() if not x["second_source_agreement"]]
    name_conflicts=[x for x in direct.values() if x["printed_original_stroke_name_conflict_requires_review"]]
    return {
       "schema_version":1,
       "status":"P9_164_GF0023_DIRECT_OFFICIAL_5TYPE_SEQUENCES_EXTRACTED_NOT_FINE_STROKE_APPROVAL",
       "actual_official_GF0023_pdf_sha256":source_sha,
       "actual_official_GF0023_pdf_pages":581,
       "official_source_link":"https://jw.beijing.gov.cn/language/bzgf/202105/P020210512414220837538.pdf",
       "official_standard":"GF 0023-2020",
       "source_original_book_pdf_sha256":SOURCE_SHA,
       "total_original_main_glyphs":201,
       "official_standard_exact_UCS_rows_extracted":164,
       "out_of_scope_or_missing_GF0023_rows":37,
       "official_count_and_code_length_checked":164,
       "official_vs_secondary_reference_agreements":164-len(mismatches),
       "official_vs_secondary_reference_conflicts":len(mismatches),
       "original_source_names_vs_official_five_type_conflict_records":len(name_conflicts),
       "original_source_ink_and_fine_names_human_approved":0,
       "uncommon_components_not_auto_substituted":True,
       "out_of_scope_characters":[{"main_id":r["main_id"],"character":r["character"],
                                   "reason":"not_listed_by_UCS_in_official_GF0023_8105_standard"}
                                  for r in sorted(outside,key=lambda x:x["main_id"])],
       "official_vs_secondary_conflict_details":mismatches,
       "original_name_vs_official_five_type_conflict_details":name_conflicts,
       "entries":[direct[k] for k in sorted(direct)],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--registry",type=Path,default=REGISTRY)
    p.add_argument("--output",required=True,type=Path)
    opts=p.parse_args()
    report=extract(opts.input,opts.registry)
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("entries","out_of_scope_characters","official_vs_secondary_conflict_details","original_name_vs_official_five_type_conflict_details")},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
