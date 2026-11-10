# CLAUDE.md — AI Assistant Working Rules for SpeakNara

> These rules apply to every AI interaction in this project. Follow them strictly.

---

## 1. One Task at a Time

- Read `TASKS.md` and find the first unchecked task.
- Create a branch: `git checkout -b feat/P{phase}-T{task}-short-name`
- Complete the full cycle: tests → code → commit → report.
- **Stop** after completing the task. Wait for "next" before starting another.

## 2. Branch Naming

- `feat/P1-T1-backend-scaffold`
- `fix/P2-T3-wpm-calculation`
- `refactor/P3-T6-recorder-component`
- Phase letter matches the task ID in `TASKS.md`.

## 3. Test-Driven Development (TDD)

- **Write tests first** — they must fail (red) before you write any implementation code.
- Run tests after every change: `cd backend && pytest` (backend) or `npx jest` (frontend).
- Every bug fix gets a regression test that fails without the fix.
- Tests must be deterministic: no network, no real LLM calls, no sleeps. Use mocks/fixtures.
- Backend tests: `pytest` with `httpx` TestClient. Frontend tests: `jest` + `@testing-library/react`.
- Aim for ≥80% coverage on business logic (services, analysis, LLM prompts).

## 4. Conventional Commits

```
feat: add whisper transcription service
fix: correct WPM calculation for short speeches
test: add regression test for pause detection edge case
refactor: extract audio validation into separate module
docs: update API spec for YouTube evaluation endpoint
chore: update dependencies
```

- One commit per task. Under ~200 lines of code per commit.
- If a task is larger, split it into sub-tasks in `TASKS.md`.

## 5. Code Style

### Backend (Python)
- **Formatter**: `black` (line length 88)
- **Linter**: `ruff`
- **Types**: `mypy` (strict mode)
- **Imports**: `isort`
- Follow the existing FastAPI patterns in the project
- Use Pydantic v2 for request/response models
- Database: Supabase (PostgreSQL) via `supabase` Python client
- Audio: `faster-whisper` (local, free), `pydub` for format conversion
- LLM: `openai` Python SDK with `base_url="https://api.euron.one/api/v1/euri"`, model from `.env`
- Multi-agent flows: `langgraph` + `langchain-openai` when needed (e.g., evaluation judge agent)

### Frontend (TypeScript / Next.js)
- **Framework**: Next.js App Router (TypeScript)
- **Styling**: Tailwind CSS + shadcn/ui components
- **Components**: Co-locate with pages in `app/` or in `components/` for shared ones
- **Data fetching**: Server components for initial data, React Query / SWR for client-side
- **Auth**: `@supabase/supabase-js` client
- **Charts**: `recharts` for progress dashboard
- **Forms**: React Hook Form + Zod validation

## 6. Secrets & Security

- All secrets in `.env` files (never committed).
- `EURI_API_KEY` — Euron API key
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_SERVICE_KEY` — Supabase service role key (backend only)
- `SUPABASE_JWT_SECRET` — for verifying Supabase JWTs
- Use parameterized queries for all SQL (Supabase client does this by default).
- Validate all user input at the API boundary (Pydantic models).
- Never `eval()` or `exec()` user input.

## 7. LLM Integration

- **API**: Euron API (OpenAI-compatible) at `https://api.euron.one/api/v1/euri`
- **Model**: Set in `.env` (e.g., `claude-sonnet-5-5`)
- **SDK**: `openai` Python SDK with custom `base_url`
- **Multi-agent**: `langgraph` + `langchain-openai` for complex flows (evaluation judge, multi-step analysis)
- **Prompt templates**: Stored in `backend/services/prompts.py` — one template per mode
- **Caching**: Cache LLM responses by (user_id, mode, transcript hash) to avoid redundant calls (P6-T1)
- **Rate limiting**: Per-user limit on LLM calls (P6-T2)

## 8. Database (Supabase)

- PostgreSQL hosted on Supabase
- Auth: Supabase Auth (email/password)
- Storage: Supabase Storage for audio files (when retention enabled)
- Migrations: SQL files in `backend/migrations/`, applied manually or via Supabase CLI
- All tables have `created_at` (TIMESTAMPTZ) and `updated_at` (TIMESTAMPTZ)
- Users table syncs with Supabase Auth via database trigger

## 9. Deployment

- **Frontend**: Vercel free tier
- **Backend**: Render free tier (accepts spin-down on inactivity)
- **Database**: Supabase (always on, generous free tier)
- Environment variables documented in `.env.example`

## 10. After Completing a Task

Report:
1. Task ID and branch name
2. Files changed (with brief description of each)
3. Tests added/run (how to run them)
4. Acceptance criteria met (yes/no for each)
5. Any blockers or concerns
6. Open an end-of-phase summary when all phase tasks are done: coverage, risks, next steps
