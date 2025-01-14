import os
import logging
import sqlite3
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_database():
    try:
        db_path = "app.db"
        
        # 1. Close any existing connections
        engine = create_engine(f'sqlite:///{db_path}')
        engine.dispose()
        
        # 2. Drop all tables if database exists
        if os.path.exists(db_path):
            logger.info("Dropping existing tables...")
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Drop each table
                for table in tables:
                    if table[0] != 'sqlite_sequence':  # Skip SQLite internal tables
                        cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
                
                conn.commit()
                conn.close()
                logger.info("Existing tables dropped")
                
            except Exception as e:
                logger.error(f"Error dropping tables: {str(e)}")
                raise
        
        # 3. Run the migrations
        logger.info("Running migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "heads")
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting database cleanup...")
    clean_database() 