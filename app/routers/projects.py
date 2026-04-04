"""Project endpoints: CRUD, name management, generation trigger, and SSE progress."""

import asyncio
import json
import logging

import arq
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.config import get_settings
from app.database import SessionLocal, get_db
from app.models import PersonalizedVideo, User, VideoProject
from app.schemas import (
    GenerateResponse,
    NamesInput,
    NamesResponse,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.storage import delete_prefix, generate_signed_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's projects, paginated and sorted by newest first."""
    offset = (page - 1) * per_page

    total = db.query(VideoProject).filter(
        VideoProject.user_id == current_user.id
    ).count()

    projects = db.query(VideoProject).filter(
        VideoProject.user_id == current_user.id
    ).order_by(
        VideoProject.created_at.desc()
    ).offset(offset).limit(per_page).all()

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        page=page,
        per_page=per_page,
        total=total,
    )


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new video project from an uploaded source video."""
    project = VideoProject(
        user_id=current_user.id,
        source_video_url=body.source_video_url,
        pause_timestamp_ms=body.pause_timestamp_ms,
        title=body.title,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    logger.info(f"User {current_user.id} created project {project.id}")
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single project by ID. Scoped to the current user."""
    project = db.query(VideoProject).filter(
        VideoProject.id == project_id,
        VideoProject.user_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
        )

    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    body: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a project's pause timestamp or title."""
    project = db.query(VideoProject).filter(
        VideoProject.id == project_id,
        VideoProject.user_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
        )

    if body.pause_timestamp_ms is not None:
        project.pause_timestamp_ms = body.pause_timestamp_ms
    if body.title is not None:
        project.title = body.title

    db.commit()
    db.refresh(project)

    logger.info(f"User {current_user.id} updated project {project_id}")
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project and all its generated videos.

    Removes all files from R2 and the ElevenLabs voice clone (if any).
    """
    project = db.query(VideoProject).options(
        joinedload(VideoProject.personalized_videos)
    ).filter(
        VideoProject.id == project_id,
        VideoProject.user_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
        )

    # Delete all personalized video records
    db.query(PersonalizedVideo).filter(
        PersonalizedVideo.project_id == project_id
    ).delete()

    # Delete all R2 files for this project
    try:
        delete_prefix(f"{current_user.id}/{project_id}/")
    except Exception:
        logger.exception(f"Failed to delete R2 files for project {project_id}")

    # Delete the ElevenLabs voice clone if one exists
    if project.elevenlabs_voice_id:
        try:
            from app.elevenlabs_client import delete_voice
            delete_voice(project.elevenlabs_voice_id)
        except Exception:
            logger.exception(f"Failed to delete ElevenLabs voice {project.elevenlabs_voice_id}")

    db.delete(project)
    db.commit()

    logger.info(f"User {current_user.id} deleted project {project_id}")


@router.post("/{project_id}/names", response_model=NamesResponse)
async def add_names(
    project_id: int,
    body: NamesInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add names to a project. Deduplicates against existing names."""
    project = db.query(VideoProject).filter(
        VideoProject.id == project_id,
        VideoProject.user_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found."},
        )

    if project.status not in ("draft", "completed"):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "GENERATION_IN_PROGRESS",
                "message": "Cannot add names while generation is in progress.",
            },
        )

    # Get existing names to deduplicate
    existing_names = {
        v.first_name.lower()
        for v in db.query(PersonalizedVideo).filter(
            PersonalizedVideo.project_id == project_id
        ).all()
    }

    new_names = [n for n in body.names if n.lower() not in existing_names]
    duplicates_removed = len(body.names) - len(new_names)

    # Create PersonalizedVideo records for each new name
    for name in new_names:
        video = PersonalizedVideo(
            project_id=project_id,
            first_name=name,
        )
        db.add(video)

    project.total_names = len(existing_names) + len(new_names)
    db.commit()

    logger.info(
        f"User {current_user.id} added {len(new_names)} names to project {project_id} "
        f"({duplicates_removed} duplicates removed)"
    )

    return NamesResponse(
        names_added=len(new_names),
        duplicates_removed=duplicates_removed,
        total_names=project.total_names,
    )


