# PRD — Personal Video (Standalone)

**Product:** Personal Video
**Product ID:** `personalvideo`
**Version:** 0.1.0
**Date:** 2026-04-03
**Author:** SuperStories BV
**Status:** Pre-build spec for Claude Code

---

## 1. What This Is

A standalone tool that takes one recorded video + a list of names and produces personalized video files where each recipient's first name is spoken naturally by the original speaker's cloned voice.

**Input:** 1 video (max 60 seconds) + CSV/list of first names
**Output:** N personalized videos, each with the recipient's name spliced in

This tool will later be integrated into Talk to the Hand as the "Personalized Video Welcome" feature. For now, it ships as a standalone product under SuperStories.

---

## 2. Why This Exists

Every survey, feedback request, and outreach email starts the same way: "Dear participant" or "Hi there." It's impersonal. Completion rates are low. People feel like a number.

A personalized video where the sender says "Hi Maria, I'd love to hear your thoughts on..." changes the experience from mass communication to personal invitation. The technology to do this exists (voice cloning + video splicing), but no tool makes it simple enough for a non-technical user to do in 5 minutes.

**Use cases:**
- Talk to the Hand: personalized welcome before voice interviews
- Sales outreach: personalized video messages at scale
- Event invitations: speaker personally inviting each attendee by name
- Training: trainer personally addressing each participant
- HR: manager personally inviting each team member to a feedback session

---

## 3. Stack

Follow the SuperStories platform stack exactly as defined in `SUPERSTORIES-PLATFORM.md` and `CLAUDE.md`.

| Layer | Technology | Why needed |
|-------|-----------|-----------|
| Backend | Python 3.11, FastAPI | Standard stack |
| Database | PostgreSQL 15+ | Store jobs, users, name lists |
| ORM | SQLAlchemy 2.0+ | Standard stack |
| Migrations | Alembic | Standard stack |
| Task queue | ARQ + Redis | Video processing is slow (5-30 sec per name) — must be background jobs |
| File storage | Cloudflare R2 | Store uploaded videos + generated personalized videos |
| Frontend | React 18, Vite, TailwindCSS | Upload UI, progress tracking, download |
| Email | Resend API | Magic link auth, job completion notifications |
| Auth | Magic link (email) | Standard stack |
| Containers | Docker | Standard stack |
| Deployment | Coolify | Standard stack |

### Additional dependencies (not in standard stack)

| Dependency | Purpose | Why |
|-----------|---------|-----|
| **ElevenLabs Python SDK** (`elevenlabs`) | Voice cloning + text-to-speech | Clones the speaker's voice from the uploaded video, then generates each first name spoken in that voice |
| **FFmpeg** (`ffmpeg-python` wrapper) | Video/audio manipulation | Extracts audio from original video, splices cloned name audio into the pause point, outputs final MP4 |
| **pydub** | Audio analysis | Detects the pause/silence in the original audio where the name should be inserted |

