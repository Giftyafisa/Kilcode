from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CodeRating(Base):
    __tablename__ = "code_ratings"

    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey("betting_codes.id", ondelete="CASCADE"), nullable=False)
    rater_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    rating = Column(Float, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    betting_code = relationship("BettingCode", back_populates="ratings")
    rater = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "code_id": self.code_id,
            "rater_id": self.rater_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 