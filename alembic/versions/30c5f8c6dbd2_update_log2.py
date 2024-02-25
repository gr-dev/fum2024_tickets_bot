"""update log2

Revision ID: 30c5f8c6dbd2
Revises: dbaf8494d15d
Create Date: 2024-03-11 19:04:46.371267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30c5f8c6dbd2'
down_revision: Union[str, None] = 'dbaf8494d15d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('UpdateLogs', sa.Column('telegramChatId', sa.BIGINT(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('UpdateLogs', 'telegramChatId')
    # ### end Alembic commands ###
