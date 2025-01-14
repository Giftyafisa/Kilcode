import os
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.db.base import Base  # This imports all models
from app.core.security import get_password_hash
from datetime import datetime, UTC

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = "sqlite:///./app.db"

def setup_all():
    try:
        # 1. Remove existing database
        if os.path.exists("app.db"):
            logger.info("Removing existing database...")
            os.remove("app.db")
            logger.info("Database file removed")

        # 2. Create engine and tables
        logger.info("Creating database and tables...")
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("Database and tables created successfully!")

        # 3. Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        try:
            # 4. Create test user
            logger.info("Creating test user...")
            hashed_password = get_password_hash("password123")
            current_time = datetime.now(UTC)
            
            # Create test user using raw SQL
            create_user_sql = text("""
                INSERT INTO users (
                    email,
                    name,
                    hashed_password,
                    country,
                    phone,
                    balance,
                    created_at,
                    updated_at,
                    is_active,
                    is_verified
                ) VALUES (
                    :email,
                    :name,
                    :password,
                    :country,
                    :phone,
                    :balance,
                    :created_at,
                    :updated_at,
                    :is_active,
                    :is_verified
                )
            """)

            db.execute(
                create_user_sql,
                {
                    "email": "tony@gmail.com",
                    "name": "Tony Test",
                    "password": hashed_password,
                    "country": "nigeria",
                    "phone": "+2341234567890",
                    "balance": 0.0,
                    "created_at": current_time,
                    "updated_at": current_time,
                    "is_active": True,
                    "is_verified": False
                }
            )
            
            db.commit()
            logger.info("Test user created successfully!")

            # 5. Verify setup
            logger.info("\nVerifying database setup...")
            
            # Check tables using inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info("\nCreated tables:")
            for table in tables:
                logger.info(f"- {table}")
                columns = inspector.get_columns(table)
                for column in columns:
                    logger.info(f"  * {column['name']} ({column['type']})")

            # Verify test user
            result = db.execute(text("SELECT email, name, country FROM users"))
            users = result.fetchall()
            
            logger.info("\nCreated users:")
            for user in users:
                logger.info(f"- {user[0]} ({user[1]}, {user[2]})")

        except Exception as e:
            logger.error(f"Error in database operations: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

        logger.info("\nSetup completed successfully!")
        logger.info("\nTest User Credentials:")
        logger.info("  Email: tony@gmail.com")
        logger.info("  Password: password123")

    except Exception as e:
        logger.error(f"Error during setup: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting database setup...")
    setup_all()  