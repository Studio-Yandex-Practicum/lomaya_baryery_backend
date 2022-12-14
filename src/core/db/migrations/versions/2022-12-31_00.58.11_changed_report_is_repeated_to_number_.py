"""changed Report is_repeated to number_attempt

Revision ID: 36ecaebc781b
Revises: 9d5d33dfbdcf
Create Date: 2022-12-30 23:58:11.426590

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '36ecaebc781b'
down_revision = '9d5d33dfbdcf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reports', sa.Column('number_attempt', sa.Integer(), server_default='0', nullable=False))
    op.drop_column('reports', 'is_repeated')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reports', sa.Column('is_repeated', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.drop_column('reports', 'number_attempt')
    # ### end Alembic commands ###
