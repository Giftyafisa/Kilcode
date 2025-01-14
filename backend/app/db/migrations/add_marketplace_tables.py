from sqlalchemy import text
from app.core.database import engine, admin_engine
import logging

logger = logging.getLogger(__name__)

def run_migration():
    """Add marketplace-related tables"""
    try:
        # Add tables to both main and admin databases
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Create code_views table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS code_views (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code_id INTEGER NOT NULL,
                        viewer_id INTEGER,
                        viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        FOREIGN KEY (code_id) REFERENCES betting_codes(id) ON DELETE CASCADE,
                        FOREIGN KEY (viewer_id) REFERENCES users(id) ON DELETE SET NULL
                    )
                """))
                
                # Create code_purchases table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS code_purchases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code_id INTEGER NOT NULL,
                        buyer_id INTEGER,
                        amount FLOAT NOT NULL,
                        currency VARCHAR NOT NULL,
                        status VARCHAR NOT NULL DEFAULT 'completed',
                        purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        FOREIGN KEY (code_id) REFERENCES betting_codes(id) ON DELETE CASCADE,
                        FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE SET NULL
                    )
                """))
                
                # Create code_ratings table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS code_ratings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code_id INTEGER NOT NULL,
                        rater_id INTEGER,
                        rating FLOAT NOT NULL,
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP,
                        FOREIGN KEY (code_id) REFERENCES betting_codes(id) ON DELETE CASCADE,
                        FOREIGN KEY (rater_id) REFERENCES users(id) ON DELETE SET NULL
                    )
                """))
                
                # Add indexes for better performance
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_code_views_code_id ON code_views(code_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_code_purchases_code_id ON code_purchases(code_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_code_ratings_code_id ON code_ratings(code_id)"))
                
                conn.commit()
                logger.info("Marketplace tables created successfully")

        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False 