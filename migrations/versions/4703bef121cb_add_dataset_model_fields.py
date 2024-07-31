"""add dataset model fields

Revision ID: 4703bef121cb
Revises: 180800810b09
Create Date: 2024-07-29 13:52:27.349902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4703bef121cb"
down_revision = "180800810b09"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(sa.Column("github_discussion", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("entity_minimum", sa.BIGINT(), nullable=True))
        batch_op.add_column(sa.Column("entity_maximum", sa.BIGINT(), nullable=True))
        batch_op.add_column(sa.Column("phase", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("realm", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("replacement_dataset", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("version", sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_column("version")
        batch_op.drop_column("replacement_dataset")
        batch_op.drop_column("realm")
        batch_op.drop_column("phase")
        batch_op.drop_column("entity_maximum")
        batch_op.drop_column("entity_minimum")
        batch_op.drop_column("github_discussion")
