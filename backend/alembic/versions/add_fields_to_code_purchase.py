"""add fields to code purchase

Revision ID: add_fields_to_code_purchase
Revises: previous_revision
Create Date: 2024-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_fields_to_code_purchase'
down_revision = None  # Update this with your previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to code_purchases table
    op.add_column('code_purchases', sa.Column('email', sa.String(), nullable=True))
    op.add_column('code_purchases', sa.Column('reference', sa.String(), nullable=True))
    op.add_column('code_purchases', sa.Column('payment_method', sa.String(), nullable=True))
    op.add_column('code_purchases', sa.Column('country', sa.String(), nullable=True))

def downgrade():
    # Remove the columns if we need to roll back
    op.drop_column('code_purchases', 'email')
    op.drop_column('code_purchases', 'reference')
    op.drop_column('code_purchases', 'payment_method')
    op.drop_column('code_purchases', 'country') 