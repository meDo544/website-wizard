"""add generation attempt fence

Revision ID: add_generation_fence
Revises: add_generation_lease
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "add_generation_fence"
down_revision = "add_generation_lease"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "generated_sites",
        sa.Column(
            "generation_attempt_id",
            postgresql.UUID(
                as_uuid=True
            ),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_generated_sites_generation_attempt_id",
        "generated_sites",
        ["generation_attempt_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_generated_sites_generation_attempt_id",
        table_name="generated_sites",
    )

    op.drop_column(
        "generated_sites",
        "generation_attempt_id",
    )
