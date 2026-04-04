# Namedropper

Personalize any video with a spoken name. Record once, generate hundreds of personal videos where your own voice says each recipient's first name.

**Product by SuperStories BV**

---

## What it does

1. Upload a short video (max 60 seconds) with a pause where names go
2. Set the timestamp where the pause starts
3. Paste a list of first names
4. Namedropper clones your voice, speaks each name, and splices it into the video
5. Download individual videos or all as ZIP

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 15 |
| Task queue | ARQ + Redis |
| File storage | Cloudflare R2 |
| Frontend | React 18, Vite, TailwindCSS |
| Voice cloning | ElevenLabs |
| Video processing | FFmpeg |
| Deployment | Docker, Coolify |

## Local development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis
- FFmpeg (`brew install ffmpeg` on macOS)
- Node.js 20+

### Setup

```bash
# Clone the repo
git clone git@github.com:SuperStoriesAmsterdam/Namedropper.git
cd Namedropper

# Create .env from example
cp .env.example .env
# Fill in your API keys and database credentials

# Create the database
createdb namedropper

# Install Python dependencies
pip3 install -r requirements.txt

# Run database migrations
python3 -m alembic upgrade head

# Seed demo data
python3 scripts/seed.py

# Start the backend (terminal 1)
uvicorn app.main:app --reload

# Start the ARQ worker (terminal 2)
python3 -m arq app.worker.WorkerSettings

# Start the frontend (terminal 3)
cd frontend && npm install && npm run dev
```

Backend runs at `http://localhost:8000`, frontend at `http://localhost:5173`.

### API docs

Open `http://localhost:8000/docs` for the interactive OpenAPI documentation.

## Production deployment

### Docker

```bash
docker compose up -d
```

This starts four containers: app, worker, PostgreSQL, Redis.

### Coolify

1. Install Coolify on a Hetzner VPS: `curl -fsSL https://get.coolify.io | bash`
2. Add the VPS as a server in Coolify
3. Create a new application pointing to this repo's `docker-compose.yml`
4. Set environment variables in Coolify UI
5. Deploy

## Environment variables

See `.env.example` for all required variables with descriptions.

## Project structure

```
app/
├── main.py              FastAPI app init
├── config.py            Settings from .env
├── database.py          SQLAlchemy engine + session
├── models.py            User, VideoProject, PersonalizedVideo
├── schemas.py           Pydantic request/response schemas
├── errors.py            Error response model
├── auth.py              Magic link authentication
├── email.py             Resend email integration
├── storage.py           Cloudflare R2 client
├── elevenlabs_client.py Voice cloning + TTS
├── video_processor.py   FFmpeg operations
├── worker.py            ARQ worker settings
├── routers/
│   ├── auth.py          Login endpoints
│   ├── projects.py      CRUD + generate + progress + download
│   ├── upload.py        Video upload
│   └── videos.py        Personalized video list + details
└── jobs/
    ├── voice_clone.py   Clone voice background job
    ├── video_gen.py     Generate video per name
    └── zip_gen.py       ZIP all videos for download
frontend/
├── src/
│   ├── pages/           Login, Dashboard, NewProject, ProjectDetail
│   └── hooks/           useAuth, useApi, useSSE
alembic/                 Database migrations
scripts/seed.py          Demo data
```

---

*SuperStories BV — Namedropper v0.1.0*
