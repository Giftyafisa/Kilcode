"""Add marketplace columns

Revision ID: add_marketplace_columns
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new columns to betting_codes table
    op.add_column('betting_codes', sa.Column('is_published', sa.Boolean(), nullable=True, server_default='0'))
    op.add_column('betting_codes', sa.Column('user_country', sa.String(50), nullable=True))
    op.add_column('betting_codes', sa.Column('marketplace_status', sa.String(20), nullable=True))
    op.add_column('betting_codes', sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True))
    
    # Add columns to code_purchases table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'code_purchases'):
        op.create_table(
            'code_purchases',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('code_id', sa.Integer(), sa.ForeignKey('betting_codes.id'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    # Remove the new columns
    op.drop_column('betting_codes', 'is_published')
    op.drop_column('betting_codes', 'user_country')
    op.drop_column('betting_codes', 'marketplace_status')
    op.drop_column('betting_codes', 'valid_until')
    
    # Drop code_purchases table if it exists
    op.drop_table('code_purchases') 