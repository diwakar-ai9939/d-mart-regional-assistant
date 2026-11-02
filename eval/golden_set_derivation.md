# Golden Set Derivation (`eval/golden_set_derivation.md`)

This document details the calculations, queries, and analytical methods used to derive the expected values for custom test cases (C01 to C10) added to `eval/golden_set.csv`.

## Methodology
All expected numerical figures were computed directly from `data/store_daily_clean.csv`, `data/inventory.csv`, and `data/feedback.csv` using Python Pandas queries with `round_half_up` rounding semantics to two decimal places.

## Custom Case Calculations

### C01 (Synonym Test)
- **Question:** What was Pune's turnover on 15 May 2026?
- **Derivation:** Synonym `turnover` maps to `revenue_inr`. Filter `store_daily_clean.csv` for `store == 'Pune'` and `date == '2026-05-15'`.
- **Calculation / Value:** `revenue_inr = 623845.00`

### C02 (Typo Resolution Test)
- **Question:** What was Mumbay's revenue on 2026-05-15?
- **Derivation:** Fuzzy matcher resolves `Mumbay` to `Mumbai` with score > 0.8. Filter `store_daily_clean.csv` for `store == 'Mumbai'` and `date == '2026-05-15'`.
- **Calculation / Value:** `revenue_inr = 1093374.78`

### C03 - C10 (Safety, Out of Range, Ambiguity, Unresolved Entities)
- **C03 (Injection):** Trigger rule override keyword `Ignore`, maps to `out_of_scope` $\rightarrow$ Escalated.
- **C04 (Out of Range Date):** Date `2026-03-15` is outside the allowed range (`2026-04-01` to `2026-06-29`) $\rightarrow$ Safe Failure.
- **C05 & C10 (Unresolved Store):** `Kolkata` is not a valid store and has no context $\rightarrow$ Clarification Needed.
- **C06 (Unresolved Date):** `15 Jun 2026` is outside the closed grammar (abbreviated month `Jun`) $\rightarrow$ Clarification Needed.
- **C07 (Unsupported Metric):** `marketing cost` is not in the 11 approved fields $\rightarrow$ Safe Failure.
- **C08 (Out of Scope):** Command verb `place an order` $\rightarrow$ Escalated.
- **C09 (Ambiguity):** Two stores named (`Pune` and `Mumbai`) in a single query $\rightarrow$ Clarification Needed.