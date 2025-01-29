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
        # Get data from each table
        tables = [
            'users', 'admins', 'betting_codes', 'activities', 'transactions',
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
            insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
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
                
                try:
                    pg_cur.execute(insert_query, row_data)
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