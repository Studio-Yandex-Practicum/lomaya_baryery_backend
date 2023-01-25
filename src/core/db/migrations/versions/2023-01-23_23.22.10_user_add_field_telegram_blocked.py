"""user_add_field_telegram_blocked

Revision ID: ff2e044f44aa
Revises: cf3ecbc0aacc
Create Date: 2023-01-23 23:22:10.292405

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ff2e044f44aa'
down_revision = 'cf3ecbc0aacc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('telegram_blocked', sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET telegram_blocked = False")
    op.alter_column('users', 'telegram_blocked', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'telegram_blocked')
    # ### end Alembic commands ###