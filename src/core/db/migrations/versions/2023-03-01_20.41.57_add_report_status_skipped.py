"""add report status skipped

Revision ID: 0f1fa84f5579
Revises: ef4034f91b1c
Create Date: 2023-03-01 20:41:57.540692

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0f1fa84f5579'
down_revision = 'ef4034f91b1c'
branch_labels = None
depends_on = None

name = 'report_status'
tmp_name = f'tmp_{name}'

NEW_STATUSES = ('reviewing', 'approved', 'declined', 'waiting', 'skipped')
OLD_STATUSES = ('reviewing', 'approved', 'declined', 'waiting')

NEW_ENUM = sa.Enum(*NEW_STATUSES, name=name)
OLD_ENUM = sa.Enum(*OLD_STATUSES, name=name)

table_name = 'reports'

target_table = sa.sql.table(table_name,
                            sa.Column('status', NEW_ENUM, nullable=False))


def upgrade():
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")

    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE {table_name} ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')

def downgrade():
    op.execute(target_table.update().where(target_table.c.status=='skipped').values({"status": "waiting"}))
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')
    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE {table_name} ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')
