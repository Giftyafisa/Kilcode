"""create admin table

Revision ID: create_admin_table
Revises: update_betting_code_status
Create Date: 2024-03-02 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_admin_table'
down_revision = 'update_betting_code_status'
branch_labels = None
depends_on = None

def upgrade():
    # Create admins table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'admins'):
        op.create_table(
            'admins',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('full_name', sa.String(), nullable=True),
            sa.Column('country', sa.String(), nullable=True),
            sa.Column('role', sa.String(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)
        op.create_index(op.f('ix_admins_id'), 'admins', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_admins_id'), table_name='admins')
    op.drop_index(op.f('ix_admins_email'), table_name='admins')
    op.drop_table('admins') 