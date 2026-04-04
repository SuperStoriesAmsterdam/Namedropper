"""Pydantic request/response schemas for the Personal Video API.

These are transport schemas only — not database models.
Organised by feature area.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ─────────────────────────────────────────────────────

class MagicLinkRequest(BaseModel):
    """Request body for sending a magic link email."""
    email: EmailStr


class MagicLinkResponse(BaseModel):
    """Response after requesting a magic link."""
    message: str


class AuthVerifyResponse(BaseModel):
    """Response after verifying a magic link token."""
    token: str
    user_id: int
    email: str


class UserResponse(BaseModel):
    """Public user information."""
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Upload ───────────────────────────────────────────────────

class UploadResponse(BaseModel):
    """Response after uploading a video file to R2."""
    url: str
    size_bytes: int
    content_type: str


# ── Projects ─────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    """Request body for creating a new video project."""
    source_video_url: str
    pause_timestamp_ms: int
    title: Optional[str] = None

    @field_validator("pause_timestamp_ms")
    @classmethod
    def pause_must_be_positive(cls, value: int) -> int:
        """Ensure pause timestamp is a positive number."""
        if value < 0:
            raise ValueError("Pause timestamp must be a positive number.")
        return value


class ProjectUpdate(BaseModel):
    """Request body for updating a project."""
    pause_timestamp_ms: Optional[int] = None
    title: Optional[str] = None

    @field_validator("pause_timestamp_ms")
    @classmethod
    def pause_must_be_positive(cls, value: Optional[int]) -> Optional[int]:
        """Ensure pause timestamp is a positive number if provided."""
        if value is not None and value < 0:
            raise ValueError("Pause timestamp must be a positive number.")
        return value


class ProjectResponse(BaseModel):
    """Response for a single video project."""
    id: int
    source_video_url: str
    source_audio_url: Optional[str]
    duration_seconds: Optional[float]
    pause_timestamp_ms: int
    voice_clone_status: str
    title: Optional[str]
    status: str
    total_names: int
    completed_names: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Paginated list of projects."""
    projects: list[ProjectResponse]
    page: int
    per_page: int
    total: int


class NamesInput(BaseModel):
    """Request body for adding names to a project."""
    names: list[str]

    @field_validator("names")
    @classmethod
    def validate_names(cls, value: list[str]) -> list[str]:
        """Clean and validate the name list.

        Strips whitespace, capitalizes first letter, removes empties and duplicates.
        """
        MAX_NAMES = 500
        MAX_NAME_LENGTH = 50

        cleaned = []
        seen = set()

        for name in value:
            name = name.strip()
            if not name:
                continue
            if len(name) > MAX_NAME_LENGTH:
                raise ValueError(f"Name '{name[:20]}...' exceeds the {MAX_NAME_LENGTH} character limit.")
            name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
            lower_name = name.lower()
            if lower_name not in seen:
                seen.add(lower_name)
                cleaned.append(name)

        if not cleaned:
            raise ValueError("At least one name is required.")

        if len(cleaned) > MAX_NAMES:
            raise ValueError(f"Maximum {MAX_NAMES} names per batch.")

        return cleaned


class NamesResponse(BaseModel):
    """Response after adding names to a project."""
    names_added: int
    duplicates_removed: int
    total_names: int


# ── Personalized Videos ──────────────────────────────────────

class PersonalizedVideoResponse(BaseModel):
    """Response for a single personalized video."""
    id: int
    first_name: str
    output_video_url: Optional[str]
    status: str
    error_message: Optional[str]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    """Paginated list of personalized videos."""
    videos: list[PersonalizedVideoResponse]
    page: int
    per_page: int
    total: int


class GenerateResponse(BaseModel):
    """Response after starting video generation."""
    message: str
    total_names: int
    project_status: str
