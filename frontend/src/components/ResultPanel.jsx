import React from "react";

export default function ResultPanel({ result }) {
  if (!result) return null;

  const selected = result.selected_flight || {};
  const confirmation = result.booking_confirmation || {};
  const disruption = result.disruption || {};

  return (
    <div className="result-panel">
      <h2 className="section-title">Recovery Result</h2>

      <div className="result-grid">
        {/* Disruption Info */}
        <div className="result-card disruption-card">
          <div className="result-card-header">
            <span className="result-icon">⚠️</span>
            <span>Disruption Detected</span>
          </div>
          <div className="result-card-body">
            <div className="result-item">
              <span className="result-label">Flight</span>
              <span className="result-value">{disruption.flight_iata || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Type</span>
              <span className="result-value disruption-type">{disruption.disruption_type || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Reason</span>
              <span className="result-value">{disruption.reason || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Real API Data</span>
              <span className="result-value">{disruption.real_api_data ? "✅ Yes" : "🔄 Simulated"}</span>
            </div>
          </div>
        </div>

        {/* New Booking */}
        <div className="result-card success-card">
          <div className="result-card-header">
            <span className="result-icon">✅</span>
            <span>Rebooked Successfully</span>
          </div>
          <div className="result-card-body">
            <div className="result-item">
              <span className="result-label">New Flight</span>
              <span className="result-value highlight">{selected.flight || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Airline</span>
              <span className="result-value">{selected.airline || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Departure</span>
              <span className="result-value">{selected.departure || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Arrival</span>
              <span className="result-value">{selected.arrival || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Price</span>
              <span className="result-value">₹{selected.price || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Score</span>
              <span className="result-value">{selected.score || "—"}</span>
            </div>
          </div>
        </div>

        {/* Confirmation */}
        <div className="result-card confirmation-card">
          <div className="result-card-header">
            <span className="result-icon">🎫</span>
            <span>Confirmation</span>
          </div>
          <div className="result-card-body">
            <div className="result-item">
              <span className="result-label">Confirmation ID</span>
              <span className="result-value highlight">{confirmation.confirmation_id || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Status</span>
              <span className="result-value">{confirmation.status || "—"}</span>
            </div>
            <div className="result-item">
              <span className="result-label">SMS</span>
              <span className="result-value">
                {result.sms_status === "sent" ? "✅ Sent" : "❌ " + result.sms_status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Alternatives Table */}
      {result.ranked_alternatives && result.ranked_alternatives.length > 0 && (
        <div className="alternatives-section">
          <h3 className="subsection-title">All Scored Alternatives</h3>
          <table className="alternatives-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Flight</th>
                <th>Airline</th>
                <th>Departure</th>
                <th>Arrival</th>
                <th>Price</th>
                <th>Score</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {result.ranked_alternatives.map((alt, idx) => (
                <tr
                  key={idx}
                  className={
                    alt.rejected
                      ? "row-rejected"
                      : idx === 0
                      ? "row-selected"
                      : ""
                  }
                >
                  <td>{idx + 1}</td>
                  <td>{alt.flight}</td>
                  <td>{alt.airline}</td>
                  <td>{alt.departure}</td>
                  <td>{alt.arrival}</td>
                  <td>₹{alt.price}</td>
                  <td>{alt.score}</td>
                  <td>
                    {alt.rejected
                      ? "❌ Rejected"
                      : idx === 0
                      ? "✅ Selected"
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
