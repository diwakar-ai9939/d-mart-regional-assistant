# Weather Tool Test Cases (`tests/weather_tool_tests.md`)

This document records the tool-level test cases and verified outputs for `tools/weather.py` running under stub mode (`WEATHER_MODE=stub`).

## Test Case 1: Mumbai Check Value
- **City:** Mumbai
- **Date:** 2026-05-15
- **Mode:** stub
- **Expected Output:** `temperature_c: 26.0`, `humidity_pct: 43.0`, `wind_kmh: 10.0`, `rain_mm: 0.0`
- **Result:** PASSED

## Test Case 2: Pune Check Value
- **City:** Pune
- **Date:** 2026-05-16
- **Mode:** stub
- **Expected Output:** `temperature_c: 25.0`, `humidity_pct: 88.0`, `wind_kmh: 11.0`, `rain_mm: 6.5`
- **Result:** PASSED

## Test Case 3: Hyderabad Check Value
- **City:** Hyderabad
- **Date:** 2026-04-01
- **Mode:** stub
- **Expected Output:** `temperature_c: 30.0`, `humidity_pct: 58.0`, `wind_kmh: 6.0`, `rain_mm: 0.0`
- **Result:** PASSED

## Test Case 4: Unsupported City Error Handling
- **City:** Kolkata (Unsupported)
- **Date:** 2026-05-15
- **Expected Output:** `{"ok": false, "error": "unsupported city: Kolkata"}`
- **Result:** PASSED (No exception raised)

## Test Case 5: Bad Date Format Error Handling
- **City:** Bengaluru
- **Date:** 15 May 2026 (Invalid ISO format)
- **Expected Output:** `{"ok": false, "error": "invalid date format: 15 May 2026"}`
- **Result:** PASSED (No exception raised)

## Test Case 6: Invalid Calendar Date Error Handling
- **City:** Ahmedabad
- **Date:** 2026-02-30 (Non-existent calendar date)
- **Expected Output:** `{"ok": false, "error": "invalid calendar date: 2026-02-30"}`
- **Result:** PASSED (No exception raised)