"""Add field description_for_message to Task model

Revision ID: e0226d762401
Revises: ef4034f91b1c
Create Date: 2023-02-26 17:25:34.245608

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e0226d762401'
down_revision = 'ef4034f91b1c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tasks', sa.Column('description_for_message', sa.String(length=150)))

    # Обновляем таблицу из файла дефолтных задач
    with open('tasks.json', 'r', encoding='UTF-8') as json_file:
        for task in json.load(json_file):
            try:
                description: str = task.get('description')
            except KeyError:
                continue

            description_for_message: str = task.get('description_for_message', description.lower())

            op.execute(
                f"UPDATE tasks SET description_for_message = '{description_for_message}' "
                f"WHERE description = '{description}'"
            )

        # В таблице могут быть какие-то таски, помимо дефолтных
        # в этом случае копируем в столбец description_for_message данные из столбца description
        op.execute(
            "UPDATE tasks "
            "SET description_for_message = lower(description) "
            "WHERE description_for_message IS NULL"
        )

    op.create_unique_constraint(None, 'tasks', ['description_for_message'])
    op.alter_column('tasks', 'description_for_message', nullable=False)


def downgrade():
    op.drop_column('tasks', 'description_for_message')
