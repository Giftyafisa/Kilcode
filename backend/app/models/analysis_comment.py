from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AnalysisComment(Base):
    __tablename__ = "analysis_comments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("code_analyses.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    analysis = relationship("CodeAnalysis", back_populates="comments")
    admin = relationship("Admin", back_populates="comments")

    def to_dict(self) -> dict:
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'admin_id': self.admin_id,
            'admin_name': self.admin.full_name if self.admin else None,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 