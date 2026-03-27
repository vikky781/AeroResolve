import React from "react";

export default function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-logo">
          <span className="logo-icon">✈️</span>
          <div>
            <h1 className="header-title">AeroResolve</h1>
            <p className="header-tagline">Zero-Touch Agentic Travel Recovery</p>
          </div>
        </div>
        <div className="header-badge">
          <span className="badge-dot"></span>
          <span>System Active</span>
        </div>
      </div>
    </header>
  );
}
