"""telegramid to bigint

Revision ID: a8016494efe2
Revises: 9324085c81e6
Create Date: 2024-03-30 22:38:47.913433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8016494efe2'
down_revision: Union[str, None] = '9324085c81e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'telegramId',
               existing_type=sa.INTEGER(),
               type_=sa.BIGINT(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'telegramId',
               existing_type=sa.BIGINT(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
