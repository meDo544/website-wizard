from alembic import op
import sqlalchemy as sa


revision = "9c108cd2cb67"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audits",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("input_url", sa.Text(), nullable=True),
        sa.Column("results_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table("audits")