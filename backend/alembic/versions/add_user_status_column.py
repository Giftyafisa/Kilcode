"""add user status column

Revision ID: add_user_status_column
Revises: 0f6b3b152370
Create Date: 2024-03-06 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_status_column'
down_revision = '0f6b3b152370'  # Point to the last successful migration
branch_labels = None
depends_on = None

def upgrade():
    # Add status column to users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('status', 
            sa.String(50),
            server_default='active',
            nullable=False
        ))
        batch_op.create_check_constraint(
            'user_status_check',
            'status IN ("active", "suspended", "pending")'
        )

def downgrade():
    # Remove status column from users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('user_status_check')
        batch_op.drop_column('status') 