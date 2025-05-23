"""add_entity_subdivided_table

Revision ID: 3244f0ccb0dc
Revises: 4703bef121cb
Create Date: 2025-03-21 16:57:24.255566

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision = "3244f0ccb0dc"
down_revision = "4703bef121cb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table(
        "entity_subdivided",
        sa.Column(
            "entity_subdivided_id", sa.BIGINT(), autoincrement=True, nullable=False
        ),
        sa.Column("entity", sa.BIGINT(), nullable=False),
        sa.Column("dataset", sa.Text(), nullable=False),
        sa.Column(
            "geometry_subdivided",
            geoalchemy2.types.Geometry(
                geometry_type="MULTIPOLYGON",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("entity_subdivided_id"),
    )
    op.create_index(
        "idx_entity_subdivided_columns", "entity_subdivided", ["entity", "dataset"]
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_entity_subdivided_columns", table_name="entity_subdivided")
    op.drop_index(
        "idx_entity_subdivided_geometry_subdivided",
        table_name="entity_subdivided",
        postgresql_using="gist",
    )
    op.drop_table("entity_subdivided")
    # ### end Alembic commands ###
