# i18n-bank

Production-grade i18n / localization QA skill for banking & fintech app UI copy
across SG / MY / HK / TH / ID markets (mobile, H5, mini-program).

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
