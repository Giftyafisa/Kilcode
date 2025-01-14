import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.run_migrations import run_all_migrations
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting migrations...")
    try:
        success = run_all_migrations()
        if success:
            logger.info("All migrations completed successfully!")
        else:
            logger.error("Some migrations failed.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        sys.exit(1) 