---
name: i18n-bank
description: "Banking app i18n/LQA skill: reviews fintech UI copy against terminology, compliance and layout rules. Invoke for app copy review or i18n defect checks (国际化走查 · 本地化质检 · 银行App文案走查 · 术语合规检查)."
---

# i18n Bank LQA

Production-grade localization QA for banking & fintech app UI copy
(mobile iOS/Android, H5, mini-program) across SG / MY / HK / TH / ID markets.

## Assets & source of truth

| Asset | Role |
|-------|------|
| `references/rules.json` | Numeric SSOT — defect codes, compliance levels, layout budgets (refinement guidance layer), stable rule IDs (`R-DEF` / `R-LAY` / `R-GEN` / `R-FMT` / `R-MET`), market format rules, quality metrics, governance thresholds. Every limit cited in a report comes from here. |
| `references/layout-thresholds.json` | Physical capacity SSOT — per-variant character limits derived from the SuperApp Design System (px math, baseline iPhone X/Xs 375pt). TRUNCATION judgment and Fix feasibility consult this layer; guidance budgets never exceed mapped physical capacities. |
| `references/termbase.csv` | Terminology SSOT — preferred / variant / forbidden terms with regulatory sources and governance fields (`status`, `review_date`, `source_url`). |
| `references/specification.md` | Human-readable judgment logic. Explains *why*; never overrides the SSOTs on numbers. |
| `references/authority-index.md` | Authority source index — per-market navigation entries (regulator, document families, entry URLs) for governance review and MANDATORY re-verification. Index only; full texts stay at the source. |
| `examples/golden-case.md` | Golden example for output alignment. |
| `validate.py` | Release gate: cross-file consistency + regex regression. |

If `specification.md` disagrees with `rules.json` or `termbase.csv`, the SSOT files win; report the disagreement as a defect.

## Input contract

One of:

1. **Annotated screenshots** — numbered red boxes marking suspect strings. Reproduce on-screen text verbatim, including truncation, line breaks and ellipsis.
2. **String table** — columns: `key, source, target, locale`.

Required context — ask before proceeding if missing:

- Target market (SG / MY / HK / TH / ID)
- UI language under review

## Workflow

1. **Load** `references/rules.json` and `references/termbase.csv`.
2. **Component identification** — classify each red box / string row by component type (keys of `layout_constraints` in rules.json) and look up its refinement budget. For truncation risk and Fix feasibility, also look up the physical capacity of the specific DS variant in `references/layout-thresholds.json` (dual-layer budgets: R-LAY budgets say how long good copy should be; DS thresholds say where it physically truncates).
3. **Terminology arbitration** — query the termbase by the triple (term, `context_component`, `scope`) among `status = ACTIVE` entries; priority `LOCAL_XX` > `REGIONAL_SEA` > `GLOBAL`. Never judge on a bare term match.
4. **Defect detection** — classify against the defect codes in rules.json. A `typical_pattern` regex hit is a **candidate hint only**: confirm it against the code's judgment criteria before reporting, and discard false positives. Number, currency and date strings are judged against `format_rules` / `format_conventions` (R-FMT-…). A rendered string that fits its DS physical capacity but still truncates (or vice versa) is an implementation deviation — report both numbers (DS capacity vs observed truncation point) and route it to development.
5. **Severity** — start from the defect code's default severity; escalate one level when the string sits in a payment / confirmation / regulatory-disclosure flow or involves a MANDATORY term; any de-escalation must be justified in the Rationale column.
6. **Report** — the 8-column table below plus the quality metrics defined in `rules.json` `metrics` (R-MET-001…006: defect density, severity distribution, code distribution, first-pass rate, compliance escalations, termbase gaps). Report language follows the language of the request.

### Escalation paths (mandatory)

- **Compliance alert** — findings tagged ALERT go to a dedicated "for compliance review" section. Never silently fix them. Never issue legal opinions.
- **DS deviation** — findings where physical rendering contradicts `layout-thresholds.json` (fits-capacity-but-truncated, or over-capacity-but-intact) go to a dedicated "for development review" section with both numbers cited. Copy refinement (R-GEN-002) may be proposed in parallel, but it is not the root-cause fix.
- **TERMBASE_GAP** — terms the termbase does not cover go into a dedicated gap table: `Term | Context | Scope | Suggested entry_id | Suggested authority | Note`. The suggested ID takes the next free slot in its domain block and must carry the `(proposed)` suffix; the gate rejects gap IDs that collide with existing entries. Gap rows are proposals for governance review — never insert them into `termbase.csv` directly, never invent termbase entries, rule IDs, or regulatory citations.

## Output contract

Markdown table, 8 columns, in order:

`# | Component | Current copy | Defect | Severity | Fix | Compliance | Rationale`

- **Current copy**: verbatim on-screen string.
- **Fix**: must fit the component's character budget and use the termbase preferred term.
- **Rationale**: cite the stable rule ID (`R-DEF-…` / `R-LAY-…` / `R-GEN-…` / `R-FMT-…`), termbase `entry_id`, or regulatory authority.
- Match the structure of `examples/golden-case.md`.

## Boundaries

- MANDATORY terms are locked to official wording — never paraphrase, abbreviate, or "improve".
- British spelling (en-GB family) is the default for SEA English locales.
- Number, currency and date formats follow the market rules in `format_rules` and the UI language locale for separators.
- Defect codes and compliance tags keep their canonical form regardless of report language.
- Run `validate.py` after any asset change; the gate must be green before a release.

## Maintenance

- Change flow: edit the SSOT (`rules.json` / `termbase.csv`) → sync `specification.md` → `python3 validate.py` → commit.
- `references/layout-thresholds.json` tracks the SuperApp Design System: re-export from the DS source when it changes; the gate re-validates schema, `threshold_ref` resolution and budget cross-checks. Never hand-edit derived numbers — fix the derivation upstream.
- Termbase `entry_id`s are permanent; never reuse a retired ID. Retired entries keep `RETIRED` status in place for traceability — never delete them.
- Gap proposals live in reports only; the working group adopts them as `ACTIVE` entries after review.
- Re-verify MANDATORY entries within `governance.mandatory_max_age_days` (the gate blocks stale ones); other ACTIVE entries trigger a warning past `stale_warning_days`.
- Governance review follows specification.md section 7.3: navigate from `references/authority-index.md`, verify against primary instruments, and record document-level URLs (never site homepages) in `source_url`.
- Add a regression case to `validate.py` for every fixed false positive / false negative.
