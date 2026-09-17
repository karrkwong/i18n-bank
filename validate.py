#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n-bank release gate.

Validates asset integrity before any change is released:

  1. termbase.csv  — structure, ID discipline, enum closures, field hygiene,
                     cross-entry preferred/forbidden conflicts
  2. rules.json    — schema closure (defect codes, compliance levels)
  3. spec <-> json — layout budget matrix consistency (both directions)
  4. regex suite   — every typical_pattern must compile and pass the
                     regression suite encoding DESIRED behavior

Exit code 0 = releasable; 1 = blocked (errors). Warnings do not block.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TERMBASE = ROOT / "references" / "termbase.csv"
RULES = ROOT / "references" / "rules.json"
SPEC = ROOT / "references" / "specification.md"

errors, warnings = [], []

CANONICAL_DEFECT_CODES = [
    "TRUNCATION", "LINE_BREAK", "MIXED_LANG", "REDUNDANCY",
    "FORMAT_GRAMMAR", "COMPLIANCE", "PLACEHOLDER",
]
CANONICAL_COMPLIANCE = ["MANDATORY", "STANDARD", "GENERAL", "ALERT"]
SCOPE_VALUES = {
    "GLOBAL", "REGIONAL_SEA", "LOCAL_SG", "LOCAL_MY", "LOCAL_HK", "LOCAL_TH", "LOCAL_ID",
}

# Desired regex behavior: (input, should_match). The suite encodes the contract
# the patterns must satisfy; known violations fail the gate until fixed.
REGEX_CASES = {
    "TRUNCATION": [("Transf…", True), ("Pay Now", False), ("Cut-off Time 15:30", False)],
    "LINE_BREAK": [
        ("Transactio\nns", True),      # mid-word split, no hyphen
        ("Transfer\nHistory", False),  # legit break at word boundary
        ("Inter-\nnational", False),   # hyphen break is not a defect (spec section 4)
        ("Pay Now", False), ("Bill", False), ("Pay", False),
    ],
    "MIXED_LANG": [
        ("FPS快速支付Transfer", True), ("แอป Transfer", True), ("DuitNow 转账", True),
        ("Pay Now", False),
    ],
    "REDUNDANCY": [("Card Application", True), ("Apply", False)],
    "FORMAT_GRAMMAR": [("1 accounts", True), ("Account:Balance", True), ("12:30 PM", False), ("Note: this", False)],
    "COMPLIANCE": [("Quick Pay", True), ("PayNow", False)],
    "PLACEHOLDER": [("{0} amount", True), ("100%", False), ("${user}", True)],
}

# spec.md layout table: component display name -> rules.json key
COMPONENT_KEY_MAP = {
    "Tab Bar": "tab_bar",
    "Grid Tile": "grid_tile",
    "Primary CTA": "primary_button",
    "Form Label": "form_label",
    "List Title": "list_title",
    "Page Header": "page_header",
    "Dialog / Toast": "dialog_toast",
}

EXPECTED_CSV_HEADER = [
    "entry_id", "scope", "domain", "context_component", "definition",
    "preferred_en", "variant_en", "forbidden_en", "preferred_zh_cn",
    "preferred_zh_hk", "compliance_level", "source_authority", "note",
]

# Fields that may legitimately be blank: a term can have no variants,
# no forbidden forms (context restrictions live in `note`), or no note.
OPTIONAL_CSV_FIELDS = {"variant_en", "forbidden_en", "note"}


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def check_termbase():
    with TERMBASE.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]
    if header != EXPECTED_CSV_HEADER:
        err(f"termbase header mismatch: {header}")
        return 0
    idx = {c: i for i, c in enumerate(header)}
    zh = re.compile(r"[\u4e00-\u9fff]")
    ids = []
    pref_map = {}
    valid = []
    for lineno, r in enumerate(data, start=2):
        if len(r) != len(header):
            err(f"termbase line {lineno}: {len(r)} columns, expected {len(header)}")
            continue
        valid.append((lineno, r))
        eid = r[idx["entry_id"]]
        ids.append(eid)
        if not re.fullmatch(r"FIN-[A-Z]{3}-\d{3}", eid):
            err(f"termbase line {lineno}: malformed entry_id '{eid}'")
        if r[idx["scope"]] not in SCOPE_VALUES:
            err(f"termbase {eid}: unknown scope '{r[idx['scope']]}'")
        if r[idx["compliance_level"]] not in CANONICAL_COMPLIANCE:
            err(f"termbase {eid}: unknown compliance_level '{r[idx['compliance_level']]}'")
        for col in header:
            if col in OPTIONAL_CSV_FIELDS:
                continue
            if not r[idx[col]].strip():
                err(f"termbase {eid}: empty required field '{col}'")
        for col in ("preferred_en", "variant_en", "forbidden_en"):
            if zh.search(r[idx[col]]):
                err(
                    f"termbase {eid}: CJK annotation inside data field '{col}': "
                    f"{r[idx[col]]!r} — move context notes to a dedicated field; "
                    f"forbidden terms are global"
                )
        if r[idx["preferred_en"]].strip() == r[idx["variant_en"]].strip():
            warn(f"termbase {eid}: variant_en identical to preferred_en ('{r[idx['preferred_en']]}')")
        for p in r[idx["preferred_en"]].split("/"):
            pref_map.setdefault(p.strip(), []).append(eid)

    dups = sorted({x for x in ids if ids.count(x) > 1})
    if dups:
        err(f"termbase duplicate entry_ids: {dups}")

    # entry_id gaps within each prefix block (warning only — may be reserved)
    by_prefix = {}
    for x in ids:
        p, n = x.rsplit("-", 1)[0], int(x.rsplit("-", 1)[1])
        by_prefix.setdefault(p, []).append(n)
    for p, ns in by_prefix.items():
        gaps = [f"{p}-{n:03d}" for n in range(min(ns) + 1, max(ns)) if n not in ns]
        if gaps:
            warn(f"termbase entry_id gaps in {p}: {gaps}")

    # cross-entry conflicts: a forbidden term must never be a preferred term elsewhere
    for lineno, r in valid:
        eid = r[idx["entry_id"]]
        for fb in r[idx["forbidden_en"]].split(";"):
            base = fb.strip()
            if base and base in pref_map and eid not in pref_map[base]:
                err(f"termbase conflict: '{base}' forbidden in {eid} but preferred in {pref_map[base]}")
    return len(valid)


