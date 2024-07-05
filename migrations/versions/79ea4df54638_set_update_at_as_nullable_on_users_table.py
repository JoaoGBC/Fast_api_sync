"""set update_at as nullable on users table

Revision ID: 79ea4df54638
Revises: 32a752d69395
Create Date: 2024-07-03 22:40:41.106421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79ea4df54638'
down_revision: Union[str, None] = '32a752d69395'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'updated_at', new_column_name= 'old_updated_at_temp', existing_type=sa.DateTime())
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.execute('UPDATE users SET updated_at = old_updated_at_temp')
    op.drop_column('users', 'old_updated_at_temp')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'updated_at', new_column_name= 'temp_updated_at', existing_type=sa.DateTime())
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.execute('UPDATE users SET updated_at = temp_updated_at')
    op.drop_column('users', 'temp_updated_at')
    # ### end Alembic commands ###
