from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String, index=True)  # payment, betting_code, verification
    description = Column(String)
    activity_metadata = Column(JSON)  # Store additional activity-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    country = Column(String)  # For country-specific filtering
    status = Column(String)  # success, pending, failed

    # Relationships
    user = relationship("User", back_populates="activities") 