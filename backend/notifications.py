"""
Twilio SMS notification service.
Sends real SMS messages to the traveler with rebooking details.
"""

from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    RECIPIENT_PHONE_NUMBER,
)


def send_sms(booking: dict, selected_flight: dict, confirmation: dict) -> dict:
    """
    Send an SMS notification with rebooking details via Twilio.
    Returns status dict with delivery info.
    """
    message_body = (
        f"AeroResolve: Flt {booking.get('flight_iata', '')} cancelled. "
        f"Rebooked on {selected_flight.get('flight', '')} "
        f"@ {selected_flight.get('departure', '')}. "
        f"Conf: {confirmation.get('confirmation_id', 'N/A')}"
    )

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=RECIPIENT_PHONE_NUMBER,
        )
        return {
            "status": "sent",
            "sid": message.sid,
            "to": RECIPIENT_PHONE_NUMBER,
            "body_preview": message_body[:100] + "...",
        }
    except Exception as e:
        print(f"[Notification] SMS send failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "to": RECIPIENT_PHONE_NUMBER,
        }
