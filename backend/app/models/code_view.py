from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CodeView(Base):
    __tablename__ = "code_views"

    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey("betting_codes.id", ondelete="CASCADE"), nullable=False)
    viewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    betting_code = relationship("BettingCode", back_populates="views")
    viewer = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "code_id": self.code_id,
            "viewer_id": self.viewer_id,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None
        } 