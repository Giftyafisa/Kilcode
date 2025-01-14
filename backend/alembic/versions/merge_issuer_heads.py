"""merge issuer migration heads

Revision ID: merge_issuer_heads
Revises: add_betting_code_issuer, merge_betting_code_heads
Create Date: 2024-03-02 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'merge_issuer_heads'
down_revision = ('add_betting_code_issuer', 'merge_betting_code_heads')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 