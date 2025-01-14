from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from enum import Enum

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    COUNTRY_ADMIN = "country_admin"
    CODE_ANALYST = "code_analyst"
    ADMIN = "admin"

class CountryEnum(str, Enum):
    GHANA = "ghana"
    NIGERIA = "nigeria"

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    country = Column(String(10), nullable=False)
    role = Column(String(20), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Analysis statistics
    analysis_stats = Column(JSON, default=lambda: {
        'total_analyzed': 0,
        'approved': 0,
        'rejected': 0,
        'pending': 0,
        'accuracy_rate': 0.0
    })
    
    # Relationships
    analyses = relationship("CodeAnalysis", back_populates="analyst", foreign_keys="CodeAnalysis.analyst_id")
    comments = relationship("AnalysisComment", back_populates="admin")
    verified_codes = relationship("BettingCode", back_populates="admin", foreign_keys="BettingCode.verified_by")

    @property
    def is_super_admin(self):
        return self.role == AdminRole.SUPER_ADMIN.value

    @property
    def is_country_admin(self):
        return self.role == AdminRole.COUNTRY_ADMIN.value

    @property
    def is_code_analyst(self):
        return self.role == AdminRole.CODE_ANALYST.value

    def can_access_country(self, target_country: str) -> bool:
        """Check if admin can access a specific country's data"""
        if self.is_super_admin:
            return True
        return self.country.lower() == target_country.lower()

    def update_analysis_stats(self):
        """Update analysis statistics"""
        if not self.analyses:
            return

        total = len(self.analyses)
        approved = len([a for a in self.analyses if a.status == 'completed'])
        rejected = len([a for a in self.analyses if a.status == 'rejected'])
        pending = len([a for a in self.analyses if a.status == 'pending'])
        
        # Calculate accuracy rate based on completed analyses
        completed_analyses = [a for a in self.analyses if a.status == 'completed']
        if completed_analyses:
            successful = len([a for a in completed_analyses if a.confidence_score >= 80])
            accuracy_rate = (successful / len(completed_analyses)) * 100
        else:
            accuracy_rate = 0

        self.analysis_stats = {
            'total_analyzed': total,
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
            'accuracy_rate': round(accuracy_rate, 2)
        }

    def to_dict(self) -> dict:
        """Convert admin to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'country': self.country,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'analysis_stats': self.analysis_stats
        }