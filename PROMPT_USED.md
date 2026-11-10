# PROMPT_USED.md

> The original prompt given to Euron Code to develop SpeakNara.
> Keep this as the single source of truth for product direction.


## PRODUCT
A private app that analyzes my speaking. Three modes:
1. Table Topics: show a random question, 30s prep, record 2 minutes, then return
   analysis (timing vs 1:00/1:30/2:00 lights, pace in words per minute, filler
   words per minute, pauses over 2s, structure: opening, points, closing).
2. Storytelling: show 3 random concrete words, 60s prep, record 2-3 minutes,
   then analyze whether all words were used, story arc (setting, conflict,
   turning point, resolution), sensory detail, vocal variety (pitch range and
   pace change at the climax), plus 3 weakest sentences rewritten.
3. Evaluations: (A) I upload a speech and record my own evaluation of it; you
   compare it and check commend-recommend-commend structure and specificity.
   (B) I upload my speech and get a Toastmasters-style evaluation.
Also a progress dashboard (pace, fillers, pitch range over time per mode).
Single user (me). Privacy first: delete audio after analysis unless I enable
storage.

## TECH STACK (do not change without asking)
- Frontend: Next.js (App Router), TypeScript, Tailwind, shadcn/ui, Recharts,
  Zod; tests with Vitest, React Testing Library, Playwright. Deploy: Vercel.
- Backend: Python 3.12, uv, FastAPI, Pydantic, SQLAlchemy 2, Alembic,
  faster-whisper, librosa/parselmouth, ffmpeg, Anthropic SDK (model
  claude-sonnet-5-5). Tests: pytest, pytest-cov, httpx. Lint: ruff, mypy.
  Deploy: Docker container on Render (or Railway/Fly).
- Database: PostgreSQL 16 (docker-compose locally, Neon in production).
- CI: GitHub Actions. Conventional Commits. pre-commit hooks.
- Note: Vercel only hosts the frontend; heavy audio work stays in the backend.

## WORKING RULES
1. DO NOT WRITE ANY APPLICATION CODE YET. Phase 0 is documents only.
2. Before writing docs, ask me up to 10 clarifying questions in one list
   (e.g. audio retention, auth for single user, budget, hosting choice).
3. Phase 0 deliverables, each as its own file, one at a time, waiting for my
   approval after each:
   - PRD.md (goals, non-goals, user stories, acceptance criteria per mode)
   - ARCHITECTURE.md (components, data flow diagram in Mermaid, folder
     structure, hosting split, security, error handling, cost estimate)
   - DB_SCHEMA.md (tables, columns, types, indexes, Mermaid ER diagram)
   - API_SPEC.md (every endpoint: method, path, request, response, errors)
   - TASKS.md (see format below)
   - CLAUDE.md (these working rules, so every session follows them)
   - ADRs in docs/adr/ for key decisions (e.g. why split Vercel and backend)
4. TASKS.md format: grouped by phase. Each task has an ID (e.g. P3-T2), title,
   description, files touched, tests required, acceptance criteria, and a
   checkbox. Each task must be small enough for one commit (under ~200 lines).
5. After I approve the docs, work strictly one task at a time:
   a. Create a branch: feat/P3-T2-short-name
   b. Write the failing test first (TDD), then the minimal code to pass it
   c. Run: pytest, ruff, mypy (backend) / vitest, eslint, tsc (frontend) and
      show me the output
   d. Commit with a Conventional Commit message, e.g.
      feat(audio): compute words per minute from word timestamps
   e. Tick the task in TASKS.md, then STOP and wait for my "next"
6. At the end of each phase, STOP, summarize what was built, show test
   coverage, list risks, and wait for my approval before the next phase.
7. Never commit secrets. Provide .env.example. Mock the LLM and Whisper in
   tests; keep a small real-audio fixture for audio metric tests.
8. Explain each step as numbered instructions with exact commands and exact
   values (file paths, env var names, field values) so I can follow along.
9. If something is ambiguous or a decision has trade-offs, ask me instead of
   guessing. Be honest about limitations (e.g. what Vercel cannot run).
10. Keep functions small, typed, documented; no dead code; no new
    dependencies without telling me why.


1. Tools and skills list

Frontend

