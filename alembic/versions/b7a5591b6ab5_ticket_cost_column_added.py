"""ticket cost column added

Revision ID: b7a5591b6ab5
Revises: d9ad251bbc08
Create Date: 2024-03-11 17:41:36.097672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7a5591b6ab5'
down_revision: Union[str, None] = 'd9ad251bbc08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('codeTickets', sa.Column('cost', sa.Integer(), nullable=True))
    op.add_column('imageTickets', sa.Column('cost', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('imageTickets', 'cost')
    op.drop_column('codeTickets', 'cost')
    # ### end Alembic commands ###
