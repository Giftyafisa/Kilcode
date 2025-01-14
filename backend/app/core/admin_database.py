from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..db.base_class import Base
from .admin_config import admin_settings
from dotenv import load_dotenv

load_dotenv()

ADMIN_DATABASE_URL = admin_settings.ADMIN_DATABASE_URL

# Create engine with proper configuration
if ADMIN_DATABASE_URL.startswith("sqlite"):
    admin_engine = create_engine(
        ADMIN_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    admin_engine = create_engine(
        ADMIN_DATABASE_URL,
        pool_pre_ping=True
    )

# Create sessionmaker
AdminSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=admin_engine,
    expire_on_commit=False
)

# Dependency
def get_admin_db() -> Session:
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def init_admin_db():
    Base.metadata.create_all(bind=admin_engine) 