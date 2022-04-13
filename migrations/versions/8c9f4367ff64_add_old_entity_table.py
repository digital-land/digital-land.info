"""add-old_entity-table

Revision ID: 8c9f4367ff64
Revises: 28051b25b1a8
Create Date: 2022-04-11 13:42:35.259004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c9f4367ff64"
down_revision = "28051b25b1a8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "old_entity",
        sa.Column("old_entity", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("entity", sa.BIGINT(), nullable=True),
        sa.PrimaryKeyConstraint("old_entity"),
    )


def downgrade():
    op.drop_table("old_entity")
