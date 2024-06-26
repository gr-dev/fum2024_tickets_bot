"""EventGroup added

Revision ID: d5f956f93e06
Revises: e875fabc1a24
Create Date: 2024-03-07 14:40:55.636437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5f956f93e06'
down_revision: Union[str, None] = 'e875fabc1a24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('eventGroups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_eventGroups_id'), 'eventGroups', ['id'], unique=False)
    op.create_foreign_key(None, 'events', 'eventGroups', ['groupId'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_index(op.f('ix_eventGroups_id'), table_name='eventGroups')
    op.drop_table('eventGroups')
    # ### end Alembic commands ###
