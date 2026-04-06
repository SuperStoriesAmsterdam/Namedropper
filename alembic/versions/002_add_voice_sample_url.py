"""Add voice_sample_url column to video_projects.

Revision ID: 002
Revises: 001
Create Date: 2026-04-06
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "video_projects",
        sa.Column("voice_sample_url", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("video_projects", "voice_sample_url")
