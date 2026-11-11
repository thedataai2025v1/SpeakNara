# SpeakNara

[![CI](https://github.com/thedataai2025v1/SpeakNara/actions/workflows/ci.yml/badge.svg)](https://github.com/thedataai2025v1/SpeakNara/actions/workflows/ci.yml)

AI-powered Lak public speaking coach, similar to Yoodli.

---

## Quick start (local development)

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** (with npm)
- A **.env** file in `backend/` (copy from `.env.example` and fill in `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`, `EURON_MODEL`)

### 1. Backend

```powershell
cd backend
python -m venv .venv                  # first time only
.\.venv\Scripts\Activate.ps1          # activate venv (Windows)
pip install -r requirements.txt        # first time only
python -m uvicorn main:app --reload --port 8000
```

The API runs at **http://localhost:8000**.

### 2. Frontend

In a second terminal:

```powershell
cd frontend
npm install                            # first time only
npm run dev
```

The app runs at **http://localhost:3000**.

### 3. Practice modes available

| Route | Mode | Description |
|---|---|---|
| `/table-topics` | Table Topics | Random topic + 3 keywords, 60 s limit |
| `/storytelling` | Storytelling | Random theme + 3 keywords, 90 s limit |
| `/impromptu` | Impromptu | Your own keywords + custom time limit (30–180 s) |
| `/prepared-speech` | Prepared Speech | Paste speech text, record delivery, get feedback |
| `/youtube` | YouTube Evaluation | Evaluate a YouTube video with AI feedback |
| `/history` | Session History | Review all your past speaking evaluations |

### 4. Test backend endpoints (from a third terminal)

```powershell
# Table Topics
curl -X POST http://localhost:8000/api/v1/table-topics/generate

# Storytelling
curl -X POST http://localhost:8000/api/v1/storytelling/generate

# Prepared Speech
curl -X POST http://localhost:8000/api/v1/prepared-speech/generate

# YouTube (requires a video URL in the body)
# curl -X POST http://localhost:8000/api/v1/youtube/transcribe -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=..."}'

# Health check
curl http://localhost:8000/health
```

### 5. Run automated tests

```powershell
# Backend (activate venv first: `.\.venv\Scripts\Activate.ps1`)
cd backend
python -m pytest -v

# Frontend (lint + e2e)
cd frontend
npm run lint
npx playwright test                   # e2e tests (requires `npx playwright install chromium` first)
```

---
