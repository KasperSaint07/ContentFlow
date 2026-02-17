"""Seed default sources.

Revision ID: 002
Revises: 001
Create Date: 2026-02-17
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO sources (name, base_url, is_active)
        SELECT 'Zakon.kz', 'https://www.zakon.kz', true
        WHERE NOT EXISTS (
            SELECT 1 FROM sources WHERE name = 'Zakon.kz'
        );
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM sources WHERE name = 'Zakon.kz';")
