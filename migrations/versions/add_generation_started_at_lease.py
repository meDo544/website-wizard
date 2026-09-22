"""add generation started at lease

Revision ID: add_generation_lease
Revises: 4381d9aa6b5d
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_generation_lease"
down_revision = "4381d9aa6b5d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "generated_sites",
        sa.Column(
            "generation_started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_generated_sites_generation_started_at",
        "generated_sites",
        ["generation_started_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_generated_sites_generation_started_at",
        table_name="generated_sites",
    )

    op.drop_column(
        "generated_sites",
        "generation_started_at",
    )
