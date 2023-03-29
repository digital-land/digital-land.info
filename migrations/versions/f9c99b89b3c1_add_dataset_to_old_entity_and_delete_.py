"""add dataset to old_entity and delete rows where dataset is null

Revision ID: f9c99b89b3c1
Revises: 6343e6290c55
Create Date: 2023-03-29 11:29:40.329480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9c99b89b3c1'
down_revision = '6343e6290c55'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("old_entity", sa.Column("dataset", sa.Text(), nullable=True))
    op.execute(
        sa.text("DELETE FROM old_entity WHERE dataset IS NULL")
    )
    op.create_check_constraint(
        "column_not_null_check",
        "old_entity",
        sa.text("dataset IS NOT NULL")
    )


def downgrade():
    op.drop_column("old_entity", "dataset")
