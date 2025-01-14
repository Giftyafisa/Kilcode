"""add phone field to payments v2

Revision ID: add_payment_phone_field_v2
Revises: add_payment_type_field
Create Date: 2024-03-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'add_payment_phone_field_v2'
down_revision = 'add_payment_type_field'
branch_labels = None
depends_on = None

def upgrade():
    # SQLite doesn't support ALTER TABLE ADD COLUMN with constraints
    # So we need to create a new table, copy data, drop old table, and rename new table
    
    # Create new table with all columns including phone
    op.execute("""
        CREATE TABLE payments_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount FLOAT NOT NULL,
            currency VARCHAR,
            reference VARCHAR,
            status VARCHAR,
            payment_method VARCHAR,
            payment_data JSON,
            type VARCHAR DEFAULT 'registration',
            verified_by INTEGER,
            verified_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            phone VARCHAR,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(verified_by) REFERENCES admins(id)
        )
    """)
    
    # Copy data from old table to new table
    op.execute("""
        INSERT INTO payments_new (
            id, user_id, amount, currency, reference, status, 
            payment_method, payment_data, type, verified_by, 
            verified_at, created_at
        )
        SELECT 
            id, user_id, amount, currency, reference, status,
            payment_method, payment_data, type, verified_by,
            verified_at, created_at
        FROM payments
    """)
    
    # Drop old table
    op.drop_table('payments')
    
    # Rename new table to original name
    op.rename_table('payments_new', 'payments')

def downgrade():
    # Create table without phone column
    op.execute("""
        CREATE TABLE payments_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount FLOAT NOT NULL,
            currency VARCHAR,
            reference VARCHAR,
            status VARCHAR,
            payment_method VARCHAR,
            payment_data JSON,
            type VARCHAR DEFAULT 'registration',
            verified_by INTEGER,
            verified_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(verified_by) REFERENCES admins(id)
        )
    """)
    
    # Copy data excluding phone column
    op.execute("""
        INSERT INTO payments_old (
            id, user_id, amount, currency, reference, status,
            payment_method, payment_data, type, verified_by,
            verified_at, created_at
        )
        SELECT 
            id, user_id, amount, currency, reference, status,
            payment_method, payment_data, type, verified_by,
            verified_at, created_at
        FROM payments
    """)
    
    # Drop new table
    op.drop_table('payments')
    
    # Rename old table to original name
    op.rename_table('payments_old', 'payments') 