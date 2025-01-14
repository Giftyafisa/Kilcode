"""merge heads v2

Revision ID: merge_heads_v2
Revises: add_payment_phone_field_v2, add_payment_type_field, add_user_status_field
Create Date: 2024-03-07 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads_v2'
down_revision = ('add_payment_phone_field_v2', 'add_payment_type_field', 'add_user_status_field')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 