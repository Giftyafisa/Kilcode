"""merge multiple heads

Revision ID: a760a7bddb49
Revises: d6b05005309f
Create Date: 2024-12-06 17:41:48.601692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a760a7bddb49'
down_revision: Union[str, None] = 'd6b05005309f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
