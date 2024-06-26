"""DataState model Added 

Revision ID: 4a9f8db10e0a
Revises: 66e79b7c21a0
Create Date: 2024-03-06 14:35:12.610583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a9f8db10e0a'
down_revision: Union[str, None] = '66e79b7c21a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('userDataStates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_user_id', sa.BIGINT(), nullable=True),
    sa.Column('chat_id', sa.BIGINT(), nullable=True),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_userDataStates_telegram_user_id'), 'userDataStates', ['telegram_user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_userDataStates_telegram_user_id'), table_name='userDataStates')
    op.drop_table('userDataStates')
    # ### end Alembic commands ###
