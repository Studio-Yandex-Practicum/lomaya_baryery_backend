"""rename AdministratorInvitation.expired_date to expired_datetime

Revision ID: ef4034f91b1c
Revises: f4645f80c3ac
Create Date: 2023-02-23 15:01:06.086482

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ef4034f91b1c'
down_revision = 'f4645f80c3ac'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'administrator_invitations',
        'expired_date',
        new_column_name='expired_datetime',
    )


def downgrade():
    op.alter_column(
        'administrator_invitations',
        'expired_datetime',
        new_column_name='expired_date',
    )
