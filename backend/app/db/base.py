# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base
from app.models.user import User
from app.models.admin import Admin
from app.models.payment import Payment
from app.models.betting_code import BettingCode
from app.models.transaction import Transaction
from app.models.activity import Activity
from app.models.notification import Notification

# Make sure all models are imported here for SQLAlchemy to detect them
__all__ = ["User", "BettingCode", "Activity", "Admin", "Payment", "Transaction", "Notification"]