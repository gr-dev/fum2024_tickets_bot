"""event.eventgroupId renamed to

Revision ID: 86c4ccbadcf9
Revises: d5f956f93e06
Create Date: 2024-03-07 14:56:23.891781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86c4ccbadcf9'
down_revision: Union[str, None] = 'd5f956f93e06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('eventGroupId', sa.Integer(), nullable=True))
    op.drop_constraint('events_groupId_fkey', 'events', type_='foreignkey')
    op.create_foreign_key(None, 'events', 'eventGroups', ['eventGroupId'], ['id'])
    op.drop_column('events', 'groupId')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('groupId', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.create_foreign_key('events_groupId_fkey', 'events', 'eventGroups', ['groupId'], ['id'])
    op.drop_column('events', 'eventGroupId')
    # ### end Alembic commands ###