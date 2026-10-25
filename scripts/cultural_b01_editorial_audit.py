#!/usr/bin/env python3
"""Fail-closed P2 editorial audit for nine B01 briefs, not a publication review.

No words, quotes, calligraphy, illustrations or standalone-character readings
are approved by this validator. It only checks scope, identity and draft gates.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = "7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
RELATIVE = "data/cultural_edition/p2_b01_editorial_briefs_20261025.json"
DRAFT_PHASE = "P2_editorial_brief_unreviewed"
LEDGER_PHASE = "P2_candidate_unreviewed"
PINYIN = re.compile(r"^[a-zāáǎàēéěèīíǐìōóǒòūúǔùüǖǘǚǜńňǹ\s]+$", re.U)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value):
    return unicodedata.normalize("NFC", value).strip()


def audit(root: Path = ROOT):
    root = Path(root)
    doc = load(root / RELATIVE)
    if (doc.get("schema_version") != 1 or doc.get("batch_id") != "B01"
            or doc.get("review_state") != "draft_not_for_release"
            or doc.get("source_pdf_sha256") != SOURCE_SHA):
        raise ValueError("B01 editorial brief is not pinned to the draft source")
    if not doc.get("spelling_policy") or not doc.get("editorial_gate"):
        raise ValueError("Cannot omit explicit publication and phonetic warnings")
    b01 = load(root / "data/B01.json")
    canonical = {x["main_id"]: x["character"] for x in b01["entries"]}
    existing_id = 39
    if canonical[existing_id] != "山":
        raise ValueError("Existing published-PDF sample has a new source identity")
    excluded = doc.get("excluded_existing_cultural_sample")
    if excluded != [{"main_id": 39, "character": "山",
                     "reason": "Existing four-character P1 candidate; do not duplicate"}]:
        raise ValueError("B01 scope must exclude already drafted 山")
    expected_ids = set(canonical) - {existing_id}
    entries = doc.get("entries")
    if not isinstance(entries, list) or len(entries) != len(expected_ids):
        raise ValueError("Exactly nine new B01 editorial briefs required")
    identifiers = [e.get("main_id") for e in entries]
    if set(identifiers) != expected_ids or len(identifiers) != len(set(identifiers)):
        raise ValueError("B01 content has missing, repeated or unauthorized main IDs")
    previous = (load(root / "data/cultural_edition/first_batch_draft.json")["entries"] +
                load(root / "data/cultural_edition/p4_multipage_prototypes.json")["entries"])
    earlier_titles = {e["title"] for e in previous}
    earlier_sentences = {e["sentence"] for e in previous}
    earlier_themes = {e["theme_key"] for e in previous}
    previous_words = {term["word"] for e in previous for term in e["terms"]}
    inventory = load(root / "data/cultural_edition/inventory/B01-B07.json")
    ledger = {x["main_id"]: x for x in inventory["entries"]}
    titles, sentences, themes, motifs, words = set(), set(), set(), set(), set()
    word_count = 0
    for e in entries:
        mid = e["main_id"]
        ch = e.get("character")
        if canonical[mid] != ch or e.get("batch_id") != "B01":
            raise ValueError("B01 main-glyph identity does not match frozen data")
        if e.get("stage") != DRAFT_PHASE or e.get("publication_eligible") is not False:
            raise ValueError("No B01 draft may be approved for publication")
        if e.get("original_pdf_pinyin_used_for_publication") is not False:
            raise ValueError("B01 raw pinyin cannot be silently called PDF-verified")
        row = ledger[mid]
        if row["character"] != ch or row.get("editorial_brief_stage") != LEDGER_PHASE:
            raise ValueError("B01 editorial inventory has not been synchronized")
        if row["reading_page_draft_phase"] != "not_started":
            raise ValueError("Editorial brief is not a rendered reading page")
        for key, seen, previous_values in (
                ("title", titles, earlier_titles),
                ("sentence", sentences, earlier_sentences),
                ("theme_key", themes, earlier_themes)):
            value = normalize(e.get(key, ""))
            if not value or value in seen or value in previous_values:
                raise ValueError("Repeated or blank cultural " + key)
            seen.add(value)
        quote = e.get("quote", {})
        if (quote.get("status") != "blocked_no_checked_primary_quote"
                or any(quote.get(key) is not None
                       for key in ("text", "attribution", "work", "source_url"))):
            raise ValueError("Unverified classic quotations must remain absent")
        meaning = e.get("meaning", {})
        if (meaning.get("status") != "review_pending"
                or not isinstance(meaning.get("lines"), list)
                or len(meaning["lines"]) != 2
                or any(not normalize(x) or len(x) > 35 for x in meaning["lines"])):
            raise ValueError("B01 glyph meanings must remain readable unreviewed prose")
        if e.get("sentence_review_status") != "review_pending":
            raise ValueError("Literary copy must not be silently approved")
        art = e.get("artwork_brief", {})
        motif = normalize(art.get("unique_motif", ""))
        if (art.get("theme_key") != e["theme_key"] or not motif or motif in motifs
                or not art.get("composition") or art.get("asset_id") is not None
                or art.get("licensing_status") != "not_started"
                or art.get("visual_review_status") != "not_started"):
            raise ValueError("Artwork plans cannot masquerade as finished art")
        motifs.add(motif)
        terms = e.get("terms", [])
        if not 4 <= len(terms) <= 6:
            raise ValueError("Need 4-6 proposed words per editorial brief")
        for t in terms:
            word = normalize(t.get("word", ""))
            pinyin = normalize(t.get("pinyin_display_candidate", ""))
            if (len(word) < 2 or len(word) > 4 or not pinyin
                    or not PINYIN.fullmatch(pinyin)
                    or not t.get("reading_risk")):
                raise ValueError("Proposed word or marked pinyin candidate incomplete")
            if word in words or word in previous_words:
                raise ValueError("Repeated P2 draft word: " + word)
            words.add(word)
            if (t.get("pronunciation_status") != "review_pending"
                    or t.get("pinyin_orthographic_candidate") is not None
                    or t.get("source_url") is not None
                    or t.get("reviewed_by") is not None):
                raise ValueError("B01 pronunciations lack direct mainland source approval")
            if ch == "一" and "yi_" not in t["reading_risk"]:
                raise ValueError("一 tone sandhi and orthographic policy must be reviewed")
            word_count += 1
    if word_count != 36:
        raise ValueError("B01 expected exactly 36 unverified word candidates")
    return {
        "result": "B01_EDITORIAL_BRIEFS_ONLY_NOT_PDF_OR_RELEASE",
        "source_pdf_sha256": SOURCE_SHA,
        "new_characters": len(entries),
        "char_order": [e["character"] for e in entries],
        "unreviewed_word_candidates": word_count,
        "unique_unfinished_artwork_briefs": len(motifs),
        "checked_mainland_word_pronunciations": 0,
        "verified_primary_quotations": 0,
        "new_pages_rendered": 0,
        "new_characters_approved": 0,
        "must_resolve": [
            "Mainland word headword/meaning/reading citations and human signoff",
            "一 original tone vs oral sandhi vs school printing policy",
            "Unique drawn SVG artwork and provenance/visual review",
            "Accurate classical quotations or no-quote approved alternative",
            "Original released PDF vector pages and exact pixel QA before book composition"
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
