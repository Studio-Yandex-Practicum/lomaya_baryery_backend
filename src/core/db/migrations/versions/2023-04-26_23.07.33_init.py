"""init

Revision ID: df71ca5ae48d
Revises: 
Create Date: 2023-04-26 23:07:33.812893

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2c304127881b'
down_revision = None
branch_labels = None
depends_on = None

# add_shift_status_field
SHIFT_STATUS_ENUM_POSTGRES = postgresql.ENUM('started', 'finished', 'ready_for_complete', 'preparing', 'cancelled', name='shift_status')
SHIFT_STATUS_ENUM = sa.Enum('started', 'finished', 'ready_for_complete', 'preparing', 'cancelled', name='shift_status')
SHIFT_STATUS_ENUM.with_variant(SHIFT_STATUS_ENUM_POSTGRES, 'postgresql')

# add_user_status_field
USER_STATUS_ENUM_POSTGRES = postgresql.ENUM('verified', 'declined', 'pending', name='user_status', create_type=False)
USER_STATUS_ENUM = sa.Enum('verified', 'declined', 'pending', name='user_status')
USER_STATUS_ENUM.with_variant(USER_STATUS_ENUM_POSTGRES, 'postgresql')

# add_request_status_field
REQUEST_STATUS_ENUM_POSTGRES = postgresql.ENUM('approved', 'declined', 'pending', name='request_status')
REQUEST_STATUS_ENUM = sa.Enum('approved', 'declined', 'pending', name='request_status')
REQUEST_STATUS_ENUM.with_variant(REQUEST_STATUS_ENUM_POSTGRES, 'postgresql')

# add_member_status__field
MEMBER_STATUS_ENUM_POSTGRES = postgresql.ENUM('active', 'excluded', name='member_status', create_type=False)
MEMBER_STATUS_ENUM = sa.Enum('active', 'excluded', name='member_status')
MEMBER_STATUS_ENUM.with_variant(MEMBER_STATUS_ENUM_POSTGRES, 'postgresql')

# add_administrator_fields
ADMIN_STATUS_ENUM_POSTGRES = postgresql.ENUM('active', 'blocked', name='administrator_status', create_type=False)
ADMIN_STATUS_ENUM = sa.Enum('active', 'blocked', name='administrator_status')
ADMIN_STATUS_ENUM.with_variant(ADMIN_STATUS_ENUM_POSTGRES, 'postgresql')

ADMIN_ROLE_ENUM_POSTGRES = postgresql.ENUM('administrator', 'expert', name='administrator_role', create_type=False)
ADMIN_ROLE_ENUM = sa.Enum('administrator', 'expert', name='administrator_role')
ADMIN_ROLE_ENUM.with_variant(ADMIN_ROLE_ENUM_POSTGRES, 'postgresql')

# add_report_status_field
REPORT_STATUS_ENUM_POSTGRES = postgresql.ENUM('reviewing', 'approved', 'declined', 'waiting', 'skipped', 'not_participate', name='report_status')
REPORT_STATUS_ENUM = sa.Enum('reviewing', 'approved', 'declined', 'waiting', 'skipped', 'not_participate', name='report_status')
REPORT_STATUS_ENUM.with_variant(REPORT_STATUS_ENUM_POSTGRES, 'postgresql')


def upgrade():
    op.create_table('shifts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('status', SHIFT_STATUS_ENUM, nullable=False),
    sa.Column('sequence_number', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False),
    sa.Column('started_at', sa.DATE(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, index=True),
    sa.Column('finished_at', sa.DATE(), nullable=False, index=True),
    sa.Column('title', sa.String(length=60), nullable=False),
    sa.Column('final_message', sa.String(length=400), nullable=False),
    sa.Column('tasks', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('tasks',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('url', sa.String(length=150), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
    sa.Column('sequence_number', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False),

    sa.PrimaryKeyConstraint('id'),

    sa.UniqueConstraint('title'),
    sa.UniqueConstraint('url')
    )

    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('surname', sa.String(length=100), nullable=False),
    sa.Column('date_of_birth', sa.DATE(), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('phone_number', sa.String(length=16), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('status', USER_STATUS_ENUM, nullable=False),
    sa.Column('telegram_blocked', sa.Boolean(), nullable=False, server_default='false'),
    sa.PrimaryKeyConstraint('id'),

    sa.UniqueConstraint('telegram_id'),
    sa.UniqueConstraint('phone_number'),
    )

    op.create_table('requests',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('shift_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('status', REQUEST_STATUS_ENUM, nullable=False),
    sa.Column('is_repeated', sa.Integer, default='1', nullable=False),
    sa.PrimaryKeyConstraint('id'),

    sa.ForeignKeyConstraint(['shift_id'], ['shifts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_table('members',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('status', MEMBER_STATUS_ENUM, nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('shift_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('numbers_lombaryers', sa.Integer(), nullable=False, default='0'),
    sa.PrimaryKeyConstraint('id'),

    sa.UniqueConstraint('user_id', 'shift_id', name='_user_shift_uc'),

    sa.ForeignKeyConstraint(['shift_id'], ['shifts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )

    op.create_table('administrators',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('surname', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=70), nullable=False),
    sa.Column('role', ADMIN_ROLE_ENUM, nullable=False, server_default='expert'),
    sa.Column('last_login_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('status', ADMIN_STATUS_ENUM, nullable=False, server_default='active'),
    sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
    sa.PrimaryKeyConstraint('id'),

    sa.UniqueConstraint('email'),
    )

    op.create_table('reports',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('shift_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('member_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('uploaded_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('reviewed_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('task_date', sa.DATE(), nullable=False),
    sa.Column('status', REPORT_STATUS_ENUM, nullable=False),
    sa.Column('report_url', sa.VARCHAR(length=4096), nullable=True),
    sa.Column('number_attempt', sa.Integer(), nullable=False, server_default='0'),
    sa.PrimaryKeyConstraint('id'),

    sa.UniqueConstraint('shift_id', 'task_date', 'member_id', name='_member_task_uc'),
    sa.UniqueConstraint('report_url'),

    sa.ForeignKeyConstraint(['shift_id'], ['shifts.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['administrators.id'])
    )

    op.create_table('administrator_invitations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('surname', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('token', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('expired_datetime', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )