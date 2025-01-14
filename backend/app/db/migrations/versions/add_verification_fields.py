"""add verification fields

Revision ID: add_verification_fields
Revises: 
Create Date: 2024-03-03 05:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_verification_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add verification fields to betting_codes table
    op.add_column('betting_codes', sa.Column('verified_by', sa.Integer(), sa.ForeignKey('admins.id', ondelete='SET NULL'), nullable=True))
    op.add_column('betting_codes', sa.Column('admin_note', sa.Text(), nullable=True))
    op.add_column('betting_codes', sa.Column('rejection_reason', sa.String(), nullable=True))
    op.add_column('betting_codes', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    # Remove verification fields from betting_codes table
    op.drop_column('betting_codes', 'verified_by')
    op.drop_column('betting_codes', 'admin_note')
    op.drop_column('betting_codes', 'rejection_reason')
    op.drop_column('betting_codes', 'verified_at') 