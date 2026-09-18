# Golden Case A — Cards section (market: SG, language: en)

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

# Golden Case B — Transfers & Accounts sections (market: SG, language: en)

Second aligned example: termbase arbitration after governance review (batch 1, 2026-09-18).
Same structure as Case A; do not copy the content blindly.

## Input

- Market: SG · UI language: English (en)
- Source: same app, Transfers & Accounts service lists, 3 red boxes + 1 supplementary check:
  1. Transfers list row: `Auto Sweep`
  2. Accounts list row: `Payroll Service`
  3. Accounts list row: `E-Statement`
  4. Accounts list row (supplementary, unmarked): `Paper Statement`
- All four terms are covered by termbase entries admitted in governance review batch 1.

## Report

| # | Component | Current copy | Defect | Severity | Fix | Compliance | Rationale |
|---|-----------|--------------|--------|----------|-----|------------|-----------|
| 1 | Transfers list row | Auto Sweep | COMPLIANCE | High | Standing Instruction | [行业标准] STANDARD | R-DEF-006 industry-naming violation: "Auto Sweep" names a funds-sweeping concept, not recurring transfers; termbase FIN-TRF-017 lists "Auto Sweep" in forbidden_en, preferred_en = "Standing Instruction"; fix fits R-LAY-005 list_title budget |
| 2 | Accounts list row | Payroll Service | REDUNDANCY | Medium | Salary Crediting | [行业标准] STANDARD | R-DEF-004 generic "Service" suffix; termbase FIN-ACT-006 preferred_en = "Salary Crediting" ("Payroll Service" is variant_en — acceptable but not preferred); fix fits R-LAY-005 budget |
| 3 | Accounts list row | E-Statement | FORMAT_GRAMMAR | Low | eStatement | [行业标准] STANDARD | R-DEF-005 casing-convention non-conformance; termbase FIN-ACT-008 preferred casing "eStatement", "E-Statement" is variant_en; de-escalated Medium → Low per R-GEN-004 — variant explicitly tolerated, finding is consistency convergence only |

## Summary

- Defect counts: COMPLIANCE 1 (High x1) · REDUNDANCY 1 (Medium x1) · FORMAT_GRAMMAR 1 (Low x1)
- Metrics (R-MET): density 3 defects / 1 screen (R-MET-001) · severity H1/M1/L1 (R-MET-002) · codes COMPLIANCE 1 / REDUNDANCY 1 / FORMAT_GRAMMAR 1 (R-MET-003) · first-pass rate 25% — 1 of 4 checked strings clean (R-MET-004) · escalations 0 (R-MET-005) · gaps 0 (R-MET-006)
- For compliance review: none — #1 is a STANDARD-level naming fix, finalized in LQA

## Notes

- Post-review arbitration: every finding cites an ACTIVE termbase entry admitted via governance review batch 1. The TERMBASE_GAP table is omitted when the gap count is 0.
- #1 vs Case A #3: the COMPLIANCE defect code covers both statutory (MANDATORY) and industry-standard naming violations; only the former routes to human compliance review. STANDARD-level fixes are finalized in LQA.
- #2 demonstrates variant arbitration: variant_en forms are acceptable, but a generic suffix is still reportable REDUNDANCY; the fix converges to preferred_en.
- #3 demonstrates justified de-escalation (R-GEN-004): the termbase note explicitly tolerates the variant, so the finding drops to Low — consistency convergence, not a functional defect.
- `Paper Statement` (FIN-ACT-009) and `eStatement` (FIN-ACT-008) are separate channel entries — never arbitrate one to the other's preferred form. In grid_tile contexts "Paper Statement" exceeds the R-LAY-002 budget and becomes a design-confirmation item.
