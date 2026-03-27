"""
Policy Agent — Agent 2 of 4
Validates rebooking against policy rules and constraints.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import (
    GROQ_API_KEY, GROQ_MODEL,
    MAX_REBOOKING_COST, SAME_DAY_ONLY, PREFER_SAME_AIRLINE,
)


def run_policy(state: dict) -> dict:
    """
    Validate the rebooking against travel policy rules.
    Updates state with approval status and constraints.
    """
    booking = state["booking"]
    assessment = state["assessment"]
    logs = state.get("logs", [])

    logs.append("[Policy Agent] Checking travel policy and rebooking rules...")

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0,
        request_timeout=30,
    )

    system_prompt = f"""You are the Policy Agent in an autonomous travel recovery system.
Your job is to validate whether rebooking is allowed under the travel policy.

Travel Policy Rules:
1. Maximum rebooking cost: ₹{MAX_REBOOKING_COST}
2. Same-day rebooking only: {"Yes" if SAME_DAY_ONLY else "No"}
3. Prefer same airline: {"Yes" if PREFER_SAME_AIRLINE else "No"}
4. Departure must be in the future (after the current time)

Based on the assessment, determine:
1. Whether rebooking is APPROVED or REJECTED
2. The specific constraints to apply when searching for alternatives

Respond in this exact format:
DECISION: APPROVED or REJECTED
MAX_COST: [number]
SAME_DAY: YES or NO
PREFER_AIRLINE: [airline code or NONE]
REASON: [brief explanation]"""

    human_prompt = f"""Assessment Report:
{assessment}

Original Booking:
- Passenger: {booking.get('user', 'Unknown')}
- Airline: {booking.get('airline', 'Unknown')} ({booking.get('airline_iata', '')})
- Route: {booking.get('route', 'Unknown')}
- Date: {booking.get('date', 'Unknown')}

Validate this rebooking request against the travel policy."""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])

        policy_response = response.content
        policy_approved = "APPROVED" in policy_response.upper()

        policy_constraints = {
            "max_cost": MAX_REBOOKING_COST,
            "same_day": SAME_DAY_ONLY,
            "preferred_airline": booking.get("airline_iata", ""),
            "policy_response": policy_response,
        }

        logs.append(
            f"[Policy Agent] Decision: {'APPROVED' if policy_approved else 'REJECTED'} "
            f"| Max cost: ₹{MAX_REBOOKING_COST} | Prefer: {booking.get('airline_iata', 'Any')}"
        )

    except Exception as e:
        # Fallback: approve with default constraints
        policy_approved = True
        policy_constraints = {
            "max_cost": MAX_REBOOKING_COST,
            "same_day": SAME_DAY_ONLY,
            "preferred_airline": booking.get("airline_iata", ""),
            "policy_response": "Auto-approved (LLM unavailable)",
        }
        logs.append(f"[Policy Agent] LLM error, auto-approving with defaults: {e}")

    return {
        **state,
        "policy_approved": policy_approved,
        "policy_constraints": policy_constraints,
        "logs": logs,
    }
