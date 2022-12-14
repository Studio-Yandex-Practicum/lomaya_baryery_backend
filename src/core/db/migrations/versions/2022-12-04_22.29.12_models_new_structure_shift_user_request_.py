"""models_new_structure_shift&user&request&member

Revision ID: 2e9a6c2fe267
Revises: b681bd3175cc
Create Date: 2022-12-04 22:29:12.729026

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2e9a6c2fe267'
down_revision = 'b681bd3175cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('requests', 'numbers_lombaryers')
    op.drop_column('users', 'numbers_lombaryers')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('numbers_lombaryers', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('requests', sa.Column('numbers_lombaryers', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
