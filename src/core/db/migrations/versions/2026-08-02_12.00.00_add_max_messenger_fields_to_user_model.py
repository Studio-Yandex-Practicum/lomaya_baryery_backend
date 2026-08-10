"""Add_max_messenger_fields_to_User_model

Revision ID: 7f3a2b9c1d45
Revises: d237eef85461
Create Date: 2026-08-02 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7f3a2b9c1d45'
down_revision = 'd237eef85461'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('max_user_id', sa.BigInteger(), nullable=True))
    op.add_column('users', sa.Column('max_blocked', sa.Boolean(), nullable=False, server_default='false'))
    op.create_unique_constraint('users_max_user_id_key', 'users', ['max_user_id'])
    # telegram_id остается основным идентификатором пользователя, но становится необязательным:
    # у пользователей, зарегистрированных через мессенджер Max, он не заполняется
    op.alter_column('users', 'telegram_id', existing_type=sa.BigInteger(), nullable=True)
    op.create_check_constraint(
        'users_messenger_id_check', 'users', 'telegram_id IS NOT NULL OR max_user_id IS NOT NULL'
    )


def downgrade():
    op.drop_constraint('users_messenger_id_check', 'users', type_='check')
    op.alter_column('users', 'telegram_id', existing_type=sa.BigInteger(), nullable=False)
    op.drop_constraint('users_max_user_id_key', 'users', type_='unique')
    op.drop_column('users', 'max_blocked')
    op.drop_column('users', 'max_user_id')
