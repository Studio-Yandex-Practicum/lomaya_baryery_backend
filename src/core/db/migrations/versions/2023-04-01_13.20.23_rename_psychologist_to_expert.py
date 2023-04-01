"""rename psychologist to expert

Revision ID: 7a07ac54fe5f
Revises: 861c749e429b
Create Date: 2023-04-01 13:20:23.038246

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7a07ac54fe5f'
down_revision = '861c749e429b'
branch_labels = None
depends_on = None


name = 'administrator_role'
tmp_name = f'tmp_{name}'

NEW_ROLES = ('administrator', 'expert', )
OLD_ROLES = ('administrator', 'psychologist', )

NEW_ENUM = sa.Enum(*NEW_ROLES, name=name)
OLD_ENUM = sa.Enum(*OLD_ROLES, name=name)

target_table = sa.sql.table('administrators',
                            sa.Column('administrator_role',
                                      NEW_ENUM,
                                      nullable=False)
                            )


def upgrade():
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")

    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE administrators ALTER COLUMN role TYPE {name} USING role::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')


def downgrade():
    op.execute(
        target_table.update().where(
            target_table.c.administrator_role == 'expert').values(
            {"administrator_role": "psychologist"}))
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')

    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE administrators ALTER COLUMN role TYPE {name} USING role::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')
