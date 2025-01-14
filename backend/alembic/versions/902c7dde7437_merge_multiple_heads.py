"""merge multiple heads

Revision ID: 902c7dde7437
Revises: 406db7f54f5f, merge_all_heads
Create Date: 2024-12-06 19:26:29.075005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '902c7dde7437'
down_revision: Union[str, None] = ('406db7f54f5f', 'merge_all_heads')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
