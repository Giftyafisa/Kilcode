"""merge multiple heads

Revision ID: 0f6b3b152370
Revises: a760a7bddb49
Create Date: 2024-12-06 18:05:10.765780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f6b3b152370'
down_revision: Union[str, None] = 'a760a7bddb49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
