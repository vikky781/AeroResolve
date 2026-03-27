"""
Mock services for alternative flight search and booking execution.
These simulate Amadeus GDS functionality for the hackathon demo.
"""

import random
import string
from datetime import datetime


def find_alternatives(flight_id: str, destination: str) -> list[dict]:
    """
    Mock alternative flight finder.
    Returns hardcoded Indian domestic flight options.
    In production, this would call Amadeus GDS or similar API.
    """
    return [
        {
            "flight": "6E-204",
            "airline": "IndiGo",
            "airline_iata": "6E",
            "departure": "14:30",
            "arrival": "17:00",
            "price": 4200,
        },
        {
            "flight": "AI-505",
            "airline": "Air India",
            "airline_iata": "AI",
            "departure": "16:00",
            "arrival": "18:30",
            "price": 3800,
        },
        {
            "flight": "SG-101",
            "airline": "SpiceJet",
            "airline_iata": "SG",
            "departure": "19:00",
            "arrival": "21:30",
            "price": 3100,
        },
    ]


def execute_booking(flight: dict, user: str) -> dict:
    """
    Mock booking execution.
    Simulates a successful rebooking and returns a confirmation.
    In production, this would call a real booking API.
    """
    confirmation_id = "CNF-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    return {
        "confirmation_id": confirmation_id,
        "status": "confirmed",
        "flight": flight.get("flight", ""),
        "airline": flight.get("airline", ""),
        "departure": flight.get("departure", ""),
        "arrival": flight.get("arrival", ""),
        "price": flight.get("price", 0),
        "passenger": user,
        "booked_at": datetime.now().isoformat(),
    }
