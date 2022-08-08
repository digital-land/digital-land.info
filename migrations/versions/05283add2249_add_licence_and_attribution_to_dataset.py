"""add licence and attribution to dataset

Revision ID: 05283add2249
Revises: 543a95beb74b
Create Date: 2022-08-08 11:19:46.625563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "05283add2249"
down_revision = "543a95beb74b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dataset", sa.Column("attribution", sa.Text(), nullable=True))
    op.add_column("dataset", sa.Column("licence", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("dataset", "licence")
    op.drop_column("dataset", "attribution")
