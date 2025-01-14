import os
import logging
import sqlite3
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_migrations():
    try:
        # 1. Close any existing connections and processes
        try:
            import psutil
            process = psutil.Process()
            for handler in process.open_files():
                if handler.path.endswith('app.db'):
                    os.close(handler.fd)
        except:
            pass

        engine = create_engine('sqlite:///app.db')
        engine.dispose()

        # 2. Remove the database file
        if os.path.exists("app.db"):
            logger.info("Removing database file...")
            try:
                os.remove("app.db")
                logger.info("Database file removed")
            except PermissionError:
                logger.warning("Could not remove database file - may be in use")
                return

        # 3. Remove all migration files except __init__.py
        versions_dir = "alembic/versions"
        if os.path.exists(versions_dir):
            for filename in os.listdir(versions_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    try:
                        file_path = os.path.join(versions_dir, filename)
                        os.remove(file_path)
                        logger.info(f"Removed migration file: {filename}")
                    except Exception as e:
                        logger.warning(f"Could not remove {filename}: {str(e)}")

        # 4. Create new migration
        logger.info("Creating new migration...")
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message="create_all_tables")
        
        # 5. Run the migration
        logger.info("Running migration...")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Migration reset completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during reset: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting migration reset...")
    reset_migrations() 