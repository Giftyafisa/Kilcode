"""empty message

Revision ID: da227da27c87
Revises: add_transaction_fields_v1
Create Date: 2024-12-12 21:20:52.580889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da227da27c87'
down_revision: Union[str, None] = 'add_transaction_fields_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
