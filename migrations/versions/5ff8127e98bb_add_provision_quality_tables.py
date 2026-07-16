"""add provision quality tables

Revision ID: 5ff8127e98bb
Revises: 08139a9624a2
Create Date: 2026-07-16 11:36:02.965197

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ff8127e98bb"
down_revision = "08139a9624a2"
branch_labels = None
depends_on = None


def upgrade():
    # provision_quality — base grain: one row per (dataset, organisation).
    # Nullable only where a value can be genuinely absent: organisation_name,
    # quality (unclassified), quality_score (deferred).
    op.create_table(
        "provision_quality",
        sa.Column("dataset", sa.Text(), nullable=False),
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.Column("organisation_name", sa.Text(), nullable=True),
        sa.Column("has_active_endpoint", sa.Boolean(), nullable=False),
        sa.Column("has_active_resource", sa.Boolean(), nullable=False),
        sa.Column("owns_entities", sa.Boolean(), nullable=False),
        sa.Column("is_designated_provider", sa.Boolean(), nullable=False),
        sa.Column("quality", sa.Text(), nullable=True),
        sa.Column("entity_count", sa.BigInteger(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("dataset", "organisation"),
    )
    op.create_index(
        "idx_provision_quality_organisation", "provision_quality", ["organisation"]
    )

    # dataset_quality — rollup per dataset
    op.create_table(
        "dataset_quality",
        sa.Column("dataset", sa.Text(), nullable=False),
        sa.Column("authoritative_organisations", sa.Integer(), nullable=False),
        sa.Column("some_organisations", sa.Integer(), nullable=False),
        sa.Column("total_organisations", sa.Integer(), nullable=False),
        sa.Column("total_entities", sa.BigInteger(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("dataset"),
    )

    # organisation_quality — rollup per organisation across datasets
    op.create_table(
        "organisation_quality",
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.Column("organisation_name", sa.Text(), nullable=True),
        sa.Column("authoritative_datasets", sa.Integer(), nullable=False),
        sa.Column("some_datasets", sa.Integer(), nullable=False),
        sa.Column("total_datasets", sa.Integer(), nullable=False),
        sa.Column("total_entities_owned", sa.BigInteger(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("organisation"),
    )


def downgrade():
    op.drop_index("idx_provision_quality_organisation", table_name="provision_quality")
    op.drop_table("provision_quality")
    op.drop_table("dataset_quality")
    op.drop_table("organisation_quality")
