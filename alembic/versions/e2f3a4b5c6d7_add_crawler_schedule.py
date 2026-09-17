"""Add idempotent schedule slots and retry state to crawler jobs.

Revision ID: e2f3a4b5c6d7
Revises: 7b93f28d9c1a
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e2f3a4b5c6d7"
down_revision: str | None = "7b93f28d9c1a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("crawl_jobs", sa.Column("schedule_key", sa.String(80)), schema="video_crawler")
    op.add_column(
        "crawl_jobs",
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        schema="video_crawler",
    )
    op.add_column("crawl_jobs", sa.Column("next_attempt_at", sa.DateTime(timezone=True)), schema="video_crawler")
    op.create_unique_constraint("uq_crawler_schedule_key", "crawl_jobs", ["schedule_key"], schema="video_crawler")


def downgrade() -> None:
    op.drop_constraint("uq_crawler_schedule_key", "crawl_jobs", schema="video_crawler", type_="unique")
    op.drop_column("crawl_jobs", "next_attempt_at", schema="video_crawler")
    op.drop_column("crawl_jobs", "attempt_count", schema="video_crawler")
    op.drop_column("crawl_jobs", "schedule_key", schema="video_crawler")
