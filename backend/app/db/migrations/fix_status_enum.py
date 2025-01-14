import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sqlalchemy import text
from app.core.database import engine, admin_engine
import logging

logger = logging.getLogger(__name__)

def run_migration():
    """Fix status enum type in betting_codes table"""
    try:
        # Apply to both main and admin databases
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Drop existing status check constraint if it exists
                try:
                    conn.execute(text("DROP INDEX IF EXISTS status_types"))
                except Exception as e:
                    logger.warning(f"Could not drop index: {str(e)}")

                # Create new status check constraint
                conn.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS check_status_types
                    BEFORE INSERT ON betting_codes
                    BEGIN
                        SELECT CASE 
                            WHEN NEW.status NOT IN ('pending', 'won', 'lost', 'analyzing', 'approved', 'rejected')
                            THEN RAISE(ABORT, 'Invalid status value')
                        END;
                    END;
                """))
                
                # Create update trigger
                conn.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS check_status_types_update
                    BEFORE UPDATE ON betting_codes
                    BEGIN
                        SELECT CASE 
                            WHEN NEW.status NOT IN ('pending', 'won', 'lost', 'analyzing', 'approved', 'rejected')
                            THEN RAISE(ABORT, 'Invalid status value')
                        END;
                    END;
                """))

                conn.commit()
                logger.info("Status enum fixed successfully")

    except Exception as e:
        logger.error(f"Error fixing status enum: {str(e)}")
        raise e

def upgrade():
    run_migration()

def downgrade():
    """Remove the triggers"""
    try:
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                conn.execute(text("DROP TRIGGER IF EXISTS check_status_types"))
                conn.execute(text("DROP TRIGGER IF EXISTS check_status_types_update"))
                conn.commit()
    except Exception as e:
        logger.error(f"Error in downgrade: {str(e)}")
        raise e
