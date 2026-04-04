"""Background job: generate a single personalized video for one name.

One job per name. Enqueued when the user clicks "Generate."
Downloads source video, generates name audio via ElevenLabs TTS,
splices it in at the pause point, uploads the final video to R2.
"""

import logging
from datetime import datetime, timezone

from app.database import SessionLocal
from app.elevenlabs_client import generate_name_audio
from app.models import PersonalizedVideo, VideoProject
from app.storage import download_file, upload_file
from app.video_processor import splice_name

logger = logging.getLogger(__name__)


async def generate_personalized_video(ctx, personalized_video_id: int):
    """Generate a personalized video for a single name.

    Steps:
    1. Get the cloned voice_id from the project
    2. Generate name audio via ElevenLabs TTS
    3. Upload name audio to R2
    4. Download source video from R2
    5. Splice name audio into the video at the pause point
    6. Upload final video to R2
    7. Update records and counters

    Args:
        ctx: ARQ context (unused but required by ARQ).
        personalized_video_id: The ID of the PersonalizedVideo record.
    """
    db = SessionLocal()
    try:
        video_record = db.query(PersonalizedVideo).filter(
            PersonalizedVideo.id == personalized_video_id
        ).first()

        if not video_record:
            logger.error(f"generate_personalized_video: record {personalized_video_id} not found")
            return

        project = db.query(VideoProject).filter(
            VideoProject.id == video_record.project_id
        ).first()

        if not project:
            logger.error(f"generate_personalized_video: project {video_record.project_id} not found")
            return

        if not project.elevenlabs_voice_id:
            _fail_video(db, video_record, "Voice clone not ready. Please wait for cloning to complete.")
            return

        video_record.status = "generating_audio"
        video_record.processing_started_at = datetime.now(timezone.utc)
        db.commit()

        # Step 1: Generate name audio via ElevenLabs TTS
        try:
            name_audio_data = generate_name_audio(project.elevenlabs_voice_id, video_record.first_name)
        except Exception:
            _fail_video(db, video_record, f"Failed to generate audio for name '{video_record.first_name}'.")
            raise

        # Step 2: Upload name audio to R2
        name_audio_key = f"{project.user_id}/{project.id}/names/{video_record.first_name.lower()}.mp3"
        name_audio_url = upload_file(name_audio_key, name_audio_data, "audio/mpeg")
        video_record.name_audio_url = name_audio_url
        video_record.status = "splicing"
        db.commit()

        # Step 3: Download source video from R2
        source_key = project.source_video_url.split("/personalvideo/")[-1]
        source_video_data = download_file(source_key)

        # Step 4: Splice name audio into source video
        try:
            output_video_data = splice_name(
                source_video_data,
                name_audio_data,
                project.pause_timestamp_ms,
            )
        except Exception:
            _fail_video(db, video_record, f"Failed to splice video for name '{video_record.first_name}'.")
            raise

        # Step 5: Upload final video to R2
        video_record.status = "uploading"
        db.commit()

        output_key = f"{project.user_id}/{project.id}/output/{video_record.first_name.lower()}.mp4"
        output_url = upload_file(output_key, output_video_data, "video/mp4")

        # Step 6: Update records
        video_record.output_video_url = output_url
        video_record.status = "completed"
        video_record.processing_completed_at = datetime.now(timezone.utc)
        db.commit()

        # Step 7: Update project counter
        completed_count = db.query(PersonalizedVideo).filter(
            PersonalizedVideo.project_id == project.id,
            PersonalizedVideo.status == "completed",
        ).count()

        project.completed_names = completed_count
        db.commit()

        # Step 8: Check if all names are done
        if completed_count >= project.total_names:
            project.status = "completed"
            db.commit()
            logger.info(f"Project {project.id} completed: all {project.total_names} videos generated")

            # Send completion email (import here to avoid circular imports)
            try:
                from app.config import get_settings
                from app.email import send_batch_complete_email
                from app.models import User

                user = db.query(User).filter(User.id == project.user_id).first()
                if user:
                    settings = get_settings()
                    project_url = f"{settings.APP_BASE_URL}/projects/{project.id}"
                    await send_batch_complete_email(
                        user.email, project.title, project.total_names, project_url
                    )
            except Exception:
                logger.exception(f"Failed to send completion email for project {project.id}")

        logger.info(
            f"generate_personalized_video: '{video_record.first_name}' done "
            f"({completed_count}/{project.total_names})"
        )

    except Exception:
        logger.exception(f"generate_personalized_video failed for record {personalized_video_id}")
        raise
    finally:
        db.close()


def _fail_video(db, video_record: PersonalizedVideo, error_message: str) -> None:
    """Mark a personalized video as failed with an error message.

    Args:
        db: The database session.
        video_record: The PersonalizedVideo record to update.
        error_message: A human-readable error description.
    """
    video_record.status = "failed"
    video_record.error_message = error_message
    video_record.processing_completed_at = datetime.now(timezone.utc)
    db.commit()
    logger.error(f"PersonalizedVideo {video_record.id} failed: {error_message}")
