import os
import csv
import json
from agent.run_agent import handle

def run_evaluation():
    golden_path = "eval/golden_set.csv"
    results_path = "eval/eval_results.csv"
    eval_log_path = "eval/eval_runs.jsonl"
    
    os.makedirs("eval", eval_ok=True) if hasattr(os, "eval_ok") else os.makedirs("eval", exist_ok=True)
    
    # Empty eval_runs.jsonl first
    with open(eval_log_path, "w", encoding="utf-8") as f:
        f.write("")
        
    os.environ["AGENT_LOG_PATH"] = eval_log_path
    os.environ["WEATHER_MODE"] = "stub"
    
    if not os.path.exists(golden_path):
        print(f"Error: {golden_path} not found.")
        return
        
    results = []
    
    with open(golden_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row["case_id"]
            category = row["category"]
            session_id = row["session_id"]
            question = row["question"]
            sim_fail = int(row["simulate_failures"]) if row["simulate_failures"] else 0
            exp_status = row["expected_status"]
            exp_intent = row["expected_intent"]
            exp_contains = row["expected_contains"].split("|") if row["expected_contains"] else []
            
            if sim_fail > 0:
                os.environ["SIMULATE_DB_FAILURES"] = str(sim_fail)
            else:
                if "SIMULATE_DB_FAILURES" in os.environ:
                    del os.environ["SIMULATE_DB_FAILURES"]
                    
            res = handle(question, session_id=session_id)
            
            act_status = res.get("status")
            act_intent = res.get("intent")
            ans_text = res.get("answer_text", "")
            latency = res.get("latency_ms", 0.0)
            tokens = res.get("tokens_est", 0)
            tool_calls = res.get("tool_calls", 0)
            ungrounded = res.get("ungrounded_numbers", 0)
            budget_ex = res.get("budget_exceeded", False)
            
            intent_match = (act_intent == exp_intent)
            status_match = (act_status == exp_status)
            
            # Check contains substrings
            contains_match = True
            for sub in exp_contains:
                sub = sub.strip()
                if sub and sub not in ans_text:
                    contains_match = False
                    break
                    
            passed = status_match and intent_match and contains_match
            
            results.append({
                "case_id": case_id,
                "category": category,
                "expected_status": exp_status,
                "actual_status": act_status,
                "intent_match": intent_match,
                "contains_match": contains_match,
                "latency_ms": latency,
                "tokens_est": tokens,
                "tool_calls": tool_calls,
                "ungrounded_numbers": ungrounded,
                "budget_exceeded": budget_exceeded,
                "passed": passed
            })
            
    # Write eval_results.csv
    fieldnames = [
        "case_id", "category", "expected_status", "actual_status", 
        "intent_match", "contains_match", "latency_ms", "tokens_est", 
        "tool_calls", "ungrounded_numbers", "budget_exceeded", "passed"
    ]
    
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Evaluation completed successfully! Results written to {results_path} and logs in {eval_log_path}.")

if __name__ == "__main__":
    run_evaluation()