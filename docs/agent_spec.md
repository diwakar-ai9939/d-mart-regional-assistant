# Agent Specification: DMart Regional Director Assistant

## 1. Pipeline Table
The agent processes every user query through an 8-step deterministic and rule-based pipeline:

| Step | Name | Type | Technique / Mechanism |
|---|---|---|---|
| 1 | Interpret | Generative (Rule-based) | Parses plain text into entities (store, metric, date, product) using regex, closed grammars, and fuzzy matching (`difflib.SequenceMatcher`). |
| 2 | Route | Deterministic | Evaluates strict intent rules in priority order to map the query to a specific handler. |
| 3 | Validate | Deterministic | Enforces schema and safety checks: validates selected columns against the 11 approved reportable metric fields and checks date boundaries (2026-04-01 to 2026-06-29). |
| 4 | Query | Deterministic | Executes parameterized SQLite queries (`?` placeholders) or optimized Python functions against cleaned data. |
| 5 | Calculate | Deterministic | Computes metrics, aggregates, and percentage achievements using integer-cent arithmetic and half-up rounding (`Decimal` with `ROUND_HALF_UP`). |
| 6 | Synthesize | Generative (Template) | Formats structured answers using fixed response templates and strict number formatting rules. |
| 7 | Ground | Deterministic | Extracts numeric values directly from fetched records/tool outputs to build `grounded_values` and verify `ungrounded_numbers == 0`. |
| 8 | Record | Deterministic | Appends a structured audit JSON log line to `logs/runs.jsonl` containing execution metadata, latency, and tokens. |

---

## 2. Intent Table
The assistant supports these 9 core intents:

| Intent | Example Question | Route |
|---|---|---|
| `lookup` | "What was Pune's revenue on 15 May 2026?" | Python function (single lookup) or SQLite SQL (range lookup) |
| `target_vs_actual` | "Did Pune hit its target on 2026-05-16?" | Python function |
| `comparison` | "Which store had the highest average revenue in May 2026?" | SQLite SQL (`GROUP BY`, `ORDER BY`) |
| `inventory` | "Which stores are below the reorder threshold for Amul Milk?" | SQLite SQL (`JOIN` / filter) |
| `feedback` | "What are customers saying about Hyderabad?" | SQLite SQL (rating average and theme grouping) |
| `weather` | "What was the weather in Pune on 2026-05-16?" | Python + Weather Tool (`tools/weather.py`) |
| `unsupported_metric` | "What was Pune's profit margin on 2026-05-15?" | None (Refused via Safe Failure) |
| `out_of_scope` | "What is the capital of India?" / "Reorder 200 units" | None (Refused via Escalated) |
| `diagnostic` | "Why is Pune's revenue so low?" | None (Refused via Escalated) |

---

## 3. Handling Rules & Status Decision Table

### Handling Rules
- **Store Matching & Typos:** Exact case-insensitive match or explicit alias (`Bangalore` $\to$ `Bengaluru`). Fuzzy matching via `SequenceMatcher` on capitalized candidate words (min 5 letters, excluding stop words and brief proper nouns) with a 0.7 confidence threshold.
- **Metric Synonyms:** Closed list (`sales`, `turnover`, `earnings` $\to$ `revenue_inr`; `target` $\to$ `daily_target_inr`; `footfall`, `visitors` $\to$ `footfall`; `stockout` $\to$ `stockout_hours`; `discount` $\to$ `discount_pct`).
- **Dates (Closed Grammar):** Accepts `YYYY-MM-DD`, `D Month YYYY`, `yesterday` (evaluated against `AS_OF_DATE = 2026-06-29`), and `between <date> and <date>`.
- **Confidence Threshold:** Minimum score across required entities. If **confidence < 0.7**, triggers `Clarification Needed`.
- **Session Context:** Carries over valid required entities (store, metric, date range, product) from previous turns in the same session. Unresolved entities or ambiguous pairs are never filled from context.

### Status Decision Table (Precedence Order)
1. **Safe Failure:** Triggered when querying an unsupported metric, an out-of-range date, or when no record matches the query.
2. **Escalated:** Triggered by out-of-scope requests, diagnostic questions, prohibited actions, or exhausting 3 retry attempts.
3. **Clarification Needed:** Triggered when confidence is < 0.7, required entities are missing, named entities fail to resolve, or ambiguous multi-store/multi-metric queries occur.
4. **Drafted:** Triggered when an operational alert fires (e.g., target achievement < 75% in the `Poor` performance band).
5. **Answered:** Default successful status when all validation, fetching, grounding, and formatting checks pass with zero ungrounded numbers.

---

## 4. Escalation and Retry Rules
- **Max Attempts:** Each data query is allowed a maximum of **3 attempts** (1 initial try plus 2 retries).
- **Failure Handling:** If all 3 attempts fail (simulated via `SIMULATE_DB_FAILURES`), the execution status immediately shifts to **`Escalated`**, and the run log records `attempts: 3`.

---

## 5. Success Criteria and Test-Case Categories
- **Success Criteria:** Observable and measurable rule compliance (e.g., every reported number must trace directly to fetched data; `ungrounded_numbers == 0` across all log entries).
- **Completion States:** `Answered`, `Drafted`, `Clarification Needed`, `Escalated`, `Safe Failure`.
- **Test-Case Categories (Part D Evaluation):** `lookup`, `target_vs_actual`, `comparison`, `inventory`, `feedback`, `weather`, `typo`, `synonym`, `ambiguity`, `unsupported_metric`, `out_of_scope`, `injection`, `out_of_range_date`, `diagnostic`, `retry`, `unresolved_store`, and `unresolved_date`.