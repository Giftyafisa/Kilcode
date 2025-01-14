"""merge heads

Revision ID: merge_heads
Revises: add_verification_fields, add_user_status_field
Create Date: 2024-03-06 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('add_verification_fields', 'add_user_status_field')  # Point to both previous migrations
branch_labels = None
depends_on = None  # Remove dependencies since we're using down_revision

def upgrade():
    # This is a merge migration, no changes needed
    pass

def downgrade():
    # This is a merge migration, no changes needed
    pass 