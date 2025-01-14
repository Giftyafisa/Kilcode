"""add user status field

Revision ID: add_user_status_field
Revises: 
Create Date: 2024-03-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'add_user_status_field'
down_revision = None  # Make this migration independent
branch_labels = None
depends_on = None

def upgrade():
    # SQLite doesn't support enum types, so we'll use a string with check constraint
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