def check_rules_json():
    with RULES.open(encoding="utf-8") as f:
        rules = json.load(f)
    codes = [d["code"] for d in rules.get("defect_types", [])]
    if codes != CANONICAL_DEFECT_CODES:
        err(f"rules.json defect_types mismatch: {codes}")
    levels = sorted(rules.get("compliance_levels", {}).keys())
    if levels != sorted(CANONICAL_COMPLIANCE):
        err(f"rules.json compliance_levels mismatch: {levels}")
    for d in rules.get("defect_types", []):
        if "severity" in d:
            err(f"rules.json {d['code']}: legacy field 'severity' — rename to 'default_severity'")
        if d.get("default_severity") not in ("HIGH", "MEDIUM", "LOW"):
            err(f"rules.json {d['code']}: missing or invalid default_severity")
    for d in rules.get("defect_types", []):
        pattern = d.get("typical_pattern", "")
        try:
            compiled = re.compile(pattern)
        except re.error as e:
            err(f"rules.json {d['code']}: typical_pattern does not compile: {e}")
            continue
        for text, should_match in REGEX_CASES.get(d["code"], []):
            got = bool(compiled.search(text))
            if got != should_match:
                kind = "false positive" if got else "false negative"
                err(f"rules.json {d['code']} regex {kind}: {text!r} (match={got}, expected={should_match})")
    return rules


def parse_spec_layout():
    text = SPEC.read_text(encoding="utf-8")
    layout = {}
    for m in re.finditer(r"^\|\s*\*\*(.+?)\*\*\s*\|(.+)\|\s*$", text, re.M):
        name, rest = m.group(1), m.group(2)
        cells = [c.strip() for c in rest.split("|")]
        if len(cells) < 3:
            continue
        key = next((k for en, k in COMPONENT_KEY_MAP.items() if en in name), None)
        if not key:
            continue
        dm = re.search(r"\d+", cells[0])
        lines = int(dm.group()) if dm else (1 if "单行" in cells[0] else None)
        en_m = re.search(r"\d+", cells[1])
        sea_m = re.search(r"\d+", cells[2])
        if lines is None or not en_m or not sea_m:
            err(f"specification.md layout row unparsable: {name}")
            continue
        layout[key] = (lines, int(en_m.group()), int(sea_m.group()))
    return layout


def check_layout_consistency(rules):
    spec_layout = parse_spec_layout()
    json_layout = rules.get("layout_constraints", {})
    for key, spec_vals in spec_layout.items():
        if key not in json_layout:
            err(f"rules.json layout_constraints missing component '{key}' "
                f"(specification.md defines lines={spec_vals[0]}, en<={spec_vals[1]}, sea<={spec_vals[2]})")
            continue
        c = json_layout[key]
        got = (c.get("max_lines"), c.get("max_en_chars"), c.get("max_sea_chars"))
        if got != spec_vals:
            err(f"layout mismatch on '{key}': rules.json {got} != specification.md {spec_vals}")
    for key in json_layout:
        if key not in spec_layout:
            err(f"specification.md layout table missing component '{key}' (defined in rules.json)")


def main():
    n_terms = check_termbase()
    rules = check_rules_json()
    check_layout_consistency(rules)

    print(f"termbase entries: {n_terms}")
    print(f"defect codes: {len(rules.get('defect_types', []))} · "
          f"compliance levels: {len(rules.get('compliance_levels', {}))} · "
          f"layout components: {len(rules.get('layout_constraints', {}))}")
    print()
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ~ {w}")
        print()
    if errors:
        print(f"BLOCKED — {len(errors)} error(s):")
        for e in errors:
            print(f"  x {e}")
        return 1
    print("PASS — assets are consistent and releasable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
