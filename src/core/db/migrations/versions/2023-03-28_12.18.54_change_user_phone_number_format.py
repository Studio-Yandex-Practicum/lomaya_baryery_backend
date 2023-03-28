"""change User.phone_number format

Revision ID: 861c749e429b
Revises: 7e2638eb39b5
Create Date: 2023-03-28 12:18:54.783920

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '861c749e429b'
down_revision = '7e2638eb39b5'
branch_labels = None
depends_on = None

PHONE_REGEXP = r"^(?\:7|8)?([0-9]{3})([0-9]{3})([0-9]{2})([0-9]{2})$"
PHONE_REPLACEMENT_STRING = r"+7 \1 \2-\3-\4"


def upgrade():
    op.alter_column(
        'users', 'phone_number',
        existing_type=sa.String(length=11),
        existing_nullable=False,
        type_=sa.String(length=16),
    )
    op.execute(
        rf"UPDATE users "
        rf"SET phone_number = REGEXP_REPLACE(phone_number,'{PHONE_REGEXP}','{PHONE_REPLACEMENT_STRING}');"
    )


def downgrade():
    op.execute(
        r"UPDATE users SET phone_number = REGEXP_REPLACE(phone_number, '[^0-9]+', '', 'g');"
    )

    op.alter_column(
        'users', 'phone_number',
        existing_type=sa.String(length=16),
        existing_nullable=False,
        type_=sa.String(length=11),
    )
