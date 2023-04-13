"""rename_administrator_role

Revision ID: 101e65411980
Revises: bcda11280d4d
Create Date: 2023-04-12 18:03:43.074512

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision ="101e65411980"
down_revision ="bcda11280d4d"
branch_labels = None
depends_on = None


T_NAME ="administrators"
ENUM_NAME ="administrator_role"
TMP_NAME = f"tmp_{ENUM_NAME}"

OLD_ROLES = ("administrator","psychologist",)
NEW_ROLES = ("administrator","expert",)
TEMP_ROLES = sorted({*OLD_ROLES, *NEW_ROLES})

OLD_ENUM = sa.Enum(*OLD_ROLES, name=ENUM_NAME)
NEW_ENUM = sa.Enum(*NEW_ROLES, name=ENUM_NAME)
TMP_ENUM = sa.Enum(*TEMP_ROLES, name=TMP_NAME)

administrators_table = sa.sql.table("administrators",
                            sa.Column("role",
                                      TMP_ENUM,
                                      nullable=False)
                            )


def upgrade():
    TMP_ENUM.create(op.get_bind(), checkfirst=False)
    op.execute(
        f"ALTER TABLE {T_NAME} ALTER COLUMN role "
        f"TYPE {TMP_NAME} "
        f"USING role::text::{TMP_NAME}"
    )
    op.execute(
        administrators_table.update().where(
            administrators_table.c.role == op.inline_literal("psychologist")).values(
            {"role": op.inline_literal("expert")})
        )
    OLD_ENUM.drop(op.get_bind(), checkfirst=False)
    NEW_ENUM.create(op.get_bind(), checkfirst=False)
    op.execute(
        f"ALTER TABLE {T_NAME} ALTER COLUMN role "
        f"TYPE {ENUM_NAME} "
        f"USING role::text::{ENUM_NAME}"
    )
    TMP_ENUM.drop(op.get_bind(), checkfirst=False)


def downgrade():
    TMP_ENUM.create(op.get_bind(), checkfirst=False)
    op.execute(
        f"ALTER TABLE {T_NAME} ALTER COLUMN role "
        f"TYPE {TMP_NAME} "
        f"USING role::text::{TMP_NAME}"
    )
    op.execute(
        administrators_table.update().where(
            administrators_table.c.role == op.inline_literal("expert")).values(
            {"role": op.inline_literal("psychologist")}))
    NEW_ENUM.drop(op.get_bind(), checkfirst=False)
    OLD_ENUM.create(op.get_bind(), checkfirst=False)
    op.execute(
        f"ALTER TABLE {T_NAME} ALTER COLUMN role "
        f"TYPE {ENUM_NAME} "
        f"USING role::text::{ENUM_NAME}"
    )
    TMP_ENUM.drop(op.get_bind(), checkfirst=False)
