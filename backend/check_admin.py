from sqlalchemy.orm import Session
from app.db.admin_session import AdminSessionLocal
from app.crud import admin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_admin():
    """Check if admin exists in database"""
    db = AdminSessionLocal()
    try:
        # Check if admin exists
        admin_user = admin.get_by_email(db, email="giftyafisa@gmail.com")
        if admin_user:
            logger.info(f"Admin found: {admin_user.email}")
            logger.info(f"Admin details: id={admin_user.id}, role={admin_user.role}, country={admin_user.country}")
        else:
            logger.warning("Admin not found!")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin() 