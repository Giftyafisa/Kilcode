"""add payment_data column

Revision ID: add_payment_data_column
Revises: add_currency_to_payments
Create Date: 2023-12-02 06:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision = 'add_payment_data_column'
down_revision = 'add_currency_to_payments'
branch_labels = None
depends_on = None

def upgrade():
    # Add payment_data column to payments table
    with op.batch_alter_table('payments') as batch_op:
        batch_op.add_column(sa.Column('payment_data', sa.JSON(), nullable=True))

def downgrade():
    # Remove payment_data column from payments table
    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_column('payment_data') 