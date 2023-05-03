"""refactored model tasks

Revision ID: 808d85cae7c0
Revises: 2c304127881b
Create Date: 2023-05-03 20:39:32.229446

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '808d85cae7c0'
down_revision = '2c304127881b'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('tasks', 'description_for_message', new_column_name='title')
    op.drop_constraint('tasks_description_for_message_key', 'tasks', type_='unique')
    op.create_unique_constraint(None, 'tasks', ['title'])

    op.drop_constraint('tasks_description_key', 'tasks', type_='unique')
    op.drop_column('tasks', 'description')

    op.add_column('tasks', sa.Column('sequence_number', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False))


def downgrade():
    op.alter_column('tasks', 'title', new_column_name='description_for_message')
    op.add_column('tasks', sa.Column('description', sa.VARCHAR(length=150), autoincrement=False, nullable=True))
    with open('tasks.json', 'r', encoding='UTF-8') as json_file:
        for task in json.load(json_file):
            description: str = task.get('description')
            description_for_message: str = task.get('description_for_message', description.lower())
            op.execute(
                f"UPDATE tasks SET description = '{description}' "
                f"WHERE description_for_message = '{description_for_message}'"
            )
    op.alter_column('tasks', 'description', nullable=False)
    op.drop_constraint('tasks_title_key', 'tasks', type_='unique')
    op.create_unique_constraint(None, 'tasks', ['description'])
    op.create_unique_constraint(None, 'tasks', ['description_for_message'])

    op.drop_column('tasks', 'sequence_number')
