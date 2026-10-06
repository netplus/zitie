#!/usr/bin/env python3
"""Audit immutable drawing-vector coverage for P6 without granting artwork approval."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REV = "68d10a4b21150cae5e1ebbd223eed289cf32d90c"
BASE = "https://raw.githubusercontent.com/chanind/hanzi-writer-data/" + REV


def retrieve(url: str) -> bytes:
    with urlopen(
        Request(url, headers={"User-Agent": "zitie-p6-vector-audit/0.1"}),
        timeout=45,
    ) as response:
        return response.read(1024 * 1024)


def frozen_batches() -> list[str]:
    plan = json.loads((ROOT / "data/batches.json").read_text(encoding="utf-8"))
    return [b["id"] for b in plan["frozen_batches"]]


def expected_stroke_count(entry: dict) -> tuple[int, str]:
    if isinstance(entry.get("stroke_names"), list):
        return len(entry["stroke_names"]), "stroke_names"
    review = entry.get("fine_stroke_names_review") or {}
    if isinstance(review.get("adjudicated_names"), list):
        return len(review["adjudicated_names"]), "fine_stroke_names_review.adjudicated_names"
    if isinstance(entry.get("stroke_names_candidate"), list):
        return len(entry["stroke_names_candidate"]), "stroke_names_candidate"
    if isinstance(entry.get("stroke_count"), int):
        return entry["stroke_count"], "stroke_count"
    raise ValueError(entry["character"] + ": no usable stroke-count field")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batches", nargs="+")
    parser.add_argument("--output", default="build/vector-audit")
    args = parser.parse_args()

    allowed = frozen_batches()
    selected = args.batches or allowed
    unknown = sorted(set(selected) - set(allowed))
    if unknown:
        raise SystemExit("Unknown/non-frozen batch: " + ", ".join(unknown))

    dest = ROOT / args.output
    vectors = dest / "vectors"
    vectors.mkdir(parents=True, exist_ok=True)

    license_url = BASE + "/ARPHICPL.TXT"
    license_bytes = retrieve(license_url)
    if b"ARPHIC PUBLIC LICENSE" not in license_bytes:
        raise ValueError("Unexpected vector license response")
    (dest / "ARPHICPL.TXT").write_bytes(license_bytes)

    entries = []
    for batch_id in selected:
        batch = json.loads((ROOT / f"data/{batch_id}.json").read_text(encoding="utf-8"))
        for entry in batch["entries"]:
            entries.append((batch_id, entry))

    records = []
    for batch_id, entry in entries:
        ch = entry["character"]
        expected, expected_from = expected_stroke_count(entry)
        url = BASE + "/data/" + quote(ch) + ".json"
        record = {
            "batch_id": batch_id,
            "character": ch,
            "main_id": entry.get("main_id"),
            "url": url,
            "expected_stroke_count": expected,
            "expected_stroke_count_from": expected_from,
            "vector_revision": REV,
        }
        try:
            raw = retrieve(url)
            obj = json.loads(raw)
            actual = len(obj.get("strokes", []))
            name = f"{ord(ch):04X}.json"
            (vectors / name).write_bytes(raw)
            record.update(
                {
                    "file": name,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "actual_stroke_count": actual,
                    "status": "compatible" if actual == expected else "stroke_count_mismatch",
                }
            )
        except HTTPError as exc:
            record.update({"status": "missing_http", "http_status": exc.code})
        except (URLError, TimeoutError) as exc:
            record.update({"status": "fetch_error", "error": str(exc)})
        except (json.JSONDecodeError, ValueError) as exc:
            record.update({"status": "invalid_vector_data", "error": str(exc)})
        records.append(record)

    compatible = [r for r in records if r["status"] == "compatible"]
    mismatch = [r for r in records if r["status"] == "stroke_count_mismatch"]
    missing = [r for r in records if r["status"] == "missing_http"]
    errors = [r for r in records if r["status"] not in {"compatible", "stroke_count_mismatch", "missing_http"}]
    summary = {
        "schema_version": 1,
        "record_kind": "P6_vector_material_coverage_audit",
        "vector_source": "Hanzi Writer / Make Me a Hanzi",
        "vector_revision": REV,
        "drawing_material_only": True,
        "selected_batches": selected,
        "target_count": len(records),
        "compatible": len(compatible),
        "stroke_count_mismatch": len(mismatch),
        "missing": len(missing),
        "other_errors": len(errors),
        "artwork_ready_granted": 0,
        "policy": (
            "Vector availability and stroke-count compatibility are material-readiness checks only. "
            "They do not grant artwork_ready; each target still requires authoritative-shape comparison "
            "and cumulative-stroke visual review."
        ),
    }
    report = {"summary": summary, "entries": records}
    (dest / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (dest / "NOTICE.txt").write_text(
        "Outlines: Hanzi Writer / Make Me a Hanzi, immutable revision " + REV + ".\n"
        "Temporary P6 review material only; no artwork approval is implied.\n"
        "See ARPHICPL.TXT. No font files included.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if mismatch:
        print("stroke_count_mismatch=" + "".join(r["character"] for r in mismatch))
    if missing:
        print("missing=" + "".join(r["character"] for r in missing))
    if errors:
        print("other_errors=" + "".join(r["character"] for r in errors))


if __name__ == "__main__":
    main()
