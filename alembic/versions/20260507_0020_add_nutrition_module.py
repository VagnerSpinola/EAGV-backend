"""add nutrition module

Revision ID: 20260507_0020
Revises: 20260507_0019
Create Date: 2026-05-07 20:10:00.000000
"""

from pathlib import Path

from alembic import op


revision = "20260507_0020"
down_revision = "20260507_0019"
branch_labels = None
depends_on = None


def _read_sql_script(filename: str) -> str:
    return (Path(__file__).resolve().parents[2] / "scripts" / filename).read_text(encoding="utf-8")


def upgrade() -> None:
    op.execute(_read_sql_script("20260507_add_nutrition_module_schema.sql"))


def downgrade() -> None:
    # This migration adapts existing shared tables in an additive way.
    # Reversal is intentionally left empty to avoid destructive schema rollback.
    pass