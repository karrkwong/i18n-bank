# i18n-bank

Production-grade i18n / localization QA skill for banking & fintech app UI copy
across SG / MY / HK / TH / ID markets (mobile, H5, mini-program).

## How it works

In plain words:

1. **You feed it screenshots or a string table.** Red boxes on screenshots mark the suspect strings (or you provide `key, source, target, locale` rows), plus two pieces of context: target market and UI language.
2. **It figures out what each string is.** A tab, a grid tile, a dialog — every component type has its own character budget in `rules.json`. The same words can be fine on a page header and broken on a grid tile.
3. **It judges words, not just strings.** Each suspect term is looked up by term + component + market scope — never by bare word match. The termbase knows "Apply" is the right grid-tile word under a "Cards" section, and "Card Application" is redundant there.
4. **It flags real defects.** Seven defect types: truncation, mixed language, redundancy, grammar/format, compliance risk, placeholders, line breaks. Amounts and dates are judged against per-market format rules — Thai UIs use Buddhist Era years, Indonesian uses `1.500.000,00` separators.
5. **It proposes fixes that actually fit — and never oversteps.** Every fix must fit the component budget and use the preferred term. Anything compliance-sensitive (e.g. interest-rate disclosure) is routed to human compliance review; terms the termbase doesn't cover go into a gap table for governance review. Nothing sensitive is silently rewritten.
6. **You get a standard report.** An 8-column findings table with stable rule citations, plus six quality metrics (defect density, severity distribution, first-pass rate...). Same shape every time, so results are comparable across teams and runs.

## Judgment priority & sources

**Which asset wins** (when documents disagree):

| Priority | Asset | Role |
|---|---|---|
| 1 | `rules.json` / `termbase.csv` | Numeric SSOT — every budget, threshold and term lives here |
| 2 | `specification.md` | Explains the why; never overrides the SSOTs |

**Which term wins** (terminology arbitration): `LOCAL_XX` > `REGIONAL_SEA` > `GLOBAL`, among `ACTIVE` entries, judged on the (term, component, scope) triple — never a bare term match.

**Where terms come from:**

| Level | Source | Examples | Discipline |
|---|---|---|---|
| MANDATORY | Regulators, statutes, scheme rules | PayNow (MAS / ABS), FPS (HKMA / HKICL), CPF, EIR disclosure (MAS Notice 635) | Official wording locked; document-level source URL required |
| STANDARD | Industry standards | IBAN (ISO 13616), BIC (ISO 9362), card-scheme terms | Follow the standard |
| GENERAL | SEA UI/UX conventions | Apply, History, Favourite (en-GB) | Editorial rules in the spec |

Verification navigation: `references/authority-index.md` · methodology: `specification.md` § 7.3.

## Why it's rigorous

- **Single source of truth.** Every budget, threshold and default lives in exactly one file; the spec explains, never overrides.
- **A release gate, not a promise.** `validate.py` must be green before any change ships: schema closure, ID discipline, cross-file consistency, governance freshness, citation resolution, format-rule / metric schemas, and a regex regression suite where every historical false positive lives on as a test case.
- **Citations that resolve.** Every finding cites a stable rule ID (`R-DEF` / `R-LAY` / `R-GEN` / `R-FMT` / `R-MET`) or termbase entry; the gate verifies every referenced ID actually exists. Dangling references block the release.
- **MANDATORY means verifiable.** Each entry carries a document-level URL to a regulator page. The process catching its own error: an early version cited MAS Notice 637 for EIR disclosure; verification against primary sources showed 637 is the capital-adequacy rule — the correct instrument is Notice 635, and the fix is in the commit history.
- **Nothing silently expires.** MANDATORY entries must be re-verified within 365 days or the gate blocks; retired entry IDs are never reused; every entry carries status, review date and source authority.
- **Honest gaps.** Uncovered terms become TERMBASE_GAP proposals for governance review (spec § 7.3 — the "citable instrument test"), never invented straight into the termbase.

## Layout

| Path | Role |
|------|------|
| `SKILL.md` | Skill entry: trigger conditions, workflow, I/O contract |
| `references/rules.json` | Numeric SSOT: defect codes, compliance levels, layout budgets, stable rule IDs, market format rules, quality metrics, governance thresholds |
| `references/specification.md` | Human-readable judgment logic and rationale |
| `references/authority-index.md` | Authority source index: per-market regulators, document families, entry URLs (index only) |
| `references/termbase.csv` | Terminology SSOT: preferred / variant / forbidden terms + governance fields |
| `examples/golden-case.md` | Golden example for output alignment |
| `validate.py` | Release gate: consistency, regex regression, governance, citation, format-rule and metric schema checks |

## Install

```bash
git clone https://github.com/karrkwong/i18n-bank <project>/.trae/skills/i18n-bank
```

## Development workflow

1. Edit the SSOT first (`references/rules.json` or `references/termbase.csv`)
2. Sync `references/specification.md`
3. `python3 validate.py` — gate must be green before release
4. Commit

## Authoritative sources

- Central banks / regulators: MAS (SG) · BNM (MY) · HKMA (HK) · BOT (TH) · BI (ID) · ABS / CPF Board (SG) · MPFA (HK)
- Industry standards: ISO 20022 · SWIFT · ISO 13616 / 9362 · Visa / Mastercard Rules
- Per-market navigation entries (regulators, document families, entry URLs): see `references/authority-index.md`; governance review methodology: specification.md section 7.3

## Roadmap

- [x] Phase 1 — skill framework (SKILL.md, references layout, golden case, release gate)
- [x] Phase 2 — P0 fixes: regex false positives/negatives, dialog_toast layout gap, termbase field hygiene, severity arbitration (gate green)
- [x] Phase 3 — quality hardening: governance fields (status / review_date / source_url), stable rule IDs (R-DEF / R-LAY / R-GEN), TERMBASE_GAP format, citation gate
- [x] Phase 4 — coverage expansion: Bills / FX / Investments termbase domains (48 entries), market format rules (R-FMT), quality metrics (R-MET)
- [x] Post-release — governance review methodology (spec 7.3) + authority source index; fix MAS EIR citation (Notice 637 → 635)
- [x] Governance review batch 1 — 5 gap proposals → 6 ACTIVE entries (FIN-TRF-016/017, FIN-ACT-006~009); review overturned 3 initial suggestions (Auto Sweep → Standing Instruction, Payroll Service → Salary Crediting, E-Statement → eStatement) and split statement channels into two entries; golden case B added to demonstrate post-review arbitration (forbidden / variant / de-escalation findings)
