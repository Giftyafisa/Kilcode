from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.base import Base

# Create admin engine
admin_engine = create_engine(settings.ADMIN_DATABASE_URL)

# Create all tables
Base.metadata.create_all(bind=admin_engine)

# Create admin session factory
AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

def get_admin_db() -> Session:
    """Get admin database session"""
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close() 