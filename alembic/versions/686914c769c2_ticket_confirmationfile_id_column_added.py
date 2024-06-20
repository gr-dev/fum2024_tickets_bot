"""ticket confirmationfile id column added

Revision ID: 686914c769c2
Revises: 09f887f3ca1b
Create Date: 2024-03-11 17:33:05.020056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '686914c769c2'
down_revision: Union[str, None] = '09f887f3ca1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('codeTickets', sa.Column('confirmationFileId', sa.String(), nullable=True))
    op.add_column('imageTickets', sa.Column('confirmationFileId', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('imageTickets', 'confirmationFileId')
    op.drop_column('codeTickets', 'confirmationFileId')
    # ### end Alembic commands ###