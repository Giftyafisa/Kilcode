import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from pathlib import Path

def get_sqlite_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall() if table[0] != 'alembic_version']

def get_table_schema(cursor, table):
    cursor.execute(f"PRAGMA table_info({table});")
    return cursor.fetchall()

def create_postgres_table(pg_cursor, table_name, schema):
    # Map SQLite types to PostgreSQL types
    type_mapping = {
        'INTEGER': 'INTEGER',
        'DATETIME': 'TIMESTAMP',
        'TEXT': 'TEXT',
        'BOOLEAN': 'BOOLEAN',
        'FLOAT': 'FLOAT',
        'VARCHAR': 'VARCHAR',
        'JSON': 'JSONB'
    }
    
    columns = []
    for col in schema:
        name = col[1]
        col_type = col[2].upper()
        
        # Handle special cases
        if 'DATETIME' in col_type:
            col_type = 'TIMESTAMP'
        elif 'VARCHAR' in col_type:
            col_type = 'VARCHAR'
        elif 'JSON' in col_type:
            col_type = 'JSONB'
        else:
            col_type = type_mapping.get(col_type, 'TEXT')
            
        nullable = 'NOT NULL' if col[3] else ''
        pk = 'PRIMARY KEY' if col[5] else ''
        
        columns.append(f"{name} {col_type} {pk} {nullable}".strip())
    
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns)}
    );
    """
    print(f"Creating table {table_name}...")
    print(create_sql)
    pg_cursor.execute(create_sql)

def convert_row_values(schema, row):
    """Convert row values based on their schema types"""
    converted_row = list(row)
    for i, col in enumerate(schema):
        col_type = col[2].upper()
        value = row[i]
        
        # Convert boolean values
        if col_type == 'BOOLEAN' or 'BOOL' in col_type:
            if isinstance(value, int):
                converted_row[i] = bool(value)
        
        # Convert JSON fields
        elif 'JSON' in col_type and value:
            if isinstance(value, str):
                converted_row[i] = value
            else:
                converted_row[i] = str(value)
    
    return tuple(converted_row)

def get_table_data(cursor, table):
    cursor.execute(f"SELECT * FROM {table};")
    return cursor.fetchall()

def migrate_data(sqlite_db_path, pg_connection_string):
    print(f"Starting migration from {sqlite_db_path}...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(pg_connection_string)
    pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    pg_cursor = pg_conn.cursor()

    # Get all tables from SQLite
    tables = get_sqlite_tables(sqlite_cursor)
    
    for table in tables:
        if table == 'sqlite_sequence':
            continue
            
        print(f"\nMigrating table: {table}")
        
        try:
            # Get table schema and create table
            schema = get_table_schema(sqlite_cursor, table)
            create_postgres_table(pg_cursor, table, schema)
            
            # Get column names
            columns = [col[1] for col in schema]
            
            # Get table data
            data = get_table_data(sqlite_cursor, table)
            
            if data:
                print(f"Found {len(data)} rows to migrate in {table}")
                
                # Create placeholders for INSERT statement
                placeholders = ','.join(['%s' for _ in columns])
                columns_str = ','.join(columns)
                
                # Insert data into PostgreSQL
                success_count = 0
                for row in data:
                    try:
                        # Convert row values based on schema
                        converted_row = convert_row_values(schema, row)
                        
                        pg_cursor.execute(
                            f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                            converted_row
                        )
                        success_count += 1
                    except Exception as e:
                        print(f"Error inserting into {table}: {e}")
                        print(f"Problematic row: {row}")
                        continue
                
                print(f"Successfully migrated {success_count} out of {len(data)} rows in {table}")
            else:
                print(f"No data found in table {table}")
                
        except Exception as e:
            print(f"Error processing table {table}: {e}")
            continue

    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    print("\nMigration completed!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate_to_postgres.py <postgres_connection_string>")
        sys.exit(1)

    pg_connection_string = sys.argv[1]
    base_dir = Path(__file__).resolve().parent.parent
    
    # Migrate app.db
    app_db_path = base_dir / "app.db"
    if app_db_path.exists():
        print("\nMigrating app.db...")
        migrate_data(str(app_db_path), pg_connection_string)
    else:
        print("\napp.db not found!")
    
    # Migrate admin.db
    admin_db_path = base_dir / "admin.db"
    if admin_db_path.exists():
        print("\nMigrating admin.db...")
        migrate_data(str(admin_db_path), pg_connection_string)
    else:
        print("\nadmin.db not found!") 