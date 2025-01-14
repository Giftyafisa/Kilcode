"""add payment type field

Revision ID: add_payment_type_field
Revises: add_user_status_column
Create Date: 2024-03-06 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_payment_type_field'
down_revision = 'add_user_status_column'
branch_labels = None
depends_on = None

def upgrade():
    # Add type column to payments table
    with op.batch_alter_table('payments') as batch_op:
        batch_op.add_column(sa.Column('type', 
            sa.String(50),
            server_default='registration',
            nullable=False
        ))

def downgrade():
    # Remove type column from payments table
    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_column('type') 