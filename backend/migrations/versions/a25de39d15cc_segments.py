"""segments

Revision ID: a25de39d15cc
Revises: a41f2c9b7e03
Create Date: 2024-06-03 14:21:08.552190

"""
import sqlalchemy as sa
from alembic import op

revision = "a25de39d15cc"
down_revision = "a41f2c9b7e03"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "segments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rollout_percentage", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_table(
        "segment_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("segment_id", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attribute", sa.String(length=64), nullable=False),
        sa.Column("operator", sa.String(length=32), nullable=False),
        sa.Column("values", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["segment_id"], ["segments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("targeting_rules") as batch:
        batch.add_column(sa.Column("segment_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_targeting_rules_segment_id", "segments", ["segment_id"], ["id"]
        )


def downgrade():
    with op.batch_alter_table("targeting_rules") as batch:
        batch.drop_constraint("fk_targeting_rules_segment_id", type_="foreignkey")
        batch.drop_column("segment_id")
    op.drop_table("segment_rules")
    op.drop_table("segments")
