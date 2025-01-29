"""add is_published to betting_codes

Revision ID: add_is_published_to_betting_codes
Revises: add_view_count_to_betting_codes
Create Date: 2024-01-07 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_published_to_betting_codes'
down_revision = 'add_view_count_to_betting_codes'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_published column with default value of false
    op.add_column('betting_codes', sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    # Remove is_published column
    op.drop_column('betting_codes', 'is_published') 