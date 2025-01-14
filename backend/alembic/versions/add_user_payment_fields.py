"""add user payment fields

Revision ID: add_user_payment_fields
Revises: create_notifications_table
Create Date: 2024-03-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers
revision = 'add_user_payment_fields'
down_revision = 'create_notifications_table'
branch_labels = None
depends_on = None

def has_column(table, column):
    # Check if column exists
    conn = op.get_bind()
    insp = inspect(conn)
    columns = [c['name'] for c in insp.get_columns(table)]
    return column in columns

def upgrade():
    # Add payment status and reference columns if they don't exist
    with op.batch_alter_table('users') as batch_op:
        if not has_column('users', 'payment_status'):
            batch_op.add_column(sa.Column('payment_status', sa.String(), server_default='pending'))
        if not has_column('users', 'payment_reference'):
            batch_op.add_column(sa.Column('payment_reference', sa.String(), nullable=True))

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('payment_reference')
        batch_op.drop_column('payment_status') 