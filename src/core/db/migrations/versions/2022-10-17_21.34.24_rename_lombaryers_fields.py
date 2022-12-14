"""rename_lombaryers_fields

Revision ID: a3e955efe582
Revises: 267aaf26546c
Create Date: 2022-10-17 21:34:24.745291

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a3e955efe582'
down_revision = '267aaf26546c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('numbers_lombaryers', sa.Integer(), nullable=True))
    op.drop_column('requests', 'lombaryers_sum')
    op.add_column('users', sa.Column('numbers_lombaryers', sa.Integer(), nullable=True))
    op.drop_column('users', 'lombaryers_sum')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('lombaryers_sum', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('users', 'numbers_lombaryers')
    op.add_column('requests', sa.Column('lombaryers_sum', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('requests', 'numbers_lombaryers')
    # ### end Alembic commands ###
