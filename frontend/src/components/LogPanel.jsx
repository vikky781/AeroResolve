import React, { useRef, useEffect } from "react";

export default function LogPanel({ logs }) {
  const logsEndRef = useRef(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const getLogClass = (log) => {
    if (log.includes("✅") || log.includes("success")) return "log-success";
    if (log.includes("❌") || log.includes("error") || log.includes("failed")) return "log-error";
    if (log.includes("🚀")) return "log-start";
    if (log.includes("Rejected")) return "log-warning";
    return "log-info";
  };

  return (
    <div className="log-panel">
      <h2 className="section-title">Agent Logs</h2>
      <div className="log-container">
        {logs && logs.length > 0 ? (
          logs.map((log, index) => (
            <div key={index} className={`log-entry ${getLogClass(log)}`}>
              <span className="log-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="log-text">{log}</span>
            </div>
          ))
        ) : (
          <div className="log-empty">
            <span>Waiting for pipeline execution...</span>
          </div>
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}
