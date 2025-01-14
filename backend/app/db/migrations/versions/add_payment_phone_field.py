"""add phone field to payments

Revision ID: add_payment_phone_field
Revises: add_payment_type_field
Create Date: 2024-03-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_payment_phone_field'
down_revision = 'add_payment_type_field'
branch_labels = None
depends_on = None

def upgrade():
    # Add phone column to payments table
    with op.batch_alter_table('payments') as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String(), nullable=True))

def downgrade():
    # Remove phone column from payments table
    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_column('phone') 