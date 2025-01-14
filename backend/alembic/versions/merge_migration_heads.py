"""merge migration heads

Revision ID: merge_migration_heads
Revises: create_admin_table, add_user_payment_fields
Create Date: 2024-03-02 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'merge_migration_heads'
down_revision = None
depends_on = ['create_admin_table', 'add_user_payment_fields']

def upgrade():
    # This is a merge migration, no upgrade needed
    pass

def downgrade():
    # This is a merge migration, no downgrade needed
    pass 