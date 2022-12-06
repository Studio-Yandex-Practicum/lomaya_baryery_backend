"""delete NEW status from usertask model

Revision ID: 6343307e2c50
Revises: 2e9a6c2fe267
Create Date: 2022-12-05 16:22:28.746542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6343307e2c50'
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
