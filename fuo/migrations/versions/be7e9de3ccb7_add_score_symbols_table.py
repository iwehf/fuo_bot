"""add score_symbols table

Revision ID: be7e9de3ccb7
Revises: 5df712964956
Create Date: 2023-06-16 16:14:02.622032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be7e9de3ccb7'
down_revision = '5df712964956'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('score_symbols',
    sa.Column('guild_id', sa.BigInteger(), nullable=False),
    sa.Column('symbol', sa.String(1, collation="utf8mb4_bin"), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_score_symbols_guild_id'), 'score_symbols', ['guild_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_score_symbols_guild_id'), table_name='score_symbols')
    op.drop_table('score_symbols')
    # ### end Alembic commands ###
