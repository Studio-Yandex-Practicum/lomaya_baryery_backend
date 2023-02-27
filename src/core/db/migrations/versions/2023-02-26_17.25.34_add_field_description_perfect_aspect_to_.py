"""Add field description_perfect_aspect to Task model

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
    op.add_column('tasks', sa.Column('description_perfect_aspect', sa.String(length=150)))

    # Обновляем таблицу из файла дефолтных задач
    with open('tasks.json', 'r') as json_file:
        for task in json.load(json_file):
            try:
                description = task.get('description')
            except KeyError:
                continue

            description_perfect_aspect = task.get('description_perfect_aspect', description)

            op.execute(
                f"UPDATE tasks SET description_perfect_aspect = '{description_perfect_aspect}' "
                f"WHERE description = '{description}'"
            )

        # В таблице могут быть какие-то таски, помимо дефолтных
        # в этом случае копируем в столбец description_perfect_aspect данные из столбца description
        op.execute(
            "UPDATE tasks "
            "SET description_perfect_aspect = description "
            "WHERE description_perfect_aspect IS NULL"
        )

    op.create_unique_constraint('uc_task_description_perfect_aspect', 'tasks', ['description_perfect_aspect'])
    op.alter_column('tasks', 'description_perfect_aspect', nullable=False)


def downgrade():
    op.drop_constraint('uc_task_description_perfect_aspect', 'tasks', type_='unique')
    op.drop_column('tasks', 'description_perfect_aspect')
