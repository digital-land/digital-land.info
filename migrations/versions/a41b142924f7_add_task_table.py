"""add task table

Revision ID: a41b142924f7
Revises: fd4c9022a6c5
Create Date: 2026-06-04 09:52:49.417574

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = "a41b142924f7"
down_revision = "fd4c9022a6c5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "task",
        sa.Column("dataset", sa.Text(), nullable=False),
        sa.Column("organisation", sa.Text(), nullable=True),
        sa.Column("endpoint", sa.Text(), nullable=True),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("details", JSONB(), nullable=True),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("responsibility", sa.Text(), nullable=False),
        sa.Column("task_source", sa.Text(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("reference"),
    )
    op.create_index("idx_task_dataset", "task", ["dataset"])
    op.create_index("idx_task_organisation", "task", ["organisation"])
    op.create_index("idx_task_severity", "task", ["severity"])
    op.create_index("idx_task_responsibility", "task", ["responsibility"])


def downgrade():
    op.drop_index("idx_task_dataset", table_name="task")
    op.drop_index("idx_task_organisation", table_name="task")
    op.drop_index("idx_task_severity", table_name="task")
    op.drop_index("idx_task_responsibility", table_name="task")
    op.drop_table("task")
