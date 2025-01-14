import logging
from app.db.migrations.add_price_column import run_migration as add_price_column
from app.db.migrations.add_admin_stats import run_migration as add_admin_stats
from app.db.migrations.add_marketplace_fields import run_migration as add_marketplace_fields
from app.db.migrations.add_marketplace_tables import run_migration as add_marketplace_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_all_migrations():
    """Run all database migrations in order"""
    migrations = [
        ("Add price column", add_price_column),
        ("Add admin stats", add_admin_stats),
        ("Add marketplace fields", add_marketplace_fields),
        ("Add marketplace tables", add_marketplace_tables),
    ]
    
    for name, migration in migrations:
        logger.info(f"Running migration: {name}")
        success = migration()
        if not success:
            logger.error(f"Migration failed: {name}")
            return False
        logger.info(f"Migration completed: {name}")
    
    return True

if __name__ == "__main__":
    run_all_migrations() 