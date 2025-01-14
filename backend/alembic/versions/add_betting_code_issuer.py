"""add issuer columns to betting_codes

Revision ID: add_betting_code_issuer
Revises: merge_betting_code_heads
Create Date: 2024-03-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_betting_code_issuer'
down_revision = 'merge_betting_code_heads'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.add_column(sa.Column('issuer', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('issuer_type', sa.String(20), nullable=True))

def downgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.drop_column('issuer_type')
        batch_op.drop_column('issuer') 