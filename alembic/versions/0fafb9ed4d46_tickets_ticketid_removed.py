"""Tickets ticketId removed

Revision ID: 0fafb9ed4d46
Revises: 6269f17b5689
Create Date: 2024-03-07 11:30:29.659979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fafb9ed4d46'
down_revision: Union[str, None] = '6269f17b5689'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('codeTickets', 'ticketId')
    op.drop_column('imageTickets', 'ticketId')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('imageTickets', sa.Column('ticketId', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('codeTickets', sa.Column('ticketId', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
