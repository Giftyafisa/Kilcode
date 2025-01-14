from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    country = Column(String(7), nullable=False)
    phone = Column(String, unique=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, server_default='0', default=False)
    payment_status = Column(String, server_default='pending')
    payment_reference = Column(String, nullable=True)
    status = Column(String(50), server_default='active', nullable=False)

    # Add check constraint for status values
    __table_args__ = (
        CheckConstraint(
            'status IN ("active", "suspended", "pending")',
            name='user_status_check'
        ),
    )

    # Relationships
    betting_codes = relationship("BettingCode", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")