# SpeakNara — Architecture Document

## 1. System Overview

```mermaid
graph TB
    subgraph Vercel["Vercel (Frontend)"]
        FE[Next.js App<br/>TypeScript + Tailwind + shadcn/ui]
    end

    subgraph Render["Render (Backend)"]
        BE[FastAPI<br/>Python 3.12]
        WH[Whisper<br/>faster-whisper]
        LA[Audio Analysis<br/>librosa + parselmouth]
        YT[YouTube Transcript<br/>youtube-transcript-api]
    end

    subgraph Supabase["Supabase"]
        DB[(PostgreSQL)]
        ST[Storage<br/>Audio files (optional)]
        SA[Auth<br/>Email/Password]
    end

    Euron[Euron API<br/>claude-sonnet-5-5]

    FE -->|HTTPS| BE
    FE -->|Auth| SA
    BE -->|Audio analysis| WH
    BE -->|Pitch/volume| LA
    BE -->|Fetch transcript| YT
    BE -->|LLM prompts| Euron
    BE -->|Read/write| DB
    BE -->|Store/retrieve| ST
```

## 2. Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend framework | Next.js 14 (App Router) | SSR, API routes, Vercel deploy |
| Frontend language | TypeScript | Type safety, better DX |
| UI components | Tailwind CSS + shadcn/ui | Consistent, accessible components |
| Charts | Recharts | SVG-based, React-friendly |
| Form validation | Zod | Schema validation, type inference |
| Backend framework | FastAPI | Async, auto docs, Pydantic |
| Backend language | Python 3.12 | Rich audio/ML ecosystem |
| Package manager | uv | Fast dependency management |
| ORM | SQLAlchemy 2 | Mature, type-safe |
| Migrations | Alembic | Version-controlled schema changes |
| Transcription | faster-whisper | Local, fast, good accuracy |
| Audio analysis | librosa, parselmouth | Pitch, volume, pause detection |
| YouTube transcript | youtube-transcript-api | Free, no API key needed |
| LLM | Euron API (claude-sonnet-5-5) | OpenAI-compatible endpoint |
| Database | PostgreSQL 16 (via Supabase) | Free tier, JSON support, auth built-in |
| File storage | Supabase Storage | Free tier, S3-compatible |
| Auth | Supabase Auth | Email/password, JWT tokens, free |
| Frontend host | Vercel | Free tier, instant deploy |
| Backend host | Render | Free tier, Docker support |
| CI | GitHub Actions | Free for public repos |
| Tests (frontend) | Vitest + RTL + Playwright | Fast, modern |
| Tests (backend) | pytest + httpx + pytest-cov | Standard Python testing |
| Lint/format | ruff + mypy (BE), ESLint + Prettier (FE) | Fast, comprehensive |

## 3. Directory Structure

```
SpeakNara/
├── app/                          # Next.js frontend
│   ├── app/                      # App Router pages
│   │   ├── page.tsx              # Home / Dashboard
│   │   ├── login/page.tsx        # Login page
│   │   ├── signup/page.tsx       # Signup page
│   │   ├── table-topics/page.tsx # Table Topics mode
│   │   ├── storytelling/page.tsx # Storytelling mode
│   │   ├── evaluations/page.tsx  # Evaluations mode
│   │   ├── sessions/[id]/page.tsx# Session detail
│   │   ├── progress/page.tsx     # Progress dashboard
│   │   ├── admin/page.tsx        # Admin (create users)
│   │   └── layout.tsx            # Root layout + nav
│   ├── components/               # React components
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── Recorder.tsx          # Audio recorder with MediaRecorder
│   │   ├── Timer.tsx             # Countdown timer
│   │   ├── SessionResults.tsx    # Analysis results display
│   │   ├── ProgressChart.tsx     # Recharts chart
│   │   └── Navbar.tsx            # Navigation
│   ├── lib/
│   │   ├── api.ts                # Typed API client (fetch wrappers)
│   │   ├── supabase.ts           # Supabase client
│   │   └── utils.ts              # Shared utilities
│   ├── hooks/
│   │   ├── useAuth.ts            # Auth state hook
│   │   └── useRecorder.ts        # Recording hook
│   └── public/                   # Static assets
├── backend/                      # Python FastAPI backend
│   ├── main.py                   # App entry point
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py           # Login, register, token refresh
│   │   │   ├── sessions.py       # CRUD sessions, upload audio
│   │   │   ├── topics.py         # Random topics, random words
│   │   │   ├── evaluations.py    # YouTube eval, speech eval
│   │   │   └── progress.py       # Aggregated stats
│   │   └── schemas.py            # Pydantic request/response models
│   ├── services/
│   │   ├── whisper.py            # Transcription with faster-whisper
│   │   ├── audio_analysis.py     # WPM, fillers, pauses, pitch
│   │   ├── llm_service.py        # Euron API client + prompt templates
│   │   ├── prompts.py            # Prompt templates per mode
│   │   ├── youtube.py            # YouTube transcript extraction
│   │   └── supabase.py           # Supabase storage client
│   ├── models/
│   │   ├── base.py               # SQLAlchemy base
│   │   ├── user.py               # User model
│   │   ├── session.py            # Session model
│   │   ├── topic.py              # Table Topics prompts
│   │   └── random_word.py        # Storytelling word pool
│   ├── core/
│   │   ├── config.py             # Settings from .env
│   │   ├── security.py           # JWT handling, password hashing
│   │   ├── rate_limit.py         # Rate limiting (10/hour default)
│   │   └── logging.py            # Structured logging
│   ├── db/
│   │   ├── session.py            # SQLAlchemy session factory
│   │   └── init_db.py            # DB initialization
│   ├── alembic/                  # Migrations
│   ├── tests/
│   │   ├── conftest.py           # Test fixtures
│   │   ├── test_audio_analysis.py
│   │   ├── test_llm_service.py
│   │   ├── test_youtube.py
│   │   └── test_api/             # API integration tests
│   ├── sample_audio/             # Test audio fixtures
│   ├── pyproject.toml
│   └── .env.example
├── e2e/                          # Playwright end-to-end tests
├── docs/
│   └── adr/                      # Architecture Decision Records
│       ├── 001-vercel-render-split.md
│       ├── 002-supabase-choice.md
│       └── 003-euron-api.md
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI
├── docker-compose.yml             # Local: PostgreSQL + Redis (cache)
├── .pre-commit-config.yaml
├── PROMPT_USED.md
├── PRD.md
├── ARCHITECTURE.md
├── DB_SCHEMA.md
├── API_SPEC.md
├── TASKS.md
├── CLAUDE.md
└── README.md
```

