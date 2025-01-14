import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def clear_database():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Drop all tables
    with engine.connect() as conn:
        # Get all table names
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        
        # Drop each table
        for table in tables:
            if table != 'sqlite_sequence':  # Skip SQLite internal table
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        conn.commit()
    
    # Remove the database file
    try:
        os.remove("app.db")
        print("Database cleared successfully")
    except FileNotFoundError:
        print("Database file not found")
    except Exception as e:
        print(f"Error clearing database: {str(e)}")

if __name__ == "__main__":
    clear_database() 