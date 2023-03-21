"""new Report status not_participate

Revision ID: 3e856b1ea0c1
Revises: dc87d0573547
Create Date: 2023-03-16 22:24:40.133238

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '3e856b1ea0c1'
down_revision = 'dc87d0573547'
branch_labels = None
depends_on = None


name = 'report_status'
tmp_name = f'tmp_{name}'

NEW_STATUSES = ('reviewing', 'approved', 'declined', 'waiting', 'skipped', 'not_participate')
OLD_STATUSES = ('reviewing', 'approved', 'declined', 'waiting', 'skipped')

NEW_ENUM = sa.Enum(*NEW_STATUSES, name=name)
OLD_ENUM = sa.Enum(*OLD_STATUSES, name=name)

table_name= 'reports'

target_table = sa.sql.table(table_name,
                            sa.Column('status', NEW_ENUM, nullable=False))


def upgrade():
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')

    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE {table_name} ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')


def downgrade():
    op.execute(target_table.update().where(target_table.c.status == 'not_participate').values({'status': 'skipped'}))
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')
    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE {table_name} ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')
