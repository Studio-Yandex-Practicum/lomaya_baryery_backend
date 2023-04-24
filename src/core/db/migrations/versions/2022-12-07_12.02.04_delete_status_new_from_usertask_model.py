"""delete_status_new_from_usertask_model

Revision ID: b8b12d5ba254
Revises: 2e9a6c2fe267
Create Date: 2022-12-07 12:02:04.620323

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b8b12d5ba254'
down_revision = '2e9a6c2fe267'
branch_labels = None
depends_on = None

name = 'user_task_status'
tmp_name = f'tmp_{name}'

NEW_STATUSES = ('under_review', 'approved', 'declined', 'wait_report')
OLD_STATUSES = ('new', ) + NEW_STATUSES

NEW_ENUM = sa.Enum(*NEW_STATUSES, name=name)
OLD_ENUM = sa.Enum(*OLD_STATUSES, name=name)

target_table = sa.sql.table('user_tasks',
                            sa.Column('status', NEW_ENUM, nullable=False))


def upgrade():
    op.execute(target_table.delete().where(target_table.c.status=='new'))
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")

    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE user_tasks ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')

def downgrade():
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')

    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE user_tasks ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')
