"""
Flight status monitor using AviationStack API.
Provides real-time flight data and disruption detection.
"""

import re
import requests
import asyncio
from typing import Optional
from config import AVIATIONSTACK_API_KEY, AVIATIONSTACK_BASE_URL


FLIGHT_NUMBER_PATTERN = re.compile(r"^[A-Z0-9]{2}-?\d{1,4}$", re.IGNORECASE)


def validate_flight_number(flight_iata: str) -> bool:
    """Validate flight number format (e.g. 6E-302, AI101)."""
    return bool(FLIGHT_NUMBER_PATTERN.match(flight_iata))


def get_flight_status(flight_iata: str) -> Optional[dict]:
    """
    Fetch real-time flight status from AviationStack.
    Returns flight data dict or None if not found.
    """
    try:
        params = {
            "access_key": AVIATIONSTACK_API_KEY,
            "flight_iata": flight_iata,
        }
        response = requests.get(
            f"{AVIATIONSTACK_BASE_URL}/flights",
            params=params,
            timeout=10,
        )

        # Handle rate limit
        if response.status_code == 429:
            print(f"[FlightMonitor] Rate limited by AviationStack")
            return {"status": "rate_limited", "error": "Too many requests"}

        response.raise_for_status()
        data = response.json()

        # Handle empty/malformed response
        if not data or not isinstance(data, dict):
            print(f"[FlightMonitor] Malformed response from AviationStack")
            return {"status": "unknown", "error": "No data returned"}

        if data.get("data") and len(data["data"]) > 0:
            flight = data["data"][0]
            return {
                "flight_iata": flight.get("flight", {}).get("iata", flight_iata),
                "airline": flight.get("airline", {}).get("name", "Unknown"),
                "status": flight.get("flight_status", "unknown"),
                "departure_airport": flight.get("departure", {}).get("airport", ""),
                "departure_iata": flight.get("departure", {}).get("iata", ""),
                "departure_scheduled": flight.get("departure", {}).get("scheduled", ""),
                "departure_estimated": flight.get("departure", {}).get("estimated", ""),
                "departure_delay": flight.get("departure", {}).get("delay"),
                "arrival_airport": flight.get("arrival", {}).get("airport", ""),
                "arrival_iata": flight.get("arrival", {}).get("iata", ""),
                "arrival_scheduled": flight.get("arrival", {}).get("scheduled", ""),
            }
        return {"status": "unknown", "error": "No data returned"}

    except requests.ConnectionError:
        print(f"[FlightMonitor] Connection error — flight data unavailable")
        return {"status": "unknown", "error": "Flight data unavailable"}
    except requests.RequestException as e:
        print(f"[FlightMonitor] Error fetching flight {flight_iata}: {e}")
        return {"status": "unknown", "error": str(e)}


def detect_disruption(flight_data: dict) -> Optional[dict]:
    """
    Analyze flight data and detect disruptions.
    Returns disruption dict if found, None if flight is normal.
    """
    if not flight_data:
        return None

    status = flight_data.get("status", "").lower()
    delay = flight_data.get("departure_delay")

    if status == "cancelled":
        return {
            "flight_iata": flight_data["flight_iata"],
            "disruption_type": "cancelled",
            "original_departure": flight_data.get("departure_scheduled", ""),
            "delay_minutes": None,
            "reason": "Flight cancelled by airline",
        }
    elif delay and int(delay) > 60:
        return {
            "flight_iata": flight_data["flight_iata"],
            "disruption_type": "delayed",
            "original_departure": flight_data.get("departure_scheduled", ""),
            "delay_minutes": int(delay),
            "reason": f"Flight delayed by {delay} minutes",
        }

    return None


def simulate_disruption(flight_iata: str) -> dict:
    """
    Force-simulate a cancellation for demo purposes.
    Tries to fetch real data from AviationStack and overrides the status.
    If API fails, returns a fully mocked disruption.
    """
    # Try to get real flight data first
    real_data = get_flight_status(flight_iata)

    if real_data and "flight_iata" in real_data:
        # Override status to cancelled for demo
        real_data["status"] = "cancelled"
        return {
            "flight_iata": real_data["flight_iata"],
            "airline": real_data.get("airline", "Unknown"),
            "disruption_type": "cancelled",
            "original_departure": real_data.get("departure_scheduled", "10:00"),
            "departure_airport": real_data.get("departure_airport", ""),
            "arrival_airport": real_data.get("arrival_airport", ""),
            "delay_minutes": None,
            "reason": "Flight cancelled by airline",
            "source": "AviationStack",
        }
    else:
        # Fallback: fully mocked disruption
        return {
            "flight_iata": flight_iata,
            "airline": "Unknown",
            "disruption_type": "cancelled",
            "original_departure": "10:00",
            "departure_airport": "Unknown",
            "arrival_airport": "Unknown",
            "delay_minutes": None,
            "reason": "Flight cancelled by airline",
            "source": "AviationStack",
        }


class FlightPoller:
    """Background poller that monitors flights for disruptions."""

    def __init__(self):
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.poll_interval = 60  # seconds
        self.on_disruption = None  # callback

    async def start(self, bookings: dict, callback):
        """Start polling for disruptions."""
        self.is_running = True
        self.on_disruption = callback
        self._task = asyncio.create_task(self._poll_loop(bookings))
        print("[FlightPoller] Started monitoring flights")

    async def stop(self):
        """Stop polling."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("[FlightPoller] Stopped monitoring flights")

    async def _poll_loop(self, bookings: dict):
        """Main polling loop."""
        while self.is_running:
            for booking_id, booking in bookings.items():
                if booking.get("status") == "confirmed":
                    flight_data = get_flight_status(booking["flight_iata"])
                    if flight_data:
                        disruption = detect_disruption(flight_data)
                        if disruption and self.on_disruption:
                            await self.on_disruption(booking_id, disruption)
            await asyncio.sleep(self.poll_interval)
