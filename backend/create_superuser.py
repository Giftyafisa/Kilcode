from sqlalchemy.orm import Session
from app.db.admin_session import AdminSessionLocal
from app.crud import admin
from app.schemas.admin import AdminCreate
from app.db.base import Base
from app.db.admin_session import admin_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=admin_engine)
    logger.info("Database tables created successfully")

def create_superuser():
    """Create superuser if it doesn't exist"""
    logger.info("Creating superuser...")
    
    # Initialize database
    init_db()
    
    # Create database session
    db = AdminSessionLocal()
    try:
        # Check if superuser already exists
        superuser = admin.get_by_email(db, email="giftyafisa@gmail.com")
        if not superuser:
            superuser_data = AdminCreate(
                email="giftyafisa@gmail.com",
                password="Admin123!",  # Change this in production
                full_name="Gifty Afisa",
                country="ghana",
                role="super_admin",
                is_active=True
            )
            admin.create(db, obj_in=superuser_data)
            logger.info("Superuser created successfully!")
        else:
            logger.info("Superuser already exists!")
    except Exception as e:
        logger.error(f"Error creating superuser: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser() 