"""SQLAlchemy models for the Personal Video application.

Three models:
- User: a registered user
- VideoProject: one source video + list of names
- PersonalizedVideo: one generated video per name
"""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """A registered user of Personal Video."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    video_projects = relationship("VideoProject", back_populates="user")


class VideoProject(Base):
    """A single video personalization project (one source video + list of names)."""

    __tablename__ = "video_projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Source video
    source_video_url = Column(String, nullable=False)
    source_audio_url = Column(String, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    pause_timestamp_ms = Column(Integer, nullable=False)

    # Voice cloning
    elevenlabs_voice_id = Column(String, nullable=True)
    voice_clone_status = Column(String, default="pending")

    # Project metadata
    title = Column(String, nullable=True)
    status = Column(String, default="draft", index=True)
    total_names = Column(Integer, default=0)
    completed_names = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="video_projects")
    personalized_videos = relationship("PersonalizedVideo", back_populates="project")


class PersonalizedVideo(Base):
    """One personalized video output (one name = one video)."""

    __tablename__ = "personalized_videos"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("video_projects.id"), nullable=False, index=True)

    first_name = Column(String, nullable=False)
    name_audio_url = Column(String, nullable=True)
    output_video_url = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    error_message = Column(String, nullable=True)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    project = relationship("VideoProject", back_populates="personalized_videos")
