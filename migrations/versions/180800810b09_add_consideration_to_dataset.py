"""add consideration to dataset

Revision ID: 180800810b09
Revises: f9c99b89b3c1
Create Date: 2024-06-26 13:46:25.381348

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "180800810b09"
down_revision = "f9c99b89b3c1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dataset", sa.Column("consideration", sa.Text, nullable=True))


def downgrade():
    op.drop_column("dataset", "consideration")
