"""Make crawler enrichment fields optional for discovery-only jobs.

Revision ID: d4e9a2c1f7b0
Revises: 7b93f28d9c1a
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d4e9a2c1f7b0"
down_revision: str | None = "7b93f28d9c1a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "video_crawler"


def _alter_existing_columns(*, nullable: bool) -> None:
    nullability = "DROP NOT NULL" if nullable else "SET NOT NULL"
    op.execute(
        sa.text(
            f"""
            DO $$
            DECLARE
                candidate_column text;
            BEGIN
                FOREACH candidate_column IN ARRAY ARRAY[
                    'transcript', 'image_url', 'summary', 'video_url'
                ]
                LOOP
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_schema = '{SCHEMA}'
                          AND table_name = 'videos'
                          AND columns.column_name = candidate_column
                    ) THEN
                        EXECUTE format(
                            'ALTER TABLE {SCHEMA}.videos ALTER COLUMN %I {nullability}',
                            candidate_column
                        );
                    END IF;
                END LOOP;
            END
            $$;
            """
        )
    )


def upgrade() -> None:
    _alter_existing_columns(nullable=True)


def downgrade() -> None:
    _alter_existing_columns(nullable=False)
