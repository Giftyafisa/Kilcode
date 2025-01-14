"""merge heads for description

Revision ID: merge_heads_for_description
Revises: da227da27c87, add_description_to_betting_code
Create Date: 2024-01-19 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_for_description'
down_revision = ('da227da27c87', 'add_description_to_betting_code')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass 