"""add user_country column to betting_codes

Revision ID: add_betting_code_country
Revises: merge_issuer_heads
Create Date: 2024-03-02 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_betting_code_country'
down_revision = 'merge_issuer_heads'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.add_column(sa.Column('user_country', sa.String(50), nullable=True))

def downgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.drop_column('user_country') 