import React from "react";
import Header from "./components/Header";
import Dashboard from "./components/Dashboard";
import "./App.css";

function App() {
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
