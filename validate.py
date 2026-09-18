#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n-bank release gate.

Validates asset integrity before any change is released:

  1. termbase.csv  — structure, ID discipline, enum closures, field hygiene,
                     governance fields (status, review_date, source_url),
                     cross-entry preferred/forbidden conflicts
  2. rules.json    — schema closure (defect codes, compliance levels),
                     rule_id discipline (R-DEF / R-LAY / R-GEN / R-FMT / R-MET),
                     format_rules / format_conventions / metrics schemas,
                     governance thresholds, regex regression suite
  3. spec <-> json — layout budget matrix consistency (both directions)
  4. governance    — review freshness (stale warning / MANDATORY re-verify);
                     ACTIVE MANDATORY entries must link to their regulator
  5. citations     — rule IDs and termbase entry IDs referenced by the docs
                     (specification.md / authority-index.md / SKILL.md /
                     golden-case.md / README.md)
                     must resolve to defined assets; "(proposed)" gap IDs
                     must not collide with existing entries
  6. layout-thresholds.json — DS physical-capacity SSOT: schema, derivation
                     sanity (recomputed from px math; +/-1 rounding warns,
                     >=2 blocks), threshold_ref resolution, and the
                     dual-layer invariant: every guidance budget (EN and SEA)
                     must fit the tightest mapped DS variant

