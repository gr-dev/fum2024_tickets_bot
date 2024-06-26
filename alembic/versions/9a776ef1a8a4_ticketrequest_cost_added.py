"""ticketRequest.cost added

Revision ID: 9a776ef1a8a4
Revises: bf2941f77550
Create Date: 2024-03-07 23:07:18.210363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a776ef1a8a4'
down_revision: Union[str, None] = 'bf2941f77550'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticketRequests', sa.Column('cost', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ticketRequests', 'cost')
    # ### end Alembic commands ###
