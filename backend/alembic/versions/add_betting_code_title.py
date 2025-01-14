"""add title column to betting_codes

Revision ID: add_betting_code_title
Revises: update_betting_code_status
Create Date: 2024-03-02 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_betting_code_title'
down_revision = 'update_betting_code_status'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(100), nullable=True))

def downgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.drop_column('title') 