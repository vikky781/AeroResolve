import React, { useState, useEffect } from "react";
import { fetchBookings, simulateDisruption, resetState } from "../api/client";
import BookingCard from "./BookingCard";
import PipelineView from "./PipelineView";
import LogPanel from "./LogPanel";
import ResultPanel from "./ResultPanel";

export default function Dashboard() {
  const [bookings, setBookings] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState("idle");

  useEffect(() => {
    loadBookings();
  }, []);

  async function loadBookings() {
    try {
      const data = await fetchBookings();
      setBookings(data.bookings || []);
    } catch (err) {
      setError("Backend unreachable. Please try again.");
    }
  }

  async function handleTrigger(bookingId) {
    setIsRunning(true);
    setError(null);
    setResult(null);
    setLogs(["[Dashboard] Triggering disruption simulation..."]);
    setPipelineStatus("running");

    try {
      const data = await simulateDisruption(bookingId);
      setResult(data.result);
      setLogs(data.logs || []);
      setPipelineStatus("completed");

      // Refresh bookings to show updated status
      await loadBookings();
    } catch (err) {
      setError(err.message);
      setLogs((prev) => [...prev, `[Dashboard] ❌ Error: ${err.message}`]);
      setPipelineStatus("error");
    } finally {
      setIsRunning(false);
    }
  }

  async function handleReset() {
    try {
      await resetState();
      setResult(null);
      setLogs([]);
      setError(null);
      setPipelineStatus("idle");
      await loadBookings();
    } catch (err) {
      setError("Failed to reset. Is the server running?");
    }
  }

  return (
    <div className="dashboard">
      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="dashboard-grid">
        {/* Left Column — Bookings */}
        <div className="bookings-section">
          <div className="section-header">
            <h2 className="section-title">Monitored Flights</h2>
            <button className="reset-btn" onClick={handleReset} disabled={isRunning}>
              🔄 Reset
            </button>
          </div>
          <div className="bookings-list">
            {bookings.length > 0 ? (
              bookings.map((b) => (
                <BookingCard
                  key={b.booking_id}
                  booking={b}
                  onTrigger={handleTrigger}
                  isRunning={isRunning}
                />
              ))
            ) : (
              <div className="no-bookings">
                <p>No bookings loaded. Check backend connection.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column — Pipeline + Logs + Result */}
        <div className="pipeline-section">
          <PipelineView status={pipelineStatus} result={result} />
          <LogPanel logs={logs} />
          <ResultPanel result={result} />
        </div>
      </div>
    </div>
  );
}
