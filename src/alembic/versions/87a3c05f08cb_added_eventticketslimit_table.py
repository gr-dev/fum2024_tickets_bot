"""Added eventTicketsLimit table

Revision ID: 87a3c05f08cb
Revises: 2b66bd1618e8
Create Date: 2025-01-22 17:08:18.488232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87a3c05f08cb'
down_revision: Union[str, None] = '2b66bd1618e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('eventTicketsLimit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_eventTicketsLimit_id'), 'eventTicketsLimit', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_eventTicketsLimit_id'), table_name='eventTicketsLimit')
    op.drop_table('eventTicketsLimit')
    # ### end Alembic commands ###
