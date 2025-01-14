import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sqlalchemy import text
from app.core.database import engine, admin_engine
import logging

logger = logging.getLogger(__name__)

def run_migration():
    """Fix betting_status_check constraint in betting_codes table"""
    try:
        # Apply to both main and admin databases
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Drop the old constraint
                conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name='betting_codes_old';
                """))
                
                # Create new table with updated constraint
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS betting_codes_new (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        bookmaker VARCHAR,
                        code VARCHAR,
                        odds FLOAT,
                        stake FLOAT NOT NULL,
                        potential_winnings FLOAT NOT NULL,
                        status VARCHAR NOT NULL,
                        admin_note VARCHAR,
                        rejection_reason VARCHAR,
                        verified_by INTEGER REFERENCES admins(id),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        verified_at DATETIME,
                        price FLOAT,
                        current_analysis_id INTEGER REFERENCES code_analyses(id) ON DELETE SET NULL,
                        analysis_status VARCHAR DEFAULT 'pending',
                        market_data JSON,
                        win_probability FLOAT,
                        expected_odds FLOAT,
                        valid_until TIMESTAMP,
                        min_stake FLOAT,
                        tags JSON,
                        marketplace_status VARCHAR DEFAULT 'draft',
                        is_published BOOLEAN DEFAULT FALSE,
                        category VARCHAR DEFAULT 'General',
                        description TEXT,
                        title VARCHAR(100),
                        issuer VARCHAR(100),
                        issuer_type VARCHAR(20),
                        user_country VARCHAR(50),
                        CONSTRAINT check_odds_positive CHECK (odds >= 1.0),
                        CONSTRAINT check_stake_positive CHECK (stake > 0),
                        CONSTRAINT check_potential_winnings CHECK (potential_winnings >= stake),
                        CONSTRAINT betting_status_check CHECK (status IN ('pending', 'won', 'lost', 'analyzing', 'approved', 'rejected'))
                    )
                """))
                
                # Copy data from old table to new table
                conn.execute(text("""
                    INSERT INTO betting_codes_new 
                    SELECT * FROM betting_codes
                """))
                
                # Drop old table
                conn.execute(text("DROP TABLE betting_codes"))
                
                # Rename new table to original name
                conn.execute(text("ALTER TABLE betting_codes_new RENAME TO betting_codes"))
                
                # Recreate the index
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_betting_codes_id 
                    ON betting_codes (id)
                """))
                
                conn.commit()
                logger.info("Successfully updated betting_status_check constraint")

    except Exception as e:
        logger.error(f"Error updating betting_status_check constraint: {str(e)}")
        raise e

def upgrade():
    run_migration()

def downgrade():
    """Revert the constraint change"""
    try:
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Create temporary table with old constraint
                conn.execute(text("""
                    CREATE TABLE betting_codes_old AS 
                    SELECT * FROM betting_codes
                """))
                
                # Drop current table
                conn.execute(text("DROP TABLE betting_codes"))
                
                # Create table with old constraint
                conn.execute(text("""
                    CREATE TABLE betting_codes (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        bookmaker VARCHAR,
                        code VARCHAR,
                        odds FLOAT,
                        stake FLOAT NOT NULL,
                        potential_winnings FLOAT NOT NULL,
                        status VARCHAR NOT NULL,
                        admin_note VARCHAR,
                        rejection_reason VARCHAR,
                        verified_by INTEGER REFERENCES admins(id),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        verified_at DATETIME,
                        price FLOAT,
                        current_analysis_id INTEGER REFERENCES code_analyses(id) ON DELETE SET NULL,
                        analysis_status VARCHAR DEFAULT 'pending',
                        market_data JSON,
                        win_probability FLOAT,
                        expected_odds FLOAT,
                        valid_until TIMESTAMP,
                        min_stake FLOAT,
                        tags JSON,
                        marketplace_status VARCHAR DEFAULT 'draft',
                        is_published BOOLEAN DEFAULT FALSE,
                        category VARCHAR DEFAULT 'General',
                        description TEXT,
                        title VARCHAR(100),
                        issuer VARCHAR(100),
                        issuer_type VARCHAR(20),
                        user_country VARCHAR(50),
                        CONSTRAINT check_odds_positive CHECK (odds >= 1.0),
                        CONSTRAINT check_stake_positive CHECK (stake > 0),
                        CONSTRAINT check_potential_winnings CHECK (potential_winnings >= stake),
                        CONSTRAINT betting_status_check CHECK (status IN ('pending', 'won', 'lost'))
                    )
                """))
                
                # Copy data back
                conn.execute(text("""
                    INSERT INTO betting_codes 
                    SELECT * FROM betting_codes_old
                """))
                
                # Drop temporary table
                conn.execute(text("DROP TABLE betting_codes_old"))
                
                # Recreate the index
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_betting_codes_id 
                    ON betting_codes (id)
                """))
                
                conn.commit()
    except Exception as e:
        logger.error(f"Error in downgrade: {str(e)}")
        raise e
