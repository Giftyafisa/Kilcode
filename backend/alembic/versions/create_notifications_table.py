"""create notifications table

Revision ID: create_notifications_table
Revises: add_payment_data_column
Create Date: 2023-12-02 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_notifications_table'
down_revision = 'add_payment_data_column'
branch_labels = None
depends_on = None

def upgrade():
    # Check if table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'notifications' not in inspector.get_table_names():
        # Create table only if it doesn't exist
        op.create_table(
            'notifications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('message', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('notification_data', sa.JSON(), nullable=True),
            sa.Column('read', sa.Boolean(), default=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)')),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications') 