"""merge multiple heads

Revision ID: e0bbb477b4fe
Revises: 902c7dde7437
Create Date: 2024-12-07 04:58:03.138099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0bbb477b4fe'
down_revision: Union[str, None] = '902c7dde7437'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
