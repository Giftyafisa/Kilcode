import sqlite3
import json

def update_admin_stats():
    conn = sqlite3.connect('admin.db')
    default_stats = json.dumps({
        'total_processed': 0,
        'approved': 0,
        'rejected': 0,
        'pending': 0,
        'total_amount_processed': 0.0,
        'average_processing_time': 0.0
    })
    
    conn.execute(
        'UPDATE admins SET payment_stats = ?, analysis_stats = ? WHERE email = ?',
        (default_stats, default_stats, 'giftyafisa@gmail.com')
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_admin_stats()
