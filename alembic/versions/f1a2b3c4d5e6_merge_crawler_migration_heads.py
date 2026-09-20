"""Merge crawler enrichment and scheduling migration heads.

Revision ID: f1a2b3c4d5e6
Revises: d4e9a2c1f7b0, e2f3a4b5c6d7
"""

from collections.abc import Sequence

revision: str = "f1a2b3c4d5e6"
down_revision: tuple[str, str] = ("d4e9a2c1f7b0", "e2f3a4b5c6d7")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
