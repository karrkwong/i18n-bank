# i18n-bank

Production-grade i18n / localization QA skill for banking & fintech app UI copy
across SG / MY / HK / TH / ID markets (mobile, H5, mini-program).

## Layout

| Path | Role |
|------|------|
| `SKILL.md` | Skill entry: trigger conditions, workflow, I/O contract |
| `references/rules.json` | Numeric SSOT: defect codes, compliance levels, layout budgets |
| `references/specification.md` | Human-readable judgment logic and rationale |
| `references/termbase.csv` | Terminology SSOT: preferred / variant / forbidden terms |
| `examples/golden-case.md` | Golden example for output alignment |
| `validate.py` | Release gate: cross-file consistency + regex regression |

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

- Central banks / regulators: MAS (SG) · BNM (MY) · HKMA (HK) · BOT (TH) · BI (ID)
- Industry standards: ISO 20022 · SWIFT · ISO 13616 / 9362 · Visa / Mastercard Rules

## Roadmap

- [x] Phase 1 — skill framework (SKILL.md, references layout, golden case, release gate)
- [x] Phase 2 — P0 fixes: regex false positives/negatives, dialog_toast layout gap, termbase field hygiene, severity arbitration (gate green)
- [ ] Phase 3 — quality hardening: governance fields, stable rule IDs
- [ ] Phase 4 — coverage expansion: domains, number/currency/date formats, metrics
