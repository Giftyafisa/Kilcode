"""merge country migration heads

Revision ID: merge_country_heads
Revises: add_betting_code_country, merge_issuer_heads
Create Date: 2024-03-02 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'merge_country_heads'
down_revision = ('add_betting_code_country', 'merge_issuer_heads')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 