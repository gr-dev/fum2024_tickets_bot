"""rename of updateLog

Revision ID: 24943af64e60
Revises: 30c5f8c6dbd2
Create Date: 2024-03-11 19:53:46.035580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '24943af64e60'
down_revision: Union[str, None] = '30c5f8c6dbd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('updateLogs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('logTimeStamp', sa.TIMESTAMP(), nullable=True),
    sa.Column('telegramTimeStamp', sa.TIMESTAMP(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('telegramChatId', sa.BIGINT(), nullable=True),
    sa.Column('update_type', sa.String(), nullable=True),
    sa.Column('exceptionMessage', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_updateLogs_id'), 'updateLogs', ['id'], unique=False)
    op.drop_index('ix_UpdateLogs_id', table_name='UpdateLogs')
    op.drop_table('UpdateLogs')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UpdateLogs',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"UpdateLogs_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('logTimeStamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('telegramTimeStamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('message', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('update_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('exceptionMessage', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('telegramChatId', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='UpdateLogs_pkey')
    )
    op.create_index('ix_UpdateLogs_id', 'UpdateLogs', ['id'], unique=False)
    op.drop_index(op.f('ix_updateLogs_id'), table_name='updateLogs')
    op.drop_table('updateLogs')
    # ### end Alembic commands ###
