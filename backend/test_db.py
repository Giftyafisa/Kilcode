from sqlalchemy import create_engine, inspect
import os

# Use the same database URL as setup_db.py
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)

def list_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("\nNo tables found in database!")
        return
        
    print("\nTables in database:")
    for table in tables:
        print(f"\n{table}:")
        for column in inspector.get_columns(table):
            print(f"  - {column['name']}: {column['type']}")
        
        # Print foreign keys
        for fk in inspector.get_foreign_keys(table):
            print(f"  FK: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

def check_database():
    if not os.path.exists("app.db"):
        print("\nDatabase file not found!")
        return False
    return True

if __name__ == "__main__":
    if check_database():
        list_tables() 