## 4. Audio Flow (Record → Analyze → Feedback)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend (Next.js)
    participant BE as Backend (FastAPI)
    participant WH as faster-whisper
    participant LA as Audio Analysis
    participant LLM as Euron API
    participant DB as Supabase (PostgreSQL)
    participant ST as Supabase Storage

    U->>FE: Click "Record"
    FE->>FE: MediaRecorder API starts
    U->>FE: Click "Stop"
    FE->>BE: POST /sessions (audio blob + mode)
    BE->>ST: Store audio (if retention enabled)
    BE->>WH: Transcribe audio
    WH-->>BE: Transcript + word timestamps
    BE->>LA: Compute WPM, fillers, pauses, pitch
    LA-->>BE: Metrics JSON
    BE->>LLM: Prompt + transcript + metrics
    LLM-->>BE: Structured feedback JSON
    BE->>DB: Save session + metrics + feedback
    BE->>ST: Delete audio (if retention disabled)
    BE-->>FE: Analysis result
    FE-->>U: Display results
```

## 5. Authentication Flow

```merabase
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant SA as Supabase Auth
    participant BE as Backend

    U->>FE: Enter email/password
    FE->>SA: signInWithPassword()
    SA-->>FE: JWT (access + refresh tokens)
    FE->>FE: Store tokens in httpOnly cookie
    FE->>BE: Request with Authorization header
    BE->>BE: Verify JWT via Supabase JWT secret
    BE-->>FE: User data + session results
```

## 6. Security Notes

- **Auth:** Supabase Auth (email/password) with JWT tokens
- **Tokens:** Stored in httpOnly cookies on frontend; sent in `Authorization` header to backend
- **Backend auth:** Verify JWT using Supabase's `JWT_SECRET` (JWSSecret)
- **RBAC:** Admin role for account creation; regular users for everything else
- **Rate limiting:** 10 analysis requests/hour per user (configurable)
- **Audio privacy:** Deleted after analysis by default; stored in Supabase Storage if opted in
- **CORS:** Restrict to Vercel domain in production
- **No secrets in code:** `.env` files only, never committed
- **Input validation:** Pydantic on all API inputs; Zod on frontend forms

## 7. Error Handling Strategy

| Error Type | Backend Response | Frontend Action |
|------------|-----------------|-----------------|
| Network error | N/A | Retry with backoff, show error toast |
| Auth expired | 401 | Redirect to login |
| Audio too large | 422 | Show file size limit message |
| Whisper failure | 500 + retry | Show "transcription failed, try again" |
| LLM rate limit | 429 | Queue and retry after delay |
| YouTube fetch fail | 400 | Show "could not fetch transcript" |
| DB error | 500 | Log internally, show generic error |

## 8. Deployment Plan

| Service | Host | Free Tier? | Notes |
|---------|------|-----------|-------|
| Frontend | Vercel | Yes | Automatic deploy from git |
| Backend | Render | Yes (spins down) | Docker container, ~50s cold start |
| Database | Supabase | Yes (500 MB) | PostgreSQL + Auth + Storage |
| CI/CD | GitHub Actions | Yes | Lint + test on push |

## 9. Cost Estimate (Monthly)

| Service | Free Tier Usage | Expected Cost |
|---------|----------------|---------------|
| Vercel | Hobby (unlimited visits) | $0 |
| Render | Free (512 MB RAM, 750 hrs/mo) | $0 |
| Supabase | Free (500 MB DB, 1 GB storage) | $0 |
| Euron API | ~30 sessions/mo × ~15 min audio each | Depends on Euron pricing |
| **Total** | | **~$0 (excluding Euron API)** |

## 10. Environment Variables

### Frontend (.env.local)

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Backend (.env)

```
DATABASE_URL=postgresql://user:pass@your-project.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
EURI_API_KEY=your-euron-api-key
EURI_BASE_URL=https://api.euron.one/api/v1/euri
EURI_MODEL=claude-sonnet-5-5
RATE_LIMIT_PER_HOUR=10
```

## 11. LangGraph / Multi-Agent (Optional)

For complex analysis flows (e.g., Evaluations mode A where we compare the YouTube speech with the user's evaluation), we can use LangGraph for multi-agent orchestration:

- **Agent 1 (Transcript Summarizer):** Summarizes the YouTube speech key points
- **Agent 2 (Evaluation Critic):** Analyzes the user's evaluation for structure and specificity
- **Agent 3 (Comparison Judge):** Compares the evaluation against the speech summary for completeness

This is optional in V1 — simple prompt chaining works too. We'll adopt LangGraph if prompt chaining becomes unwieldy.
