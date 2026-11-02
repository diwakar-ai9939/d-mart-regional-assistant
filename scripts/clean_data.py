import os
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(val):
    if pd.isna(val):
        return val
    return float(Decimal(str(val)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def clean_data():
    os.makedirs("data", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)
    
    # 1. Read raw data
    df = pd.read_csv("data/store_daily.csv")
    
    # 2. Remove exact duplicate rows, keeping the first occurrence
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    
    # 3. Treat any negative footfall as missing
    df["footfall"] = pd.to_numeric(df["footfall"], errors="coerce")
    df.loc[df["footfall"] < 0, "footfall"] = np.nan
    
    cleaning_logs = []
    
    # 4. Per-store Q1/Q3 bounds and IQR capping, then median imputation
    stores = df["store"].unique()
    cleaned_groups = []
    
    for store in stores:
        sub = df[df["store"] == store].copy()
        
        # Calculate Q1, Q3 using linear interpolation (default pandas quantile)
        valid_ff = sub["footfall"].dropna()
        q1 = valid_ff.quantile(0.25)
        q3 = valid_ff.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # IQR Capping
        for idx, row in sub.iterrows():
            ff = row["footfall"]
            if pd.notna(ff):
                if ff > upper_bound:
                    old_val = ff
                    new_val = round_half_up(upper_bound)
                    sub.loc[idx, "footfall"] = new_val
                    cleaning_logs.append({
                        "store": store,
                        "date": row["date"],
                        "old_footfall": old_val,
                        "new_footfall": new_val,
                        "rule": "iqr_cap"
                    })
                elif ff < lower_bound:
                    old_val = ff
                    new_val = round_half_up(lower_bound)
                    sub.loc[idx, "footfall"] = new_val
                    cleaning_logs.append({
                        "store": store,
                        "date": row["date"],
                        "old_footfall": old_val,
                        "new_footfall": new_val,
                        "rule": "iqr_cap"
                    })
                    
        # Check negative to missing logging (from raw before capping)
        # We can check raw values for negative
        raw_sub = pd.read_csv("data/store_daily.csv")
        raw_sub = raw_sub[(raw_sub["store"] == store)]
        for idx, row in raw_sub.iterrows():
            try:
                val = float(row["footfall"])
                if val < 0:
                    # find matching row in sub by date
                    d = row["date"]
                    cleaning_logs.append({
                        "store": store,
                        "date": d,
                        "old_footfall": val,
                        "new_footfall": "",
                        "rule": "negative_to_missing"
                    })
            except ValueError:
                pass

        # Median Imputation for remaining missing footfall
        store_median = sub["footfall"].median()
        missing_mask = sub["footfall"].isna()
        for idx, row in sub[missing_mask].iterrows():
            old_val = ""
            new_val = round_half_up(store_median)
            sub.loc[idx, "footfall"] = new_val
            cleaning_logs.append({
                "store": store,
                "date": row["date"],
                "old_footfall": old_val,
                "new_footfall": new_val,
                "rule": "median_impute"
            })
            
        cleaned_groups.append(sub)
        
    df_clean = pd.concat(cleaned_groups).sort_values(by=["date", "store_id"]).reset_index(drop=True)
    
    # 5. Add feature columns
    df_clean["revenue_per_footfall"] = df_clean.apply(lambda r: round_half_up(r["revenue_inr"] / r["footfall"]), axis=1)
    df_clean["marketing_efficiency"] = df_clean.apply(lambda r: round_half_up(r["revenue_inr"] / r["marketing_spend_inr"]), axis=1)
    df_clean["achievement_pct"] = df_clean.apply(lambda r: round_half_up((r["revenue_inr"] / r["daily_target_inr"]) * 100), axis=1)
    df_clean["shortfall_inr"] = df_clean.apply(lambda r: round_half_up(r["daily_target_inr"] - r["revenue_inr"]), axis=1)
    
    def get_weekend(date_str):
        dt = pd.to_datetime(date_str)
        return "Yes" if dt.day_of_week >= 5 else "No"
        
    df_clean["weekend_flag"] = df_clean["date"].apply(get_weekend)
    
    def get_band(ach):
        if ach >= 100:
            return "Excellent"
        elif ach >= 75:
            return "Good"
        else:
            return "Poor"
            
    df_clean["performance_band"] = df_clean["achievement_pct"].apply(get_band)
    
    # Ensure numeric rounding for standard columns
    df_clean["revenue_inr"] = df_clean["revenue_inr"].apply(round_half_up)
    df_clean["daily_target_inr"] = df_clean["daily_target_inr"].apply(round_half_up)
    df_clean["marketing_spend_inr"] = df_clean["marketing_spend_inr"].apply(round_half_up)
    df_clean["stockout_hours"] = df_clean["stockout_hours"].apply(round_half_up)
    df_clean["discount_pct"] = df_clean["discount_pct"].apply(round_half_up)
    
    # Save cleaned data
    df_clean.to_csv("data/store_daily_clean.csv", index=False)
    
    # Save cleaning log
    log_df = pd.DataFrame(cleaning_logs)
    # Filter or ensure exact order/rows as required
    log_df.to_csv("analysis/cleaning_log.csv", index=False)
    
    print("Data cleaning completed successfully. Cleaned rows:", len(df_clean))

if __name__ == "__main__":
    clean_data()