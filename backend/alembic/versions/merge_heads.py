"""merge heads

Revision ID: merge_heads
Revises: add_user_payment_fields, create_admin_table
Create Date: 2024-03-02 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'merge_heads'
down_revision = None
branch_labels = None
depends_on = ['add_user_payment_fields', 'create_admin_table']

def upgrade():
    pass

def downgrade():
    pass 