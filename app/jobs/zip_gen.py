"""Background job: generate a ZIP file of all completed videos for a project.

Triggered when the user clicks "Download all."
Downloads all completed videos from R2, zips them, uploads the ZIP to R2,
and returns a time-limited signed URL.
"""

import io
import logging
import zipfile

from app.database import SessionLocal
from app.models import PersonalizedVideo, VideoProject
from app.storage import download_file, generate_signed_url, upload_file

logger = logging.getLogger(__name__)

ZIP_URL_EXPIRY_SECONDS = 86400  # 24 hours


async def generate_zip(ctx, project_id: int) -> str:
    """Generate a ZIP of all completed personalized videos for a project.

    Steps:
    1. Query all completed PersonalizedVideo records for the project
    2. Download each video from R2
    3. Create a ZIP file in memory
    4. Upload the ZIP to R2
    5. Return a signed URL valid for 24 hours

    Args:
        ctx: ARQ context (unused but required by ARQ).
        project_id: The ID of the VideoProject.

    Returns:
        A signed URL for downloading the ZIP file.
    """
    db = SessionLocal()
    try:
        project = db.query(VideoProject).filter(
            VideoProject.id == project_id
        ).first()

        if not project:
            logger.error(f"generate_zip: project {project_id} not found")
            return ""

        completed_videos = db.query(PersonalizedVideo).filter(
            PersonalizedVideo.project_id == project_id,
            PersonalizedVideo.status == "completed",
        ).all()

        if not completed_videos:
            logger.warning(f"generate_zip: no completed videos for project {project_id}")
            return ""

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for video_record in completed_videos:
                if not video_record.output_video_url:
                    continue

                # Download from R2
                video_key = video_record.output_video_url.split("/personalvideo/")[-1]
                try:
                    video_data = download_file(video_key)
                except Exception:
                    logger.exception(
                        f"generate_zip: failed to download video for '{video_record.first_name}'"
                    )
                    continue

                # Add to ZIP with a clean filename
                filename = f"{video_record.first_name}.mp4"
                zip_file.writestr(filename, video_data)

        zip_data = zip_buffer.getvalue()
        logger.info(f"generate_zip: created ZIP for project {project_id}: {len(zip_data)} bytes")

        # Upload ZIP to R2
        zip_key = f"{project.user_id}/{project.id}/download/all_videos.zip"
        upload_file(zip_key, zip_data, "application/zip")

        # Generate signed URL
        signed_url = generate_signed_url(zip_key, ZIP_URL_EXPIRY_SECONDS)

        logger.info(f"generate_zip: project {project_id} ZIP uploaded and signed URL generated")
        return signed_url

    except Exception:
        logger.exception(f"generate_zip failed for project {project_id}")
        raise
    finally:
        db.close()
