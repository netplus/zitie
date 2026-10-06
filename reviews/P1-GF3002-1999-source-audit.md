# P1 GF3002—1999 source audit

Date: 2026-10-06

## Purpose

Evaluate GF3002—1999《GB 13000.1字符集汉字笔顺规范》as a normative source for the fixed 37 P1 stroke-order residual targets.

## Acquisition

- GitHub Actions run: 37410985779
- Artifact: 11389595541 `normative-reference-acquisition`
- File: `gf3002-1999.pdf`
- Bytes: 6,730,497
- SHA256: `cb5cb74f108dafed41a3583bc8d33d8dd318d1a21d714923c0f1ced89443cf3e`
- Mirror pinned commit: `d26705ffc52b81b6e1a45483c7b591f62962f49f`

## Visual inspection

All 8 PDF physical pages were rendered and inspected.

Observed contents:
1. cover;
2. contents;
3. foreword;
4-6. scope / references / terminology / rules;
7-8. beginning of the normative table.

The contents page states the GB13000.1 ideograph stroke-order table spans printed pp.4-343 and the appendix starts at p.344. However, this mirror has only 8 PDF pages. The last page reaches table item 134 and then explicitly shows “（略）”.

## Decision

This file is a byte-stable abridged extract, not the complete 20,902-character normative table. It is therefore **not admissible for closing any of the 37 fixed P1 residual targets**. No canonical field is upgraded from this source audit.

The 37 residual set remains:

匚、冂、勹、亠、冫、冖、凵、卩、厶、廴、艹、廾、宀、辶、彐、丨、丿、丶、乛、囗、彡、夂、丬、攴、罒、屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥。

Next action: locate a complete GF3002—1999 original or another applicable normative source, then review only these 37 targets.
