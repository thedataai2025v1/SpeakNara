# SpeakNara — Task List

> Rules: one task per branch (`feat/P{phase}-T{task}-short-name`), TDD, one commit per task, stop and wait for "next".

## Working Rules

1. **One task at a time** — complete the entire flow: branch → tests → code → commit → PR → merge
2. **Branch per task** — `feat/P{phase}-T{task}-short-name` (e.g., `feat/P1-T1-supabase-config`)
3. **TDD** — write tests first; they must fail green before writing code; run tests after every change
4. **Small commits** — each task < ~200 lines of code; if larger, split into sub-tasks
5. **Conventional Commits** — `feat:`, `fix:`, `chore:`, `test:`, `refactor:`, `docs:`
6. **Stop & wait** — after completing a task, report results; do not start the next until told "next"
7. **End-of-phase summary** — when all tasks in a phase are done: coverage report, risks, next steps

---

## Phase 0 — Documentation (DONE ✅)

| Task | Description | Branch | Status |
|------|------------|--------|--------|
| P0-T1 | PRD, Architecture, DB Schema, API Spec, Tasks, ADRs | `main` | ✅ Done |

---

## Phase 1 — Project Foundation

### P1-T1: Backend project scaffold + Supabase config

- **Branch**: `feat/P1-T1-backend-scaffold` ✅ Merged 2026-11-10
- **Tests**: 6/6 passing (ruff + black clean)
- [x] Backend project scaffold with pydantic-settings
- [x] Supabase client module (mocked tests)
- [x] Health endpoint
- [x] Tests: settings, health, supabase client
- [x] Code quality: ruff + black
- **Files**: `backend/pyproject.toml`, `backend/core/settings.py`, `.env.example`
- **Description**: Scaffold the FastAPI backend project. Configure Supabase client, connection pooling, environment settings.
- **Tests required**:
  - `test_settings.py`: settings loads from env vars, defaults work
  - `test_supabase_client.py`: Supabase client connects (mocked)
- **Acceptance criteria**:
  - `pyproject.toml` with all dependencies (fastapi, uvicorn, supabase, python-multipart, pydantic, python-jose, faster-whisper, pydub, requests, yt-dlp)
  - `settings.py` reads `.env` via pydantic-settings
  - `.env.example` lists all required vars (EURI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET)
- **Lines**: ~100

---

### P1-T2: Frontend project scaffold (Next.js + shadcn/ui)

