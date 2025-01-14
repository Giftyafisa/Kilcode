from sqlalchemy import create_engine, MetaData
from alembic import command
from alembic.config import Config
import os
import logging
import sqlite3

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create engine
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)

def drop_all_tables():
    """Drop all tables in SQLite database"""
    try:
        if os.path.exists("app.db"):
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Drop each table
            for table in tables:
                if table[0] != "sqlite_sequence":  # Skip SQLite internal table
                    logger.info(f"Dropping table: {table[0]}")
                    cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
            
            conn.commit()
            conn.close()
            logger.info("All tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping tables: {str(e)}")
        raise

def setup_database():
    try:
        # Drop all existing tables
        drop_all_tables()
        
        # Run Alembic migrations
        logger.info("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "heads")
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting database setup...")
    setup_database() 