"""Add video crawler schema and tables.

Revision ID: 7b93f28d9c1a
Revises: c4e74ec4736e
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "7b93f28d9c1a"
down_revision: str | None = "c4e74ec4736e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "video_crawler"


def upgrade() -> None:
    op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
    op.create_table(
        "crawl_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("discovered_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("accepted_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rejected_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("indexed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ingest_failed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "rejection_reasons",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index("ix_crawler_jobs_status", "crawl_jobs", ["status"], schema=SCHEMA)
    op.create_index("ix_crawler_jobs_lease", "crawl_jobs", ["lease_expires_at"], schema=SCHEMA)
    op.create_table(
        "videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("platform_video_id", sa.String(length=255), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("hashtag", sa.Text(), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("video_url", sa.Text(), nullable=False),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "provenance",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "quality_warnings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ingest_error", sa.Text(), nullable=True),
        sa.Column("ingest_attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("next_ingest_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], [f"{SCHEMA}.crawl_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "platform_video_id", name="uq_crawler_video_native"),
        sa.UniqueConstraint("canonical_url", name="uq_crawler_video_canonical_url"),
        schema=SCHEMA,
    )
    op.create_index("ix_crawler_videos_job_id", "videos", ["job_id"], schema=SCHEMA)
    op.create_index("ix_crawler_videos_indexed_at", "videos", ["indexed_at"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_table("videos", schema=SCHEMA)
    op.drop_table("crawl_jobs", schema=SCHEMA)
    op.execute(sa.text(f"DROP SCHEMA IF EXISTS {SCHEMA}"))
