"""add currency to payments

Revision ID: add_currency_to_payments
Revises: 9f5b877d13fc  # Link to previous migration
Create Date: 2023-12-02 05:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_currency_to_payments'
down_revision = '9f5b877d13fc'  # Set previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Add currency column to payments table
    op.add_column('payments', sa.Column('currency', sa.String(), nullable=True))

def downgrade():
    # Remove currency column from payments table
    op.drop_column('payments', 'currency') 