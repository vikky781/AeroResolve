"""
AeroResolve — FastAPI Application
Autonomous AI Agent for Managing Travel Disruption
"""

import os
import copy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load env FIRST
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Startup validation — fail fast if keys are missing
REQUIRED_VARS = [
    "GROQ_API_KEY",
    "AVIATIONSTACK_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_PHONE_NUMBER",
    "RECIPIENT_PHONE_NUMBER",
]
_missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
if _missing:
    raise RuntimeError(
        f"Missing required environment variable(s): {', '.join(_missing)}. "
        f"Fill them in .env before starting the server."
    )

from config import BOOKINGS, RECIPIENT_PHONE_NUMBER, INITIAL_BOOKINGS
from flight_monitor import simulate_disruption, validate_flight_number, FlightPoller
from graph import run_pipeline


app = FastAPI(
    title="AeroResolve API",
    description="Zero-Touch Agentic Travel Recovery System",
    version="1.0.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
pipeline_status = {
    "is_running": False,
    "current_agent": None,
    "logs": [],
    "last_result": None,
}
flight_poller = FlightPoller()


# --- Request Models ---

class SimulateRequest(BaseModel):
    booking_id: Optional[str] = "BK001"


# --- Routes ---

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "service": "AeroResolve",
        "status": "running",
        "tagline": "Zero-Touch Agentic Travel Recovery",
    }


@app.get("/bookings")
def list_bookings():
    """List all monitored bookings."""
    bookings_list = []
    for booking_id, booking in BOOKINGS.items():
        b = copy.deepcopy(booking)
        b["booking_id"] = booking_id
        bookings_list.append(b)
    return {"bookings": bookings_list}


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):
    """Get a specific booking."""
    if booking_id not in BOOKINGS:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    booking = copy.deepcopy(BOOKINGS[booking_id])
    booking["booking_id"] = booking_id
    return booking


@app.post("/simulate-disruption")
def trigger_disruption(request: SimulateRequest):
    """
    Manually trigger a flight disruption and run the full recovery pipeline.
    This is the main demo endpoint.
    """
    global pipeline_status

    booking_id = request.booking_id
    if booking_id not in BOOKINGS:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")

    if pipeline_status["is_running"]:
        raise HTTPException(status_code=409, detail="Pipeline is already running")

    booking = copy.deepcopy(BOOKINGS[booking_id])

    # Validate flight number format (Audit #3)
    if not validate_flight_number(booking.get("flight_iata", "")):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid flight number format: {booking.get('flight_iata')}"
        )

    booking["phone"] = RECIPIENT_PHONE_NUMBER

    # Simulate disruption
    pipeline_status["is_running"] = True
    pipeline_status["current_agent"] = "starting"
    pipeline_status["logs"] = []

    # Run the full pipeline
    try:
        disruption = simulate_disruption(booking["flight_iata"])
        result = run_pipeline(booking, disruption)

        pipeline_status["is_running"] = False
        pipeline_status["current_agent"] = "completed"
        pipeline_status["logs"] = result.get("logs", [])
        pipeline_status["last_result"] = {
            "booking_id": booking_id,
            "disruption": disruption,
            "assessment": result.get("assessment", ""),
            "policy_approved": result.get("policy_approved", False),
            "policy_constraints": result.get("policy_constraints", {}),
            "alternatives": result.get("alternatives", []),
            "ranked_alternatives": result.get("ranked_alternatives", []),
            "selected_flight": result.get("selected_flight", {}),
            "booking_confirmation": result.get("booking_confirmation", {}),
            "sms_status": result.get("sms_status", "not_sent"),
        }

        # Update booking status
        BOOKINGS[booking_id]["status"] = "rebooked"

        return {
            "status": "success",
            "message": "Recovery pipeline completed",
            "result": pipeline_status["last_result"],
            "logs": pipeline_status["logs"],
        }

    except Exception as e:
        pipeline_status["is_running"] = False
        pipeline_status["current_agent"] = "error"
        pipeline_status["logs"].append(f"[Pipeline] ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.get("/pipeline-status")
def get_pipeline_status():
    """Get current pipeline status and logs (for frontend polling)."""
    return pipeline_status


@app.post("/reset")
def reset_state():
    """
    Reset all in-memory state back to defaults.
    Allows re-running demos without restarting the server.
    """
    global pipeline_status

    # Reset pipeline status
    pipeline_status = {
        "is_running": False,
        "current_agent": None,
        "logs": [],
        "last_result": None,
    }

    # Reset bookings to initial state
    BOOKINGS.clear()
    BOOKINGS.update(copy.deepcopy(INITIAL_BOOKINGS))

    return {"status": "reset_complete", "message": "All state reset to defaults"}


@app.post("/start-monitor")
async def start_monitor():
    """Start background flight monitoring."""
    if flight_poller.is_running:
        return {"status": "already_running"}

    async def on_disruption(booking_id, disruption):
        """Callback when a disruption is detected by the poller."""
        booking = copy.deepcopy(BOOKINGS[booking_id])
        booking["phone"] = RECIPIENT_PHONE_NUMBER
        result = run_pipeline(booking, disruption)
        BOOKINGS[booking_id]["status"] = "rebooked"

    await flight_poller.start(BOOKINGS, on_disruption)
    return {"status": "monitoring_started", "interval_seconds": flight_poller.poll_interval}


@app.post("/stop-monitor")
async def stop_monitor():
    """Stop background flight monitoring."""
    await flight_poller.stop()
    return {"status": "monitoring_stopped"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
