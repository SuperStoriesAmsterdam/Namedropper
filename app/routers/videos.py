"""Personalized video endpoints: list and get individual."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import PersonalizedVideo, User, VideoProject
from app.schemas import PersonalizedVideoResponse, VideoListResponse
from app.storage import generate_signed_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/videos", tags=["videos"])


def _get_user_project(project_id: int, current_user: User, db: Session) -> VideoProject:
    """Fetch a project scoped to the current user, or raise 404.

    Args:
        project_id: The project ID from the URL path.
        current_user: The authenticated user.
        db: The database session.

    Returns:
        The VideoProject instance.

    Raises:
        HTTPException: If the project is not found or belongs to another user.
    """
    project = db.query(VideoProject).filter(
        VideoProject.id == project_id,
        VideoProject.user_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
        )

    return project


@router.get("", response_model=VideoListResponse)
async def list_videos(
    project_id: int,
    page: int = 1,
    per_page: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all personalized videos for a project, paginated."""
    _get_user_project(project_id, current_user, db)

    offset = (page - 1) * per_page

    total = db.query(PersonalizedVideo).filter(
        PersonalizedVideo.project_id == project_id
    ).count()

    videos = db.query(PersonalizedVideo).filter(
        PersonalizedVideo.project_id == project_id
    ).order_by(
        PersonalizedVideo.first_name.asc()
    ).offset(offset).limit(per_page).all()

    return VideoListResponse(
        videos=[PersonalizedVideoResponse.model_validate(v) for v in videos],
        page=page,
        per_page=per_page,
        total=total,
    )


@router.get("/{video_id}", response_model=PersonalizedVideoResponse)
async def get_video(
    project_id: int,
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single personalized video with a signed download URL."""
    _get_user_project(project_id, current_user, db)

    video = db.query(PersonalizedVideo).filter(
        PersonalizedVideo.id == video_id,
        PersonalizedVideo.project_id == project_id,
    ).first()

    if not video:
        raise HTTPException(
            status_code=404,
            detail={"code": "VIDEO_NOT_FOUND", "message": "Video not found."},
        )

    response = PersonalizedVideoResponse.model_validate(video)

    # Replace the R2 URL with a signed URL for streaming/download
    if video.output_video_url:
        video_key = video.output_video_url.split("/personalvideo/")[-1]
        response.output_video_url = generate_signed_url(video_key)

    return response
