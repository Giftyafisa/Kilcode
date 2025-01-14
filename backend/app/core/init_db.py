from app.core.database import engine
from app.db.base_class import Base
from app.models.payment import Payment  # Import all your models
from app.models.user import User  # Import all your models

def init_db():
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_db() 