from alembic import command
from alembic.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_heads():
    try:
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Create a new merge migration
        logger.info("Creating merge migration...")
        command.merge(alembic_cfg, "heads", message="merge multiple heads")
        
        logger.info("Migration heads merged successfully!")
        
    except Exception as e:
        logger.error(f"Error merging migration heads: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting migration heads merge...")
    merge_heads() 