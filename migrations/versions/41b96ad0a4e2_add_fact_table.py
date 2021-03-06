"""add fact table

Revision ID: 41b96ad0a4e2
Revises: 996863046410
Create Date: 2022-05-31 15:41:54.845079

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "41b96ad0a4e2"
down_revision = "996863046410"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "fact",
        sa.Column("fact", sa.Text(), nullable=False),
        sa.Column("entity", sa.BIGINT(), nullable=False),
        sa.Column("field", sa.Text(), nullable=True),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("reference_entity", sa.BIGINT(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("fact"),
    )
    op.create_index("idx_fact_entity", "fact", ["entity"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_fact_entity", table_name="fact")
    op.drop_table("fact")
    # ### end Alembic commands ###
