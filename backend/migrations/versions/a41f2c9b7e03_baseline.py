"""baseline the schema that has been running since 2021

Everything up to this point was created by create_all. This reproduces the
tables exactly as they exist in prod so alembic has somewhere to start.

Revision ID: a41f2c9b7e03
Revises:
Create Date: 2023-08-14 11:02:33.417265

"""
import sqlalchemy as sa
from alembic import op

revision = "a41f2c9b7e03"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "flags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("default_variant", sa.String(length=64), nullable=False),
        sa.Column("rollout_percentage", sa.Integer(), nullable=False),
        sa.Column("bucketing_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_table(
        "targeting_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("flag_id", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attribute", sa.String(length=64), nullable=False),
        sa.Column("operator", sa.String(length=32), nullable=False),
        sa.Column("values", sa.Text(), nullable=False),
        sa.Column("variant", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["flag_id"], ["flags.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("targeting_rules")
    op.drop_table("flags")
