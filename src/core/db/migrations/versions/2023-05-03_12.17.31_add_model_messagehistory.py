"""add model MessageHistory

Revision ID: 707f448b5271
Revises: 2c304127881b
Create Date: 2023-05-03 12:17:31.013484

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '707f448b5271'
down_revision = '2c304127881b'
branch_labels = None
depends_on = None

STATUS_ENUM_POSTGRES = postgresql.ENUM(
    'registration',
    'get_task',
    'report_mention',
    'request_accepted',
    'request_canceled',
    'task_accepted',
    'task_not_accepted',
    'exclude_from_shift',
    'shift_ended',
    'shift_canceled',
    'start_shift_changed',
    name='message_history_event',
    create_type=False
)
STATUS_ENUM = sa.Enum(
    'registration',
    'get_task',
    'report_mention',
    'request_accepted',
    'request_canceled',
    'task_accepted',
    'task_not_accepted',
    'exclude_from_shift',
    'shift_ended',
    'shift_canceled',
    'start_shift_changed',
    name='message_history_event'
)
STATUS_ENUM.with_variant(STATUS_ENUM_POSTGRES, 'postgresql')

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message_history',
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('message', sa.String(length=400), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('event', STATUS_ENUM, nullable=False),
    sa.Column('shift_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['shift_id'], ['shifts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_history')
    STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
