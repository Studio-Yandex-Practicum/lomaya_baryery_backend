"""rename_administrator_role

Revision ID: 101e65411980
Revises: bcda11280d4d
Create Date: 2023-04-12 18:03:43.074512

"""
from alembic import op
from alembic_enums import Column, EnumMigration

# revision identifiers, used by Alembic.
revision = '101e65411980'
down_revision = 'bcda11280d4d'
branch_labels = None
depends_on = None


column = Column("administrators", "role", old_server_default=None, new_server_default=None)


enum_migration = EnumMigration(
    op=op,
    enum_name="administrator_role",
    old_options=["administrator", "psychologist"],
    new_options=["administrator", "expert"],
    columns=[column],
)


def upgrade():
    with enum_migration.upgrade_ctx():
        enum_migration.update_value(column, "administrator", "administrator")
        enum_migration.update_value(column, "psychologist", "expert")


def downgrade():
    with enum_migration.downgrade_ctx():
        enum_migration.update_value(column, "administrator", "administrator")
        enum_migration.update_value(column, "expert", "psychologist")
