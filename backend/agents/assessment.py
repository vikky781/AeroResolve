"""
Assessment Agent — Agent 1 of 4
Analyzes the flight disruption and calculates its impact on the traveler.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import GROQ_API_KEY, GROQ_MODEL


def run_assessment(state: dict) -> dict:
    """
    Analyze the disruption and assess its impact.
    Updates state with assessment summary.
    """
    booking = state["booking"]
    disruption = state["disruption"]
    logs = state.get("logs", [])

    logs.append("[Assessment Agent] Starting disruption impact analysis...")

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0,
        request_timeout=30,
    )

    system_prompt = """You are the Assessment Agent in an autonomous travel recovery system.
Your job is to analyze a flight disruption and assess its impact on the traveler.

Provide a concise assessment covering:
1. Disruption severity (HIGH/MEDIUM/LOW)
2. Impact on traveler's plans
3. Urgency level for rebooking
4. Key constraints to consider

Be brief, factual, and structured. Output in plain text, not markdown."""

    human_prompt = f"""Flight Disruption Detected:
- Flight: {disruption.get('flight_iata', 'Unknown')}
- Type: {disruption.get('disruption_type', 'Unknown')}
- Original Departure: {disruption.get('original_departure', 'Unknown')}
- Reason: {disruption.get('reason', 'Unknown')}

Traveler Booking:
- Passenger: {booking.get('user', 'Unknown')}
- Route: {booking.get('route', 'Unknown')}
- Original Departure: {booking.get('departure', 'Unknown')}
- Original Arrival: {booking.get('arrival', 'Unknown')}

Analyze the impact and provide your assessment."""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])
        assessment = response.content
        logs.append(f"[Assessment Agent] Assessment complete: Disruption analyzed")
    except Exception as e:
        assessment = (
            f"ASSESSMENT (Fallback — LLM unavailable): "
            f"Flight {disruption.get('flight_iata')} {disruption.get('disruption_type')}. "
            f"Severity: HIGH. Immediate rebooking required for {booking.get('user')}. "
            f"Route: {booking.get('route')}."
        )
        logs.append(f"[Assessment Agent] LLM error, using fallback: {e}")

    return {
        **state,
        "assessment": assessment,
        "logs": logs,
    }
