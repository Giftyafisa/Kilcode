"""add betting code admin fields

Revision ID: add_betting_code_admin_fields
Revises: create_notifications_table
Create Date: 2024-03-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers
revision = 'add_betting_code_admin_fields'
down_revision = 'create_notifications_table'
branch_labels = None
depends_on = None

def has_column(table, column):
    # Check if column exists
    conn = op.get_bind()
    insp = inspect(conn)
    columns = [c['name'] for c in insp.get_columns(table)]
    return column in columns

def upgrade():
    # Add columns if they don't exist
    if not has_column('betting_codes', 'verified_at'):
        op.add_column('betting_codes', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
    
    if not has_column('betting_codes', 'verified_by'):
        op.add_column('betting_codes', sa.Column('verified_by', sa.Integer(), nullable=True))
    
    if not has_column('betting_codes', 'admin_note'):
        op.add_column('betting_codes', sa.Column('admin_note', sa.Text(), nullable=True))
    
    # Add foreign key constraint
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.create_foreign_key(
            'fk_betting_codes_admin',
            'admins',
            ['verified_by'],
            ['id']
        )

def downgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.drop_constraint('fk_betting_codes_admin', type_='foreignkey')
    
    op.drop_column('betting_codes', 'admin_note')
    op.drop_column('betting_codes', 'verified_by')
    op.drop_column('betting_codes', 'verified_at') 