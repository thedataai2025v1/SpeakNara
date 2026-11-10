# SpeakNara — Product Requirements Document

> Phase 0 planning. No code until docs are approved.

## 1. Vision

A private Toastmasters-style communication coach for me and a few friends. Record a speech, get AI-powered analysis on pace, fillers, structure, and storytelling — with progress tracking over time.

## 2. Target Users

- **Primary:** Me (the owner) — practicing public speaking daily
- **Secondary:** 1-2 friends who also want to practice
- **Admin:** Me — can create/manage user accounts

## 3. Modes

### 3.1 Table Topics (Impromptu Speaking)

- System shows a random speech prompt/question
- 30-second preparation timer
- Record up to 2 minutes
- **Analysis includes:**
  - Pace (words per minute) — Toastmasters ideal is 100-130 WPM
  - Filler words per minute (um, uh, like, so, you know, etc.)
  - Pauses longer than 2 seconds
  - Structure score: opening, main points, closing
  - LLM-generated improvement suggestions

### 3.2 Storytelling

- System shows 3 random concrete words
- 60-second preparation timer
- Record 2-3 minutes
- **Analysis includes:**
  - Whether all 3 words were used in the story
  - Story arc: setting, conflict, turning point, resolution
  - Sensory detail richness
  - Vocal variety: pitch range and pace changes (especially at climax)
  - 3 weakest sentences with suggested rewrites

### 3.3 Evaluations

Two sub-modes:

**(A) Practice Evaluating Others:**
- Paste a YouTube link to a speech
- Record your evaluation of that speech
- Analysis checks: commend-recommend-commend structure, specificity of feedback, whether you missed key points from the original speech

**(B) Get Evaluated:**
- Record your speech
- Get a Toastmasters-style evaluation (structure, delivery, content, body language suggestions if video, overall score with specific improvement points)

## 4. Progress Dashboard

- Charts of key metrics over time (pace, fillers, pitch range, structure scores)
- **Per-mode breakdown** — compare Table Topics vs Storytelling vs Evaluations
- **Range selectors:** last 7 days, 30 days, 90 days, custom date range
- Weekly aggregation for trend lines

## 5. Non-Goals (V1)

- ❌ No group/club management
- ❌ No video recording (audio only)
- ❌ No real-time coaching during speech
- ❌ No public sharing or leaderboards
- ❌ No mobile app
- ❌ No notifications

## 6. User Stories

| ID | As a... | I want to... | So that... |
|----|---------|-------------|------------|
| US-1 | New user | Sign up with email/password | I can access my own practice data |
| US-2 | Practitioner | Practice Table Topics with random prompts | I improve impromptu speaking |
| US-3 | Practitioner | Practice Storytelling with random words | I improve narrative skills |
| US-4 | Evaluator | Evaluate a YouTube speech and record my evaluation | I practice Toastmasters evaluation skills |
| US-5 | Speaker | Record a speech and get a Toastmasters-style evaluation | I know what to improve |
| US-6 | Practitioner | See my progress over time with charts | I track improvement |
| US-7 | Admin (me) | Create accounts for friends | They can use the app too |
| US-8 | User | Review past sessions and their feedback | I revisit what I learned |

## 7. Acceptance Criteria Per Mode

### Table Topics

- [ ] Random topic shown from a pool of 50+ questions
- [ ] 30s prep timer with countdown display
- [ ] Recording up to 2 minutes
- [ ] Analysis returned within 30 seconds
- [ ] WPM, filler count, pause count, structure score all displayed
- [ ] LLM feedback with 3 specific improvement suggestions

### Storytelling

- [ ] 3 random concrete words shown from a pool of 200+
- [ ] 60s prep timer with countdown display
- [ ] Recording 2-3 minutes
- [ ] Analysis shows which words were used (green/red checkmarks)
- [ ] Story arc score with breakdown (setting, conflict, turning point, resolution)
- [ ] 3 weakest sentences highlighted with rewrites

### Evaluations (A)

- [ ] YouTube URL accepted and transcript fetched
- [ ] My evaluation recording analyzed
- [ ] Commend-recommend-commend structure checked
- [ ] Specificity score given

### Evaluations (B)

- [ ] Speech recording analyzed
- [ ] Toastmasters-style evaluation returned (structure, delivery, content, overall)
- [ ] Specific improvement points with examples

### Progress Dashboard

- [ ] Charts render for pace, fillers, pitch range over time
- [ ] Filterable by mode (Table Topics / Storytelling / Evaluations)
- [ ] Range selector works (7/30/90 days + custom)
- [ ] Data aggregates by week

## 8. Privacy & Data

- Audio deleted after analysis by default
- User can opt-in to store audio (stored in Supabase Storage)
- No data shared with third parties beyond LLM API (for analysis only)
- Each user sees only their own data

## 9. Success Metrics (V1)

- User can complete a full practice session (record → analyze → see results) in under 3 minutes
- LLM feedback is actionable (specific, not generic)
- Progress charts show trends after 5+ sessions
- App loads in under 2 seconds (frontend)

## 10. Open Questions

1. Should we add a "goal setting" feature per mode? (e.g., "reduce fillers to under 2/min")
2. Should we track non-speaking metrics too? (session frequency, streak)
3. YouTube transcript extraction: use YouTube subtitles API, or a third-party service?
