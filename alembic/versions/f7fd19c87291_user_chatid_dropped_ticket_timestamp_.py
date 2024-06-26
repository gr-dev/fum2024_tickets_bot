"""User chatId dropped, ticket timestamp and status added

Revision ID: f7fd19c87291
Revises: 152a3876dcd2
Create Date: 2024-03-11 14:47:27.609457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7fd19c87291'
down_revision: Union[str, None] = '152a3876dcd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('codeTickets', sa.Column('created', sa.TIMESTAMP(), nullable=True))
    op.add_column('codeTickets', sa.Column('checked', sa.Boolean(), nullable=True))
    op.add_column('codeTickets', sa.Column('checkedTimestamp', sa.TIMESTAMP(), nullable=True))
    op.add_column('imageTickets', sa.Column('created', sa.TIMESTAMP(), nullable=True))
    op.add_column('imageTickets', sa.Column('checked', sa.Boolean(), nullable=True))
    op.add_column('imageTickets', sa.Column('checkedTimestamp', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('imageTickets', 'checkedTimestamp')
    op.drop_column('imageTickets', 'checked')
    op.drop_column('imageTickets', 'created')
    op.drop_column('codeTickets', 'checkedTimestamp')
    op.drop_column('codeTickets', 'checked')
    op.drop_column('codeTickets', 'created')
    # ### end Alembic commands ###
