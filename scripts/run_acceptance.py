import os
import json
from agent.run_agent import handle

CASES = [
    {"id": "A01", "session": "s1", "question": "What was Pune's revenue on 15 May 2026?", "sim_fail": 0},
    {"id": "A02", "session": "s1", "question": "And the target?", "sim_fail": 0},
    {"id": "A03", "session": "s1", "question": "How about Mumbai?", "sim_fail": 0},
    {"id": "A04", "session": "s2", "question": "How is Hyderabad doing?", "sim_fail": 0},
    {"id": "A05", "session": "s2", "question": "revenue on 2026-05-15", "sim_fail": 0},
    {"id": "A06", "session": "s3", "question": "What was Hydrabad's turnover yesterday?", "sim_fail": 0},
    {"id": "A07", "session": "s4", "question": "Did Pune hit its target on 2026-05-16?", "sim_fail": 0},
    {"id": "A08", "session": "s4", "question": "Did Pune hit its target on 2026-05-20?", "sim_fail": 0},
    {"id": "A09", "session": "s4", "question": "Did Mumbai hit its target on 2026-05-21?", "sim_fail": 0},
    {"id": "A10", "session": "s5", "question": "Which store had the highest average revenue between 2026-05-01 and 2026-05-31?", "sim_fail": 0},
    {"id": "A11", "session": "s5", "question": "Which store had the lowest revenue on 2026-06-10?", "sim_fail": 0},
    {"id": "A12", "session": "s6", "question": "Which stores are below the reorder threshold for Amul Milk?", "sim_fail": 0},
    {"id": "A13", "session": "s6", "question": "What are customers saying about Hyderabad?", "sim_fail": 0},
    {"id": "A14", "session": "s7", "question": "What was Pune's profit margin on 2026-05-15?", "sim_fail": 0},
    {"id": "A15", "session": "s8", "question": "What is the capital of India?", "sim_fail": 0},
    {"id": "A16", "session": "s9", "question": "What was Mumbai's revenue on 2026-07-15?", "sim_fail": 0},
    {"id": "A17", "session": "s10", "question": "Why is Pune's revenue so low?", "sim_fail": 0},
    {"id": "A18", "session": "s11", "question": "What was Kolkata's revenue on 2026-05-15?", "sim_fail": 0},
    {"id": "A19", "session": "s12", "question": "What was Pune's revenue on 15 May 2026?", "sim_fail": 2},
    {"id": "A20", "session": "s13", "question": "What was Pune's revenue on 15 May 2026?", "sim_fail": 3},
]

def run_acceptance():
    log_path = "logs/runs.jsonl"
    os.makedirs("logs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    # Empty logs/runs.jsonl first
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("")
        
    os.environ["AGENT_LOG_PATH"] = log_path
    
    transcript_lines = ["# Acceptance Test Transcript\n"]
    
    for case in CASES:
        c_id = case["id"]
        s_id = case["session"]
        q = case["question"]
        sim = case["sim_fail"]
        
        if sim > 0:
            os.environ["SIMULATE_DB_FAILURES"] = str(sim)
        else:
            if "SIMULATE_DB_FAILURES" in os.environ:
                del os.environ["SIMULATE_DB_FAILURES"]
                
        res = handle(q, session_id=s_id)
        
        status = res.get("status")
        intent = res.get("intent")
        conf = res.get("confidence")
        route = res.get("route")
        attempts = res.get("attempts")
        ans = res.get("answer_text")
        
        transcript_lines.append(f"## Case {c_id} (Session: {s_id})")
    
        transcript_lines.append(f"- **Question:** {q}")
        transcript_lines.append(f"- **Status:** {status}")
        transcript_lines.append(f"- **Intent:** {intent}")
        transcript_lines.append(f"- **Confidence:** {conf}")
        transcript_lines.append(f"- **Route:** {route}")
        transcript_lines.append(f"- **Attempts:** {attempts}")
        transcript_lines.append(f"- **Answer:** {ans}\n")
        
    with open("outputs/acceptance_transcript.md", "W", encoding="utf-8") as f:
        f.write("\n".join(transcript_lines))
        
    print("Acceptance tests completed successfully! Transcript written to outputs/acceptance_transcript.md and logs/runs.jsonl updated.")

if __name__ == "__main__":
    run_acceptance()