#!/usr/bin/env python3
"""P7 formal-release preflight gate.

This gate does not fabricate GF0011—2022 full-text verification.
It requires the archived RC1, terminal fail-closed disclosure, and all
content/artwork/layout/publication QA prerequisites before a formal PDF
may be generated for final visual review.
"""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

coverage=load("data/coverage.json")
batches=load("data/batches.json")
manifest=load("deliverables/manifest.json")
progress=coverage["phase1_content_progress"]
p4=progress["p4_identity_position_migration"]
p5=progress["p5_content_ready"]
p6=progress["p6_artwork_layout"]
p7=progress["p7_publication"]

assert progress["active_remaining_phase"]=="P7"
assert coverage["target_edition"]=="GF0011—2022"
assert coverage["target_edition_status"]=="fulltext_pending"

exact=p4["exact_2022_item_fields"]
assert exact["target_count"]==201
assert exact["reviewed"]==0
assert exact["source_blocked_fail_closed"]==201
assert exact["ordinary_pending"]==0
assert exact["evidence"] and exact["reopen_condition"]

migration=p4["position_migration_cumulative"]
assert migration["target_count"]==201
assert migration["reviewed"]==198
assert migration["conflict_fail_closed"]==3
assert migration["ordinary_pending"]==0
assert migration["status"]=="complete_reviewed_or_fail_closed"

assert p5["status"]=="completed"
assert p5["content_ready"]==201
assert p5["ordinary_pending"]==0
assert p6["status"]=="completed"
assert p6["artwork_ready"]["main_count"]==201
assert p6["layout_ready"]["status"]=="complete"
assert p6["layout_ready"]["main_count"]==201

assert len(batches["frozen_batches"])==21
assert sum(len(b["main_glyphs"]) for b in batches["frozen_batches"])==201
for b in batches["frozen_batches"]:
    assert b["content_status"]=="content_ready", b["id"]
    assert b["artwork_status"]=="artwork_ready", b["id"]
    assert b["layout_status"]=="layout_ready", b["id"]

assert p7["manifest_registered"] is True
assert p7["final_pdf_visual_QA"].startswith("passed_")
assert p7["toc_index_page_QA"]=="passed"
assert p7["variants_and_legacy27_regression"]=="passed"

rc=p7["release_candidate"]
assert rc["version"]=="0.4.0-rc1"
assert rc["status"]=="candidate_archived"
assert rc["release_eligible"] is False
assert rc["pages"]==276
assert rc["review"]=="reviews/P7-RC1-visual-QA-20261007.md"

entry=next(x for x in manifest["artifacts"] if x.get("path")==rc["path"])
for key in ("version","pages","bytes","sha256","source_commit","workflow_run_id","artifact_id"):
    assert entry[key]==rc[key], key
assert entry["status"]=="release_candidate"
assert entry["release_eligible"] is False
assert entry["review_record"]==rc["review"]

pdf=ROOT/rc["path"]
raw=pdf.read_bytes()
assert len(raw)==rc["bytes"]
assert hashlib.sha256(raw).hexdigest()==rc["sha256"]
assert len(PdfReader(str(pdf)).pages)==276

assert not any(x.get("status")=="released" for x in manifest["artifacts"])
release_dir=ROOT/"deliverables/releases"
if release_dir.exists():
    assert not any(release_dir.rglob("*.pdf")), "Formal release directory already contains PDF(s)"

assert p7["formal_release"]=="pending"

print(json.dumps({
    "status":"formal_release_preflight_passed",
    "formal_pdf_generated":False,
    "formal_release":False,
    "main_count":201,
    "content_ready":201,
    "artwork_ready":201,
    "layout_ready":201,
    "release_candidate":rc,
    "terminal_fail_closed":{
        "fine_stroke_names":14,
        "position_migration":3,
        "exact_GF0011_2022_item_fields":201
    },
    "note":"Terminal fail-closed states remain disclosed; no item-level GF0011—2022 full-text verification is claimed."
},ensure_ascii=False,indent=2))
