"""ARQ worker settings for background job processing.

Start the worker with: arq app.worker.WorkerSettings
Or: python3 -m arq app.worker.WorkerSettings
"""

import os

import arq

from app.jobs.video_gen import generate_personalized_video
from app.jobs.voice_clone import clone_voice
from app.jobs.zip_gen import generate_zip


class WorkerSettings:
    """ARQ worker configuration."""

    functions = [clone_voice, generate_personalized_video, generate_zip]

    redis_settings = arq.connections.RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
    )

    max_jobs = 10
    job_timeout = 600  # 10 minutes max per job (video processing can be slow)
    max_tries = 3
