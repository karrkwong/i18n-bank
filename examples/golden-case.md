# Golden Case — Cards section (market: SG, language: en)

Aligned example for report output. Match this structure; do not copy the content blindly.

## Input

- Market: SG · UI language: English (en)
- Source: home screen → Cards section, 3 red boxes:
  1. Grid tile label: `Card Application`
  2. Grid tile label: `Card Activation`
  3. Loan promo list row: `Personal loan from 2.5% interest rate`

## Report

| # | Component | Current copy | Defect | Severity | Fix | Compliance | Rationale |
|---|-----------|--------------|--------|----------|-----|------------|-----------|
| 1 | Cards grid tile 01 | Card Application | REDUNDANCY | Medium | Apply | [基础表达] GENERAL | Context omission: repeats parent section "Cards" (specification §2.2); termbase FIN-CRD-001 preferred_en = "Apply"; fits grid_tile budget |
| 2 | Cards grid tile 02 | Card Activation | REDUNDANCY | Medium | Activate | [基础表达] GENERAL | Same rule; termbase FIN-CRD-002 preferred_en = "Activate" |
| 3 | Loan promo list row | Personal loan from 2.5% interest rate | COMPLIANCE | High | Personal loan from 2.5% EIR p.a. (pending compliance confirmation) | [合规预警] ALERT | "Interest rate" without effective-rate qualification risks misleading disclosure; MAS Notice 637 requires EIR; termbase FIN-LON-001 — escalate, do not finalize wording in LQA |

## Summary

- Defect counts: REDUNDANCY 2 (Medium x2) · COMPLIANCE 1 (High x1)
- For compliance review: #3 (ALERT — routed, not auto-fixed)
- TERMBASE_GAP: none

## Notes

- Fixes for #1/#2 stay within the grid_tile character budget (`layout_constraints.grid_tile` in rules.json).
- #3 demonstrates the mandatory escalation path: the Fix column carries a proposal, but the finding is routed to human compliance review before any wording is finalized.
- Severity values start from the defect code defaults in rules.json; #3 stays at High because it sits in a promotional/disclosure context.
