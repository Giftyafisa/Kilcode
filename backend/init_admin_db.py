from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.core.database import admin_engine
from app.db.admin_session import AdminSessionLocal
from app.models.admin import Admin, AdminRole, CountryEnum
from app.core.security import get_password_hash
import logging
from sqlalchemy.orm import Session
import sqlite3

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_drop_admin_table():
    """Check if admin table exists and drop it if needed"""
    try:
        # Connect directly to SQLite database
        conn = sqlite3.connect('./admin.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admins'")
        if cursor.fetchone():
            logger.info("Found existing admins table, dropping it...")
            cursor.execute("DROP TABLE IF EXISTS admins")
            conn.commit()
            logger.info("Dropped existing admins table")
        
        conn.close()
    except Exception as e:
        logger.error(f"Error checking/dropping admin table: {str(e)}")
        raise

def create_admin_tables():
    """Create admin tables with correct schema"""
    try:
        # Create tables using SQLAlchemy models
        Base.metadata.create_all(bind=admin_engine, tables=[Admin.__table__])
        logger.info("Created admin table with new schema")
    except Exception as e:
        logger.error(f"Error creating admin table: {str(e)}")
        raise

def init_admin_db():
    logger.info("Initializing admin database...")
    
    try:
        # First check and drop existing table
        check_and_drop_admin_table()
        
        # Create admin table with correct schema
        create_admin_tables()
        
        # Create a database session
        db: Session = AdminSessionLocal()
        
        try:
            # Create Ghana admin
            ghana_admin = Admin(
                email="giftyafisa@gmail.com",
                full_name="Gifty Afisa",
                country="ghana",
                role=AdminRole.SUPER_ADMIN.value,
                hashed_password=get_password_hash("0553366244"),
                is_active=True
            )
            
            db.add(ghana_admin)
            logger.info("Created Ghana admin user")
            
            # Create Nigeria admin
            nigeria_admin = Admin(
                email="admin.nigeria@example.com",
                full_name="Nigeria Admin",
                country="nigeria",
                role=AdminRole.COUNTRY_ADMIN.value,
                hashed_password=get_password_hash("Admin123!"),
                is_active=True
            )
            
            db.add(nigeria_admin)
            logger.info("Created Nigeria admin user")
            
            # Commit the changes
            db.commit()
            
            # Verify admins were created
            admins = db.query(Admin).all()
            logger.info("\nCreated Admin Users:")
            for admin in admins:
                logger.info(f"""
                Admin user details:
                - Email: {admin.email}
                - Full Name: {admin.full_name}
                - Country: {admin.country}
                - Role: {admin.role}
                - Is active: {admin.is_active}
                """)
                
        except Exception as e:
            logger.error(f"Error creating admins: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        init_admin_db()
        logger.info("Admin database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize admin database: {str(e)}") 