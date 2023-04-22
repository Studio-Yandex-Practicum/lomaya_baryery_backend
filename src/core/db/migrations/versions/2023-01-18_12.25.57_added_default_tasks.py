"""added default tasks

Revision ID: a6d858f5a96e
Revises: 36ecaebc781b
Create Date: 2023-01-18 12:25:57.080431

"""

import json
from urllib.parse import urljoin

from alembic import op

from src.core.settings import settings

# revision identifiers, used by Alembic.
revision = 'a6d858f5a96e'
down_revision = '36ecaebc781b'
branch_labels = None
depends_on = None


def upgrade():
    with open('tasks.json', 'r', encoding='UTF-8') as file:
        for task in json.load(file):
            op.execute(
                "INSERT INTO "
                "tasks(id, url, description) "
                "VALUES "
                f"(gen_random_uuid(), '{urljoin(settings.task_image_url, task['filename'])}', '{task['description']}')"
            )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM tasks")
    # ### end Alembic commands ###