Exit code 0 = releasable; 1 = blocked (errors). Warnings do not block.
"""
import csv
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TERMBASE = ROOT / "references" / "termbase.csv"
RULES = ROOT / "references" / "rules.json"
THRESHOLDS = ROOT / "references" / "layout-thresholds.json"
SPEC = ROOT / "references" / "specification.md"
AUTHORITY_INDEX = ROOT / "references" / "authority-index.md"
SKILL = ROOT / "SKILL.md"
GOLDEN = ROOT / "examples" / "golden-case.md"
README = ROOT / "README.md"

errors, warnings = [], []

CANONICAL_DEFECT_CODES = [
    "TRUNCATION", "LINE_BREAK", "MIXED_LANG", "REDUNDANCY",
    "FORMAT_GRAMMAR", "COMPLIANCE", "PLACEHOLDER",
]
CANONICAL_COMPLIANCE = ["MANDATORY", "STANDARD", "GENERAL", "ALERT"]
SCOPE_VALUES = {
    "GLOBAL", "REGIONAL_SEA", "LOCAL_SG", "LOCAL_MY", "LOCAL_HK", "LOCAL_TH", "LOCAL_ID",
}
STATUS_VALUES = {"ACTIVE", "RETIRED"}
MARKETS = {"SG", "MY", "HK", "TH", "ID"}

RULE_ID_RE = re.compile(r"R-(?:DEF|LAY|GEN|FMT|MET)-\d{3}")
# A cited entry ID must exist — unless it is a gap proposal "(proposed)".
FIN_CITED_RE = re.compile(r"FIN-[A-Z]{3}-\d{3}(?!\s*\(proposed\))")
FIN_PROPOSED_RE = re.compile(r"(FIN-[A-Z]{3}-\d{3})\s*\(proposed\)")

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
    "Dialog": "dialog",
    "Toast": "toast",
}

EXPECTED_CSV_HEADER = [
    "entry_id", "scope", "domain", "context_component", "definition",
    "preferred_en", "variant_en", "forbidden_en", "preferred_zh_cn",
    "preferred_zh_hk", "compliance_level", "source_authority",
    "source_url", "status", "review_date", "note",
]

# Fields that may legitimately be blank: a term can have no variants,
# no forbidden forms (context restrictions live in `note`), no external
# source URL (internal standards), or no note.
OPTIONAL_CSV_FIELDS = {"variant_en", "forbidden_en", "note", "source_url"}

TODAY = datetime.date.today()


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def check_termbase():
    """Returns (entries, n_active, n_retired); entries maps entry_id -> meta."""
    if not TERMBASE.exists():
        err("references/termbase.csv is missing")
        return {}, 0, 0
    with TERMBASE.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        err("termbase.csv is empty")
        return {}, 0, 0
    header, data = rows[0], rows[1:]
    if header != EXPECTED_CSV_HEADER:
        err(f"termbase header mismatch: {header}")
        return {}, 0, 0
    idx = {c: i for i, c in enumerate(header)}
    zh = re.compile(r"[\u4e00-\u9fff]")
    ids = []
    pref_map = {}
    valid = []
    entries = {}
    n_active = n_retired = 0
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
        status = r[idx["status"]]
        if status not in STATUS_VALUES:
            err(f"termbase {eid}: unknown status '{status}' (expected ACTIVE / RETIRED)")
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

        rd = r[idx["review_date"]]
        review = None
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", rd):
            err(f"termbase {eid}: invalid review_date '{rd}' (expected YYYY-MM-DD)")
        else:
            try:
                review = datetime.date.fromisoformat(rd)
            except ValueError:
                err(f"termbase {eid}: invalid review_date '{rd}' (not a real date)")
                review = None
        if review and review > TODAY:
            err(f"termbase {eid}: review_date {rd} is in the future")
        entries[eid] = {
            "compliance": r[idx["compliance_level"]],
            "status": status,
            "date": review,
            "url": r[idx["source_url"]].strip(),
        }
        if status == "RETIRED":
            n_retired += 1
        else:
            n_active += 1

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
    return entries, n_active, n_retired


def check_rules_json():
    """Returns (rules, rule_ids)."""
    if not RULES.exists():
        err("references/rules.json is missing")
        return {}, set()
    try:
        with RULES.open(encoding="utf-8") as f:
            rules = json.load(f)
    except json.JSONDecodeError as e:
        err(f"rules.json is not valid JSON: {e}")
        return {}, set()

    codes = [d["code"] for d in rules.get("defect_types", [])]
    if codes != CANONICAL_DEFECT_CODES:
        err(f"rules.json defect_types mismatch: {codes}")
    levels = sorted(rules.get("compliance_levels", {}).keys())
    if levels != sorted(CANONICAL_COMPLIANCE):
        err(f"rules.json compliance_levels mismatch: {levels}")

    rule_ids = set()
    for d in rules.get("defect_types", []):
        if "severity" in d:
            err(f"rules.json {d['code']}: legacy field 'severity' — rename to 'default_severity'")
        if d.get("default_severity") not in ("HIGH", "MEDIUM", "LOW"):
            err(f"rules.json {d['code']}: missing or invalid default_severity")
        rid = d.get("rule_id", "")
        if not re.fullmatch(r"R-DEF-\d{3}", rid):
            err(f"rules.json {d['code']}: rule_id missing or malformed '{rid}' (expected R-DEF-###)")
        if rid in rule_ids:
            err(f"rules.json: duplicate rule_id '{rid}'")
        rule_ids.add(rid)

    for key, c in rules.get("layout_constraints", {}).items():
        rid = c.get("rule_id", "")
        if not re.fullmatch(r"R-LAY-\d{3}", rid):
            err(f"rules.json layout '{key}': rule_id missing or malformed '{rid}' (expected R-LAY-###)")
        if rid in rule_ids:
            err(f"rules.json: duplicate rule_id '{rid}'")
        rule_ids.add(rid)

    gr = rules.get("global_rules")
    if not isinstance(gr, list) or not gr:
        err("rules.json: global_rules must be a non-empty list of R-GEN rules")
    else:
        for g in gr:
            rid = g.get("rule_id", "")
            if not re.fullmatch(r"R-GEN-\d{3}", rid):
                err(f"rules.json global_rules: rule_id missing or malformed '{rid}' (expected R-GEN-###)")
            for field in ("name", "statement", "spec_ref"):
                if not str(g.get(field, "")).strip():
                    err(f"rules.json global_rules {rid or '<no-id>'}: missing '{field}'")
            if rid in rule_ids:
                err(f"rules.json: duplicate rule_id '{rid}'")
            rule_ids.add(rid)

    for fr in rules.get("format_rules", []):
        rid = fr.get("rule_id", "")
        if not re.fullmatch(r"R-FMT-\d{3}", rid):
            err(f"rules.json format_rules: rule_id missing or malformed '{rid}' (expected R-FMT-###)")
        if rid in rule_ids:
            err(f"rules.json: duplicate rule_id '{rid}'")
        rule_ids.add(rid)
        if fr.get("market") not in MARKETS:
            err(f"rules.json format_rules {rid}: unknown market '{fr.get('market')}' (expected one of {sorted(MARKETS)})")
        if not re.fullmatch(r"[A-Z]{3}", fr.get("currency_code", "")):
            err(f"rules.json format_rules {rid}: currency_code must be an ISO 4217 alpha code")
        for field in ("currency_symbol", "date_format", "thousands_sep", "decimal_sep"):
            if not str(fr.get(field, "")).strip():
                err(f"rules.json format_rules {rid}: missing '{field}'")
        ts, ds = fr.get("thousands_sep", ""), fr.get("decimal_sep", "")
        if ts and ds and (len(ts) != 1 or len(ds) != 1 or ts == ds):
            err(f"rules.json format_rules {rid}: thousands_sep/decimal_sep must be distinct single characters")

    for fc in rules.get("format_conventions", []):
        rid = fc.get("rule_id", "")
        if not re.fullmatch(r"R-FMT-\d{3}", rid):
            err(f"rules.json format_conventions: rule_id missing or malformed '{rid}' (expected R-FMT-###)")
        if rid in rule_ids:
            err(f"rules.json: duplicate rule_id '{rid}'")
        if not str(fc.get("statement", "")).strip():
            err(f"rules.json format_conventions {rid or '<no-id>'}: missing 'statement'")
        rule_ids.add(rid)

    met_keys = set()
    for mt in rules.get("metrics", []):
        rid = mt.get("rule_id", "")
        if not re.fullmatch(r"R-MET-\d{3}", rid):
            err(f"rules.json metrics: rule_id missing or malformed '{rid}' (expected R-MET-###)")
        if rid in rule_ids:
            err(f"rules.json: duplicate rule_id '{rid}'")
        rule_ids.add(rid)
        key = str(mt.get("key", "")).strip()
        if not key:
            err(f"rules.json metrics {rid}: missing 'key'")
        if key in met_keys:
            err(f"rules.json metrics: duplicate key '{key}'")
        met_keys.add(key)
        for field in ("name", "formula", "unit"):
            if not str(mt.get(field, "")).strip():
                err(f"rules.json metrics {rid}: missing '{field}'")

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
    return rules, rule_ids


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


DS_SOURCES = {"explicit", "derived", "explicit+derived", "derived+explicit"}


def _slot_capacities(s):
    """Returns (total_en, per_line_en) capacity for a DS slot.

    Honours the export's conventions:
      - source "explicit"          -> stored values are DS-stated totals
      - source "derived" / compound -> stored values are per-line; a few
        multiline variants store line totals instead (detected when the
        stored value equals per-line math x max_lines and differs from the
        per-line value itself)
    """
    en = s.get("max_chars_en")
    if not isinstance(en, int) or isinstance(en, bool) or en <= 0:
        return None, None
    ml = s.get("max_lines", 1)
    if not isinstance(ml, int) or isinstance(ml, bool) or ml < 1:
        ml = 1
    if s.get("source") == "explicit":
        return en, en / ml
    if ml > 1 and en % ml == 0:
        w, fs = s.get("available_width_px"), s.get("font_size_px")
        if isinstance(w, int) and isinstance(w, bool) is False and w > 0 \
                and isinstance(fs, int) and isinstance(fs, bool) is False and fs > 0:
            per_line_math = int(w // (fs * 0.55))
            if en == per_line_math * ml and en != per_line_math:
                return en, en / ml  # totals stored, not per-line
    return en * ml, en


def check_thresholds(rules):
    """Validates references/layout-thresholds.json (DS physical capacity SSOT).

    Schema, derivation sanity (recomputed from px math), threshold_ref
    resolution, and the dual-layer invariant: every guidance budget in
    rules.json layout_constraints must fit the tightest mapped DS variant.
    Returns (n_components, n_variants, n_slots, version) or None.
    """
    if not THRESHOLDS.exists():
        err("references/layout-thresholds.json is missing")
        return None
    try:
        ds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"layout-thresholds.json is not valid JSON: {e}")
        return None

    meta = ds.get("metadata")
    if not isinstance(meta, dict):
        err("layout-thresholds.json: metadata block is missing")
        return None
    for field in ("name", "version", "baseline_device"):
        if not str(meta.get(field, "")).strip():
            err(f"layout-thresholds.json metadata: missing '{field}'")
    bw = meta.get("baseline_width_pt")
    if not isinstance(bw, int) or isinstance(bw, bool) or bw <= 0:
        err("layout-thresholds.json metadata: baseline_width_pt must be a positive integer")
    cm = meta.get("calculation_method")
    if not isinstance(cm, dict) or any(not str(cm.get(k, "")).strip() for k in ("cjk", "latin", "multiline")):
        err("layout-thresholds.json metadata: calculation_method must define cjk / latin / multiline")
    lu = str(meta.get("last_updated", ""))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lu):
        err(f"layout-thresholds.json metadata: invalid last_updated '{lu}' (expected YYYY-MM-DD)")
    elif datetime.date.fromisoformat(lu) > TODAY:
        err(f"layout-thresholds.json metadata: last_updated {lu} is in the future")

    comps = ds.get("components")
    if not isinstance(comps, dict) or not comps:
        err("layout-thresholds.json: components must be a non-empty object")
        return None

    n_variants = n_slots = 0
    slot_index = {}  # "comp.variant" -> text_slots dict
    for comp, cdata in comps.items():
        if not isinstance(cdata, dict) or not str(cdata.get("category", "")).strip():
            err(f"layout-thresholds.json component '{comp}': missing category")
            continue
        variants = cdata.get("variants")
        if not isinstance(variants, dict) or not variants:
            err(f"layout-thresholds.json component '{comp}': variants must be a non-empty object")
            continue
        for var, vdata in variants.items():
            slots = vdata.get("text_slots") if isinstance(vdata, dict) else None
            if not isinstance(slots, dict) or not slots:
                err(f"layout-thresholds.json {comp}.{var}: text_slots must be a non-empty object")
                continue
            n_variants += 1
            slot_index[f"{comp}.{var}"] = slots
            for slot, s in slots.items():
                where = f"{comp}.{var}.{slot}"
                if not isinstance(s, dict):
                    err(f"layout-thresholds.json {where}: slot must be an object")
                    continue
                n_slots += 1
                fs = s.get("font_size_px")
                if not isinstance(fs, int) or isinstance(fs, bool) or fs <= 0:
                    err(f"layout-thresholds.json {where}: font_size_px must be a positive integer")
                    fs = None
                for field in ("max_chars_cn", "max_chars_en"):
                    v = s.get(field)
                    if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
                        err(f"layout-thresholds.json {where}: {field} must be a positive integer")
                src = s.get("source")
                if src not in DS_SOURCES:
                    err(f"layout-thresholds.json {where}: unknown source '{src}' "
                        f"(expected one of {sorted(DS_SOURCES)})")
                    src = None
                if not str(s.get("derivation", "")).strip():
                    err(f"layout-thresholds.json {where}: missing derivation")
                if "max_lines" in s:
                    ml = s.get("max_lines")
                    if not isinstance(ml, int) or isinstance(ml, bool) or ml < 1:
                        err(f"layout-thresholds.json {where}: max_lines must be an integer >= 1")
                if "wrap" in s and not isinstance(s.get("wrap"), bool):
                    err(f"layout-thresholds.json {where}: wrap must be a boolean")
                if "truncation" in s and not str(s.get("truncation", "")).strip():
                    err(f"layout-thresholds.json {where}: truncation must be a non-empty string")
                # Derivation sanity: recompute the floors from px math to
                # guard against hand-edited numbers. The export itself rounds
                # +/-1 in a few places (warn); larger contradictions block.
                if src and src != "explicit" and isinstance(fs, int):
                    w = s.get("available_width_px")
                    if not isinstance(w, int) or isinstance(w, bool) or w <= 0:
                        warn(f"layout-thresholds.json {where}: derived slot lacks available_width_px — "
                             f"capacity taken at face value")
                    else:
                        ml = s.get("max_lines", 1)
                        ml = ml if isinstance(ml, int) and ml >= 1 else 1
                        for field, denom in (("max_chars_cn", fs), ("max_chars_en", fs * 0.55)):
                            stored = s.get(field)
                            if not isinstance(stored, int):
                                continue
                            per_line = int(w // denom)
                            if stored not in (per_line, per_line * ml):
                                if abs(stored - per_line) >= 2 and abs(stored - per_line * ml) >= 2:
                                    err(f"layout-thresholds.json {where}: {field} {stored} contradicts its "
                                        f"derivation (width {w}px / {denom:.2f} -> {per_line}/line) — never "
                                        f"hand-edit derived numbers; fix the derivation upstream")
                                else:
                                    warn(f"layout-thresholds.json {where}: {field} {stored} differs from "
                                         f"computed {per_line} by rounding in the DS export")

    # threshold_ref resolution + budget-vs-capacity cross-check
    for key, c in rules.get("layout_constraints", {}).items():
        rid = c.get("rule_id", key)
        refs = c.get("threshold_ref")
        if not isinstance(refs, list) or not refs \
                or not all(isinstance(r, str) and r.strip() for r in refs):
            err(f"rules.json layout '{key}' ({rid}): threshold_ref must be a non-empty list "
                f"of 'component.variant' paths")
            continue
        cap_total = cap_per_line = None
        binding = None
        for ref in refs:
            slots = slot_index.get(ref)
            if slots is None:
                err(f"rules.json layout '{key}' ({rid}): threshold_ref '{ref}' "
                    f"does not resolve in layout-thresholds.json")
                continue
            for slot, s in slots.items():
                total, per_line = _slot_capacities(s)
                if total is None:
                    continue
                if cap_total is None or total < cap_total:
                    cap_total, binding = total, f"{ref}.{slot}"
                if cap_per_line is None or per_line < cap_per_line:
                    cap_per_line = per_line
        if cap_total is None:
            continue
        for field in ("max_en_chars", "max_sea_chars"):
            b = c.get(field)
            if isinstance(b, int) and b > cap_total:
                err(f"rules.json layout '{key}' ({rid}): {field} {b} exceeds DS physical capacity "
                    f"{cap_total} (binding: {binding}; SEA scripts are Latin-width based and "
                    f"share the EN capacity)")
        pl = c.get("max_en_chars_per_line")
        if isinstance(pl, int) and cap_per_line is not None and pl > cap_per_line:
            err(f"rules.json layout '{key}' ({rid}): max_en_chars_per_line {pl} exceeds "
                f"per-line capacity {cap_per_line}")
    return len(comps), n_variants, n_slots, str(meta.get("version", ""))


def check_governance(entries, rules):
    gov = rules.get("governance", {})
    swd = gov.get("stale_warning_days")
    mmd = gov.get("mandatory_max_age_days")
    if not isinstance(swd, int) or not isinstance(mmd, int) or swd <= 0 or mmd <= 0:
        err("rules.json governance: stale_warning_days / mandatory_max_age_days must be positive integers")
        return
    for eid, e in entries.items():
        if e["status"] != "ACTIVE":
            continue  # retired entries are traceability placeholders only
        if e["compliance"] == "MANDATORY":
            if not e["url"]:
                err(f"termbase {eid}: ACTIVE MANDATORY entry must carry a source_url to its regulator")
            if e["date"] is None:
                continue
            age = (TODAY - e["date"]).days
            if age > mmd:
                err(f"termbase {eid}: MANDATORY entry review_date is {age} days old (> {mmd}) — "
                    f"regulatory re-verification required")
        elif e["date"] is not None:
            age = (TODAY - e["date"]).days
            if age > swd:
                warn(f"termbase {eid}: review_date is {age} days old (> {swd}) — due for re-verification")


def check_citations(rule_ids, entries):
    docs = [
        ("references/specification.md", SPEC),
        ("references/authority-index.md", AUTHORITY_INDEX),
        ("SKILL.md", SKILL),
        ("examples/golden-case.md", GOLDEN),
        ("README.md", README),
    ]
    for name, path in docs:
        if not path.exists():
            err(f"{name}: file is missing — citations cannot be validated")
            continue
        text = path.read_text(encoding="utf-8")
        for rid in sorted(set(RULE_ID_RE.findall(text))):
            if rid not in rule_ids:
                err(f"{name}: cites unknown rule_id '{rid}' (not defined in rules.json)")
        for eid in sorted(set(FIN_CITED_RE.findall(text))):
            if eid not in entries:
                err(f"{name}: cites termbase entry '{eid}' which does not exist")
        for eid in sorted(set(FIN_PROPOSED_RE.findall(text))):
            if eid in entries:
                err(f"{name}: gap proposal '{eid} (proposed)' collides with an existing termbase entry — "
                    f"update the example to the next free ID")


def main():
    entries, n_active, n_retired = check_termbase()
    rules, rule_ids = check_rules_json()
    ds_stats = None
    if rules:
        check_layout_consistency(rules)
        ds_stats = check_thresholds(rules)
    if entries and rules:
        check_governance(entries, rules)
    check_citations(rule_ids, entries)

    print(f"termbase entries: {n_active} active / {n_retired} retired")
    if rules:
        print(f"defect codes: {len(rules.get('defect_types', []))} · "
              f"compliance levels: {len(rules.get('compliance_levels', {}))} · "
              f"layout components: {len(rules.get('layout_constraints', {}))}")
        print(f"format rules: {len(rules.get('format_rules', [])) + len(rules.get('format_conventions', []))} · "
              f"metrics: {len(rules.get('metrics', []))}")
    if ds_stats:
        print(f"DS thresholds: {ds_stats[0]} components · {ds_stats[1]} variants · "
              f"{ds_stats[2]} slots (layout-thresholds.json v{ds_stats[3] or '?'})")
    print(f"rule IDs defined: {len(rule_ids)} (R-DEF / R-LAY / R-GEN / R-FMT / R-MET)")
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
