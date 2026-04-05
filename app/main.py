"""FastAPI application init, router registration, and lifespan."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
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


# Serve the React frontend — must be last so API routes take priority
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
