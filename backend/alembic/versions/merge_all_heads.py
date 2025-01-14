"""merge all heads

Revision ID: merge_all_heads
Revises: add_payment_type_field, add_user_status_column, add_user_payment_fields
Create Date: 2024-03-06 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_all_heads'
down_revision = ('add_payment_type_field', 'add_user_status_column', 'add_user_payment_fields')
branch_labels = None
depends_on = None

def upgrade():
    # This is a merge migration, no changes needed
    pass

def downgrade():
    # This is a merge migration, no changes needed
    pass 