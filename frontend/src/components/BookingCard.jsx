import React from "react";

export default function BookingCard({ booking, onTrigger, isRunning }) {
  const statusClass =
    booking.status === "confirmed"
      ? "status-confirmed"
      : booking.status === "rebooked"
      ? "status-rebooked"
      : "status-default";

  return (
    <div className="booking-card">
      <div className="booking-header">
        <span className="booking-id">{booking.booking_id}</span>
        <span className={`booking-status ${statusClass}`}>{booking.status}</span>
      </div>
      <div className="booking-route">
        <div className="route-point">
          <span className="route-code">{booking.route?.split("-")[0]}</span>
          <span className="route-label">{booking.origin}</span>
        </div>
        <div className="route-line">
          <span className="route-arrow">✈</span>
        </div>
        <div className="route-point">
          <span className="route-code">{booking.route?.split("-")[1]}</span>
          <span className="route-label">{booking.destination}</span>
        </div>
      </div>
      <div className="booking-details">
        <div className="detail-item">
          <span className="detail-label">Flight</span>
          <span className="detail-value">{booking.flight_iata}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Airline</span>
          <span className="detail-value">{booking.airline}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Date</span>
          <span className="detail-value">{booking.date}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Departure</span>
          <span className="detail-value">{booking.departure}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Passenger</span>
          <span className="detail-value">{booking.user}</span>
        </div>
      </div>
      <button
        className="trigger-btn"
        onClick={() => onTrigger(booking.booking_id)}
        disabled={isRunning || booking.status === "rebooked"}
      >
        {isRunning
          ? "⏳ Pipeline Running..."
          : booking.status === "rebooked"
          ? "✅ Rebooked"
          : "⚡ Simulate Disruption"}
      </button>
    </div>
  );
}
