"""add reset token columns

Revision ID: add_reset_token_columns
Revises: merge_migration_heads
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_reset_token_columns'
down_revision = 'merge_migration_heads'
branch_labels = None
depends_on = None


def upgrade():
    # Add reset_token and reset_token_expires columns
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # Remove the columns
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token') 