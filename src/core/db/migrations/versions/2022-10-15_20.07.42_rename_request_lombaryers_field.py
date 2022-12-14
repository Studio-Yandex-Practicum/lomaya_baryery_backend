"""rename_request_lombaryers_field

Revision ID: 267aaf26546c
Revises: fb9db4c9f3f9
Create Date: 2022-10-15 20:07:42.333603

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '267aaf26546c'
down_revision = 'fb9db4c9f3f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('lombaryers_sum', sa.Integer(), nullable=True))
    op.drop_column('requests', 'lombaryers')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('lombaryers', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('requests', 'lombaryers_sum')
    # ### end Alembic commands ###
