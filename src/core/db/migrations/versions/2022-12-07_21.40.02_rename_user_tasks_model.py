"""rename user_tasks model

Revision ID: a418e2ead89b
Revises: 741503bbbd5c
Create Date: 2022-12-07 21:40:02.791225

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a418e2ead89b'
down_revision = '741503bbbd5c'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('user_tasks', 'reports')



def downgrade():
    op.rename_table('reports', 'user_tasks')
