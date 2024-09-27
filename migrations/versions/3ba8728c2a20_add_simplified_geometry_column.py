"""Add simplified_geometry column

Revision ID: 3ba8728c2a20
Revises: 4703bef121cb
Create Date: 2024-09-24 14:02:29.091241

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "3ba8728c2a20"
down_revision = "4703bef121cb"
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column to the entity table
    op.drop_column("entity", "simplified_geometry")
