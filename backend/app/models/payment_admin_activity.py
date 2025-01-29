from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class PaymentAdminActivity(Base):
    __tablename__ = "payment_admin_activities"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    action = Column(String, nullable=False)  # approved, rejected, reviewed
    status = Column(String, nullable=False)  # success, failed
    processing_time = Column(Float, nullable=True)  # Time taken to process
    activity_metadata = Column(JSON, nullable=True)  # Additional activity data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    country = Column(String(10), nullable=False)  # Country this activity is for
    note = Column(Text, nullable=True)  # Admin notes or reason for rejection
    payment_method = Column(String, nullable=True)  # Payment method used
    amount = Column(Float, nullable=True)  # Payment amount
    currency = Column(String(3), nullable=True)  # Payment currency
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User who requested withdrawal
    user_balance_before = Column(Float, nullable=True)  # User balance before action
    user_balance_after = Column(Float, nullable=True)  # User balance after action
    
    # Relationships
    admin = relationship("Admin", back_populates="payment_activities")
    payment = relationship("Payment")
    user = relationship("User")
    
    def to_dict(self) -> dict:
        """Convert activity to dictionary"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'payment_id': self.payment_id,
            'action': self.action,
            'status': self.status,
            'processing_time': self.processing_time,
            'activity_metadata': self.activity_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'country': self.country,
            'note': self.note,
            'payment_method': self.payment_method,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'user_id': self.user_id,
            'user_balance_before': float(self.user_balance_before) if self.user_balance_before else None,
            'user_balance_after': float(self.user_balance_after) if self.user_balance_after else None
        }