import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"

# AviationStack
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY", "")
AVIATIONSTACK_BASE_URL = "http://api.aviationstack.com/v1"

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER", "")

# Policy Rules
MAX_REBOOKING_COST = 6000  # INR
SAME_DAY_ONLY = True
PREFER_SAME_AIRLINE = True

# Scoring Weights
PRICE_WEIGHT = 0.4
TIME_WEIGHT = 0.3
AIRLINE_WEIGHT = 0.3

# Bookings (in-memory)
BOOKINGS = {
    "BK001": {
        "booking_id": "BK001",
        "user": "Vikhyat Gupta",
        "phone": "",  # Will use RECIPIENT_PHONE_NUMBER from env
        "flight_iata": "6E-302",
        "airline": "IndiGo",
        "airline_iata": "6E",
        "route": "HYD-DEL",
        "origin": "Hyderabad",
        "destination": "Delhi",
        "date": "2026-03-27",
        "departure": "10:00",
        "arrival": "12:30",
        "status": "confirmed"
    },
    "BK002": {
        "booking_id": "BK002",
        "user": "Gurnoor Singh",
        "phone": "",
        "flight_iata": "AI-101",
        "airline": "Air India",
        "airline_iata": "AI",
        "route": "DEL-BOM",
        "origin": "Delhi",
        "destination": "Mumbai",
        "date": "2026-03-27",
        "departure": "14:00",
        "arrival": "16:15",
        "status": "confirmed"
    }
}

# Immutable snapshot for reset endpoint
import copy
INITIAL_BOOKINGS = copy.deepcopy(BOOKINGS)

