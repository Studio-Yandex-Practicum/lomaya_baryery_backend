"""change statuses, remove delete field

Revision ID: 741503bbbd5c
Revises: b8b12d5ba254
Create Date: 2022-12-07 21:07:13.909937

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '741503bbbd5c'
down_revision = 'b8b12d5ba254'
branch_labels = None
depends_on = None

name = 'user_task_status'
tmp_name = f'tmp_{name}'

NEW_STATUSES = ('reviewing', 'approved', 'declined', 'waiting')
OLD_STATUSES = ('under_review', 'approved', 'declined', 'wait_report')

NEW_ENUM = sa.Enum(*NEW_STATUSES, name=name)
OLD_ENUM = sa.Enum(*OLD_STATUSES, name=name)

target_table = sa.sql.table('user_tasks',
                            sa.Column('status', NEW_ENUM, nullable=False))


def upgrade():
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")

    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE user_tasks ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')

    op.drop_column('members', 'deleted')
    op.drop_column('user_tasks', 'deleted')
    op.drop_column('requests', 'deleted')
    op.drop_column('shifts', 'deleted')
    op.drop_column('tasks', 'deleted')
    op.drop_column('users', 'deleted')

def downgrade():
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')

    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE user_tasks ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')

    op.add_column('users', sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('tasks', sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('shifts', sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('requests', sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user_tasks', sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('members', sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True))
