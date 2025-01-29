"""add marketplace indexes

Revision ID: 202412251400
Revises: 202412251330
Create Date: 2024-12-25 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '202412251400'
down_revision = '202412251330'
branch_labels = None
depends_on = None

def upgrade():
    # Add indexes for better marketplace query performance
    op.create_index(
        'ix_betting_codes_marketplace',
        'betting_codes',
        ['is_in_marketplace', 'is_published', 'user_country'],
        unique=False
    )
    
    op.create_index(
        'ix_code_purchases_code_id',
        'code_purchases',
        ['code_id'],
        unique=False
    )
    
    op.create_index(
        'ix_code_ratings_code_id',
        'code_ratings',
        ['code_id'],
        unique=False
    )

def downgrade():
    # Remove indexes
    op.drop_index('ix_betting_codes_marketplace', table_name='betting_codes')
    op.drop_index('ix_code_purchases_code_id', table_name='code_purchases')
    op.drop_index('ix_code_ratings_code_id', table_name='code_ratings') 