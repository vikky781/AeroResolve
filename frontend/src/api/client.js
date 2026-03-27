const API_BASE = "http://localhost:8000";

export async function fetchBookings() {
  const res = await fetch(`${API_BASE}/bookings`);
  if (!res.ok) throw new Error("Failed to fetch bookings");
  return res.json();
}

export async function simulateDisruption(bookingId = "BK001") {
  const res = await fetch(`${API_BASE}/simulate-disruption`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ booking_id: bookingId }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Pipeline error");
  }
  return res.json();
}

export async function fetchPipelineStatus() {
  const res = await fetch(`${API_BASE}/pipeline-status`);
  if (!res.ok) throw new Error("Failed to fetch pipeline status");
  return res.json();
}

export async function startMonitor() {
  const res = await fetch(`${API_BASE}/start-monitor`, { method: "POST" });
  return res.json();
}

export async function stopMonitor() {
  const res = await fetch(`${API_BASE}/stop-monitor`, { method: "POST" });
  return res.json();
}

export async function resetState() {
  const res = await fetch(`${API_BASE}/reset`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reset state");
  return res.json();
}
