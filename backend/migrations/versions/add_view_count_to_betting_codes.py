"""add view_count and marketplace fields to betting_codes

Revision ID: add_view_count_to_betting_codes
Revises: None
Create Date: 2024-01-07 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_view_count_to_betting_codes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add view_count column with default value of 0
    op.add_column('betting_codes', sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add is_in_marketplace column with default value of false
    op.add_column('betting_codes', sa.Column('is_in_marketplace', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add is_published column with default value of false
    op.add_column('betting_codes', sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add marketplace fields
    op.add_column('betting_codes', sa.Column('title', sa.String(100), nullable=True))
    op.add_column('betting_codes', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('betting_codes', sa.Column('issuer', sa.String(100), nullable=True))
    op.add_column('betting_codes', sa.Column('issuer_type', sa.String(20), nullable=True))
    op.add_column('betting_codes', sa.Column('marketplace_status', sa.String(20), nullable=True))
    op.add_column('betting_codes', sa.Column('analysis_status', sa.String(20), nullable=True))
    op.add_column('betting_codes', sa.Column('user_country', sa.String(50), nullable=True))

def downgrade():
    # Remove all added columns
    op.drop_column('betting_codes', 'view_count')
    op.drop_column('betting_codes', 'is_in_marketplace')
    op.drop_column('betting_codes', 'is_published')
    op.drop_column('betting_codes', 'title')
    op.drop_column('betting_codes', 'category')
    op.drop_column('betting_codes', 'issuer')
    op.drop_column('betting_codes', 'issuer_type')
    op.drop_column('betting_codes', 'marketplace_status')
    op.drop_column('betting_codes', 'analysis_status')
    op.drop_column('betting_codes', 'user_country') 