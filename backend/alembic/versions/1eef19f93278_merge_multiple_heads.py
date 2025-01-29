"""merge multiple heads

Revision ID: 1eef19f93278
Revises: add_note_to_payments, add_reset_token_columns
Create Date: 2024-12-21 12:32:13.797568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1eef19f93278'
down_revision: Union[str, None] = ('add_note_to_payments', 'add_reset_token_columns')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
