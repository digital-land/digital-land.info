"""reconcile task table details jsonb cols and indexes

The previous migration (a41b142924f7) was edited in place after it had already
been applied to staging — its `details` column was changed from Text to JSONB
(plus NOT NULL constraints and indexes) under the same revision id. Because
Alembic only tracks the revision id, not the file contents, staging never re-ran
it and kept the old Text schema, which made /task.json fail with "details value
is not a valid dict". This migration is a fresh revision that re-applies those
changes so every environment converges on the correct schema.


Revision ID: 08139a9624a2
Revises: a41b142924f7
Create Date: 2026-06-22 12:53:01.587036

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = "08139a9624a2"
down_revision = "a41b142924f7"
branch_labels = None
depends_on = None


def upgrade():
    # text -> jsonb. USING is required to cast; NULLIF guards empty-string rows
    # (''::jsonb errors) by turning them into NULL first.
    op.alter_column(
        "task",
        "details",
        type_=JSONB(),
        existing_type=sa.Text(),
        postgresql_using="NULLIF(btrim(details::text), '')::jsonb",
        existing_nullable=True,
    )
    for col in ("dataset", "severity", "responsibility", "task_source"):
        op.alter_column("task", col, existing_type=sa.Text(), nullable=False)
    # idempotent - dev already has these from the edited migration
    for idx, cols in [
        ("idx_task_dataset", "dataset"),
        ("idx_task_organisation", "organisation"),
        ("idx_task_severity", "severity"),
        ("idx_task_responsibility", "responsibility"),
    ]:
        op.execute(f"CREATE INDEX IF NOT EXISTS {idx} ON task ({cols})")


def downgrade():
    op.alter_column(
        "task",
        "details",
        type_=sa.Text(),
        existing_type=JSONB(),
        postgresql_using="details::text",
        existing_nullable=True,
    )
    for col in ("dataset", "severity", "responsibility", "task_source"):
        op.alter_column("task", col, existing_type=sa.Text(), nullable=True)
