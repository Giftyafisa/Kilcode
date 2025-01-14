from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
from sqlalchemy.sql import func

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    currency = Column(String)
    reference = Column(String)
    status = Column(String)
    payment_method = Column(String)
    payment_data = Column(JSON)
    type = Column(String, default="registration")  # registration, betting, withdrawal
    verified_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    phone = Column(String, nullable=True)  # For mobile money payments
    
    # Relationships
    user = relationship("User", back_populates="payments")
    admin = relationship("Admin", foreign_keys=[verified_by])