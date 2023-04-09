"""rename psychologist to expert

Revision ID: 8e31cf9b1c8a
Revises: bcda11280d4d
Create Date: 2023-04-06 21:17:27.741990

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '8e31cf9b1c8a'
down_revision = 'bcda11280d4d'
branch_labels = None
depends_on = None

name = 'administrator_role'
tmp_name = f'tmp_{name}'

OLD_ROLES = ('administrator', 'psychologist',)
NEW_ROLES = ('administrator', 'expert',)
TMP_ROLES = ('administrator', 'psychologist', 'expert',)

OLD_ENUM = sa.Enum(*OLD_ROLES, name=name)
NEW_ENUM = sa.Enum(*NEW_ROLES, name=name)
TMP_ENUM = sa.Enum(*TMP_ROLES, name=name)

target_table = sa.sql.table('administrators',
                            sa.Column('role',
                                      TMP_ENUM,
                                      nullable=False)
                            )


def upgrade():
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")
    TMP_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE administrators ALTER COLUMN role TYPE {name} USING role::text::{name}')
    op.execute(
        target_table.update().where(
            target_table.c.role == op.inline_literal('psychologist')).values(
            {'role': op.inline_literal('expert')}))
    op.execute(f'DROP TYPE {tmp_name}')
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")
    NEW_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE administrators ALTER COLUMN role TYPE {name} USING role::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')


def downgrade():
    op.execute(f'ALTER TYPE {name} RENAME TO {tmp_name}')
    TMP_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE administrators ALTER COLUMN role TYPE {name} USING role::text::{name}')
    op.execute(
        target_table.update().where(
            target_table.c.role == op.inline_literal('expert')).values(
            {'role': op.inline_literal('psychologist')}))
    op.execute(f'DROP TYPE {tmp_name}')
    op.execute(f"ALTER TYPE {name} RENAME TO {tmp_name}")
    OLD_ENUM.create(op.get_bind())
    op.execute(f'ALTER TABLE administrators ALTER COLUMN role TYPE {name} USING role::text::{name}')
    op.execute(f'DROP TYPE {tmp_name}')
