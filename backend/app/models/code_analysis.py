from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from sqlalchemy.ext.declarative import declared_attr
from enum import Enum as PyEnum

class AnalysisStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class RiskLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CodeAnalysis(Base):
    __tablename__ = "code_analyses"

    id = Column(Integer, primary_key=True, index=True)
    betting_code_id = Column(Integer, ForeignKey("betting_codes.id"), nullable=False)
    analyst_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    
    # Analysis Details
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    risk_level = Column(Enum(RiskLevel), nullable=True)
    confidence_score = Column(Float, nullable=True)
    expert_analysis = Column(Text, nullable=True)
    ai_analysis = Column(JSON, nullable=True)  # Store AI analysis results
    
    # Validation Results
    odds_validation = Column(JSON, nullable=True)  # Store odds validation details
    stake_validation = Column(JSON, nullable=True)  # Store stake validation details
    pattern_validation = Column(JSON, nullable=True)  # Store code pattern validation
    
    # Market Data
    recommended_price = Column(Float, nullable=True)
    market_category = Column(String, nullable=True)  # e.g., "premium", "standard"
    
    # Country-specific data
    country = Column(String(10), nullable=False)  # Store the country this analysis is for
    bookmaker = Column(String, nullable=False)  # Store the bookmaker
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    betting_code = relationship("BettingCode", back_populates="analysis")
    analyst = relationship("Admin", back_populates="analyses")
    comments = relationship("AnalysisComment", back_populates="analysis", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ai_analysis is None:
            self.ai_analysis = {}
        if self.odds_validation is None:
            self.odds_validation = {}
        if self.stake_validation is None:
            self.stake_validation = {}
        if self.pattern_validation is None:
            self.pattern_validation = {}

    def update_ai_analysis(self, analysis_data: dict):
        """Update AI analysis results"""
        self.ai_analysis = analysis_data
        if 'confidence_score' in analysis_data:
            self.confidence_score = analysis_data['confidence_score']
        if 'risk_level' in analysis_data:
            self.risk_level = analysis_data['risk_level']

    def to_dict(self) -> dict:
        """Convert analysis to dictionary"""
        return {
            'id': self.id,
            'betting_code_id': self.betting_code_id,
            'analyst_id': self.analyst_id,
            'status': self.status,
            'risk_level': self.risk_level,
            'confidence_score': self.confidence_score,
            'expert_analysis': self.expert_analysis,
            'ai_analysis': self.ai_analysis,
            'odds_validation': self.odds_validation,
            'stake_validation': self.stake_validation,
            'pattern_validation': self.pattern_validation,
            'recommended_price': self.recommended_price,
            'market_category': self.market_category,
            'country': self.country,
            'bookmaker': self.bookmaker,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        } 