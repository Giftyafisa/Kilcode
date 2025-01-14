"""add description to betting code

Revision ID: add_description_to_betting_code
Revises: da227da27c87
Create Date: 2024-01-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_description_to_betting_code'
down_revision = 'da227da27c87'
branch_labels = None
depends_on = None


def upgrade():
    # Add description column to betting_codes table
    op.add_column('betting_codes', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # Remove description column from betting_codes table
    op.drop_column('betting_codes', 'description') 