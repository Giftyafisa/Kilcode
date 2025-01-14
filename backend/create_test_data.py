from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash
import logging
from datetime import datetime, UTC

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_data():
    db = SessionLocal()
    try:
        # Create test user
        hashed_password = get_password_hash("password123")
        current_time = datetime.now(UTC)
        
        # Insert test user using text()
        user_sql = text("""
            INSERT INTO users (
                email, 
                name, 
                hashed_password, 
                country, 
                phone, 
                balance, 
                created_at,
                is_active,
                is_verified
            ) VALUES (:email, :name, :password, :country, :phone, :balance, :created_at, :is_active, :is_verified)
        """)
        
        db.execute(
            user_sql,
            {
                "email": "tony@gmail.com",
                "name": "Tony Test",
                "password": hashed_password,
                "country": "nigeria",
                "phone": "+2341234567890",
                "balance": 0.0,
                "created_at": current_time,
                "is_active": True,
                "is_verified": False
            }
        )
        
        db.commit()
        logger.info("Test user created successfully!")
        logger.info("\nTest User Credentials:")
        logger.info("  Email: tony@gmail.com")
        logger.info("  Password: password123")
        
    except Exception as e:
        logger.error(f"Error creating test data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Creating test data...")
    create_test_data() 