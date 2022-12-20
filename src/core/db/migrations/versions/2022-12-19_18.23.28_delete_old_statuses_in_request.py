"""Delete old statuses in Request

Revision ID: fe3121a7c29d
Revises: 691cdea87322
Create Date: 2022-12-19 18:23:28.521349

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'fe3121a7c29d'
down_revision = '691cdea87322'
branch_labels = None
depends_on = None



name = 'request_status'
tmp_name = f'tmp_{name}'

NEW_STATUSES = ('approved', 'declined', 'pending')
OLD_STATUSES = ('excluded', 'repeated request') + NEW_STATUSES

NEW_ENUM = sa.Enum(*NEW_STATUSES, name=name)
OLD_ENUM = sa.Enum(*OLD_STATUSES, name=name)

target_table = sa.sql.table('requests',
                            sa.Column('status', NEW_ENUM, nullable=False))


def upgrade():
    op.execute(target_table.delete().where(target_table.c.status=='repeated request'))
    op.execute(target_table.delete().where(target_table.c.status=='excluded'))
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")

    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE requests ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')

def downgrade():
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')

    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE requests ALTER COLUMN status TYPE {name} USING status::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')
