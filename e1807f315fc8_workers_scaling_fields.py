from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("audits", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("audits", sa.Column("claimed_by", sa.String(), nullable=True))
    op.add_column("audits", sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("audits", sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("audits", "retry_count")
    op.drop_column("audits", "claimed_by")
    op.drop_column("audits", "heartbeat_at")
    op.drop_column("audits", "last_error_at")
