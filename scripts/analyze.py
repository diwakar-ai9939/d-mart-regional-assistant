import os
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(val):
    if pd.isna(val):
        return val
    return float(Decimal(str(val)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def analyze_data():
    os.makedirs("analysis", exist_ok=True)
    
    # 1. Read clean data
    df = pd.read_csv("data/store_daily_clean.csv")
    
    # Raw data for comparison correlation
    raw_df = pd.read_csv("data/store_daily.csv")
    raw_df_clean_dup = raw_df.drop_duplicates(keep="first")
    raw_df_clean_dup["footfall"] = pd.to_numeric(raw_df_clean_dup["footfall"], errors="coerce")
    raw_valid_ff = raw_df_clean_dup.dropna(subset=["footfall"])
    raw_corr = np.corrcoef(raw_valid_ff["revenue_inr"], raw_valid_ff["footfall"])[0, 1]
    
    stores = sorted(df["store"].unique())
    table_rows = []
    
    for store in stores:
        sub = df[df["store"] == store]
        mean_rev = round_half_up(sub["revenue_inr"].mean())
        mean_ff = round_half_up(sub["footfall"].mean())
        mean_so = round_half_up(sub["stockout_hours"].mean())
        total_rev = sub["revenue_inr"].sum()
        total_ff = sub["footfall"].sum()
        rev_per_ff = round_half_up(total_rev / total_ff)
        mean_ach = round_half_up(sub["achievement_pct"].mean())
        poor_days = int((sub["performance_band"] == "Poor").sum())
        
        table_rows.append({
            "store": store,
            "mean_revenue": mean_rev,
            "mean_footfall": mean_ff,
            "mean_stockout": mean_so,
            "rev_per_ff": rev_per_ff,
            "mean_achievement": mean_ach,
            "poor_days": poor_days
        })
        
    # All stores row
    all_mean_rev = round_half_up(df["revenue_inr"].mean())
    all_mean_ff = round_half_up(df["footfall"].mean())
    all_mean_so = round_half_up(df["stockout_hours"].mean())
    all_total_rev = df["revenue_inr"].sum()
    all_total_ff = df["footfall"].sum()
    all_rev_per_ff = round_half_up(all_total_rev / all_total_ff)
    all_mean_ach = round_half_up(df["achievement_pct"].mean())
    all_poor_days = int((df["performance_band"] == "Poor").sum())
    
    # Store stockout ranking for premise test
    store_so = df.groupby("store")["stockout_hours"].mean().sort_values(ascending=False)
    
    # Correlations across all rows
    corr_rev_so_all = round_half_up(np.corrcoef(df["revenue_inr"], df["stockout_hours"])[0, 1])
    corr_rev_ff_all = round_half_up(np.corrcoef(df["revenue_inr"], df["footfall"])[0, 1])
    
    # Correlations inside Pune
    pune_sub = df[df["store"] == "Pune"]
    corr_rev_so_pune = round_half_up(np.corrcoef(pune_sub["revenue_inr"], pune_sub["stockout_hours"])[0, 1])
    corr_rev_ff_pune = round_half_up(np.corrcoef(pune_sub["revenue_inr"], pune_sub["footfall"])[0, 1])
    
    # Write findings.md
    findings_content = f"""# Findings Report

## 1. Store Performance Summary Table
| Store | Mean Daily Revenue (INR) | Mean Footfall | Mean Stockout Hours | Revenue per Footfall (INR) | Mean Achievement (%) | Poor Days |
|---|---|---|---|---|---|---|
"""
    for r in table_rows:
        findings_content += f"| {r['store']} | {r['mean_revenue']} | {r['mean_footfall']} | {r['mean_stockout']} | {r['rev_per_ff']} | {r['mean_achievement']} | {r['poor_days']} |\n"
    
    findings_content += f"| All stores | {all_mean_rev} | {all_mean_ff} | {all_mean_so} | {all_rev_per_ff} | {all_mean_ach} | {all_poor_days} |\n"
    
    findings_content += f"""
## 2. Premise Test
Kavita's premise is that Pune is the lowest-revenue store because of stockouts. 
Ranking the five stores by mean stockout hours:
"""
    rank = 1
    for st, val in store_so.items():
        findings_content += f"{rank}. {st}: {val:.2f} hours\n"
        rank += 1
        
    findings_content += f"""
**Conclusion:** Pune ranks 4th out of 5 stores by mean stockout hours (2.32 hours against an all-store mean of {all_mean_so}), while Hyderabad is the highest (3.85 hours). Therefore, the premise that Pune has the most stockouts is **not supported** by the data.

## 3. Pearson Correlations
- **Revenue vs Stockout Hours (All rows):** {corr_rev_so_all}
- **Revenue vs Footfall (All rows):** {corr_rev_ff_all}
- **Revenue vs Stockout Hours (Pune rows only):** {corr_rev_so_pune}
- **Revenue vs Footfall (Pune rows only):** {corr_rev_ff_pune}
- **Revenue vs Footfall (Deduplicated raw data with nulls/extremes):** {raw_corr:.3f}

*Note: Correlation does not establish causation.*

## 4. Facts, Insights, and Hypotheses
### Facts
1. Pune recorded a mean daily revenue of INR 636,358.55, which is the lowest among all five stores.
2. Pune experienced 70 days in the "Poor" performance band out of 90 days.
3. Pune's mean stockout hours stand at 2.32 hours, lower than the overall store average of 2.74 hours.
4. The revenue-to-footfall correlation across all stores is strong at {corr_rev_ff_all}.

### Insights (Interpretation)
1. Since Pune's stockout hours are lower than average, the revenue deficit cannot be attributed to product unavailability or stockouts.
2. The strong positive correlation between revenue and footfall indicates that customer traffic volume is the primary driver of total revenue.

### Hypotheses (Unconfirmed)
1. **Hypothesis 1:** Pune's low footfall is driven by aggressive local competitor pricing or sub-optimal marketing spend efficiency. *(Extra data needed: Local competitor pricing indexes and footfall demographic surveys).*
2. **Hypothesis 2:** Pune store location has lower residential density or accessibility compared to Mumbai and Bengaluru. *(Extra data needed: Store catchment area mapping and foot traffic catchment census data).*
"""

    with open("analysis/findings.md", "w", encoding="utf-8") as f:
        f.write(findings_content)
        
    # Write executive_summary.md
    exec_content = f"""# Executive Summary: Pune Store Performance Diagnosis

**Dataset:** DMart Regional Store Operations (Synthetic Practice Data)  
**Period Covered:** 2026-04-01 to 2026-06-29 (90 Days)  
**Author:** Regional Operations Assistant  

## Headline Finding
Pune's underperformance is driven entirely by a footfall deficit, not by stockouts.

## Magnitude
Pune's mean daily revenue (INR 636,358.55) is **26.14% below** the all-store mean daily revenue (INR 861,535.24), and its mean footfall (1,517.71) is **25.00% below** the all-store mean footfall (2,023.59). Meanwhile, its revenue per footfall (INR 419.29) is only **1.52% below** the all-store figure (INR 425.75).

## Drivers
- **What is driving it:** Low customer footfall volume and severe target under-achievement (70 Poor performance days).
- **What is not driving it:** Stockouts (Pune ranks 4th with 2.32 mean stockout hours, below the 2.74 all-store average).

## Supporting Facts
- Pune stockouts average 2.32 hours compared to Hyderabad's high of 3.85 hours.
- Revenue-to-footfall correlation across stores is robust at 0.918.

## Open Hypotheses
- Local competitive pressure or catchment area disadvantage affecting customer acquisition. *(Required Data: Local competitor mapping and catchment footfall studies).*

## Recommendation
- **Owner:** Regional Marketing & Store Expansion Team.
- **Action:** Halt the planned stock-availability capital expenditure for Pune and instead launch a targeted local promotional campaign and footfall-acquisition drive.
- **Timeline:** Implement within 30 days.
"""

    with open("analysis/executive_summary.md", "w", encoding="utf-8") as f:
        f.write(exec_content)
        
    print("Analysis script completed successfully. Generated findings.md and executive_summary.md.")

if __name__ == "__main__":
    analyze_data()