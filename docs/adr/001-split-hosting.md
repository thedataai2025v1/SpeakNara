# ADR-001: Vercel Frontend + Render Backend (Split Hosting)

**Status**: Accepted  
**Date**: 2026-11-10  
**Deciders**: Project team  
**Technical Story**: P6-T3 (Vercel deployment), P6-T4 (Render deployment)

## Context

We need to host both the frontend (Next.js) and the backend (FastAPI Python) for the SpeakNara public speaking coach. Options considered:

1. **Vercel only** — Vercel supports Next.js natively but has limited Python support (Serverless Functions only, cold starts, memory limits for audio processing).
2. **Render only** — Render can host both a static Next.js app and a Python worker, but frontend deployment experience is better on Vercel.
3. **Railway / Fly.io** — Railway charges per-minute (not ideal for free tier); Fly has egress costs.
4. **Vercel (frontend) + Render (backend)** — Split: Vercel for the Next.js frontend, Render for the FastAPI backend.

## Decision

**Vercel for frontend, Render for backend.**

- Frontend (Next.js + shadcn/ui) deploys to Vercel free tier
- Backend (FastAPI + faster-whisper + LLM calls) deploys to Render free tier
- Both communicate via HTTP (frontend calls backend REST API)
- Database is Supabase (separate, always-on free tier)

## Consequences

### Pros
- Vercel has the best Next.js deployment experience (instant builds, preview deployments, edge caching)
- Render free tier supports long-running Python processes (needed for audio processing)
- No per-minute charges (Render only charges when active, spins down on free tier)
- Clear separation of concerns: frontend team can work independently of backend
- Supabase handles DB + auth + storage — no need to self-host Postgres

### Cons
- **Spin-down on Render**: Free tier spins down after 15 min of inactivity. First request after spin-down has a ~30s cold start.
  - **Mitigation**: Health check pings every 10 min (can use UptimeRobot free tier for 50 monitors)
- **Two deployments to manage**: Must configure env vars in both Vercel and Render dashboards
- **CORS**: Must configure CORS on the backend to allow the Vercel frontend domain
- **Cross-origin calls**: Frontend must call backend API via HTTPS (configured via `NEXT_PUBLIC_API_URL` env var)

## Alternatives Considered

| Option | Frontend | Backend | Cost | Verdict |
|--------|----------|---------|------|---------|
| Vercel only | ✅ | ❌ (Python limited) | Free | ❌ No full Python support |
| Render only | ✅ | ✅ | Free | ⚠️ OK but Vercel is better for Next.js |
| Railway | ✅ | ✅ | $5/mo+ | ❌ Costs money |
| Fly.io | ✅ | ✅ | $7/mo+ egress | ❌ Egress costs |
| **Vercel + Render** | ✅ | ✅ | **Free** | ✅ Best of both |
