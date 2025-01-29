"""add note to payments table

Revision ID: add_note_to_payments
Revises: be02c604eb30
Create Date: 2023-12-19 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError


# revision identifiers, used by Alembic.
revision = 'add_note_to_payments'
down_revision = 'be02c604eb30'
branch_labels = None
depends_on = None


def upgrade():
    # Add note column to payments table if it doesn't exist
    try:
        op.add_column('payments', sa.Column('note', sa.String(), nullable=True))
    except OperationalError:
        # Column already exists, skip
        pass


def downgrade():
    # Remove note column from payments table
    try:
        op.drop_column('payments', 'note')
    except OperationalError:
        # Column doesn't exist, skip
        pass