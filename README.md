# DMart Regional Director Assistant: Store Diagnosis & Conversational Analytics Agent

An enterprise-grade, rule-based conversational analytics agent built for Kavita Rao (Regional Operations Director, DMart) to diagnose store performance, analyze inventory and feedback, and answer routine questions with 100% grounded data traceability.

## Repository Layout
```text
README.md
.gitignore
requirements.txt
data/        store_daily.csv, inventory.csv, feedback.csv, store_daily_clean.csv
scripts/     generate_data.py, clean_data.py, analyze.py, run_acceptance.py
analysis/    data_quality_report.md, cleaning_log.csv, findings.md, executive_summary.md
docs/        requirement.md, data_context.md, agent_spec.md, release_gate.md
agent/       understand.py, fetch.py, answer.py, run_agent.py
tools/       weather.py
tests/       weather_tool_tests.md
outputs/     acceptance_transcript.md
logs/        runs.jsonl
eval/        golden_set.csv, golden_set_derivation.md, run_eval.py, eval_results.csv, eval_runs.jsonl, eval_summary.md