"""merge_heads

Revision ID: d6b05005309f
Revises: merge_heads, merge_migration_heads
Create Date: 2024-12-03 06:45:44.023795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6b05005309f'
down_revision: Union[str, None] = ('merge_heads', 'merge_migration_heads')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
