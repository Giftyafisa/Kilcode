"""merge betting code migration heads

Revision ID: merge_betting_code_heads
Revises: add_betting_code_title, merge_heads_for_description
Create Date: 2024-03-02 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'merge_betting_code_heads'
down_revision = ('add_betting_code_title', 'merge_heads_for_description')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 