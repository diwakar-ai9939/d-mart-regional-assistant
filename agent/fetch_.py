import sqlite3
import pandas as pd
import os
import time
from decimal import Decimal, ROUND_HALF_UP

DB_PATH = "data/dmart.db"

APPROVED_METRICS = [
    "revenue_inr", "daily_target_inr", "footfall", "stockout_hours", 
    "discount_pct", "achievement_pct", "performance_band", 
    "stock_units", "reorder_threshold", "rating", "theme"
]

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # Load CSVs
    daily_df = pd.read_csv("data/store_daily_clean.csv")
    inv_df = pd.read_csv("data/inventory.csv")
    fb_df = pd.read_csv("data/feedback.csv")
    
    daily_df.to_sql("store_daily", conn, if_exists="replace", index=False)
    inv_df.to_sql("inventory", conn, if_exists="replace", index=False)
    fb_df.to_sql("feedback", conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()

def validate_columns(columns):
    for col in columns:
        if col not in APPROVED_METRICS and col not in ["store", "store_id", "date", "product", "product_id", "*"]:
            return False
    return True

def execute_query_with_retry(query, params=(), is_sql=True):
    fail_env = os.environ.get("SIMULATE_DB_FAILURES")
    simulated_failures = int(fail_env) if fail_env else 0
    
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        attempts += 1
        if attempts <= simulated_failures:
            # Simulate failure
            if attempts == max_attempts:
                return None, attempts, "Failed after simulated errors"
            continue
            
        try:
            if not os.path.exists(DB_PATH):
                init_db()
                
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                rows = [dict(row) for row in cursor.fetchall()]
                conn.close()
                return rows, attempts, None
            else:
                conn.commit()
                conn.close()
                return [], attempts, None
        except Exception as e:
            if attempts == max_attempts:
                return None, attempts, str(e)
        finally:
            if 'conn' in locals() and conn:
                try:
                    conn.close()
                except:
                    pass
    return None, max_attempts, "Max attempts reached"

def fetch_data(intent, store, metric, date_val, product, simulate_failures=0):
    if not os.path.exists(DB_PATH):
        init_db()
        
    # Date range validation (2026-04-01 to 2026-06-29)
    if date_val and intent in ["lookup", "target_vs_actual", "comparison", "weather"]:
        if date_val < "2026-04-01" or date_val > "2026-06-29":
            return {"status": "Safe Failure", "error": "Date outside available range (2026-04-01 to 2026-06-29)"}, 0

    if intent == "lookup":
        # Check if single lookup or range
        if date_val and " to " in date_val:
            # Range lookup (average)
            start_d, end_d = date_val.split(" to ")
            query = f"SELECT AVG({metric}) as val FROM store_daily WHERE store = ? AND date BETWEEN ? AND ?"
            rows, attempts, err = execute_query_with_retry(query, (store, start_d, end_d))
            if err or not rows or rows[0]["val"] is None:
                return {"status": "Safe Failure", "error": "No record found"}, attempts
            return {"data": rows[0]["val"], "attempts": attempts}, attempts
        else:
            # Python function for single lookup
            query = f"SELECT {metric}, store, date, daily_target_inr, achievement_pct, performance_band FROM store_daily WHERE store = ? AND date = ?"
            rows, attempts, err = execute_query_with_retry(query, (store, date_val))
            if err or not rows:
                return {"status": "Safe Failure", "error": "No record found"}, attempts
            return {"data": rows[0], "attempts": attempts}, attempts

    elif intent == "target_vs_actual":
        query = "SELECT revenue_inr, daily_target_inr, achievement_pct, performance_band FROM store_daily WHERE store = ? AND date = ?"
        rows, attempts, err = execute_query_with_retry(query, (store, date_val))
        if err or not rows:
            return {"status": "Safe Failure", "error": "No record found"}, attempts
        return {"data": rows[0], "attempts": attempts}, attempts

    elif intent == "comparison":
        # SQL for comparison
        # Default date range if not given is full dataset or query range
        if not date_val:
            date_range = ("2026-04-01", "2026-06-29")
        else:
            if " to " in date_val:
                date_range = date_val.split(" to ")
            else:
                date_range = (date_val, date_val)
                
        query = f"SELECT store, AVG({metric}) as avg_val FROM store_daily WHERE date BETWEEN ? AND ? GROUP BY store ORDER BY avg_val DESC"
        rows, attempts, err = execute_query_with_retry(query, (date_range[0], date_range[1]))
        if err or not rows:
            return {"status": "Safe Failure", "error": "No record found"}, attempts
        return {"data": rows, "attempts": attempts}, attempts

    elif intent == "inventory":
        if store:
            query = "SELECT store, product, stock_units, reorder_threshold FROM inventory WHERE product = ? AND store = ? AND stock_units < reorder_threshold"
            rows, attempts, err = execute_query_with_retry(query, (product, store))
        else:
            query = "SELECT store, product, stock_units, reorder_threshold FROM inventory WHERE product = ? AND stock_units < reorder_threshold"
            rows, attempts, err = execute_query_with_retry(query, (product,))
        if err:
            return {"status": "Safe Failure", "error": "Query error"}, attempts
        return {"data": rows, "attempts": attempts}, attempts

    elif intent == "feedback":
        query = "SELECT AVG(CAST(rating AS REAL)) as avg_rating, SUM(CASE WHEN rating != '' AND rating IS NOT NULL THEN 1 ELSE 0 end) as rated_count, COUNT(*) as total_count FROM feedback WHERE store = ?"
        rows, attempts, err = execute_query_with_retry(query, (store,))
        if err or not rows:
            return {"status": "Safe Failure", "error": "No record found"}, attempts
        
        # Most frequent theme
        theme_query = "SELECT theme, COUNT(*) as cnt FROM feedback WHERE store = ? GROUP BY theme ORDER BY cnt DESC, theme ASC LIMIT 1"
        t_rows, _, _ = execute_query_with_retry(theme_query, (store,))
        top_theme = t_rows[0]["theme"] if t_rows else "N/A"
        
        res = rows[0]
        res["top_theme"] = top_theme
        return {"data": res, "attempts": attempts}, attempts

    return {"status": "Safe Failure", "error": "Unsupported intent"}, 0