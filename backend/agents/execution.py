"""
Execution Agent — Agent 4 of 4
Books the best flight option and triggers SMS notification.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import GROQ_API_KEY, GROQ_MODEL
from mock_services import execute_booking
from notifications import send_sms


def run_execution(state: dict) -> dict:
    """
    Execute the rebooking and send notification.
    Updates state with confirmation and SMS status.
    """
    booking = state["booking"]
    selected_flight = state.get("selected_flight", {})
    policy_approved = state.get("policy_approved", False)
    logs = state.get("logs", [])

    # Guard: no flight selected or policy rejected
    if not selected_flight or not policy_approved:
        logs.append("[Execution Agent] No valid flight to book — pipeline ending without rebooking")
        return {
            **state,
            "booking_confirmation": {},
            "sms_status": "not_sent",
            "logs": logs,
        }

    logs.append(f"[Execution Agent] Booking flight {selected_flight.get('flight', '')}...")

    # Execute mock booking
    confirmation = execute_booking(selected_flight, booking.get("user", "Traveler"))

    logs.append(
        f"[Execution Agent] Booking confirmed! ID: {confirmation.get('confirmation_id', 'N/A')} "
        f"| Flight: {confirmation.get('flight', '')} "
        f"| Departure: {confirmation.get('departure', '')} "
        f"| Price: ₹{confirmation.get('price', 0)}"
    )

    # Send real SMS via Twilio
    logs.append("[Execution Agent] Sending SMS notification via Twilio...")
    sms_result = send_sms(booking, selected_flight, confirmation)
    sms_status = sms_result.get("status", "failed")

    if sms_status == "sent":
        logs.append(f"[Execution Agent] ✅ SMS sent successfully to {sms_result.get('to', 'recipient')}")
    else:
        logs.append(f"[Execution Agent] ❌ SMS failed: {sms_result.get('error', 'Unknown error')}")

    # LLM summary of the whole operation
    try:
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
            temperature=0,
            request_timeout=30,
        )
        summary_prompt = f"""Summarize this completed travel recovery operation in 2-3 sentences:
- Original flight {booking.get('flight_iata')} was {state.get('disruption', {}).get('disruption_type', 'disrupted')}
- Rebooked to {selected_flight.get('flight')} ({selected_flight.get('airline')})
- New departure: {selected_flight.get('departure')}, arrival: {selected_flight.get('arrival')}
- Cost: ₹{selected_flight.get('price')}
- SMS notification: {sms_status}
Be concise and positive."""

        response = llm.invoke([
            SystemMessage(content="You are a travel recovery AI. Summarize operations briefly."),
            HumanMessage(content=summary_prompt),
        ])
        logs.append(f"[Execution Agent] Summary: {response.content}")
    except Exception:
        logs.append(
            f"[Execution Agent] Recovery complete: "
            f"{booking.get('flight_iata')} → {selected_flight.get('flight')}"
        )

    logs.append("[Pipeline] ✅ All agents completed — recovery successful!")

    return {
        **state,
        "booking_confirmation": confirmation,
        "sms_status": sms_status,
        "logs": logs,
    }