- **Branch**: `feat/P1-T2-frontend-scaffold` ✅ Merged 2026-11-10
- **Test branch**: `feat/P1-T2-frontend-tests` ✅ Merged 2026-11-10 (PR #2)
- **Tests**: 6/6 passing (vitest + jsdom), lint clean
- [x] Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui scaffold
- [x] Supabase browser client with createBrowserClient
- [x] Login and register pages with client-side auth forms
- [x] Home page with Sign In / Register navigation
- [x] ESLint configured, lint passes
- [x] Vitest test for scaffold structure
- **Files**: `frontend/package.json`, `frontend/next.config.mjs`, `frontend/tailwind.config.js`, `frontend/tsconfig.json`, `frontend/src/app/`, `frontend/src/utils/supabase/client.ts`, `frontend/src/lib/utils.ts`
- **Description**: Scaffold Next.js app with App Router, Tailwind, shadcn/ui, Supabase client.
- **Tests required**:
  - `app/page.test.tsx`: renders home page, links to sign-in
- **Acceptance criteria**:
  - `npx create-next-app@latest` scaffold with TypeScript, Tailwind
  - shadcn/ui initialized
  - Supabase client configured in `lib/supabase/client.ts`
  - Home page with "Sign In" button, app name "SpeakNara"
- **Lines**: ~80

---

### P1-T3: Database migrations + seed data

- **Branch**: `feat/P1-T3-db-migrations` ✓ merged
- **Files**: `backend/migrations/001_initial.sql`, `backend/core/migrations.py`, `backend/core/database.py`, `backend/core/seed_data.py`
- **Description**: Write SQL migration for all tables (users, sessions, session_metrics, topics, random_words). Seed ~30 table topics, ~50 random words.
- **Tests required**:
  - `test_migrations_seed.py`: 6 tests (apply migrations, tables exist, foreign keys, seed counts, idempotency, word distribution) — all pass
- **Acceptance criteria**:
  - [x] Migration creates all tables with correct constraints, foreign keys, indexes
  - [x] Seed script is idempotent (safe to re-run)
  - [x] 6/6 tests pass
- **Lines**: ~500

---

### P1-T4: Auth middleware + JWT verification

- **Branch**: `feat/P1-T4-auth-middleware` ✓ merged
- **Files**: `backend/core/auth.py`, `backend/api/deps.py`
- **Description**: JWT verification middleware for FastAPI that validates Supabase JWTs. Dependency injection to get current user.
- **Tests required**:
  - `test_auth.py`: 13 tests — valid JWT returns user, expired/invalid JWT returns 401, admin-only route rejects non-admin
- **Acceptance criteria**:
  - [x] Verify JWT using Supabase `SUPABASE_JWT_SECRET`
  - [x] FastAPI dependency `get_current_user()` returns user dict
  - [x] `require_admin()` dependency raises HTTPException(403) for non-admins
  - [x] 13/13 tests pass
- **Lines**: ~80

---

### P1-T5: Health check endpoint

- **Branch**: `feat/P1-T5-health-check`
- **Files**: `backend/api/endpoints/health.py`, `backend/main.py`
- **Description**: GET /health with database and LLM connectivity checks.
- **Tests required**:
  - `test_health.py`: returns 200, checks db and llm status
- **Acceptance criteria**:
  - `GET /health` returns `{"status": "ok", "version": "...", "services": {"database": "connected", "llm": "connected"}}`
  - No auth required
  - Gracefully reports service failures
- **Lines**: ~40

---

### P1-T6: CI pipeline (GitHub Actions)

- **Branch**: `feat/P1-T6-ci-pipeline`
- **Files**: `.github/workflows/ci.yml`
- **Description**: GitHub Actions workflow: lint + test backend, lint + build frontend.
- **Tests required**: (run locally first to verify)
- **Acceptance criteria**:
  - Runs on push to main and PRs
  - Installs deps, runs `pytest` for backend, `next lint` + `next build` for frontend
  - Caches dependencies
- **Lines**: ~60

---

**Phase 1 summary**: 6 tasks, ~510 lines total.

---

## Phase 2 — Core Audio Pipeline

### P2-T1: Audio upload + file validation

- **Branch**: `feat/P2-T1-audio-upload`
- **Files**: `backend/api/endpoints/audio.py`, `backend/services/audio_upload.py`
- **Description**: Handle multipart audio upload. Validate format (WebM/Opus, WAV, MP3), size (<50MB), duration (<5 min).
- **Tests required**:
  - `test_audio_upload.py`: rejects oversized files, rejects unsupported formats, accepts valid audio, validates duration
- **Acceptance criteria**:
  - `POST /audio/analyze` accepts multipart file
  - Validates format, size, duration
  - Returns structured error for invalid inputs
- **Lines**: ~100

---

### P2-T2: Whisper transcription (faster-whisper)

- **Branch**: `feat/P2-T2-whisper-transcription`
- **Files**: `backend/services/whisper_service.py`
- **Description**: Transcribe audio using faster-whisper (local, free). Return transcript with word-level timestamps.
- **Tests required**:
  - `test_whisper_service.py`: transcribe a short test audio file, verify transcript is non-empty, timestamps are ordered
- **Acceptance criteria**:
  - Uses `faster-whisper` library (tiny model for speed)
  - Returns transcript string + word-level timestamps
  - Handles multiple audio formats (convert via pydub if needed)
  - Works offline (no API calls)
- **Lines**: ~80

---

### P2-T3: Audio metrics extraction

- **Branch**: `feat/P2-T3-audio-metrics`
- **Files**: `backend/services/audio_analysis.py`
- **Description**: Extract speech metrics: WPM, filler count, pauses, pitch, intensity from audio + transcript.
- **Tests required**:
  - `test_audio_analysis.py`: calculate WPM from word count/duration, detect fillers from transcript, find pauses from audio silence
- **Acceptance criteria**:
  - WPM = word_count / duration_minutes
  - Filler detection: count "um", "uh", "like", "you know" from transcript
  - Pause detection: silence > 1 second in audio (pydub/whisper timestamps)
  - Pitch & intensity via librosa (avg, variation, range)
- **Lines**: ~120

---

### P2-T4: LLM service (Euron API integration)

- **Branch**: `feat/P2-T4-llm-service`
- **Files**: `backend/services/llm_service.py`, `backend/services/prompts.py`
- **Description**: Call Euron API (OpenAI-compatible) for speech feedback. Define prompt templates for each mode.
- **Tests required**:
  - `test_llm_service.py`: calls Euron API with correct model/prompt, parses response, handles API errors, retries on 429
- **Acceptance criteria**:
  - Uses `openai` Python SDK with `base_url="https://api.euron.one/api/v1/euri"`, model="claude-sonnet-5-5"
  - Prompt templates in `prompts.py` for each mode (impromptu, table_topics, storytelling, prepared_speech, evaluations)
  - Returns structured JSON: strengths, areas_for_improvement, score, score_breakdown, specific_suggestions
  - Retry logic for rate limits (max 3 retries, exponential backoff)
- **Lines**: ~100

---

### P2-T5: Audio analysis orchestration + session storage

- **Branch**: `feat/P2-T5-audio-analysis-orchestration`
- **Files**: `backend/api/endpoints/audio.py` (extend), `backend/services/analysis_orchestrator.py`
- **Description**: Orchestrate the full pipeline: validate → transcribe → extract metrics → LLM feedback → store in DB.
- **Tests required**:
  - `test_analysis_orchestrator.py`: full pipeline with mocked services, session stored in DB, returns correct response
- **Acceptance criteria**:
  - Orchestrates whisper → metrics → LLM in sequence
  - Stores session, metrics, and LLM feedback in Supabase
  - Deletes audio file after processing (unless `store_audio=true`)
  - Stores audio in Supabase Storage if `store_audio=true`
  - Returns full session response matching API spec
- **Lines**: ~120

---

**Phase 2 summary**: 5 tasks, ~520 lines total.

---

## Phase 3 — Practice Modes (Backend + Frontend)

### P3-T1: Table Topics mode

- **Branch**: `feat/P3-T1-table-topics`
- **Files**: `backend/api/endpoints/topics.py`, `backend/models/topic.py`, `app/table-topics/page.tsx`
- **Description**: Random topic generation endpoint + recording page with topic display.
- **Tests required**:
  - `test_topics.py`: returns random topic, category, difficulty; no duplicates in sequence
- **Acceptance criteria**:
  - `GET /topics/random` returns a topic with category and difficulty
  - Frontend: shows topic, starts recording, uploads on stop, shows feedback
- **Lines**: ~150

---

### P3-T2: Storytelling mode (random words)

- **Branch**: `feat/P3-T2-storytelling`
- **Files**: `backend/models/random_word.py`, `backend/api/endpoints/topics.py` (extend), `app/storytelling/page.tsx`
- **Description**: Generate 3 random words for storytelling prompts. Recording page shows words.
- **Tests required**:
  - `test_random_words.py`: returns exactly 3 words, no duplicates in same set
- **Acceptance criteria**:
  - `GET /topics/random-words` returns 3 words
  - Frontend: shows 3 words, recording UI, feedback display
- **Lines**: ~120

---

### P3-T3: Impromptu mode

- **Branch**: `feat/P3-T3-impromptu`
- **Files**: `app/record/page.tsx`
- **Description**: Simple "just start speaking" mode — no topic prompt, just record.
- **Tests required**: (frontend only)
- **Acceptance criteria**:
  - Landing page of the app — big "Start Speaking" button
  - Records audio, uploads, shows feedback
- **Lines**: ~100

---

### P3-T4: Prepared speech mode

- **Branch**: `feat/P3-T4-prepared-speech`
- **Files**: `app/prepared-speech/page.tsx`
- **Description**: Upload a pre-written speech or record a rehearsed speech.
- **Tests required**: (frontend + backend)
- **Acceptance criteria**:
  - Option to paste a speech text (saved with session) + record delivery
  - LLM evaluates both content (text) and delivery (audio)
- **Lines**: ~120

---

### P3-T5: YouTube evaluations mode

- **Branch**: `feat/P3-T5-youtube-evaluations`
- **Files**: `backend/api/endpoints/evaluations.py`, `backend/services/youtube_transcript.py`, `app/evaluations/page.tsx`
- **Description**: Extract YouTube transcript (yt-dlp), send to LLM for evaluation as judge.
- **Tests required**:
  - `test_youtube_transcript.py`: extracts transcript from a known URL (mocked), handles no-subtitle videos
  - `test_evaluations.py`: sends transcript to LLM with evaluation prompt
- **Acceptance criteria**:
  - `POST /evaluations/youtube` accepts YouTube URL
  - Extracts transcript via yt-dlp (subtitle extraction)
  - LLM evaluates using "public_speaking" criteria prompt
  - Frontend: URL input field, shows transcript preview, shows evaluation results
  - Returns 422 if no subtitles available
- **Lines**: ~150

---

### P3-T6: Shared frontend components

- **Branch**: `feat/P3-T6-shared-components`
- **Files**: `components/Recorder.tsx`, `components/FeedbackCard.tsx`, `components/Navbar.tsx`, `components/SessionList.tsx`
- **Description**: Reusable components used across all practice modes.
- **Tests required**:
  - `Recorder.test.tsx`: starts/stops recording, handles browser permission denied
  - `FeedbackCard.test.tsx`: renders score, strengths, areas for improvement
- **Acceptance criteria**:
  - `Recorder`: browser-based recording (MediaRecorder API), WebM format, shows recording indicator
  - `FeedbackCard`: renders score badge, score breakdown, strengths list, areas for improvement
  - `Navbar`: app name, mode links, user avatar/sign-out
  - `SessionList`: paginated list of past sessions with score + date
- **Lines**: ~200

---

**Phase 3 summary**: 6 tasks, ~840 lines total.

---

## Phase 4 — Progress Dashboard

### P4-T1: Progress backend endpoints

- **Branch**: `feat/P4-T1-progress-endpoints`
- **Files**: `backend/api/endpoints/progress.py`
- **Description**: Aggregate stats + time-series data with range selectors (7/30/90d, custom).
- **Tests required**:
  - `test_progress.py`: aggregates correctly for different ranges, filters by mode, handles empty data
- **Acceptance criteria**:
  - `GET /progress/summary` with range + mode filters
  - `GET /progress/history` with metric + range filters
  - Returns weekly-aggregated trend data
- **Lines**: ~120

---

### P4-T2: Progress dashboard UI

- **Branch**: `feat/P4-T2-progress-ui`
- **Files**: `app/progress/page.tsx`, `components/ProgressChart.tsx`
- **Description**: Dashboard with range selector, per-mode breakdown, Recharts charts.
- **Tests required**:
  - `Progress.test.tsx`: renders charts, switches range, filters by mode
- **Acceptance criteria**:
  - Range selector: 7d / 30d / 90d / custom
  - Line chart for metric trends (WPM, fillers, score)
  - Per-mode breakdown cards (sessions count, avg score)
  - Bar chart for weekly scores
- **Lines**: ~150

---

**Phase 4 summary**: 2 tasks, ~270 lines total.

---

## Phase 5 — Auth & Admin

### P5-T1: Sign-in / Sign-up pages (Supabase Auth)

- **Branch**: `feat/P5-T1-auth-pages`
- **Files**: `app/login/page.tsx`, `app/register/page.tsx`, `lib/supabase/client.ts`, middleware
- **Description**: Email/password sign-in and sign-up using Supabase Auth. Protected routes via Next.js middleware.
- **Tests required**:
  - `login.test.tsx`: redirects to home on success, shows error on failure
  - `register.test.tsx`: creates account, sets role='user'
- **Acceptance criteria**:
  - Clean login/register forms with validation
  - Supabase Auth handles password hashing, email confirmation
  - Protected routes redirect to login
  - New users get role='user' via Supabase DB trigger
- **Lines**: ~120

---

### P5-T2: Admin user management

- **Branch**: `feat/P5-T2-admin-users`
- **Files**: `app/admin/users/page.tsx`, `backend/api/endpoints/admin.py`
- **Description**: Admin page to list users, create new users, change roles.
- **Tests required**:
  - `test_admin.py`: non-admin gets 403, admin can list/create users
  - `admin-users.test.tsx`: renders user list, create form
- **Acceptance criteria**:
  - `GET /admin/users` (admin only) returns paginated user list
  - `POST /admin/users/create` (admin only) creates user, triggers Supabase email confirmation
  - Frontend: table of users with email, name, role, created date
  - Create user form with email, name, role select
- **Lines**: ~120

---

**Phase 5 summary**: 2 tasks, ~240 lines total.

---

## Phase 6 — Polish & Deployment

### P6-T1: LLM response caching

- **Branch**: `feat/P6-T1-llm-caching`
- **Files**: `backend/services/llm_cache.py`
- **Description**: Cache LLM responses by (user_id, mode, transcript hash) to avoid redundant API calls during testing.
- **Tests required**:
  - `test_llm_cache.py`: cache hit returns cached response, cache miss calls LLM and stores, TTL expiry
- **Acceptance criteria**:
  - Hash transcript → check cache → return or call LLM
  - TTL: 24 hours (configurable via env)
  - Cache in Supabase (table: `llm_cache`)
- **Lines**: ~80

---

### P6-T2: Rate limiting

- **Branch**: `feat/P6-T2-rate-limiting`
- **Files**: `backend/core/rate_limit.py`
- **Description**: Per-user rate limiting on LLM calls (e.g., 30 sessions/month on free tier).
- **Tests required**:
  - `test_rate_limit.py`: allows N requests, rejects N+1, resets after window
- **Acceptance criteria**:
  - Sliding window rate limit: configurable per user role
  - Default: 30 sessions/month for users, unlimited for admin
  - Returns 429 with retry-after header
- **Lines**: ~60

---

### P6-T3: Vercel deployment config

- **Branch**: `feat/P6-T3-vercel-deployment`
- **Files**: `vercel.json`, `next.config.*`, `.env.example` (frontend)
- **Description**: Configure Vercel for frontend deployment. Set environment variables.
- **Acceptance criteria**:
  - `vercel.json` with correct build settings
  - Frontend deploys to Vercel free tier
  - Environment variables documented
- **Lines**: ~30

---

### P6-T4: Render deployment config

- **Branch**: `feat/P6-T4-render-deployment`
- **Files**: `render.yaml` or deployment docs
- **Description**: Configure Render for backend deployment. Set build command, start command, env vars.
- **Acceptance criteria**:
  - Backend deploys to Render free tier
  - Build: `pip install -e .`, Start: `uvicorn backend.main:app`
  - Environment variables configured (EURI_API_KEY, SUPABASE_*)
  - Health check endpoint configured
- **Lines**: ~30

---

### P6-T5: Error handling + logging

- **Branch**: `feat/P6-T5-error-handling`
- **Files**: `backend/core/logging.py`, `backend/api/exceptions.py`, global error handlers
- **Description**: Structured logging, global exception handlers, user-friendly error messages.
- **Tests required**:
  - `test_exceptions.py`: 404, 403, 422, 500 all return consistent format
- **Acceptance criteria**:
  - Global FastAPI exception handlers for ValidationException, HTTPException
  - Structured logging (JSON format for production)
  - User-friendly error messages (no stack traces in production)
- **Lines**: ~80

---

### P6-T6: Session detail page + audio playback (optional)

- **Branch**: `feat/P6-T6-session-detail`
- **Files**: `app/sessions/[id]/page.tsx`
- **Description**: Full session detail view: transcript, metrics, LLM feedback, audio playback (if stored).
- **Tests required**:
  - `session-detail.test.tsx`: renders all sections, handles missing audio
- **Acceptance criteria**:
  - Shows full transcript with timestamps
  - Metrics cards (WPM, fillers, pauses, pitch)
  - LLM feedback (strengths, areas for improvement, suggestions)
  - Audio playback if `audio_stored=true`
  - "Practice this topic again" button
- **Lines**: ~100

---

**Phase 6 summary**: 6 tasks, ~380 lines total.

---

## Grand Summary

| Phase | Tasks | Est. Lines |
|-------|-------|------------|
| P1 — Foundation | 6 | ~510 |
| P2 — Audio Pipeline | 5 | ~520 |
| P3 — Practice Modes | 6 | ~840 |
| P4 — Progress | 2 | ~270 |
| P5 — Auth & Admin | 2 | ~240 |
| P6 — Polish & Deploy | 6 | ~380 |
| **Total** | **27** | **~2,760** |

---

## Task Progress

- [x] P1-T1: Backend scaffold + Supabase config (feat/P1-T1-backend-scaffold, merged 2026-11-10)
- [x] P1-T2: Frontend scaffold (Next.js + shadcn/ui) (feat/P1-T2-frontend-scaffold, merged 2026-11-10)
- [ ] P1-T3: Database migrations + seed data
- [x] P1-T4: Auth middleware + JWT verification (feat/P1-T4-auth-middleware, merged 2026-11-10)
- [x] P1-T5: Health check endpoint (feat/P1-T5-health-endpoint, merged 2026-11-10)
- [x] P1-T6: CI pipeline (GitHub Actions) (feat/P1-T6-ci-pipeline, merged 2026-11-10)
- [ ] P2-T1: Audio upload + file validation
- [ ] P2-T2: Whisper transcription
- [ ] P2-T3: Audio metrics extraction
- [ ] P2-T4: LLM service (Euron API)
- [ ] P2-T5: Audio analysis orchestration
- [ ] P3-T1: Table Topics mode
- [ ] P3-T2: Storytelling mode
- [ ] P3-T3: Impromptu mode
- [ ] P3-T4: Prepared speech mode
- [ ] P3-T5: YouTube evaluations
- [ ] P3-T6: Shared frontend components
- [ ] P4-T1: Progress backend endpoints
- [ ] P4-T2: Progress dashboard UI
- [ ] P5-T1: Sign-in / Sign-up pages
- [ ] P5-T2: Admin user management
- [ ] P6-T1: LLM response caching
- [ ] P6-T2: Rate limiting
- [ ] P6-T3: Vercel deployment config
- [ ] P6-T4: Render deployment config
- [ ] P6-T5: Error handling + logging
- [ ] P6-T6: Session detail page
 
 # #   C o m p l e t e d   T a s k s  
  
 |   T a s k   |   B r a n c h   |   M e r g e d   |   T e s t s   |  
 | - - - - - - | - - - - - - - - | - - - - - - - - | - - - - - - - |  
 |   P 1 - T 1 :   B a c k e n d   S c a f f o l d   |    e a t / P 1 - T 1 - b a c k e n d - s c a f f o l d   |   2 0 2 6 - 1 1 - 1 0   |   3 / 3   p y t e s t ,   l i n t / f o r m a t   O K   |  
 |   P 1 - T 2 :   F r o n t e n d   S c a f f o l d   |    e a t / P 1 - T 2 - f r o n t e n d - s c a f f o l d   |   2 0 2 6 - 1 1 - 1 0   ( P R   # 1 )   |   s c a f f o l d   +   l i n t   O K   |  
 |   P 1 - T 2 :   F r o n t e n d   T e s t s   |    e a t / P 1 - T 2 - f r o n t e n d - t e s t s   |   2 0 2 6 - 1 1 - 1 0   ( P R   # 2 )   |   6 / 6   v i t e s t ,   l i n t   c l e a n   |  
 