"""UserState.user_id renamed to telegram_user_id

Revision ID: a16f1b1a42b1
Revises: 4a9f8db10e0a
Create Date: 2024-03-06 17:09:18.650683

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a16f1b1a42b1'
down_revision: Union[str, None] = '4a9f8db10e0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userStates', sa.Column('telegram_user_id', sa.BIGINT(), nullable=True))
    op.drop_column('userStates', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userStates', sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.drop_column('userStates', 'telegram_user_id')
    # ### end Alembic commands ###
