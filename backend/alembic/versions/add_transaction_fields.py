"""add description and currency to transactions

Revision ID: add_transaction_fields_v1
Revises: e0bbb477b4fe
Create Date: 2023-12-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_transaction_fields_v1'
down_revision = 'e0bbb477b4fe'  # This points to the latest merge
branch_labels = None
depends_on = None

def upgrade():
    # Add description and currency columns to transactions table
    op.add_column('transactions', sa.Column('description', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('currency', sa.String(), nullable=True))

def downgrade():
    # Remove the columns if we need to roll back
    op.drop_column('transactions', 'description')
    op.drop_column('transactions', 'currency') 