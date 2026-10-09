#!/usr/bin/env python3
"""A1 read-only median audit against all 201 legacy glyphs and nine offline previews.

Drawing completeness is NOT trajectory-direction approval. No PDF, manifest or
normative source file is changed. Run after scripts/acquire_vectors.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from apply_artwork import ROOT, apply_artwork

REV = "68d10a4b21150cae5e1ebbd223eed289cf32d90c"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_entries():
    items = []
    for batch in range(1, 22):
        code = f"B{batch:02}"
        for e in load(ROOT / "data" / (code + ".json"))["entries"]:
            items.append((code, e))
    ids = [e["main_id"] for _, e in items]
    if len(ids) != 201 or set(ids) != set(range(1, 202)):
        raise ValueError("Expected 201 unique canonical main IDs")
    return items


def stroke_count(entry):
    names = entry.get("stroke_names")
    if isinstance(names, list):
        return len(names)
    reviewed = (entry.get("fine_stroke_names_review") or {}).get("adjudicated_names")
    if isinstance(reviewed, list):
        return len(reviewed)
    # This is only a count fallback, never an authority for stroke names.
    return entry["stroke_count"]


def order_code(entry):
    return (entry.get("stroke_order_review") or {}).get("order_code") or \
        entry.get("order_code") or entry.get("order_code_candidate")


def sample_pack():
    raw = (ROOT / "animation/samples.js").read_text(encoding="utf-8")
    prefix = "window.ZITIE_SAMPLES = "
    if raw.count(prefix) != 1 or not raw.rstrip().endswith(";"):
        raise ValueError("Unexpected sample script envelope")
    return json.loads(raw.split(prefix, 1)[1].rstrip().removesuffix(";"))


def verified_polyline(points):
    if not isinstance(points, list) or len(points) < 2:
        return False
    if any(not isinstance(point, list) or len(point) != 2 or
           any(type(n) not in (float, int) or not math.isfinite(n) for n in point)
           for point in points):
        return False
    return any(math.dist(points[i-1], points[i]) > 0.01
               for i in range(1, len(points)))


def audit(source_dir: Path, output: Path, require_all: bool = False):
    entries = canonical_entries()
    samples = sample_pack()
    if samples["source_revision"] != REV or samples["review_state"] != "trajectory_not_teaching_approved":
        raise ValueError("Unpinned or prematurely approved sample data")
    samples_by_id = {g["main_id"]: g for g in samples["glyphs"]}
    if len(samples_by_id) != len(samples["glyphs"]) or len(samples_by_id) != 9:
        raise ValueError("Unexpected sample set")
    policy = load(ROOT / "data/teaching-source-policy.json")
    blocked_names = set(next(r["main_ids"] for r in policy["rules"]
                             if r["field"] == "fine_stroke_names"))
    report = []
    problems = []
    total_medians = 0
    available = 0
    structurally_usable = 0
    for batch, entry in entries:
        ch = entry["character"]
        n = stroke_count(entry)
        row = {"batch":batch,"main_id":entry["main_id"],"character":ch,
               "expected_stroke_count":n,
               "canonical_order_code":order_code(entry),
               "trajectory_review_status":"not_reviewed_A1",
               "teaching_approved":False}
        path = source_dir / f"{ord(ch):04X}.json"
        if not path.is_file():
            row["material_status"] = "not_available_locally"
            problems.append(ch + ":missing")
            report.append(row)
            continue
        raw = path.read_bytes()
        row["source_sha256"] = hashlib.sha256(raw).hexdigest()
        try:
            obj, adaptation = apply_artwork(ch, raw)
            outlines, medians = obj.get("strokes"), obj.get("medians")
            row["modified_strokes_0_based"] = adaptation["modified_stroke_indices"]
            row["actual_stroke_count"] = len(outlines) if isinstance(outlines, list) else 0
            row["actual_median_count"] = len(medians) if isinstance(medians, list) else 0
            good = isinstance(outlines, list) and len(outlines) == n and \
                isinstance(medians, list) and len(medians) == n and \
                all(isinstance(s, str) and s.lstrip().startswith("M ") and
                    s.rstrip().endswith("Z") for s in outlines) and \
                all(verified_polyline(points) for points in medians)
            if not good:
                row["material_status"] = "missing_or_invalid_geometry"
                problems.append(ch + ":geometry")
            else:
                available += 1
                total_medians += len(medians)
                structurally_usable += 1
                row["material_status"] = "structurally_usable_not_direction_reviewed"
                row["median_points"] = [len(m) for m in medians]
            sample = samples_by_id.get(entry["main_id"])
            if sample:
                if not good or sample["character"] != ch or sample["batch_id"] != batch or \
                   sample["expected_stroke_count"] != n or sample["order_code"] != order_code(entry) or \
                   sample["normative_ref"] != f"{batch}/{entry['main_id']}" or \
                   sample["trajectory_review_status"] != "engineering_preview_unreviewed" or \
                   len(sample["strokes"]) != n:
                    raise ValueError(ch + ":canonical offline sample mismatch")
                for i, stroke in enumerate(sample["strokes"]):
                    if (stroke["index"] != i+1 or stroke["outline"] != outlines[i] or
                        stroke["median"] != medians[i]):
                        raise ValueError(ch + ":offline geometry differs from pinned adapted source")
                    if entry["main_id"] in blocked_names and stroke["name_status"] != "ordinal_only":
                        raise ValueError(ch + ":blocked name leaked")
                row["offline_prototype"] = True
        except (ValueError, KeyError, TypeError) as exc:
            row["material_status"] = "source_validation_error"
            row["error"] = str(exc)
            problems.append(ch + ":validation_error")
        report.append(row)
    summary = {"target_primary_radicals":201, "vector_material_available":available,
               "median_material_structurally_usable":structurally_usable,
               "individual_medians_present":total_medians,
               "offline_demo_primary_radicals":len(samples_by_id),
               "trajectory_direction_teaching_approved":0,
               "blocked_or_not_locally_verified":len(problems),
               "blocked_examples":problems,
               "scope_note":"Only 201 canonical main radicals; never count variants or whole-character cases.",
               "gate":"Structural presence is not a review of start/end, turn, hook, timing, or writing direction."}
    result = {"schema_version":1,"kind":"A1_separate_trajectory_material_audit",
              "source_revision":REV,"source_dir":str(source_dir),"summary":summary,"records":report}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if require_all and (problems or len(samples_by_id) != 9):
        raise SystemExit("A1 material audit failed: " + "; ".join(problems))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", default="build/vectors")
    parser.add_argument("--output", default="build/a1/coverage-report.json")
    parser.add_argument("--require-all", action="store_true")
    args = parser.parse_args()
    audit(ROOT / args.source_dir, ROOT / args.output, args.require_all)
