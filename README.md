# AeroResolve — Zero-Touch Agentic Travel Recovery

> Autonomous AI Agent for Managing Travel Disruption  
> Built for IIIT Sri City IdeaVerse Hackathon 2026

## Team: Code Alchemists
- Vikhyat Gupta
- Gurnoor Singh Bagga
- Mohit Choudhary

## Tech Stack
- **LLM:** Groq (Llama 3.1 8B Instant)
- **Orchestration:** LangGraph (4-agent pipeline)
- **Backend:** FastAPI + Python
- **Frontend:** React + Vite
- **Notifications:** Twilio SMS
- **Flight Data:** AviationStack API
- **Infra:** Docker

## Architecture
```
Flight Status Monitor (AviationStack)
  → Assessment Agent (analyze disruption impact)
    → Policy Agent (validate rebooking rules)
      → Solution Agent (find & rank alternatives)
        → Execution Agent (book + send SMS via Twilio)
```

## Quick Start

### 1. Setup Environment
```bash
# Fill in your API keys in .env
cp .env.example .env  # or edit .env directly
```

### 2. Run with Docker
```bash
docker compose up --build
```

### 3. Run Locally (without Docker)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### 4. Demo
1. Open http://localhost:5173 (React dashboard)
2. Click "Simulate Disruption" on any booking
3. Watch the 4 agents execute in sequence
4. Receive SMS notification on your phone

## API Endpoints
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/` | Health check |
| GET | `/bookings` | List monitored bookings |
| POST | `/simulate-disruption` | Trigger full recovery pipeline |
| GET | `/pipeline-status` | Current pipeline state |
| POST | `/start-monitor` | Start background flight poller |
| POST | `/stop-monitor` | Stop background poller |

## Contributions

| Role | Name |
|------|------|
| Architecture, implementation & all code | Vikhyat Gupta |
| Ideation & presentation | Gurnoor Singh Bagga, Mohit Choudhary |