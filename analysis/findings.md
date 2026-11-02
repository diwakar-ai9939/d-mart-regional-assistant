# Findings Report

## 1. Store Performance Summary Table
| Store | Mean Daily Revenue (INR) | Mean Footfall | Mean Stockout Hours | Revenue per Footfall (INR) | Mean Achievement (%) | Poor Days |
|---|---|---|---|---|---|---|
| Ahmedabad | 782647.37 | 1922.59 | 3.19 | 407.08 | 92.08 | 1 |
| Bengaluru | 931065.68 | 2076.86 | 2.38 | 448.31 | 98.01 | 0 |
| Hyderabad | 893233.01 | 2209.51 | 3.85 | 404.27 | 94.02 | 0 |
| Mumbai | 1064371.6 | 2391.27 | 1.93 | 445.11 | 101.37 | 0 |
| Pune | 636358.55 | 1517.71 | 2.32 | 419.29 | 70.71 | 70 |
| All stores | 861535.24 | 2023.59 | 2.74 | 425.75 | 91.24 | 71 |

## 2. Premise Test
Kavita's premise is that Pune is the lowest-revenue store because of stockouts. 
Ranking the five stores by mean stockout hours:
1. Hyderabad: 3.85 hours
2. Ahmedabad: 3.19 hours
3. Bengaluru: 2.38 hours
4. Pune: 2.32 hours
5. Mumbai: 1.93 hours

**Conclusion:** Pune ranks 4th out of 5 stores by mean stockout hours (2.32 hours against an all-store mean of 2.74), while Hyderabad is the highest (3.85 hours). Therefore, the premise that Pune has the most stockouts is **not supported** by the data.

## 3. Pearson Correlations
- **Revenue vs Stockout Hours (All rows):** -0.15
- **Revenue vs Footfall (All rows):** 0.92
- **Revenue vs Stockout Hours (Pune rows only):** -0.25
- **Revenue vs Footfall (Pune rows only):** 0.74
- **Revenue vs Footfall (Deduplicated raw data with nulls/extremes):** 0.548

*Note: Correlation does not establish causation.*

## 4. Facts, Insights, and Hypotheses
### Facts
1. Pune recorded a mean daily revenue of INR 636,358.55, which is the lowest among all five stores.
2. Pune experienced 70 days in the "Poor" performance band out of 90 days.
3. Pune's mean stockout hours stand at 2.32 hours, lower than the overall store average of 2.74 hours.
4. The revenue-to-footfall correlation across all stores is strong at 0.92.

### Insights (Interpretation)
1. Since Pune's stockout hours are lower than average, the revenue deficit cannot be attributed to product unavailability or stockouts.
2. The strong positive correlation between revenue and footfall indicates that customer traffic volume is the primary driver of total revenue.

### Hypotheses (Unconfirmed)
1. **Hypothesis 1:** Pune's low footfall is driven by aggressive local competitor pricing or sub-optimal marketing spend efficiency. *(Extra data needed: Local competitor pricing indexes and footfall demographic surveys).*
2. **Hypothesis 2:** Pune store location has lower residential density or accessibility compared to Mumbai and Bengaluru. *(Extra data needed: Store catchment area mapping and foot traffic catchment census data).*
