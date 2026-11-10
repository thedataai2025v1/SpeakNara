# ADR-002: Supabase for Database, Auth, and File Storage

**Status**: Accepted  
**Date**: 2026-11-10  
**Deciders**: Project team  
**Technical Story**: P1-T3 (DB migrations), P5-T1 (Auth), P2-T5 (audio storage)

## Context

The application needs:
- **Relational database** for sessions, users, topics, metrics
- **Authentication** with email/password, multi-user support, admin roles
- **File storage** for audio recordings (when retention is enabled)
- **Free tier** to keep costs at $0 for the initial phase

Options considered:
1. **Supabase** — Postgres + Auth + Storage in one service, generous free tier
2. **MongoDB Atlas** — NoSQL, good free tier, but we need relational queries for progress aggregation
3. **Firebase** — Auth + Firestore + Storage, but Firestore has query limitations for our aggregation needs
4. **Self-hosted Postgres** — Free but requires a VPS (costs money or devops effort)
5. **Vercel Postgres** — Limited to Vercel deployments; we need the backend (on Render) to access it too

## Decision

**Supabase for database, authentication, and file storage.**

- **PostgreSQL** on Supabase for all relational data (users, sessions, metrics, topics, random_words, llm_cache)
- **Supabase Auth** for email/password authentication with JWT tokens
- **Supabase Storage** for audio files (when retention is enabled via `store_audio=true`)
- **Supabase Python client** (`supabase` package) for backend database access
- **Supabase JS client** (`@supabase/supabase-js`) for frontend auth

## Consequences

### Pros
- **All-in-one**: Database + Auth + Storage in one service = fewer services to manage
- **Generous free tier**: 500MB database, 1GB storage, 50,000 monthly active users for auth
- **JWT auth built-in**: Supabase handles password hashing, token generation, refresh tokens
- **Row Level Security (RLS)**: Can enforce per-user data isolation at the database level
- **Postgres**: Full SQL support for complex aggregation queries (progress dashboard)
- **Realtime**: Built-in realtime subscriptions (useful for future live feedback features)
- **Good SDKs**: Python and JavaScript clients are well-maintained

### Cons
- **500MB database limit**: May be tight if we store audio blobs in the DB (mitigated by using Supabase Storage for files)
- **1GB storage limit**: For audio files, this is ~20-30 sessions of 30MB each (mitigated by deleting audio by default)
- **Vendor lock-in**: Supabase-specific features (RLS, realtime) may not port easily
- **Free tier limits**: 50,000 MAUs is generous for a 2-user app but may be limiting if we open it to more users later

### Mitigations
- Delete audio by default after analysis (only store in Supabase Storage when `store_audio=true`)
- Archive old sessions beyond 90 days to stay within storage limits
- Use efficient data models: store metrics as JSONB to avoid wide tables

## Alternatives Considered

| Option | DB | Auth | Storage | Free Tier | Verdict |
|--------|----|----|----|----|----|
| **Supabase** | ✅ | ✅ | ✅ | Generous | ✅ Best fit |
| MongoDB Atlas | ✅ | ❌ | ✅ | Good | ❌ No auth, NoSQL |
| Firebase | ✅ (Firestore) | ✅ | ✅ | Good | ❌ Query limitations |
| Self-hosted Postgres | ✅ | ❌ | ❌ | Free but needs VPS | ❌ Devops overhead |
| Vercel Postgres | ✅ | ❌ | ❌ | Limited | ❌ Backend can't access |
