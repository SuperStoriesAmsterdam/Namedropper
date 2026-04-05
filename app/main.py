"""FastAPI application init, router registration, and lifespan."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.errors import api_exception_handler
from app.routers import auth as auth_router
from app.routers import projects as projects_router
from app.routers import upload as upload_router
from app.routers import videos as videos_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)

static_dir = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown tasks for the application."""
    logger.info("Namedropper application starting up")
    yield
    logger.info("Namedropper application shutting down")


app = FastAPI(
    title="Namedropper",
    description="Personalize any video with a spoken name.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(Exception, api_exception_handler)

app.include_router(auth_router.router)
app.include_router(projects_router.router)
app.include_router(upload_router.router)
app.include_router(videos_router.router)


@app.get("/health")
async def health_check():
    """Return a simple health check response."""
    return {"status": "ok"}


# Serve built frontend assets (JS, CSS, images)
if static_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")


@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """Serve index.html for all non-API routes (SPA catch-all)."""
    # Try to serve an actual file first (favicon, etc.)
    file_path = static_dir / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    # Otherwise serve index.html for client-side routing
    return FileResponse(static_dir / "index.html")
