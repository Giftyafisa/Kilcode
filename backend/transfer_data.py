import sqlite3
import psycopg2
import json
from psycopg2.extras import Json

def transfer_data():
    # SQLite connection
    sqlite_conn = sqlite3.connect('admin.db')
    sqlite_cur = sqlite_conn.cursor()

    # PostgreSQL connection
    pg_conn = psycopg2.connect(
        "postgresql://neondb_owner:SXTcliLd3P2t@ep-patient-hall-a9zlztc2.gwc.azure.neon.tech/neondb?sslmode=require"
    )
    pg_cur = pg_conn.cursor()

    try:
        # First, let's handle the admins table separately
        print("Transferring admins...")
        sqlite_cur.execute("SELECT * FROM admins")
        admin_rows = sqlite_cur.fetchall()
        
        for row in admin_rows:
            # Convert row to list for modification
            row_data = list(row)
            
            # Convert JSON strings to PostgreSQL JSON
            analysis_stats = Json(json.loads(row_data[9])) if row_data[9] else Json({})
            payment_stats = Json(json.loads(row_data[10])) if row_data[10] else Json({})
            
            # Convert integer to boolean for is_active
            is_active = bool(row_data[6])
            
            # Insert admin data
            insert_query = """
                INSERT INTO admins (
                    id, email, hashed_password, full_name, country, role, 
                    is_active, created_at, updated_at, analysis_stats, payment_stats
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    email = EXCLUDED.email,
                    hashed_password = EXCLUDED.hashed_password,
                    full_name = EXCLUDED.full_name,
                    country = EXCLUDED.country,
                    role = EXCLUDED.role,
                    is_active = EXCLUDED.is_active,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    analysis_stats = EXCLUDED.analysis_stats,
                    payment_stats = EXCLUDED.payment_stats
            """
            
            pg_cur.execute(insert_query, (
                row_data[0], row_data[1], row_data[2], row_data[3], row_data[4],
                row_data[5], is_active, row_data[7], row_data[8], analysis_stats,
                payment_stats
            ))
            print(f"Inserted/Updated admin: {row_data[1]}")
        
        pg_conn.commit()
        print(f"Transferred {len(admin_rows)} rows to admins")

        # Get data from other tables
        tables = [
            'users', 'betting_codes', 'activities', 'transactions',
            'notifications', 'payments', 'code_analyses', 'analysis_comments',
            'code_views', 'code_purchases', 'code_ratings', 'payment_admin_activities'
        ]

        for table in tables:
            print(f"Transferring {table}...")
            
            # Get all data from SQLite
            sqlite_cur.execute(f"SELECT * FROM {table}")
            rows = sqlite_cur.fetchall()
            
            if not rows:
                print(f"No data in {table}")
                continue

            # Get column names
            sqlite_cur.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in sqlite_cur.fetchall()]
            
            # Prepare INSERT statement
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"""
                INSERT INTO {table} ({columns_str}) 
                VALUES ({placeholders}) 
                ON CONFLICT (id) DO NOTHING
            """
            
            # Insert data into PostgreSQL
            for row in rows:
                # Convert row to list for modification
                row_data = list(row)
                
                # Convert any JSON strings to PostgreSQL JSON
                for i, value in enumerate(row_data):
                    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                        try:
                            row_data[i] = Json(json.loads(value))
                        except:
                            pass
                    # Convert integer to boolean for boolean fields
                    elif isinstance(value, int) and columns[i] in ['is_active', 'is_verified', 'read', 'is_published']:
                        row_data[i] = bool(value)
                
                try:
                    pg_cur.execute(insert_query, row_data)
                    print(f"Inserted row in {table}: {row_data}")
                except Exception as e:
                    print(f"Error inserting row in {table}: {e}")
                    continue
            
            pg_conn.commit()
            print(f"Transferred {len(rows)} rows to {table}")

    except Exception as e:
        print(f"Error: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.commit()
        pg_cur.close()
        pg_conn.close()

if __name__ == "__main__":
    transfer_data() 