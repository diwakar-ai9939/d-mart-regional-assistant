import os
import json
import time
import uuid
from datetime import datetime

from agent.understand import understand
from agent.fetch import fetch_data
from agent.answer import build_answer

def handle(question: str, session_id: str, user_id: str = "u1") -> dict:
    start_time = time.perf_counter()
    run_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Read log path from env, default to logs/runs.jsonl
    log_path = os.environ.get("AGENT_LOG_PATH", "logs/runs.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Context management (simple session store simulation or passed context)
    # For acceptance tests, session continuity can be managed via a global or module-level store if needed, 
    # but here we rely on the understand and fetch calls.
    
    # 1. Understand
    understand_res = understand(question)
    intent = understand_res.get("intent")
    confidence = understand_res.get("confidence", 1.0)
    store = understand_res.get("store")
    metric = understand_res.get("metric")
    date_val = understand_res.get("date")
    product = understand_res.get("product")
    weather_requested = understand_res.get("weather", False)
    
    # Determine Route & Executed SQL/Function
    route = "none"
    executed = None
    tools_called = []
    tool_calls = 0
    attempts = 0
    
    fetch_result = None
    
    # Check if rejected before query
    rejected_statuses = ["Safe Failure", "Escalated", "Clarification Needed"]
    
    # Pre-check for immediate rejection intents
    if intent in ["unsupported_metric", "out_of_scope", "diagnostic"]:
        answer_dict = build_answer(intent, None, understand_res, attempts=0)
    elif confidence < 0.7 or understand_res.get("missing_entities"):
        answer_dict = build_answer(intent, None, understand_res, attempts=0)
    else:
        # Determine route type
        if intent in ["lookup", "target_vs_actual"]:
            route = "python"
        elif intent in ["comparison", "inventory", "feedback"]:
            route = "sql"
            
        if weather_requested and intent in ["lookup", "target_vs_actual"]:
            route = "python+weather"
            tools_called.append("weather_tool")
            tool_calls += 1
            
        # Fetch data
        fetch_result, attempts = fetch_data(intent, store, metric, date_val, product)
        
        # Build answer
        answer_dict = build_answer(intent, fetch_result, understand_res, attempts=attempts)

    status = answer_dict.get("status")
    answer_text = answer_dict.get("answer_text")
    evidence = answer_dict.get("evidence", [])
    grounded_values = answer_dict.get("grounded_values", [])
    ungrounded_numbers = answer_dict.get("ungrounded_numbers", 0)
    
    if route != "none" and status not in ["Clarification Needed", "Safe Failure", "Escalated"]:
        tool_calls += 1 # 1 for data route (python or sql)
    elif route != "none" and attempts > 0:
        tool_calls += 1

    end_time = time.perf_counter()
    latency_ms = round((end_time - start_time) * 1000, 2)
    
    # Token estimation: whitespace-separated words in question + answer
    tokens_est = len(question.split()) + len(answer_text.split())
    budget_exceeded = tokens_est > 150
    
    run_record = {
        "run_id": run_id,
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": timestamp,
        "question": question,
        "intent": intent,
        "confidence": confidence,
        "route": route,
        "executed": executed,
        "attempts": attempts,
        "tools_called": tools_called,
        "status": status,
        "answer_text": answer_text,
        "evidence": evidence,
        "grounded_values": grounded_values,
        "latency_ms": latency_ms,
        "tokens_est": tokens_est,
        "tool_calls": tool_calls,
        "ungrounded_numbers": ungrounded_numbers,
        "budget_exceeded": budget_exceeded
    }
    
    # Append to runs.jsonl
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(run_record) + "\n")
        
    return run_record