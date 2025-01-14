from sqlalchemy import text
from app.core.database import engine, admin_engine
import logging
from alembic import op
import sqlalchemy as sa

logger = logging.getLogger(__name__)

def run_migration():
    """Add marketplace fields to betting_codes table"""
    try:
        # Add columns to both main and admin databases
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Add win_probability if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='win_probability'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding win_probability column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN win_probability FLOAT"
                    ))
                    conn.commit()
                    logger.info("win_probability column added successfully")

                # Add expected_odds if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='expected_odds'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding expected_odds column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN expected_odds FLOAT"
                    ))
                    conn.commit()
                    logger.info("expected_odds column added successfully")

                # Add valid_until if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='valid_until'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding valid_until column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN valid_until TIMESTAMP"
                    ))
                    conn.commit()
                    logger.info("valid_until column added successfully")

                # Add min_stake if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='min_stake'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding min_stake column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN min_stake FLOAT"
                    ))
                    conn.commit()
                    logger.info("min_stake column added successfully")

                # Add tags if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='tags'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding tags column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN tags JSON"
                    ))
                    conn.commit()
                    logger.info("tags column added successfully")

                # Add marketplace_status if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='marketplace_status'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding marketplace_status column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN marketplace_status VARCHAR DEFAULT 'draft'"
                    ))
                    conn.commit()
                    logger.info("marketplace_status column added successfully")

                # Add is_published if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='is_published'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding is_published column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN is_published BOOLEAN DEFAULT FALSE"
                    ))
                    conn.commit()
                    logger.info("is_published column added successfully")

                # Add category if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='category'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding category column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN category VARCHAR DEFAULT 'General'"
                    ))
                    conn.commit()
                    logger.info("category column added successfully")

        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False 

def upgrade():
    # Add new columns to betting_codes table
    op.add_column('betting_codes', sa.Column('title', sa.String(100), nullable=True))
    op.add_column('betting_codes', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('betting_codes', sa.Column('issuer', sa.String(100), nullable=True))
    op.add_column('betting_codes', sa.Column('issuer_type', sa.String(20), nullable=True))
    op.add_column('betting_codes', sa.Column('marketplace_status', sa.String(20), nullable=True))
    op.add_column('betting_codes', sa.Column('analysis_status', sa.String(20), nullable=True))
    op.add_column('betting_codes', sa.Column('user_country', sa.String(50), nullable=True))

def downgrade():
    # Remove the new columns
    op.drop_column('betting_codes', 'title')
    op.drop_column('betting_codes', 'category')
    op.drop_column('betting_codes', 'issuer')
    op.drop_column('betting_codes', 'issuer_type')
    op.drop_column('betting_codes', 'marketplace_status')
    op.drop_column('betting_codes', 'analysis_status')
    op.drop_column('betting_codes', 'user_country') 