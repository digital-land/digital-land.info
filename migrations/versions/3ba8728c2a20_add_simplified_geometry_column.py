"""Add simplified_geometry column

Revision ID: 3ba8728c2a20
Revises: 4703bef121cb
Create Date: 2024-09-24 14:02:29.091241

"""
import geoalchemy2

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3ba8728c2a20"
down_revision = "4703bef121cb"
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column to the entity table
    op.add_column(
        "entity",
        sa.Column(
            "simplified_geometry",
            geoalchemy2.types.Geometry(
                geometry_type="MULTIPOLYGON",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
    )
    op.execute(
        sa.text(
            """ UPDATE entity SET simplified_geometry = ST_SimplifyPreserveTopology(geometry, 0.0001)
             WHERE geometry IS NOT NULL AND ST_GeometryType(geometry) = 'ST_MultiPolygon'
             AND ST_GeometryType(ST_SimplifyPreserveTopology(geometry, 0.0001)) = 'ST_MultiPolygon';;"""
        )
    )  # noqa


def downgrade():
    # Remove the column if downgrading
    op.drop_column("entity", "simplified_geometry")
