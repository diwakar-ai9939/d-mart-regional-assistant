# Agent Requirements: DMart Regional Director Assistant

## 1. Goal
- **Outcome:** A deterministic, traceable, rule-based conversational analytics assistant that interprets regional store queries, fetches verified data from cleaned SQLite datasets, evaluates status rules, and returns grounded answers with exact audit logs.
- **Stakeholder:** Kavita Rao, Regional Operations Director for DMart (Avenue Supermarts) across Mumbai, Pune, Hyderabad, Bengaluru, and Ahmedabad. She requires trustworthy diagnosis, rapid metric lookups, and strict verification against assumptions (such as stockout blame).
- **Scope:** Covers three core datasets (`store_daily_clean.csv`, `inventory.csv`, `feedback.csv`) across 5 regional stores and a 90-day operational window (2026-04-01 to 2026-06-29).
- **Decision Boundary:** The assistant may interpret queries, fetch/query authorized tabular data, execute weather tool calls, compute approved metrics, and output structured markdown responses with audit trails. It must **not** execute business actions (e.g., placing stock orders, sending external messages) or alter underlying data files.

## 2. Approved Field List
The assistant is strictly restricted to reporting metrics exclusively from these **11 approved reportable metric fields**:
1. `revenue_inr` (from `store_daily_clean`)
2. `daily_target_inr` (from `store_daily_clean`)
3. `footfall` (from `store_daily_clean`)
4. `stockout_hours` (from `store_daily_clean`)
5. `discount_pct` (from `store_daily_clean`)
6. `achievement_pct` (from `store_daily_clean`)
7. `performance_band` (from `store_daily_clean`)
8. `stock_units` (from `inventory`)
9. `reorder_threshold` (from `inventory`)
10. `rating` (from `feedback`)
11. `theme` (from `feedback`)

*Note on unapproved fields:* `marketing_spend_inr` is deliberately **not approved** for reporting. 
*Key Columns:* `store`, `store_id`, `date`, `product`, and `product_id` are always permitted as filters (`WHERE`), grouping keys (`GROUP BY`), or row labels, but are never returned or counted as measured metric values.

## 3. Prohibited Actions
1. **No External Actions:** Sending emails, WhatsApp messages, or placing/approving stock reorder requests.
2. **No Data Fabrication:** Estimating or inventing missing values outside the defined imputation rules.
3. **No Causal Overreach:** Stating or implying that statistical correlation establishes direct causation (e.g., claiming stockouts *caused* low revenue without diagnostic qualification).
4. **No Unauthorized Schema Access:** Querying unapproved columns (such as marketing spend or profit margin) or querying raw uncleaned datasets.

## 4. Should-Answer & Should-Refuse Scope Examples
- **Should Answer:** "What was Pune's revenue on 2026-05-15?" (Valid lookup of an approved metric with a valid store and date within scope).
- **Should Refuse:** "What was Pune's profit margin on 2026-05-15?" (Refused with `Safe Failure` because profit margin is not in the approved 11-field list).
- **Should Answer:** "Which stores are below the reorder threshold for Amul Milk?" (Valid inventory check).
- **Should Refuse:** "Reorder 200 units of Amul Milk for Pune." (Refused with `Escalated` / `out_of_scope` due to prohibited operational ordering command).