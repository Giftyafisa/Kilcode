"""merge multiple heads

Revision ID: be02c604eb30
Revises: merge_country_heads
Create Date: 2024-12-19 09:43:42.971264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be02c604eb30'
down_revision: Union[str, None] = 'merge_country_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
