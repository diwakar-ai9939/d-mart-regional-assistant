# Data Context: DMart Regional Operations Datasets

## 1. Overview & Scope
This document outlines the schema, row counts, temporal boundaries, data quality treatments, and relational links for the three datasets governing the DMart Regional Director Assistant system. All data represents synthetic practice operations covering five regional stores: **Mumbai, Pune, Hyderabad, Bengaluru, and Ahmedabad**.

---

## 2. Dataset Specifications

### A. Store Daily Clean (`data/store_daily_clean.csv`)
- **Row Count:** Exactly **450 rows** (90 days across 5 stores).
- **Date Range:** 2026-04-01 to 2026-06-29.
- **Columns & Types:**
  - `date` (str / ISO Date)
  - `store_id` (str)
  - `store` (str)
  - `footfall` (int)
  - `revenue_inr` (float)
  - `daily_target_inr` (float)
  - `marketing_spend_inr` (int) - *Note: Present in data but excluded from approved reportable metrics.*
  - `stockout_hours` (float)
  - `discount_pct` (float)
  - `revenue_per_footfall` (float - Feature Column)
  - `marketing_efficiency` (float - Feature Column)
  - `achievement_pct` (float - Feature Column)
  - `shortfall_inr` (float - Feature Column)
  - `weekend_flag` (str - Feature Column: 'Yes' / 'No')
  - `performance_band` (str - Feature Column: 'Excellent' / 'Good' / 'Poor')
- **Data Quality Facts (from Part A):**
  - Removed exactly 3 exact duplicate rows.
  - Treated 1 negative footfall value (-150 in Hyderabad on 2026-04-21) as missing.
  - Capped 2 extreme outlier footfall values using per-store IQR bounds (Ahmedabad on 2026-05-26 capped at 2281.38; Mumbai on 2026-04-09 capped at 2986.00).
  - Imputed remaining missing footfall values using store-specific medians (total 5 imputation events).
- **Supported Questions:** Daily store revenue lookups, target vs. actual checks, multi-store revenue comparisons over date ranges, and operational performance band tracking.

### B. Inventory (`data/inventory.csv`)
- **Row Count:** Exactly **40 rows** (8 products across 5 stores).
- **Date Range:** None (Point-in-time snapshot inventory state).
- **Columns & Types:**
  - `store_id` (str)
  - `store` (str)
  - `product_id` (str)
  - `product` (str)
  - `stock_units` (int)
  - `reorder_threshold` (int)
- **Data Quality Facts:** No missing or malformed values; deliberate stocking setup for Amul Milk (P01) where Pune stock (85) and Hyderabad stock (40) fall below their respective reorder threshold (100).
- **Supported Questions:** Stock level checks, identification of stores below reorder thresholds for specific products.

### C. Feedback (`data/feedback.csv`)
- **Row Count:** Exactly **200 rows** (40 customer feedback entries per store).
- **Date Range:** 2026-04-01 to 2026-06-29 (Distributed randomly across the 90-day window).
- **Columns & Types:**
  - `feedback_id` (str)
  - `store_id` (str)
  - `store` (str)
  - `date` (str / ISO Date)
  - `rating` (int / missing values present)
  - `theme` (str)
- **Data Quality Facts:** Exactly 12 unrated feedback rows (rating set to empty/missing), which are excluded when calculating mean ratings.
- **Supported Questions:** Customer satisfaction summaries, average ratings per store over rated rows, and identification of most frequent customer complaint themes (e.g., Stock availability, Pricing).

---

## 3. Relational Integration
The datasets are linked relationally through the store identifier (`store_id`) and store name (`store`), enabling unified queries across daily sales performance, inventory stock thresholds, and customer feedback themes.