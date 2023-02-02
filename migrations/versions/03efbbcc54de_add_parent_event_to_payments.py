"""Add parent event to payments

Revision ID: 03efbbcc54de
Revises: 0d576470d1ed
Create Date: 2022-10-03 21:27:30.668256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "03efbbcc54de"
down_revision = "0d576470d1ed"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("item_prices") as batch_op:
        if not column_exists("item_prices", "parent_event_id"):
            batch_op.add_column(
                sa.Column("parent_event_id", sa.Integer(), nullable=True)
            )

        batch_op.create_foreign_key(
            "item_prices", "events", ["parent_event_id"], ["id"]
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "item_prices", type_="foreignkey")
    op.drop_column("item_prices", "parent_event_id")
    # ### end Alembic commands ###


def column_exists(table_name, column_name):
    bind = op.get_context().bind
    insp = sa.inspect(bind)
    columns = insp.get_columns(table_name)
    return any(c["name"] == column_name for c in columns)
