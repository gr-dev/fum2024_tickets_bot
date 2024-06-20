"""Add UserState state field

Revision ID: 7f8bf3b9eca2
Revises: 47ea6ae7d560
Create Date: 2024-03-05 23:29:14.526058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f8bf3b9eca2'
down_revision: Union[str, None] = '47ea6ae7d560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userStates', sa.Column('timeStamp', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('userStates', 'timeStamp')
    # ### end Alembic commands ###