Next.js (App Router) with TypeScript
Tailwind CSS and shadcn/ui for the interface
MediaRecorder API for in-browser recording
Recharts for progress charts
Zod for form and API validation
Vitest and React Testing Library for unit tests, Playwright for end-to-end tests
ESLint and Prettier

Backend

Python 3.12 with uv for packages
FastAPI for the API, with Pydantic for schemas
SQLAlchemy 2 for the database layer and Alembic for migrations
faster-whisper for transcription (or the Whisper API)
librosa or parselmouth for pitch and volume analysis, plus ffmpeg
Anthropic Python SDK for the LLM
pytest, pytest-cov, pytest-asyncio and httpx for tests
ruff for linting and formatting, mypy for type checks

Data and storage

PostgreSQL 16 (local via Docker, production on Neon)
Audio files: either delete them right after analysis (my recommendation, for privacy and cost) or store them in Cloudflare R2

DevOps and process

Git and GitHub with Conventional Commits
GitHub Actions that run lint and tests on every push
Docker and docker-compose for local development
pre-commit hooks
.env files for secrets, never committed

Planning documents (written before any code)

PRD.md, ARCHITECTURE.md, DB_SCHEMA.md, API_SPEC.md
TASKS.md and CLAUDE.md (the rules Claude Code reads each session)
2. Phases
Phase	Goal	Done when
0	Planning docs only, no code	You have approved all docs
1	Repo, tooling, CI, docker-compose	CI is green on an empty app
2	Backend skeleton, DB, migrations	/health works and a DB test passes
3	Audio core: transcript, pace, fillers, pauses, pitch	Metrics tested on sample audio
4	LLM service, prompts, JSON output validation	Tests pass with a mocked LLM
5	Table Topics, backend	2-min audio in, analysis out, saved to DB
6	Frontend skeleton, recorder, Table Topics UI	Record, upload and see results
7	Storytelling mode	Random words, arc analysis
8	Evaluations mode	Both modes (practice and get evaluated)
9	Progress dashboard	Charts of sessions over time
10	Deployment	Frontend on Vercel, backend on host, Neon DB
11	Hardening	Error handling, rate limits, README
---

## ANSWERS TO CLARIFYING QUESTIONS

> Recorded on 2026-11-10. Update this section when answers change.

### Q1: LLM model version
**Answer:** Use Euron API (not Anthropic directly). The model is `claude-sonnet-5-5`
accessed via an OpenAI-compatible endpoint at `https://api.euron.one/api/v1/euri`.
Use the `openai` Python SDK with `api_key=EURI_API_KEY` and `base_url=https://api.euron.one/api/v1/euri`.
No need for Anthropic SDK. LangGraph / LangChain-OpenAI can also be used for multi-agent flows.

### Q2: Backend hosting
**Answer:** Render free tier for the backend. Accept spin-down on idle.
Upgrade later if usage warrants it.

### Q3: Audio retention and storage
**Answer:** Use Supabase for both database (PostgreSQL) and file storage.
Audio can be stored in Supabase Storage when the user enables retention.
Free tier of Supabase is sufficient for now.

### Q4: Auth
**Answer:** Multi-user with admin page. Me + friend(s) as users.
Admin can create/manage users. Simple email/password auth via Supabase Auth
is the recommended approach (free, built-in).

### Q5: Evaluations mode (A)
**Answer:** Accept YouTube links instead of uploading speech audio.
The backend will fetch the YouTube transcript (via API or subtitle extraction),
then the user records their evaluation audio for analysis.

### Q6: Progress dashboard
**Answer:** Range selectors: last 7 / 30 / 90 days + custom date range.
Per-mode breakdowns. Weekly aggregation for trends.

### Q7: Usage / budget
**Answer:** ~2 sessions per day, each ~15 minutes.
Total ~30 sessions/month. Low volume — free tiers of all services should suffice.

### Q8: Table Topics timing lights
**Answer:** No visual lights needed. Just record, analyze, show feedback,
and store in history for review.

### Q9: ADRs
**Answer:** Yes — create docs/adr/ with key architectural decisions.

### Q10: TASKS.md format
**Answer:** Rewrite in industry-standard format: P{phase}-T{task} IDs,
branch names, TDD notes, checkboxes, ~200 lines per task max.
