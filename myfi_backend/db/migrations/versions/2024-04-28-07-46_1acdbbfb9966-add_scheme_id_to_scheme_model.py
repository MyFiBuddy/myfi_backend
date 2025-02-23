"""add scheme_id to scheme model

Revision ID: 1acdbbfb9966
Revises: 9950efa20a3c
Create Date: 2024-04-28 07:46:24.497389

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1acdbbfb9966"
down_revision = "9950efa20a3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "mutual_fund_schemes",
        sa.Column("scheme_id", sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_mutual_fund_schemes_scheme_id",
        "mutual_fund_schemes",
        ["scheme_id"],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "uq_mutual_fund_schemes_scheme_id",
        "mutual_fund_schemes",
        type_="unique",
    )
    op.drop_column("mutual_fund_schemes", "scheme_id")
    # ### end Alembic commands ###