@router.post("/{project_id}/generate", response_model=GenerateResponse)
async def start_generation(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start generating personalized videos for all pending names in a project.

    First clones the voice (if not already done), then enqueues one job per name.
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

    if project.status == "processing":
        raise HTTPException(
            status_code=409,
            detail={
                "code": "GENERATION_IN_PROGRESS",
                "message": "Generation is already in progress.",
            },
        )

    # Check there are names to process
    pending_videos = db.query(PersonalizedVideo).filter(
        PersonalizedVideo.project_id == project_id,
        PersonalizedVideo.status == "pending",
    ).all()

    if not pending_videos:
        raise HTTPException(
            status_code=422,
            detail={"code": "NO_NAMES", "message": "No names to generate videos for."},
        )

    project.status = "processing"
    project.completed_names = 0
    db.commit()

    # Connect to Redis and enqueue jobs
    settings = get_settings()
    redis_pool = await arq.create_pool(
        arq.connections.RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        )
    )

    try:
        # Step 1: Enqueue voice clone job if not already done
        if project.voice_clone_status != "ready":
            await redis_pool.enqueue_job("clone_voice", project.id)
            logger.info(f"Enqueued voice_clone job for project {project_id}")

        # Step 2: Enqueue one video generation job per pending name
        for video_record in pending_videos:
            await redis_pool.enqueue_job(
                "generate_personalized_video",
                video_record.id,
                _defer_by=10 if project.voice_clone_status != "ready" else 0,
            )

        logger.info(
            f"User {current_user.id} started generation for project {project_id}: "
            f"{len(pending_videos)} videos queued"
        )
    finally:
        await redis_pool.close()

    return GenerateResponse(
        message=f"Generation started for {len(pending_videos)} names.",
        total_names=len(pending_videos),
        project_status="processing",
    )


@router.get("/{project_id}/progress")
async def project_progress(
    project_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stream real-time progress updates for a project via Server-Sent Events (SSE).

    Events:
    - video_completed: a name finished processing
    - video_failed: a name failed
    - project_completed: all names done
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

    async def event_stream():
        """Poll the database for progress updates and yield SSE events."""
        seen_video_ids = set()

        while True:
            # Check if the client disconnected
            if await request.is_disconnected():
                break

            # Open a fresh session for each poll to get current state
            poll_db = SessionLocal()
            try:
                current_project = poll_db.query(VideoProject).filter(
                    VideoProject.id == project_id
                ).first()

                if not current_project:
                    break

                # Get newly completed or failed videos
                videos = poll_db.query(PersonalizedVideo).filter(
                    PersonalizedVideo.project_id == project_id,
                    PersonalizedVideo.status.in_(["completed", "failed"]),
                ).all()

                for video in videos:
                    if video.id not in seen_video_ids:
                        seen_video_ids.add(video.id)

                        if video.status == "completed":
                            event_data = {
                                "name": video.first_name,
                                "video_id": video.id,
                                "completed": current_project.completed_names,
                                "total": current_project.total_names,
                            }
                            yield f"event: video_completed\ndata: {json.dumps(event_data)}\n\n"

                        elif video.status == "failed":
                            event_data = {
                                "name": video.first_name,
                                "video_id": video.id,
                                "error": video.error_message or "Unknown error",
                            }
                            yield f"event: video_failed\ndata: {json.dumps(event_data)}\n\n"

                # Check if the project is fully done
                if current_project.status == "completed":
                    event_data = {
                        "project_id": project_id,
                        "total": current_project.total_names,
                    }
                    yield f"event: project_completed\ndata: {json.dumps(event_data)}\n\n"
                    break

                # If project failed entirely, stop streaming
                if current_project.status == "failed":
                    break

            finally:
                poll_db.close()

            await asyncio.sleep(2)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{project_id}/download")
async def download_all(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a ZIP of all completed videos and return a signed download URL.

    If a ZIP already exists, returns it immediately.
    Otherwise enqueues a background job to create one.
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

    completed_count = db.query(PersonalizedVideo).filter(
        PersonalizedVideo.project_id == project_id,
        PersonalizedVideo.status == "completed",
    ).count()

    if completed_count == 0:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "NO_COMPLETED_VIDEOS",
                "message": "No completed videos to download yet.",
            },
        )

    # Check if a ZIP already exists in R2
    zip_key = f"{current_user.id}/{project_id}/download/all_videos.zip"
    try:
        signed_url = generate_signed_url(zip_key)
        return {"status": "ready", "download_url": signed_url}
    except Exception:
        pass

    # Enqueue ZIP generation
    settings = get_settings()
    redis_pool = await arq.create_pool(
        arq.connections.RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        )
    )

    try:
        await redis_pool.enqueue_job("generate_zip", project_id)
    finally:
        await redis_pool.close()

    return {"status": "preparing", "message": "ZIP is being prepared. Check back in a moment."}
