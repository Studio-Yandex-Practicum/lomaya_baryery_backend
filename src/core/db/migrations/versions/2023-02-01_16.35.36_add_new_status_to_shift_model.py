"""Add new status to shift model

Revision ID: 0123bd454728
Revises: 73c0ad19dc7a
Create Date: 2023-02-01 16:35:36.806595

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0123bd454728'
down_revision = '73c0ad19dc7a'
branch_labels = None
depends_on = None


name = 'shift_status'
tmp_name = f'tmp_{name}'

NEW_STATUSES = ('preparing', 'started', 'ready_for_complete', 'finished', 'cancelled')
OLD_STATUSES = ('preparing', 'started', 'finished', 'cancelled')

NEW_ENUM = sa.Enum(*NEW_STATUSES, name=name)
OLD_ENUM = sa.Enum(*OLD_STATUSES, name=name)

target_table = sa.sql.table('shifts',
                            sa.Column('status', NEW_ENUM, nullable=False))


def upgrade():
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")

    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE shifts ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')

def downgrade():
    op.execute(target_table.delete().where(target_table.c.status=='ready_for_complete'))
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')

    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE shifts ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')
