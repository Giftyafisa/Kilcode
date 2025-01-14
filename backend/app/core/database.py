from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from ..db.base import Base
from .config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Database URLs
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
SQLALCHEMY_ADMIN_DATABASE_URL = "sqlite:///./admin.db"

# Ensure the database directories exist for SQLite
for db_url in [SQLALCHEMY_DATABASE_URL, SQLALCHEMY_ADMIN_DATABASE_URL]:
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        # Remove leading ./ if present
        db_path = db_path.replace("./", "")
        # Get the directory path, use '.' if empty
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

# Create engines
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
    echo=True
)

admin_engine = create_engine(
    SQLALCHEMY_ADMIN_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)

# Create SessionLocal classes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_admin_db():
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    try:
        # Create tables
        logger.info("Creating database tables...")
        
        # Import all models to ensure they're registered
        from app.db.base import Base
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=admin_engine)  # Also create admin tables
        
        # Verify databases
        for db_engine in [engine, admin_engine]:
            with db_engine.connect() as conn:
                # Enable foreign keys for SQLite
                if str(db_engine.url).startswith("sqlite"):
                    conn.execute(text("PRAGMA foreign_keys=ON"))
                
                # Verify tables exist
                inspector = inspect(db_engine)
                tables = inspector.get_table_names()
                logger.info(f"Available tables in {db_engine.url}: {tables}")
                
                if "users" not in tables:
                    logger.error("Users table not found after creation!")
                    raise Exception("Users table was not created properly")
                else:
                    logger.info("Users table verified successfully")
                    
                # Log all tables
                for table in tables:
                    logger.info(f"Found table: {table}")
                    
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise