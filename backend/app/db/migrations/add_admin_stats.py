from sqlalchemy import text
from app.core.database import engine, admin_engine
import logging

logger = logging.getLogger(__name__)

def run_migration():
    """Add analysis_stats column to admins table"""
    try:
        # Add column to both main and admin databases
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Check if column exists
                result = conn.execute(text(
                    "SELECT name FROM pragma_table_info('admins') WHERE name='analysis_stats'"
                ))
                if result.fetchone() is None:
                    logger.info("Adding analysis_stats column to admins table...")
                    conn.execute(text(
                        "ALTER TABLE admins ADD COLUMN analysis_stats JSON DEFAULT '{\"total_analyzed\": 0, \"approved\": 0, \"rejected\": 0, \"pending\": 0, \"accuracy_rate\": 0.0}'"
                    ))
                    conn.commit()
                    logger.info("analysis_stats column added successfully")
                else:
                    logger.info("analysis_stats column already exists")
                
        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False 