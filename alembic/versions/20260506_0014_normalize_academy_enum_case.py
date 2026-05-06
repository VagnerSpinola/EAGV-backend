"""normalize academy enum case

Revision ID: 20260506_0014
Revises: 20260506_0013
Create Date: 2026-05-06 23:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260506_0014"
down_revision = "20260506_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE members
            SET status = CASE lower(status)
                WHEN 'active' THEN 'active'
                WHEN 'inactive' THEN 'inactive'
                WHEN 'blocked' THEN 'blocked'
                ELSE status
            END
            WHERE status <> lower(status)
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE checkins
            SET type = CASE lower(type)
                WHEN 'gym' THEN 'gym'
                WHEN 'pool' THEN 'pool'
                WHEN 'court' THEN 'court'
                ELSE type
            END
            WHERE type <> lower(type)
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE body_photos
            SET type = CASE lower(type)
                WHEN 'front' THEN 'front'
                WHEN 'side' THEN 'side'
                WHEN 'back' THEN 'back'
                ELSE type
            END
            WHERE type <> lower(type)
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE members
            SET status = CASE lower(status)
                WHEN 'active' THEN 'ACTIVE'
                WHEN 'inactive' THEN 'INACTIVE'
                WHEN 'blocked' THEN 'BLOCKED'
                ELSE status
            END
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE checkins
            SET type = CASE lower(type)
                WHEN 'gym' THEN 'GYM'
                WHEN 'pool' THEN 'POOL'
                WHEN 'court' THEN 'COURT'
                ELSE type
            END
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE body_photos
            SET type = CASE lower(type)
                WHEN 'front' THEN 'FRONT'
                WHEN 'side' THEN 'SIDE'
                WHEN 'back' THEN 'BACK'
                ELSE type
            END
            """
        )
    )