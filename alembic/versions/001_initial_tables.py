"""Create initial tables: users, video_projects, personalized_videos.

Revision ID: 001
Revises:
Create Date: 2026-04-05
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "video_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_video_url", sa.String(), nullable=False),
        sa.Column("source_audio_url", sa.String(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("pause_timestamp_ms", sa.Integer(), nullable=False),
        sa.Column("elevenlabs_voice_id", sa.String(), nullable=True),
        sa.Column("voice_clone_status", sa.String(), server_default="pending"),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("status", sa.String(), server_default="draft"),
        sa.Column("total_names", sa.Integer(), server_default="0"),
        sa.Column("completed_names", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_video_projects_user_id", "video_projects", ["user_id"])
    op.create_index("ix_video_projects_status", "video_projects", ["status"])

    op.create_table(
        "personalized_videos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("video_projects.id"), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("name_audio_url", sa.String(), nullable=True),
        sa.Column("output_video_url", sa.String(), nullable=True),
        sa.Column("status", sa.String(), server_default="pending"),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("processing_started_at", sa.DateTime(), nullable=True),
        sa.Column("processing_completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_personalized_videos_project_id", "personalized_videos", ["project_id"])
    op.create_index("ix_personalized_videos_status", "personalized_videos", ["status"])


def downgrade() -> None:
    op.drop_table("personalized_videos")
    op.drop_table("video_projects")
    op.drop_table("users")
