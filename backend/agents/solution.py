"""
Solution Agent — Agent 3 of 4
Searches for alternative flights, scores them, and recommends the best option.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import (
    GROQ_API_KEY, GROQ_MODEL,
    PRICE_WEIGHT, TIME_WEIGHT, AIRLINE_WEIGHT,
)
from mock_services import find_alternatives


def _score_alternatives(alternatives: list, constraints: dict, original_airline: str) -> list:
    """
    Score alternatives using weighted formula:
    score = (0.4 * price_score) + (0.3 * time_score) + (0.3 * airline_preference)
    """
    if not alternatives:
        return []

    # Normalize prices (lower is better)
    prices = [a["price"] for a in alternatives]
    max_price = max(prices)
    min_price = min(prices)
    price_range = max_price - min_price if max_price != min_price else 1

    # Normalize departure times (earlier is better)
    def time_to_minutes(t: str) -> int:
        parts = t.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    times = [time_to_minutes(a["departure"]) for a in alternatives]
    max_time = max(times)
    min_time = min(times)
    time_range = max_time - min_time if max_time != min_time else 1

    scored = []
    max_cost = constraints.get("max_cost", 6000)

    for i, alt in enumerate(alternatives):
        # Skip if over budget
        if alt["price"] > max_cost:
            alt["score"] = 0
            alt["rejected"] = True
            alt["reject_reason"] = f"Over budget (₹{alt['price']} > ₹{max_cost})"
            scored.append(alt)
            continue

        # Price score (lower price = higher score)
        price_score = 1 - ((alt["price"] - min_price) / price_range)

        # Time score (earlier departure = higher score)
        time_score = 1 - ((times[i] - min_time) / time_range)

        # Airline preference score
        airline_score = 1.0 if alt.get("airline_iata", "") == original_airline else 0.3

        # Weighted total
        total_score = (
            PRICE_WEIGHT * price_score
            + TIME_WEIGHT * time_score
            + AIRLINE_WEIGHT * airline_score
        )

        alt["score"] = round(total_score, 3)
        alt["rejected"] = False
        scored.append(alt)

    # Sort by score descending
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored


def run_solution(state: dict) -> dict:
    """
    Find and rank alternative flights.
    Updates state with alternatives and recommendation.
    """
    booking = state["booking"]
    policy_approved = state["policy_approved"]
    policy_constraints = state.get("policy_constraints", {})
    logs = state.get("logs", [])

    if not policy_approved:
        logs.append("[Solution Agent] Policy REJECTED — skipping alternative search")
        return {
            **state,
            "alternatives": [],
            "ranked_alternatives": [],
            "selected_flight": {},
            "logs": logs,
        }

    logs.append("[Solution Agent] Searching for alternative flights...")

    # Get mock alternatives
    alternatives = find_alternatives(
        booking.get("flight_iata", ""),
        booking.get("destination", ""),
    )

    logs.append(f"[Solution Agent] Found {len(alternatives)} alternatives")

    # Score them
    original_airline = booking.get("airline_iata", "")
    ranked = _score_alternatives(alternatives, policy_constraints, original_airline)

    # Filter out rejected
    valid = [a for a in ranked if not a.get("rejected", False)]
    rejected = [a for a in ranked if a.get("rejected", False)]

    if rejected:
        for r in rejected:
            logs.append(f"[Solution Agent] Rejected {r['flight']}: {r.get('reject_reason', 'Policy violation')}")

    # Use LLM to explain the recommendation
    if valid:
        selected = valid[0]

        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
            temperature=0,
            request_timeout=30,
        )

        try:
            explanation_prompt = f"""You recommended flight {selected['flight']} ({selected['airline']}) 
departing at {selected['departure']}, arriving {selected['arrival']}, price ₹{selected['price']}, 
score {selected['score']}.

Other options were:
{chr(10).join([f"- {a['flight']} ({a['airline']}): ₹{a['price']}, dep {a['departure']}, score {a['score']}" for a in valid[1:]])}

Explain in 2 sentences why this is the best choice considering price, timing, and airline preference."""

            response = llm.invoke([
                SystemMessage(content="You are a travel AI assistant. Be concise."),
                HumanMessage(content=explanation_prompt),
            ])
            logs.append(f"[Solution Agent] Recommendation: {selected['flight']} — {response.content}")
        except Exception:
            logs.append(f"[Solution Agent] Selected: {selected['flight']} (score: {selected['score']})")
    else:
        selected = {}
        logs.append("[Solution Agent] No valid alternatives found within policy constraints")

    return {
        **state,
        "alternatives": alternatives,
        "ranked_alternatives": ranked,
        "selected_flight": selected,
        "logs": logs,
    }
