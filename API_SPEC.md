# SpeakNara — API Specification

> Base URL: `{BACKEND_URL}` (e.g., `https://your-backend.onrender.com`)
> Auth: Bearer token (JWT from Supabase Auth) required for all endpoints except `/health`

---

## 1. Health Check

### GET /health

No auth required.

**Response (200):**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "services": {
    "database": "connected",
    "llm": "connected"
  }
}
```

---

## 2. Auth (Delegated to Supabase)

Auth is handled by **Supabase Auth** (email/password). The frontend uses `@supabase/supabase-js` client.

### Flow

1. User signs up → Supabase creates account, triggers DB RPC to set `role = 'user'` in our `users` table
2. User logs in → Supabase returns JWT
3. Frontend sends JWT as `Authorization: Bearer <token>` header on all requests
4. Backend verifies JWT using Supabase JWT secret (`SUPABASE_JWT_SECRET`)
5. Admin users can create/manage other users via the admin UI

### GET /auth/user-info

Verify the current user's token and return their profile.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response (200):**
```json
{
  "id": "550e8400-e29b-41b4-941e-001a00000003",
  "email": "user@example.com",
  "display_name": "John",
  "role": "user"
}
```

**Response (401):**
```json
{
  "error": "Invalid or expired token"
}
```

---

## 3. Admin: User Management

### GET /admin/users

List all users (admin only).

**Headers:**
- `Authorization: Bearer <admin_jwt>`

**Query Parameters:**
- `page`: Integer (default 1)
- `per_page`: Integer (default 20)

**Response (200):**
```json
{
  "users": [
    {
      "id": "550e8400-e29b-41b4-941e-001a00000003",
      "email": "user@example.com",
      "display_name": "John",
      "role": "user",
      "created_at": "2026-11-10T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### POST /admin/users/create

Create a new user (admin only). Sends a confirmation email via Supabase.

**Headers:**
- `Authorization: Bearer <admin_jwt>`

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "display_name": "Jane",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41b4-941e-001a00000004",
  "email": "newuser@example.com",
  "display_name": "Jane",
  "role": "user"
}
```

---

## 4. Audio Analysis (Core Feature)

### POST /audio/analyze

Upload audio (from recording modes) for transcription and analysis.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Request (multipart/form-data):**
- `audio`: File — audio file (WebM/Opus, WAV, MP3; max 50MB, max 5 min)
- `mode`: String — `"impromptu"`, `"table_topics"`, `"storytelling"`, `"prepared_speech"`, `"evaluations"`
- `topic`: String — the topic/prompt the user spoke on (optional)
- `random_words`: Array of strings — 3 words for storytelling mode (optional)
- `store_audio`: Boolean — keep audio in Supabase Storage (default: false)

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41b4-941e-001a00000003",
  "user_id": "550e8400-e29b-41b4-941e-001a00000001",
  "mode": "table_topics",
  "topic": "What would you do if you found a wallet?",
  "metrics": {
    "duration_seconds": 118,
    "word_count": 180,
    "wpm": 92,
    "filler_count": 4,
    "filler_instances": [
      {"word": "um", "timestamp": 12.5},
      {"word": "uh", "timestamp": 45.2}
    ],
    "pause_count": 3,
    "pauses": [
      {"start": 25.0, "end": 28.5, "duration": 3.5},
      {"start": 70.1, "end": 74.8, "duration": 4.7}
    ],
    "avg_pause_seconds": 4.1,
    "longest_pause_seconds": 4.7,
    "avg_pitch_hz": 142,
    "pitch_variation": 18.5,
    "intensity_range_db": 15.2
  },
  "transcript": "What I would do if I found a wallet... um... I think I would first check if there's any ID inside...",
  "llm_feedback": {
    "strengths": [
      "Clear opening statement",
      "Good structure: problem → action → reasoning"
    ],
    "areas_for_improvement": [
      "4 filler words detected — try pausing instead",
      "One 4.7-second pause at 1:10 — consider using a transitional phrase",
      "Speaking rate (92 WPM) is below average — try to reach 130-150 WPM"
    ],
    "score": 6.5,
    "score_breakdown": {
      "content": 7,
      "delivery": 6,
      "language": 6,
      "visual": 7
    },
    "specific_suggestions": [
      "Replace 'um' with a brief pause; this projects more confidence",
      "Use signposting: 'First...', 'Second...', 'Finally...'",
      "Vary your sentence length for more impact"
    ]
  },
  "audio_stored": false,
  "created_at": "2026-11-10T12:30:00Z"
}
```

**Response (400):**
```json
{
  "error": "Audio file too large (max 50MB)"
}
```

---

## 5. Table Topics

### GET /topics/random

Get a random table topic.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response (200):**
```json
{
  "id": 42,
  "text": "What would you do if you found a wallet on the street?",
  "category": "ethical",
  "difficulty": 1
}
```

---

### GET /topics/random-words

Get 3 random words for Storytelling mode.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response (200):**
```json
{
  "words": ["lighthouse", "whisper", "umbrella"]
}
```

---

## 6. YouTube Evaluations

### POST /evaluations/youtube

Submit a YouTube video URL for evaluation. The backend extracts the transcript via YouTube subtitles, then analyzes it through the LLM as a judge.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "evaluation_criteria": "public_speaking"
}
```

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41b4-941e-001a00000004",
  "mode": "evaluations",
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "TED Talk: The Power of Vulnerability",
  "transcript": "Hi, I'm Brené Brown, and I'm a vulnerable kind of professor...",
  "llm_evaluation": {
    "strengths": [
      "Excellent opening hook",
      "Strong use of personal stories",
      "Clear structure with signposting"
    ],
    "areas_for_improvement": [
      "Some sections could be more concise",
      "Occasional repetition of key points"
    ],
    "score": 8.5,
    "score_breakdown": {
      "content": 9,
      "delivery": 8,
      "language": 9,
      "visual": 8
    },
    "takeaways": [
      "Notice how the speaker uses pauses for emphasis",
      "The storytelling arc builds from personal to universal",
      "Direct audience engagement through eye contact (even in recording)"
    ]
  },
  "created_at": "2026-11-10T13:00:00Z"
}
```

**Response (422):**
```json
{
  "error": "Could not extract transcript — no subtitles available for this video"
}
```

---

### POST /evaluations/practice

Submit your own speech audio for evaluation mode. Similar to `/audio/analyze` but uses the evaluation/judge prompt template.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Request (multipart/form-data):**
- `audio`: File — audio file (same constraints as /audio/analyze)
- `evaluation_criteria`: String — `"public_speaking"`, `"storytelling"`, `"persuasion"` (optional, default: "public_speaking")

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41b4-941e-001a00000005",
  "mode": "evaluations",
  "metrics": { /* same as /audio/analyze */ },
  "transcript": "...",
  "llm_evaluation": {
    "strengths": [...],
    "areas_for_improvement": [...],
    "score": 7.0,
    "score_breakdown": { /* same as /audio/analyze */ },
    "takeaways": [...]
  },
  "audio_stored": false,
  "created_at": "2026-11-10T13:30:00Z"
}
```

---

## 7. Progress

### GET /progress/summary

Get aggregated statistics across all your sessions.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `mode`: String — filter by mode (optional)
- `range`: String — `"7d"`, `"30d"`, `"90d"`, or `"custom"` (default: "30d")
- `start_date`: ISO date — required when range is "custom" (optional otherwise)
- `end_date`: ISO date — required when range is "custom" (optional otherwise)

**Response (200):**
```json
{
  "total_sessions": 25,
  "average_wpm": 142,
  "average_filler_count": 6.3,
  "average_score": 7.2,
  "trend": {
    "wpm": [145, 140, 142, 138, 142],
    "filler_count": [10, 8, 7, 6, 5],
    "score": [5, 6, 7, 7, 8]
  },
  "by_mode": {
    "table_topics": { "sessions": 10, "avg_score": 6.8 },
    "storytelling": { "sessions": 5, "avg_score": 7.5 },
    "prepared_speech": { "sessions": 8, "avg_score": 7.9 },
    "evaluations": { "sessions": 2, "avg_score": 8.0 }
  }
}
```

---

### GET /progress/history

Get time-series data for charts.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `metric`: String — `"wpm"`, `"filler_count"`, `"score"`, `"pitch_variation"` (required)
- `mode`: String — filter by mode (optional)
- `range`: String — `"7d"`, `"30d"`, `"90d"`, or `"custom"` (default: "30d")
- `start_date`: ISO date — required when range is "custom" (optional otherwise)
- `end_date`: ISO date — required when range is "custom" (optional otherwise)

**Response (200):**
```json
{
  "data": [
    {"date": "2026-11-01", "value": 145, "label": "Week 1"},
    {"date": "2026-11-03", "value": 140, "label": "Week 2"},
    {"date": "2026-11-05", "value": 142, "label": "Week 3"}
  ]
}
```

---

## 8. Session History

### GET /sessions

List your past sessions.

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Query Parameters:**
- `page`: Integer (default 1)
- `per_page`: Integer (default 20)
- `mode`: String — filter by mode (optional)

**Response (200):**
```json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41b4-941e-001a00000003",
      "mode": "table_topics",
      "topic": "What would you do if you found a wallet?",
      "score": 6.5,
      "wpm": 92,
      "filler_count": 4,
      "duration_seconds": 118,
      "created_at": "2026-11-10T12:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20
}
```

---

### GET /sessions/{id}

Get a single session with full details (transcript, metrics, LLM feedback).

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response (200):**
```json
{
  "id": "550e8400-e29b-41b4-941e-001a00000003",
  "mode": "table_topics",
  "topic": "What would you do if you found a wallet?",
  "metrics": { /* full metrics object */ },
  "transcript": "...",
  "llm_feedback": { /* full LLM feedback object */ },
  "audio_url": null,
  "created_at": "2026-11-10T12:30:00Z"
}
```

**Response (404):**
```json
{
  "error": "Session not found"
}
```

**Response (403):**
```json
{
  "error": "You do not have permission to view this session"
}
```

---

## Error Format (All Endpoints)

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

Common codes: `INVALID_TOKEN`, `EXPIRED_TOKEN`, `INVALID_INPUT`, `FILE_TOO_LARGE`, `SUPPORTED_FORMATS_ONLY`, `LLM_ERROR`, `TRANSCRIPT_NOT_FOUND`, `NOT_FOUND`, `FORBIDDEN`
