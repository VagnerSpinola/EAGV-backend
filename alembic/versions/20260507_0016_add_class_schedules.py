"""add class schedules

Revision ID: 20260507_0016
Revises: 20260506_0015
Create Date: 2026-05-07 10:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_0016"
down_revision = "20260506_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "classes",
        sa.Column("schedules", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
    )

    op.execute(
        """
        UPDATE classes
        SET schedules = COALESCE(
            (
                SELECT json_agg(
                    json_build_object(
                        'day', day_value,
                        'start_time', NULL,
                        'end_time', NULL
                    )
                )
                FROM json_array_elements_text(days) AS day_value
            ),
            '[]'::json
        )
        """
    )

    op.alter_column("classes", "schedules", server_default=None)


def downgrade() -> None:
    op.drop_column("classes", "schedules")