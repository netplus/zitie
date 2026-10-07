#!/usr/bin/env python3
"""P7 full-book release-candidate gate.

This gate accepts only terminal, explicitly evidenced fail-closed states.
It does not turn source-blocked fields into reviewed fields and does not
create a formal release.
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

phase=progress["active_remaining_phase"]
assert phase in ("P7","completed"), phase
if phase=="completed":
    assert p7["status"]=="completed"
    assert p7.get("exit_condition")=="met"
assert coverage["target_edition"]=="GF0011—2022"
# Do not fake access to a source that remains unavailable.
assert coverage["target_edition_status"]=="fulltext_pending"

exact=p4["exact_2022_item_fields"]
assert exact["target_count"]==201
assert exact["reviewed"]==0
assert exact["source_blocked_fail_closed"]==201
assert exact["ordinary_pending"]==0
assert exact["evidence"]
assert exact["reopen_condition"]

migration=p4["position_migration_cumulative"]
assert migration["target_count"]==201
assert migration["reviewed"]==198
assert migration["conflict_fail_closed"]==3
assert migration["ordinary_pending"]==0
assert migration["status"]=="complete_reviewed_or_fail_closed"

assert p5["status"]=="completed"
assert p5["target_count"]==p5["content_ready"]==201
assert p5["ordinary_pending"]==0

assert p6["status"]=="completed"
assert p6["artwork_ready"]["main_count"]==201
assert p6["artwork_ready"]["remaining_main_count"]==0
assert p6["artwork_ready"]["status"]=="complete"
assert p6["layout_ready"]["status"]=="complete"
assert p6["layout_ready"]["main_count"]==201
assert p6["layout_ready"]["rendered_practice_pages"]==258

frozen=batches["frozen_batches"]
assert len(frozen)==21
assert sum(len(x["main_glyphs"]) for x in frozen)==201
for b in frozen:
    assert b["content_status"]=="content_ready", b["id"]
    assert b["artwork_status"]=="artwork_ready", b["id"]
    assert b["layout_status"]=="layout_ready", b["id"]

assert p7["manifest_registered"] is True
assert p7["final_pdf_visual_QA"].startswith("passed_")
assert p7["toc_index_page_QA"]=="passed"
assert p7["variants_and_legacy27_regression"]=="passed"
archive=p7["draft_archive"]
assert archive["version"]=="0.4.0"
assert archive["pages"]==276
assert archive["release_eligible"] is False

entry=next(x for x in manifest["artifacts"] if x.get("path")==archive["path"])
for key in ("version","pages","bytes","sha256","source_commit","workflow_run_id"):
    assert entry[key]==archive[key], key
assert entry["status"]=="draft"
assert entry["release_eligible"] is False
assert entry["review_record"]==archive["review"]

pdf=ROOT/archive["path"]
raw=pdf.read_bytes()
assert len(raw)==archive["bytes"]
assert hashlib.sha256(raw).hexdigest()==archive["sha256"]
assert len(PdfReader(str(pdf)).pages)==archive["pages"]

result={
    "status":"release_candidate_gate_passed",
    "formal_release":False,
    "main_count":201,
    "content_ready":201,
    "artwork_ready":201,
    "layout_ready":201,
    "position_migration":{"reviewed":198,"conflict_fail_closed":3,"ordinary_pending":0},
    "exact_GF0011_2022_item_fields":{
        "reviewed":0,
        "source_blocked_fail_closed":201,
        "ordinary_pending":0,
        "reopen_condition":exact["reopen_condition"],
    },
    "draft":archive,
    "note":"Candidate gate accepts documented terminal fail-closed states; it does not claim GF0011—2022 item-level fulltext verification."
}
print(json.dumps(result,ensure_ascii=False,indent=2))
