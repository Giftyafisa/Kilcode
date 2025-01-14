from app.db.base_class import Base
from app.core.admin_database import admin_engine, AdminSessionLocal
from app.models.admin import Admin, AdminRole
from app.core.security import get_password_hash
import logging

# Import all models to ensure they are registered with SQLAlchemy
from app.db.base import *  # This line is important!

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    
    # Drop all tables first
    Base.metadata.drop_all(bind=admin_engine)
    logger.info("Dropped existing tables")
    
    # Create all tables
    Base.metadata.create_all(bind=admin_engine)
    logger.info("Database tables created successfully!")
    
    # Create a new session
    session = AdminSessionLocal()
    
    try:
        # Create Ghana admin
        ghana_admin = Admin(
            email="giftyafisa@gmail.com",
            name="Gifty Afisa",
            country="GHANA",
            role=AdminRole.SUPER_ADMIN,
            hashed_password=get_password_hash("0553366244"),
            is_active=True
        )
        
        # Add to session
        session.add(ghana_admin)
        session.flush()
        
        # Create Nigeria admin
        nigeria_admin = Admin(
            email="admin.nigeria@example.com",
            name="Nigeria Admin",
            country="NIGERIA",
            role=AdminRole.COUNTRY_ADMIN,
            hashed_password=get_password_hash("Admin123!"),
            is_active=True
        )
        
        # Add to session
        session.add(nigeria_admin)
        session.flush()
        
        # Commit the changes
        session.commit()
        logger.info("Admin users created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating admins: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}") 