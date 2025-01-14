from sqlalchemy import text
from app.core.database import engine, admin_engine
import logging

logger = logging.getLogger(__name__)

def run_migration():
    """Add missing columns to betting_codes table"""
    try:
        # Add columns to both main and admin databases
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Add current_analysis_id if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='current_analysis_id'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding current_analysis_id column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN current_analysis_id INTEGER REFERENCES code_analyses(id) ON DELETE SET NULL"
                    ))
                    conn.commit()
                    logger.info("current_analysis_id column added successfully")

                # Add analysis_status if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='analysis_status'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding analysis_status column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN analysis_status VARCHAR DEFAULT 'pending'"
                    ))
                    conn.commit()
                    logger.info("analysis_status column added successfully")

                # Add market_data if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='market_data'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding market_data column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN market_data JSON"
                    ))
                    conn.commit()
                    logger.info("market_data column added successfully")

                # Add price if it doesn't exist
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('betting_codes') WHERE name='price'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding price column...")
                    conn.execute(text(
                        "ALTER TABLE betting_codes ADD COLUMN price FLOAT"
                    ))
                    conn.commit()
                    logger.info("price column added successfully")

        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False 