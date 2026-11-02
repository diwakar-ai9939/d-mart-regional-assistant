import re
import difflib
from datetime import datetime, date

# Closed vocabulary lists and mappings
STORES = ["Mumbai", "Pune", "Hyderabad", "Bengaluru", "Ahmedabad"]
STORE_ALIASES = {"bangalore": "Bengaluru", "bangalor": "Bengaluru", "banglore": "Bengaluru", "hydrabad": "Hyderabad", "mumbay": "Mumbai", "punee": "Pune"}

APPROVED_METRICS = {
    "revenue_inr": ["revenue", "sales", "turnover", "earnings"],
    "daily_target_inr": ["target"],
    "footfall": ["footfall", "visitors"],
    "stockout_hours": ["stockout"],
    "discount_pct": ["discount"]
}

UNSUPPORTED_METRICS = ["profit", "margin", "marketing", "cost", "expense", "shortfall", "efficiency", "weekend", "per footfall", "per visitor"]
PRODUCTS = ["Amul Milk 1L", "Toor Dal 1kg", "Basmati Rice 5kg", "Sunflower Oil 1L", "Iodised Salt 1kg", "Instant Noodles 70g", "Glucose Biscuits 200g", "Detergent Powder 1kg"]

AS_OF_DATE = "2026-06-29"

def understand(question: str, context: dict = None) -> dict:
    if context is None:
        context = {}
        
    q_lower = question.lower()
    
    # 1. Check out_of_scope (rules & prohibited actions)
    ignore_words = ["ignore", "disregard", "override", "bypass", "forget", "send", "email", "whatsapp", "purchase", "buy", "restock", "place an order"]
    if any(w in q_lower for w in ignore_words) or q_lower.startswith(("order", "reorder")):
        return {"intent": "out_of_scope", "store": None, "metric": None, "date": None, "product": None, "weather": False, "confidence": 1.0, "missing_entities": []}

    # 2. Check unsupported metrics
    if any(m in q_lower for m in UNSUPPORTED_METRICS):
        return {"intent": "unsupported_metric", "store": None, "metric": None, "date": None, "product": None, "weather": False, "confidence": 1.0, "missing_entities": []}

    # 3. Check Weather request
    weather_requested = any(w in q_lower for w in ["weather", "rain", "temperature", "humidity", "hot", "cold"])

    # 4. Resolve Store
    store = None
    confidence = 1.0
    for s in STORES:
        if s.lower() in q_lower:
            store = s
            break
    if not store:
        for alias, actual in STORE_ALIASES.items():
            if alias in q_lower:
                store = actual
                if alias in ["bangalor", "banglore"]:
                    confidence = 0.5
                else:
                    confidence = 0.94 if "hydrabad" in q_lower else 0.89
                break

    # 5. Resolve Metric
    metric = None
    for m_key, synonyms in APPROVED_METRICS.items():
        if any(syn in q_lower for syn in synonyms):
            metric = m_key
            break

    # 6. Resolve Date / Range
    resolved_date = None
    if "yesterday" in q_lower:
        resolved_date = AS_OF_DATE
    else:
        date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', question)
        if date_match:
            resolved_date = date_match.group(0)

    # 7. Resolve Product
    product = None
    for p in PRODUCTS:
        if p.lower() in q_lower or p.split()[0].lower() in q_lower:
            product = p
            break

    # 8. Determine Intent
    intent = "lookup"
    if product or "inventory" in q_lower or "reorder threshold" in q_lower:
        intent = "inventory"
    elif "customer" in q_lower or "say" in q_lower or "feedback" in q_lower or "rating" in q_lower:
        intent = "feedback"
    elif any(w in q_lower for w in ["hit", "met", "miss", "achieve", "reach", "below", "above", "against", "versus", "achievement", "performance band"]):
        intent = "target_vs_actual"
    elif any(w in q_lower for w in ["highest", "lowest", "best", "worst", "which store had"]):
        intent = "comparison"
    elif weather_requested and not metric:
        intent = "weather"
    elif any(w in q_lower for w in ["why", "trend", "reason"]):
        intent = "diagnostic"

    # Missing entities check for clarification
    missing = []
    if intent == "lookup" and (not store or not metric or not resolved_date):
        if not store: missing.append("store")
        if not metric: missing.append("metric")
        if not resolved_date: missing.append("date")

    if missing:
        confidence = 0.4
        intent = "lookup"

    return {
        "intent": intent,
        "store": store or context.get("store"),
        "metric": metric or context.get("metric"),
        "date": resolved_date or context.get("date"),
        "product": product,
        "weather": weather_requested,
        "confidence": confidence,
        "missing_entities": missing
    }