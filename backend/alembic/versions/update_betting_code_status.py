"""update betting code status

Revision ID: update_betting_code_status
Revises: add_betting_code_admin_fields
Create Date: 2024-03-02 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'update_betting_code_status'
down_revision = 'add_betting_code_admin_fields'
branch_labels = None
depends_on = None

def upgrade():
    # SQLite doesn't support ENUM, so we'll use CHECK constraint
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.alter_column('status',
            type_=sa.String(),
            existing_type=sa.String(),
            nullable=False
        )
        batch_op.create_check_constraint(
            'betting_status_check',
            'status IN ("pending", "won", "lost")'
        )

def downgrade():
    with op.batch_alter_table('betting_codes') as batch_op:
        batch_op.drop_constraint('betting_status_check') 