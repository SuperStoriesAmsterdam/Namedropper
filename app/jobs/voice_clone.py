"""Background job: clone a voice from an uploaded voice sample.

Downloads the uploaded voice sample audio and sends it to ElevenLabs
for cloning. No longer extracts audio from the video.
"""

import logging

from app.database import SessionLocal
from app.elevenlabs_client import clone_voice as elevenlabs_clone_voice
from app.models import VideoProject
from app.storage import download_file
from app.video_processor import get_duration

logger = logging.getLogger(__name__)


async def clone_voice(ctx, project_id: int):
    """Clone the speaker's voice from the uploaded voice sample.

    Steps:
    1. Download voice sample from R2
    2. Validate video duration and pause timestamp
    3. Send voice sample to ElevenLabs for voice cloning
    4. Store the voice_id on the project record

    Args:
        ctx: ARQ context (unused but required by ARQ).
        project_id: The ID of the VideoProject to process.
    """
    db = SessionLocal()
    try:
        project = db.query(VideoProject).filter(
            VideoProject.id == project_id
        ).first()

        if not project:
            logger.error(f"clone_voice: project {project_id} not found")
            return

        if not project.voice_sample_url:
            project.voice_clone_status = "failed"
            db.commit()
            logger.error(f"clone_voice: project {project_id} has no voice sample")
            return

        project.voice_clone_status = "processing"
        db.commit()

        # Step 1: Download voice sample from R2
        voice_key = project.voice_sample_url.split("/personalvideo/")[-1]
        voice_data = download_file(voice_key)

        # Step 2: Validate video duration and pause timestamp
        source_key = project.source_video_url.split("/personalvideo/")[-1]
        video_data = download_file(source_key)
        duration = get_duration(video_data)
        project.duration_seconds = duration
        db.commit()

        if duration > 60:
            project.voice_clone_status = "failed"
            db.commit()
            logger.error(f"clone_voice: project {project_id} video too long ({duration:.1f}s)")
            return

        if project.pause_timestamp_ms > duration * 1000:
            project.voice_clone_status = "failed"
            db.commit()
            logger.error(
                f"clone_voice: project {project_id} pause timestamp "
                f"({project.pause_timestamp_ms}ms) exceeds video duration ({duration:.1f}s)"
            )
            return

        # Step 3: Clone voice via ElevenLabs using the voice sample
        voice_id = elevenlabs_clone_voice(voice_data, project.id)

        # Step 4: Store voice_id
        project.elevenlabs_voice_id = voice_id
        project.voice_clone_status = "ready"
        db.commit()

        logger.info(f"clone_voice: project {project_id} voice cloned successfully (voice_id={voice_id})")

    except Exception as error:
        logger.exception(f"clone_voice failed for project {project_id}")
        try:
            project.voice_clone_status = "failed"
            db.commit()
        except Exception:
            pass
        raise
    finally:
        db.close()
