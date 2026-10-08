#!/usr/bin/env python3
"""Validate exact locally reviewed PDF derivatives without fabricating CI provenance.

This deliberately does NOT grant publication or replace the immutable M3 RC1
freeze. An imported, PDF-level edit has no source generation commit. That is
recorded explicitly rather than falsely attributing it to the RC1 build.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
KIND = "locally_reviewed_pdf_derivative"
RECORD = "reviews/q1-local-20261008/import-provenance.json"
RECORD_SHA = "8be15928b00e12a2df07a088e0c8be276bdb4b6479399df50762b3bbc8c0dfb2"
REVIEW = "reviews/Q1-local-import-20261008.md"
RC1 = "deliverables/drafts/v0.5.0-rc1/zitie-v0.5.0-rc1.pdf"
RC1_SHA = "3b26fd0a85b063b83f7090f9b38735908b6e64dc763614c12f17e4f727ef556a"
EXPECTED = {'deliverables/drafts/v0.5.0-rc2/zitie-v0.5.0-rc2.pdf': {'version': '0.5.0-rc2', 'pages': 299, 'bytes': 4430739, 'sha256': 'f3337350919580de3d768864c58fcce5f69965b9fc2b86edc592f06ea181c03e', 'variant_kind': 'render_revision'}, 'deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3.pdf': {'version': '0.5.0-rc3', 'pages': 299, 'bytes': 4691990, 'sha256': 'f3f46458d24776834691dc0525b335569ea558a717d987e0dd3440efee8342af', 'variant_kind': 'render_revision'}, 'deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3-finalcheck.pdf': {'version': '0.5.0-rc3', 'pages': 299, 'bytes': 4747107, 'sha256': 'd54184705c6849d6617c7ea201a659d77796cad9b05792782032b320127bbb27', 'variant_kind': 'integrity_attachment_variant'}}


def require(value, message):
    if not value:
        raise ValueError(message)


def safe_file(root, relative):
    root = Path(root).resolve()
    p = Path(relative)
    require(isinstance(relative, str) and not p.is_absolute() and ".." not in p.parts,
            "Unsafe Q1 import path")
    result = root / p
    require(not result.is_symlink() and result.resolve().is_relative_to(root),
            "Q1 import path escapes repository")
    require(result.is_file(), "Missing Q1 import file: " + relative)
    return result


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_record(root):
    raw = safe_file(root, RECORD).read_bytes()
    require(sha(raw) == RECORD_SHA, "Immutable Q1 provenance record changed")
    value = json.loads(raw)
    require(value["kind"] == "Q1_local_derivative_import_not_remote_build", "Wrong provenance kind")
    require(value["remote_archive_completed"] is False
            and value["remote_CI_completed"] is False
            and value["formal_publication_completed"] is False
            and value["release_eligible"] is False, "Import receipt cannot grant publication")
    return value


def validate_entry(root, entry):
    require(entry.get("provenance_kind") == KIND, "Unsupported import provenance")
    expected = EXPECTED.get(entry.get("path"))
    require(expected is not None, "Unapproved local PDF import")
    for key, value in expected.items():
        require(entry.get(key) == value, "Imported PDF metadata mismatch: " + key)
    require(entry.get("source_commit", "missing") is None,
            "A local PDF revision must not be attributed to a fabricated source commit")
    require(entry.get("status") == "release_candidate" and entry.get("release_eligible") is False,
            "Local derivative is not a released edition")
    for key in ("source_tree", "workflow_run_id", "artifact_id"):
        require(entry.get(key) is None, "Local derivative must not claim generated CI provenance")
    require(entry.get("provenance_record") == RECORD and entry.get("review_record") == REVIEW,
            "Missing exact import/review record")
    safe_file(root, REVIEW)
    record = load_record(root)
    rows = [x for x in record["artifacts"] if x["path"] == entry["path"]]
    require(len(rows) == 1 and all(rows[0][k] == v for k, v in expected.items()),
            "Import record/manifest mismatch")
    data = safe_file(root, entry["path"]).read_bytes()
    require(len(data) == expected["bytes"] and sha(data) == expected["sha256"],
            "Imported PDF bytes were changed")
    return True


def verify(root=ROOT, render=False, start=1, end=299):
    root = Path(root)
    manifest = json.loads(safe_file(root, "deliverables/manifest.json").read_text(encoding="utf-8"))
    entries = [x for x in manifest["artifacts"] if x.get("provenance_kind") == KIND]
    if not entries:
        require(not (root / RECORD).exists(), "Provenance exists without imported artifacts")
        return {"status": "not_imported", "release_eligible": False}
    require(len(entries) == len(EXPECTED)
            and {x["path"] for x in entries} == set(EXPECTED), "Incomplete/unapproved import set")
    for entry in entries:
        validate_entry(root, entry)
    record = load_record(root)
    require(sha(safe_file(root, RC1).read_bytes()) == RC1_SHA, "Historical RC1 changed")
    paths = list(EXPECTED)
    rc2, rc3, final = [safe_file(root, p) for p in paths]
    evidence = {}
    for key in ("review_attachment", "integrity_attachment", "historical_verifier", "history_readme"):
        item = record[key]
        raw = safe_file(root, item["path"]).read_bytes()
        require(sha(raw) == item["sha256"], "Preserved evidence changed: " + key)
        evidence[key] = raw
    review, integrity = [json.loads(evidence[k]) for k in ("review_attachment","integrity_attachment")]
    require(review["source"]["sha256"] == EXPECTED[paths[0]]["sha256"], "RC2 review chain broken")
    require(integrity["base_pdf"]["sha256"] == EXPECTED[paths[1]]["sha256"], "RC3 integrity chain broken")
    require(final.read_bytes().startswith(rc3.read_bytes()), "Original RC3 prefix was changed")
    require(review["result"]["local_visual_review_complete"] is True
            and review["result"]["blocking_layout_findings_remaining"] == 0, "Prior review incomplete")
    require(review["result"]["formal_publication_completed"] is False, "Historical status changed")
    require([r["page"] for r in review["page_results"]] == list(range(1,300)),
            "Incomplete/duplicate historical visual pages")
    require([r["page"] for r in integrity["page_results"]] == list(range(1,300)),
            "Incomplete integrity record")
    for a, b in zip(review["page_results"], integrity["page_results"]):
        require(a["source_full_page_visually_read"] is True and not a["remaining_layout_findings"],
                "Missing prior page review")
        require(a["rc3_rgb96_sha256"] == b["rgb96_sha256"] and b["passed"] is True
                and not b["failures"], "Visual/integrity binding mismatch")
    require(len(set(review["second_renderer_pages"])) == 41
            and set(range(264,286)) <= set(review["second_renderer_pages"]),
            "Risk-page cross-rendering evidence incomplete")
    require(len(review["grayscale_pages"]) == 4
            and review["result"]["physical_print_test_performed"] is False,
            "Print simulation scope changed")
    for path in (rc3, final):
        pdf = PdfReader(path)
        require(len(pdf.pages) == 299 and not pdf.is_encrypted, "Invalid imported PDF")
        values = pdf.attachments.get("Q1-page-review-rc3.json")
        require(values == [evidence["review_attachment"]], "Original attached review changed")
    pdf = PdfReader(final)
    for name, key in (("Q1-final-integrity.json", "integrity_attachment"),
                      ("verify_rc3.py", "historical_verifier"), ("Q1-readme.txt", "history_readme")):
        require(pdf.attachments.get(name) == [evidence[key]], "Final attached evidence changed")
    result = {"status": "local_derivative_import_validated", "imported_variants": 3,
              "local_historical_visual_pages": 299, "remote_CI_executed": False,
              "new_visual_review_performed": False, "Q1_completed": False,
              "release_eligible": False, "formal_publication_completed": False}
    if render:
        require(1 <= start <= end <= 299, "Invalid render range")
        # This exact passive verifier was reviewed and is hash-bound above.
        spec = importlib.util.spec_from_file_location("preserved_rc3_verifier",
                safe_file(root, record["historical_verifier"]["path"]))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.inspect(final, start, end, rc2, safe_file(root, RC1))
        require(not report["failures"], "Rendered page does not match preserved review: " +
                repr([r["page"] for r in report["failures"]]))
        result["machine_render_check"] = report
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=299)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(render=args.render, start=args.start, end=args.end)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    summary = {k:v for k,v in result.items() if k != "machine_render_check"}
    if args.render:
        summary["pages_checked"] = args.end - args.start + 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
