"""merge multiple heads

Revision ID: 406db7f54f5f
Revises: add_user_status_column
Create Date: 2024-12-06 18:06:24.461682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '406db7f54f5f'
down_revision: Union[str, None] = 'add_user_status_column'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
