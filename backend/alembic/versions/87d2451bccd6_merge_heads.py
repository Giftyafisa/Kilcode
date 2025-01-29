"""merge_heads

Revision ID: 87d2451bccd6
Revises: 1eef19f93278
Create Date: 2024-12-21 13:04:24.327492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87d2451bccd6'
down_revision: Union[str, None] = '1eef19f93278'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