**Why ElevenLabs over alternatives:**
- Instant voice cloning from as little as 30 seconds of audio (the uploaded video IS the training data)
- High quality, natural-sounding output
- Simple API: upload audio sample → get voice ID → generate any text
- Supports 29 languages (important for SuperStories' international market)
- Cost: ~$0.01-0.03 per name generation (negligible at scale)

**Why not build our own voice cloning:**
- This is a solved problem. ElevenLabs does it better than we ever will.
- Focus engineering time on the UX and integration, not on ML infrastructure.

---

## 4. How It Works (User Flow)

### Step 1: Record or upload your video

User records a short video (max 60 seconds) with a deliberate pause where names will be inserted.

**Example script the user follows:**
> "Hi ... [2-second pause] ... thanks for taking 5 minutes to share your perspective. I'm really curious to hear what you think about [topic]."

The user can:
- **Upload** an existing video file (MP4, MOV, WebM)
- **Record** directly in the browser (MediaRecorder API)

**Validation:**
- Max file size: 50 MB
- Max duration: 60 seconds
- Accepted formats: MP4, MOV, WebM
- Must contain audio track (reject silent video)

### Step 2: Mark the pause point

After upload, the user sees a simple audio waveform timeline of their video. They click to mark **where the name should be inserted**. This sets the `pause_timestamp_ms` value.

**Alternative (simpler V1):** Skip the waveform. Instead, ask the user: "At what second does the pause for the name start?" with a simple number input. The user plays their video, notes the timestamp, enters it. Less elegant but ships faster.

**Decision for Claude Code: build the simple number input for V1.** The waveform marker is a V2 enhancement.

### Step 3: Add names

User enters first names. Three input methods:
- **Paste a list** — one name per line in a textarea
- **Upload CSV** — single column of first names
- **Type individually** — add one at a time

**Validation:**
- Min 1 name, max 500 names per batch
- Names must be 1-50 characters
- Strip whitespace, capitalize first letter
- Deduplicate (warn user if duplicates found)
- Display the clean list for confirmation before processing

### Step 4: Process

User clicks "Generate." The system:

1. **Extracts audio** from the uploaded video (FFmpeg)
2. **Clones the voice** using ElevenLabs Instant Voice Cloning (upload extracted audio → receive voice_id)
3. **For each name in the list:**
   a. Generate name audio via ElevenLabs TTS using the cloned voice_id
   b. Split original video audio at `pause_timestamp_ms`
   c. Insert name audio at the split point
   d. Merge modified audio back onto the video track
   e. Output as MP4
   f. Upload to R2
4. **Update job status** in real-time (SSE to frontend)

**Processing time estimate:** ~3-5 seconds per name (ElevenLabs TTS ~1-2s, FFmpeg splice ~1-2s, R2 upload ~1s). 50 names ≈ 3-4 minutes. 500 names ≈ 30-40 minutes.

### Step 5: Download

User sees a grid of completed videos. They can:
- **Preview** any individual video (plays in browser)
- **Download individual** video (MP4)
- **Download all** as ZIP
- **Copy share link** for any individual video (public R2 URL, optionally time-limited)

---

## 5. Data Model

```python
# app/models.py

class User(Base):
    """A registered user of Personal Video."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    video_projects = relationship("VideoProject", back_populates="user")


class VideoProject(Base):
    """A single video personalization project (one source video + list of names)."""
    __tablename__ = "video_projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Source video
    source_video_url = Column(String, nullable=False)        # R2 URL of uploaded video
    source_audio_url = Column(String, nullable=True)         # R2 URL of extracted audio
    duration_seconds = Column(Float, nullable=True)          # Duration of source video
    pause_timestamp_ms = Column(Integer, nullable=False)     # Where to insert the name

    # Voice cloning
    elevenlabs_voice_id = Column(String, nullable=True)      # Cloned voice ID from ElevenLabs
    voice_clone_status = Column(String, default="pending")   # pending | processing | ready | failed

    # Project metadata
    title = Column(String, nullable=True)                    # Optional project name
    status = Column(String, default="draft")                 # draft | processing | completed | failed
    total_names = Column(Integer, default=0)
    completed_names = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="video_projects")
    personalized_videos = relationship("PersonalizedVideo", back_populates="project")


class PersonalizedVideo(Base):
    """One personalized video output (one name = one video)."""
    __tablename__ = "personalized_videos"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("video_projects.id"), nullable=False, index=True)

    first_name = Column(String, nullable=False)               # The name spoken in this video
    name_audio_url = Column(String, nullable=True)            # R2 URL of generated name audio
    output_video_url = Column(String, nullable=True)          # R2 URL of final personalized video
    status = Column(String, default="pending")                # pending | generating_audio | splicing | uploading | completed | failed
    error_message = Column(String, nullable=True)             # If failed, why
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    project = relationship("VideoProject", back_populates="personalized_videos")
```

---

## 6. API Endpoints

All endpoints follow `CLAUDE.md` conventions: `response_model` set, docstrings, auth via `Depends(get_current_user)`, consistent error shape.

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/magic-link` | Send magic link to email |
| GET | `/api/auth/verify` | Verify magic link token, create session |
| POST | `/api/auth/logout` | End session |

### Projects

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects` | List user's projects (paginated) |
| POST | `/api/projects` | Create new project (upload source video) |
| GET | `/api/projects/{id}` | Get project details + status |
| PATCH | `/api/projects/{id}` | Update project (set pause_timestamp_ms, title) |
| DELETE | `/api/projects/{id}` | Delete project + all generated videos |
| POST | `/api/projects/{id}/names` | Add names to project (textarea or CSV) |
| POST | `/api/projects/{id}/generate` | Start generation (enqueues background jobs) |
| GET | `/api/projects/{id}/progress` | SSE endpoint — real-time progress updates |

### Videos

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects/{id}/videos` | List all personalized videos for a project (paginated) |
| GET | `/api/projects/{id}/videos/{video_id}` | Get single video details + download URL |
| GET | `/api/projects/{id}/download` | Generate ZIP of all completed videos, return download URL |

### Upload

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload/video` | Upload source video file to R2, return URL |

---

## 7. Background Jobs

All jobs live in `app/jobs/` per `CLAUDE.md` conventions. Each job is idempotent, has try/except with logging, opens its own database session.

### `clone_voice`
**Trigger:** After source video is uploaded and pause_timestamp_ms is set
**What it does:**
1. Download source video from R2
2. Extract audio track using FFmpeg (`ffmpeg -i input.mp4 -vn -acodec pcm_s16le output.wav`)
3. Upload extracted audio to R2 (keep as reference)
4. Send audio to ElevenLabs Instant Voice Cloning API → receive `voice_id`
5. Store `voice_id` on the VideoProject record
6. Update `voice_clone_status` to "ready"

**Error handling:**
- ElevenLabs API timeout → retry up to 3 times
- Audio too short (< 10 seconds) → fail with clear message: "Video must be at least 10 seconds for voice cloning to work"
- ElevenLabs quota exceeded → fail with message: "Voice generation quota reached. Please try again later."

### `generate_personalized_video`
**Trigger:** One job per name, enqueued when user clicks "Generate"
**What it does:**
1. Get the cloned `voice_id` from the project
2. Call ElevenLabs TTS: generate audio of just the first name using the cloned voice
   - Use `stability=0.7`, `similarity_boost=0.8` for natural but consistent output
   - Model: `eleven_multilingual_v2` (supports international names)
3. Upload name audio to R2
4. Download the source video from R2 (cache locally if multiple names processing)
5. Use FFmpeg to:
   a. Split source audio at `pause_timestamp_ms`
   b. Concatenate: `[audio_before_pause]` + `[name_audio]` + `[audio_after_pause]`
   c. Merge new audio onto original video track
   d. Output as MP4 (H.264 video, AAC audio)
6. Upload final video to R2
7. Update PersonalizedVideo record with output_video_url and status="completed"
8. Update project's `completed_names` counter
9. If all names completed → update project status to "completed", send email notification

**FFmpeg command pattern:**
```bash
# Extract audio
ffmpeg -i source.mp4 -vn -acodec pcm_s16le source_audio.wav

# Split audio at pause point (e.g., 3500ms)
ffmpeg -i source_audio.wav -t 3.5 before_pause.wav
ffmpeg -i source_audio.wav -ss 3.5 after_pause.wav

# Concatenate: before + name + after
ffmpeg -i "concat:before_pause.wav|name_maria.wav|after_pause.wav" -acodec pcm_s16le combined.wav

# Merge new audio back onto video (keep original video track)
ffmpeg -i source.mp4 -i combined.wav -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output_maria.mp4
```

**Note for Claude Code:** The concat filter is more reliable than the concat protocol for this use case. Use:
```bash
ffmpeg -i before.wav -i name.wav -i after.wav \
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]" \
  -map "[out]" combined.wav
```

### `generate_zip`
**Trigger:** User clicks "Download all"
**What it does:**
1. Collect all completed video URLs for the project
2. Download each from R2
3. Create ZIP file with naming: `{first_name}.mp4`
4. Upload ZIP to R2 with a time-limited URL (24 hours)
5. Return URL to frontend

---

## 8. ElevenLabs Integration Details

### API calls used

**1. Instant Voice Clone**
```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

voice = client.clone(
    name=f"project_{project_id}",
    description="Voice clone for personalized video",
    files=[extracted_audio_file]
)
voice_id = voice.voice_id
```

**2. Text-to-Speech (per name)**
```python
audio = client.generate(
    text=first_name,
    voice=voice_id,
    model="eleven_multilingual_v2",
    voice_settings={
        "stability": 0.7,
        "similarity_boost": 0.8
    }
)
# audio is a generator of bytes — write to file
with open(f"name_{first_name}.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

**3. Delete voice clone (cleanup)**
```python
client.voices.delete(voice_id)
```

After a project is completed (or deleted), delete the voice clone from ElevenLabs to stay within the voice limit.

### ElevenLabs pricing (as of April 2026)

| Plan | Price | Characters/month | Instant clones |
|------|-------|------------------|----------------|
| Free | $0 | 10,000 | 3 voices |
| Starter | $5/mo | 30,000 | 10 voices |
| Creator | $22/mo | 100,000 | 30 voices |
| Pro | $99/mo | 500,000 | 160 voices |

A first name is ~5-10 characters. At 100,000 chars/month (Creator plan), that's ~10,000-20,000 name generations. More than enough for launch.

### Required .env variables

```bash
ELEVENLABS_API_KEY=           # API key from elevenlabs.io dashboard
ELEVENLABS_MODEL=eleven_multilingual_v2   # Default model for TTS
```

---

## 9. Frontend Pages

Built with React 18 + Vite + TailwindCSS per standard stack. Design system matches TTH: Space Grotesk headings, Roboto Serif body (or just Space Grotesk throughout for a tool UI), `#dc2626` red accent, `#fdfbf7` off-white background.

### Pages

**1. Landing / Login**
- Simple page: headline "Personalize any video with a name" + magic link login
- Show example: before/after video comparison

**2. Dashboard (`/dashboard`)**
- List of user's projects with status badges (draft / processing / completed)
- "New project" button
- Each project card shows: title, date, total names, completed count, status

**3. New Project (`/projects/new`)**
- Step 1: Upload or record video
- Step 2: Set pause timestamp (simple number input: "At what second does the pause start?") + video playback so they can check
- Step 3: Add names (textarea, one per line, or CSV upload)
- Step 4: Review (show video thumbnail + cleaned name list + "Generate X videos" button)

**4. Project Detail (`/projects/:id`)**
- Source video player
- Progress bar (X of Y completed) — updates via SSE
- Grid of generated videos with status per name:
  - Pending: gray badge
  - Processing: yellow badge + spinner
  - Completed: green badge + play button + download button
  - Failed: red badge + error message + retry button
- "Download all (ZIP)" button — appears when all complete
- "Share" — copy individual video link

### Real-time progress

Use Server-Sent Events (SSE) per `CLAUDE.md` conditional stack. The `/api/projects/{id}/progress` endpoint streams updates:

```json
{"event": "video_completed", "data": {"name": "Maria", "video_id": 42, "completed": 15, "total": 50}}
{"event": "video_failed", "data": {"name": "Xiǎomíng", "video_id": 43, "error": "TTS generation failed"}}
{"event": "project_completed", "data": {"project_id": 7, "total": 50, "zip_url": "..."}}
```

---

## 10. File Storage Structure (R2)

```
personalvideo/
├── {user_id}/
│   ├── {project_id}/
│   │   ├── source.mp4              ← Original uploaded video
│   │   ├── source_audio.wav        ← Extracted audio
│   │   ├── names/
│   │   │   ├── maria.mp3           ← Generated name audio
│   │   │   ├── thomas.mp3
│   │   │   └── ...
│   │   ├── output/
│   │   │   ├── maria.mp4           ← Final personalized video
│   │   │   ├── thomas.mp4
│   │   │   └── ...
│   │   └── download/
│   │       └── all_videos.zip      ← Generated on demand, TTL 24h
```

R2 public URL: `https://media.superstories.com/personalvideo/{user_id}/{project_id}/output/{name}.mp4`

---

## 11. Environment Variables

Add these to `.env.example` alongside the standard SuperStories variables from `SUPERSTORIES-PLATFORM.md`:

```bash
# ── Personal Video specific ─────────────────────────────────
ELEVENLABS_API_KEY=              # ElevenLabs API key for voice cloning + TTS
ELEVENLABS_MODEL=eleven_multilingual_v2  # TTS model (supports international names)

# ── Standard SuperStories variables (from SUPERSTORIES-PLATFORM.md) ──
DATABASE_URL=postgresql://user:password@localhost:5432/personalvideo
REDIS_HOST=localhost
REDIS_PORT=6379
R2_ENDPOINT_URL=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=personalvideo
R2_PUBLIC_URL=https://media.superstories.com
RESEND_API_KEY=
EMAIL_FROM=noreply@superstories.nl
APP_SECRET_KEY=
APP_BASE_URL=https://personalvideo.superstories.com
```

---

## 12. FFmpeg Installation

FFmpeg must be available on the system. In the Dockerfile:

```dockerfile
# In the runtime stage, add FFmpeg
FROM python:3.11-slim AS runtime
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
```

For local development on macOS:
```bash
brew install ffmpeg
```

The Python wrapper `ffmpeg-python` provides a clean API:
```python
import ffmpeg

# Example: extract audio
ffmpeg.input("source.mp4").output("audio.wav", vn=None, acodec="pcm_s16le").run()
```

Add `ffmpeg-python` to `requirements.txt`.

---

## 13. Error Handling

Follow `CLAUDE.md` error patterns. Specific error codes for this product:

| Code | HTTP | When |
|------|------|------|
| `VIDEO_TOO_LARGE` | 413 | Upload exceeds 50 MB |
| `VIDEO_TOO_LONG` | 422 | Video duration exceeds 60 seconds |
| `VIDEO_NO_AUDIO` | 422 | Video has no audio track |
| `INVALID_VIDEO_FORMAT` | 422 | Not MP4, MOV, or WebM |
| `TOO_MANY_NAMES` | 422 | More than 500 names in batch |
| `NO_NAMES` | 422 | Name list is empty |
| `VOICE_CLONE_FAILED` | 502 | ElevenLabs voice cloning API error |
| `TTS_FAILED` | 502 | ElevenLabs TTS API error |
| `TTS_QUOTA_EXCEEDED` | 429 | ElevenLabs character quota reached |
| `FFMPEG_ERROR` | 500 | FFmpeg processing failed |
| `PAUSE_OUT_OF_RANGE` | 422 | pause_timestamp_ms is beyond video duration |
| `PROJECT_NOT_FOUND` | 404 | Project doesn't exist or belongs to another user |
| `GENERATION_IN_PROGRESS` | 409 | Tried to start generation while already processing |

---

## 14. Security Considerations

Per `CLAUDE.md` section 6:

- **Multi-tenant isolation:** Every query scopes to `current_user.id`. User A cannot see or download User B's videos.
- **File access:** R2 URLs for output videos should be either:
  - Behind auth (proxy through FastAPI — safer, slightly slower)
  - Time-limited signed URLs (faster, sufficient for MVP)
  - **Decision: use signed URLs for V1.** Simpler, performs better for video streaming.
- **Voice data:** Voice clones are personal biometric data. Delete from ElevenLabs when project is deleted. Note in privacy policy.
- **Upload validation:** Validate file type server-side (don't trust Content-Type header). Check file magic bytes.

---

## 15. Scope for V1 (Build This)

**In scope:**
- [ ] Upload video (MP4, MOV, WebM, max 50 MB, max 60 sec)
- [ ] Set pause timestamp (number input in seconds)
- [ ] Add names (textarea paste, one per line)
- [ ] Voice cloning via ElevenLabs
- [ ] Name audio generation via ElevenLabs TTS
- [ ] FFmpeg audio splice + video merge
- [ ] Background processing via ARQ
- [ ] Real-time progress via SSE
- [ ] Preview individual videos in browser
- [ ] Download individual video
- [ ] Download all as ZIP
- [ ] Magic link auth
- [ ] Dashboard with project list
- [ ] Delete project (cleanup R2 + ElevenLabs voice)
- [ ] Email notification when batch is complete

**Out of scope (V2+):**
- [ ] In-browser video recording (MediaRecorder API)
- [ ] Waveform-based visual pause marker
- [ ] CSV upload for names
- [ ] Share links (public URLs for individual videos)
- [ ] TTH integration (auto-generate from participant list)
- [ ] Batch templates (save a video for reuse with different name lists)
- [ ] Analytics (which videos were viewed)
- [ ] Stripe billing
- [ ] Licence key validation (add when commercializing)

---

## 16. Project Structure

Per `CLAUDE.md` section 3:

```
personalvideo/
├── app/
│   ├── main.py              ← FastAPI app init, router registration, lifespan
│   ├── config.py            ← Settings via pydantic-settings (reads .env)
│   ├── database.py          ← SQLAlchemy engine, session, Base
│   ├── models.py            ← User, VideoProject, PersonalizedVideo
│   ├── schemas.py           ← Pydantic request/response schemas
│   ├── errors.py            ← Error response model + exception handlers
│   ├── auth.py              ← Magic link generation + verification
│   ├── email.py             ← Resend email (magic links + completion notifications)
│   ├── storage.py           ← Cloudflare R2 (copy from platform doc)
│   ├── worker.py            ← ARQ worker settings
│   ├── elevenlabs_client.py ← ElevenLabs API wrapper (voice clone + TTS)
│   ├── video_processor.py   ← FFmpeg operations (extract audio, splice, merge)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          ← Magic link endpoints
│   │   ├── projects.py      ← CRUD + generate + progress SSE
│   │   ├── videos.py        ← List, get, download individual/ZIP
│   │   └── upload.py        ← Video file upload to R2
│   └── jobs/
│       ├── __init__.py
│       ├── voice_clone.py   ← clone_voice job
│       ├── video_gen.py     ← generate_personalized_video job
│       └── zip_gen.py       ← generate_zip job
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoUploader.jsx
│   │   │   ├── PauseTimestampInput.jsx
│   │   │   ├── NameListInput.jsx
│   │   │   ├── ProgressTracker.jsx
│   │   │   ├── VideoGrid.jsx
│   │   │   └── VideoPlayer.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── NewProject.jsx
│   │   │   └── ProjectDetail.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   └── useSSE.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── alembic/
├── tests/
│   ├── conftest.py
│   ├── test_projects.py
│   ├── test_videos.py
│   ├── test_upload.py
│   └── test_video_processor.py
├── scripts/
│   └── seed.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── CLAUDE.md                ← Copy from SaaS/CLAUDE.md
└── README.md
```

---

## 17. Requirements.txt

```
# Core
fastapi==0.110.*
uvicorn[standard]==0.29.*
sqlalchemy==2.0.*
alembic==1.13.*
psycopg2-binary==2.9.*
pydantic==2.6.*
pydantic-settings==2.2.*

# Background jobs
arq==0.25.*
redis==5.0.*

# File storage
boto3==1.34.*

# Email
resend==0.8.*

# Auth
pyjwt==2.8.*
cryptography==42.*

# ElevenLabs
elevenlabs==1.*

# Video processing
ffmpeg-python==0.2.*

# HTTP client
httpx==0.27.*

# Dev
pytest==8.*
pytest-asyncio==0.23.*
```

---

## 18. Build Order for Claude Code

Follow this sequence. Each step should be fully working before moving to the next.

### Phase 1: Backend foundation
1. Set up project structure (files, folders per section 16)
2. `config.py` — pydantic-settings reading `.env`
3. `database.py` — SQLAlchemy engine + session
4. `models.py` — all three models (User, VideoProject, PersonalizedVideo)
5. `errors.py` — error response model + global handler
6. `main.py` — FastAPI app init with lifespan
7. Alembic init + first migration
8. `scripts/seed.py` — create a demo user

### Phase 2: Auth
9. `auth.py` — magic link generation + verification
10. `email.py` — Resend integration for magic links
11. `routers/auth.py` — magic link endpoints

### Phase 3: Upload + Project CRUD
12. `storage.py` — R2 client (copy from platform doc)
13. `routers/upload.py` — video upload endpoint with validation
14. `schemas.py` — all request/response schemas
15. `routers/projects.py` — CRUD endpoints (create, list, get, update, delete)

### Phase 4: Video processing core
16. `elevenlabs_client.py` — wrapper: `clone_voice(audio_file)`, `generate_name_audio(voice_id, name)`, `delete_voice(voice_id)`
17. `video_processor.py` — wrapper: `extract_audio(video_path)`, `splice_name(source_video, name_audio, pause_ms)`, `get_duration(video_path)`
18. `worker.py` — ARQ worker settings
19. `jobs/voice_clone.py` — clone_voice background job
20. `jobs/video_gen.py` — generate_personalized_video background job
21. `jobs/zip_gen.py` — generate_zip background job

### Phase 5: Generation endpoints + SSE
22. Add `POST /api/projects/{id}/generate` to `routers/projects.py`
23. Add `GET /api/projects/{id}/progress` SSE endpoint
24. `routers/videos.py` — list, get, download endpoints
25. Email notification on batch completion

### Phase 6: Frontend
26. Vite + React + Tailwind setup
27. `Login.jsx` — magic link flow
28. `Dashboard.jsx` — project list
29. `NewProject.jsx` — multi-step form (upload → timestamp → names → generate)
30. `ProjectDetail.jsx` — progress + video grid + download
31. `useSSE.js` — hook for real-time progress
32. `useAuth.js` — auth state management

### Phase 7: Docker + deploy
33. Dockerfile (with FFmpeg installed)
34. docker-compose.yml
35. `.env.example` with all variables documented
36. README.md with setup instructions

---

## 19. Testing Checklist

Per `CLAUDE.md` section 11:

- [ ] Auth: magic link send, verify, expired link rejected, used link rejected
- [ ] Upload: valid video accepted, oversized rejected, wrong format rejected, no-audio rejected
- [ ] Projects: CRUD operations, multi-tenant isolation (user A can't see user B's projects)
- [ ] Names: validation (empty, too many, duplicates, special characters, international names)
- [ ] Generation: happy path (1 name), batch (10 names), pause_timestamp out of range
- [ ] ElevenLabs mock: test that API errors are handled gracefully
- [ ] FFmpeg mock: test that processing errors are handled gracefully
- [ ] SSE: progress events fire correctly
- [ ] ZIP: generated correctly with right filenames
- [ ] Cleanup: deleting project removes R2 files + ElevenLabs voice clone

---

## 20. Integration Path to TTH (Future)

When integrating into Talk to the Hand:

1. **TTH interview creation flow** gets a new optional step: "Add a video welcome"
2. Interviewer uploads/records a welcome video in TTH
3. TTH already has the participant list with first names
4. When interview is published → TTH calls the Personal Video pipeline (either as internal module or API call to standalone service)
5. Each participant's interview page shows their personalized welcome video before the first question
6. No extra work for the interviewer — they record once, every participant gets a personal version

**Architecture decision for integration:** Import the processing code as a Python module into TTH's codebase (not a separate service call). The `elevenlabs_client.py` and `video_processor.py` modules are designed to be portable.

---

*SuperStories BV — Personal Video PRD — v0.1.0 — 2026-04-03*
