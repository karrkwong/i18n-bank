# Golden Case — Cards section (market: SG, language: en)

Aligned example for report output. Match this structure; do not copy the content blindly.

## Input

- Market: SG · UI language: English (en)
- Source: home screen → Cards section, 3 red boxes + 1 supplementary observation:
  1. Grid tile label: `Card Application`
  2. Grid tile label: `Card Activation`
  3. Loan promo list row: `Personal loan from 2.5% interest rate`
  4. Card detail balance row (supplementary, unmarked): `Available Balance — SGD1,234.50`
- Same screen also uses `Credit Limit` (card detail header) — checked for termbase coverage.

## Report

| # | Component | Current copy | Defect | Severity | Fix | Compliance | Rationale |
|---|-----------|--------------|--------|----------|-----|------------|-----------|
| 1 | Cards grid tile 01 | Card Application | REDUNDANCY | Medium | Apply | [基础表达] GENERAL | R-GEN-002 context omission: repeats parent section "Cards"; termbase FIN-CRD-001 preferred_en = "Apply"; fits R-LAY-002 grid_tile budget |
| 2 | Cards grid tile 02 | Card Activation | REDUNDANCY | Medium | Activate | [基础表达] GENERAL | R-GEN-002; termbase FIN-CRD-002 preferred_en = "Activate"; fits R-LAY-002 grid_tile budget |
| 3 | Loan promo list row | Personal loan from 2.5% interest rate | COMPLIANCE | High | Personal loan from 2.5% EIR p.a. (pending compliance confirmation) | [合规预警] ALERT | R-DEF-006: "Interest rate" without effective-rate qualification risks misleading disclosure; MAS Notice 635 requires EIR; termbase FIN-LON-001 — escalate, do not finalize wording in LQA |
| 4 | Card detail balance row | SGD1,234.50 | FORMAT_GRAMMAR | Medium | S$1,234.50 | [基础表达] GENERAL | R-DEF-005: no separator space between ISO code and amount (R-FMT-006); fix adopts the SG symbol style per R-FMT-001 |

## Summary

- Defect counts: REDUNDANCY 2 (Medium x2) · COMPLIANCE 1 (High x1) · FORMAT_GRAMMAR 1 (Medium x1)
- Metrics (R-MET): density 4 defects / 1 screen (R-MET-001) · severity H1/M3 (R-MET-002) · codes REDUNDANCY 2 / COMPLIANCE 1 / FORMAT_GRAMMAR 1 (R-MET-003) · first-pass rate 0% (R-MET-004) · escalations 1 (R-MET-005) · gaps 1 (R-MET-006)
- For compliance review: #3 (ALERT — routed, not auto-fixed)

## TERMBASE_GAP

| Term | Context | Scope | Suggested entry_id | Suggested authority | Note |
|------|---------|-------|--------------------|--------------------|------|
| Credit Limit | Card detail header | GLOBAL | FIN-CRD-007 (proposed) | International card schemes (Visa/Mastercard) | Proposal only — requires governance review before adoption |

## Notes

- Fixes for #1/#2 stay within the grid_tile character budget (R-LAY-002; `layout_constraints.grid_tile` in rules.json).
- #3 demonstrates the mandatory escalation path: the Fix column carries a proposal, but the finding is routed to human compliance review before any wording is finalized.
- #4 demonstrates amount-format judgment: format defects cite both the defect code (R-DEF-005) and the format rule (R-FMT-006).
- Severity values start from the defect code defaults in rules.json; #3 stays at High because it sits in a promotional/disclosure context (R-GEN-004).
- The gap row demonstrates the TERMBASE_GAP flow: suggested entry IDs take the next free slot in the domain block and carry the `(proposed)` suffix; the release gate rejects gap examples whose ID already exists in the termbase.
