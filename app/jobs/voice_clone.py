"""Background job: clone a voice from the source video's audio.

Triggered after a project is created with a source video and pause timestamp.
Downloads the video, extracts audio, sends to ElevenLabs for cloning.
"""

import logging

from app.database import SessionLocal
from app.elevenlabs_client import clone_voice as elevenlabs_clone_voice
from app.models import VideoProject
from app.storage import download_file, upload_file
from app.video_processor import extract_audio, get_duration

logger = logging.getLogger(__name__)

MINIMUM_AUDIO_DURATION_SECONDS = 10


async def clone_voice(ctx, project_id: int):
    """Clone the speaker's voice from the source video.

    Steps:
    1. Download source video from R2
    2. Extract audio track (WAV)
    3. Upload extracted audio to R2 for reference
    4. Check audio is long enough (min 10 seconds)
    5. Send audio to ElevenLabs for voice cloning
    6. Store the voice_id on the project record

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

        project.voice_clone_status = "processing"
        db.commit()

        # Step 1: Download source video from R2
        # Extract the storage key from the full URL
        source_key = project.source_video_url.split("/personalvideo/")[-1]
        video_data = download_file(source_key)

        # Step 2: Get video duration and validate
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

        # Step 3: Extract audio
        audio_data = extract_audio(video_data)

        if duration < MINIMUM_AUDIO_DURATION_SECONDS:
            project.voice_clone_status = "failed"
            db.commit()
            logger.error(
                f"clone_voice: project {project_id} audio too short ({duration:.1f}s). "
                f"Minimum {MINIMUM_AUDIO_DURATION_SECONDS} seconds required for voice cloning."
            )
            return

        # Step 4: Upload extracted audio to R2
        audio_key = f"{project.user_id}/{project.id}/source_audio.wav"
        audio_url = upload_file(audio_key, audio_data, "audio/wav")
        project.source_audio_url = audio_url
        db.commit()

        # Step 5: Clone voice via ElevenLabs
        voice_id = elevenlabs_clone_voice(audio_data, project.id)

        # Step 6: Store voice_id
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
