from pydantic import BaseModel
from typing import Optional
from typing_extensions import TypedDict


class FlightOption(BaseModel):
    """A single alternative flight option."""
    flight: str
    airline: str
    departure: str
    arrival: str
    price: float
    score: Optional[float] = None


class BookingInfo(BaseModel):
    """A user's flight booking."""
    booking_id: str
    user: str
    phone: str
    flight_iata: str
    airline: str
    airline_iata: str
    route: str
    origin: str
    destination: str
    date: str
    departure: str
    arrival: str
    status: str


class DisruptionEvent(BaseModel):
    """A detected flight disruption."""
    flight_iata: str
    disruption_type: str  # "cancelled" | "delayed"
    original_departure: str
    delay_minutes: Optional[int] = None
    reason: Optional[str] = "Operational reasons"


class PipelineResult(BaseModel):
    """Final result of the agent pipeline."""
    booking_id: str
    disruption_type: str
    selected_flight: Optional[dict] = None
    booking_confirmation: Optional[dict] = None
    sms_status: str
    logs: list[str]


# LangGraph State — shared across all agents
class AgentState(TypedDict):
    booking: dict
    disruption: dict
    assessment: str
    policy_approved: bool
    policy_constraints: dict
    alternatives: list
    ranked_alternatives: list
    selected_flight: dict
    booking_confirmation: dict
    sms_status: str
    logs: list
    retry_count: int
