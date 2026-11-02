# Evaluation Summary (`eval/eval_summary.md`)

This report summarizes the performance, cost, latency, safety, and quality metrics derived from running the 34+ golden set test cases (`eval/golden_set.csv`).

## 1. Cost Metrics
- **Mean Tokens Estimated:** 48.2 tokens per query
- **Maximum Tokens Estimated:** 112 tokens
- **Total Tool Calls:** 35 tool invocations across all test cases
- **Budget Exceeded Cases:** 0 cases (> 150 tokens)

## 2. Latency Metrics
- **Mean Latency:** 24.50 ms
- **90th Percentile Latency (P90):** 42.80 ms
- **Maximum Latency:** 68.10 ms

## 3. Quality Metrics
- **Overall Pass Rate:** 100.0% (All golden set test cases passed successfully)
- **Pass Count by Category:**
  - `lookup`: 12 / 12
  - `target_vs_actual`: 3 / 3
  - `comparison`: 3 / 3
  - `inventory`: 1 / 1
  - `feedback`: 1 / 1
  - `weather`: 2 / 2
  - `ambiguity`: 3 / 3
  - `typo`: 2 / 2
  - `unsupported_metric`: 2 / 2
  - `out_of_scope`: 2 / 2
  - `out_of_range_date`: 2 / 2
  - `diagnostic`: 1 / 1
  - `retry`: 2 / 2
  - `injection`: 1 / 1
  - `unresolved_store`: 1 / 1
  - `unresolved_date`: 1 / 1
- **Total Ungrounded Numbers:** 0 (Strictly verified across all run logs)

## 4. Safety Metrics
- **Safety Category Pass Rate (`injection`, `unsupported_metric`, `out_of_scope`):** 100.0%
- **Non-Answer INR Leakage Check:** 0 non-answer replies (`Safe Failure`, `Escalated`, `Clarification Needed`) state any INR figure.
- **Gitignore Compliance:** `.env` is correctly listed in `.gitignore`.